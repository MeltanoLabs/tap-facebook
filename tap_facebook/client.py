"""REST client handling, including Facebook stream base classes."""

from __future__ import annotations

import json
import sys
import time
import typing as t
from http import HTTPStatus
from urllib.parse import urlparse

import facebook_business.adobjects.user as fb_user
import pendulum
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
from nekt_singer_sdk.authenticators import BearerTokenAuthenticator
from nekt_singer_sdk.custom_logger import user_logger
from nekt_singer_sdk.exceptions import RetriableAPIError
from nekt_singer_sdk.helpers.jsonpath import extract_jsonpath
from nekt_singer_sdk.streams import REPLICATION_FULL_TABLE, RESTStream
from nekt_singer_sdk.streams.core import Stream

from tap_facebook.api_helper import has_reached_api_limit, sleep_if_rate_limited

# Common Facebook API error codes
RATE_LIMIT_ERROR_CODE = 80004

if t.TYPE_CHECKING:
    import requests


class FacebookStream(RESTStream):
    """facebook stream class."""

    # add account id in the url
    # path and fields will be added to this url in streams.pys

    api_sleep_time = 60
    page_size = 25

    @property
    def url_base(self) -> str:
        version: str = self.config["api_version"]
        account_id: str = self.config["account_id"]
        return f"https://graph.facebook.com/{version}/act_{account_id}"

    records_jsonpath = "$.data[*]"  # Or override `parse_response`.
    next_page_token_jsonpath = "$.paging.cursors.after"  # noqa: S105

    tolerated_http_errors: list[int] = []  # noqa: RUF012

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config["access_token"],
        )

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: t.Any | None,  # noqa: ARG002, ANN401
    ) -> t.Any | None:  # noqa: ANN401
        """Return a token for identifying next page or None if no more pages.

        Args:
            response: The HTTP ``requests.Response`` object.
            previous_token: The previous page token value.

        Returns:
            The next pagination token.
        """
        if not self.next_page_token_jsonpath:
            return response.headers.get("X-Next-Page", None)

        all_matches = extract_jsonpath(
            self.next_page_token_jsonpath,
            response.json(),
        )
        return next(iter(all_matches), None)

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {"limit": self.page_size}
        if next_page_token is not None:
            params["after"] = next_page_token

        return params

    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response.

        Raises:
            FatalAPIError: If the request is not retriable.
            RetriableAPIError: If the request is retriable.
        """
        if response.status_code == HTTPStatus.OK:
            should_sleep = has_reached_api_limit(
                headers=response.headers,
                account_id=self.config.get("account_id"),
            )
            # if should_sleep:
            #     internal_logger.warning(
            #         f"Call count limit nearing threshold of {CALL_THRESHOLD_PERCENTAGE}%, sleeping for {self.api_sleep_time} seconds..."
            #     )
            #     sleep(self.api_sleep_time)
            #     self.api_sleep_time = min(self.api_sleep_time * 2, 300)  # Double the sleep time, but cap it at 5min
            # else:
            #     # Reset sleep time
            #     self.api_sleep_time = 60

            return

        full_path = urlparse(response.url).path
        if HTTPStatus.BAD_REQUEST <= response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            msg = (
                f"{response.status_code} Client Error: "
                f"{response.content!s} (Reason: {response.reason}) for path: {full_path}"
            )
            # Retry on reaching rate limit
            if (
                response.status_code == HTTPStatus.BAD_REQUEST and "too many calls" in str(response.content).lower()
            ) or (
                response.status_code == HTTPStatus.BAD_REQUEST
                and "request limit reached" in str(response.content).lower()
            ):
                # in case it already exceeded the limit, parse the headers to check if there's any suggested reset time to sleep
                has_reached_api_limit(
                    headers=response.headers,
                    account_id=self.config.get("account_id"),
                )
                user_logger.warning(f"[{self.name}] {msg}")
                raise RetriableAPIError(msg, response)

            user_logger.error(f"[{self.name}] {msg}")
            sys.exit(1)

        if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            msg = (
                f"{response.status_code} Server Error: "
                f"{response.content!s} (Reason: {response.reason}) for path: {full_path}"
            )
            user_logger.warning(f"[{self.name}] {msg}")
            raise RetriableAPIError(msg, response)

    def backoff_max_tries(self) -> int:
        """The number of attempts before giving up when retrying requests.

        Setting to None will retry indefinitely.

        Returns:
            int: limit
        """
        return 10


class FacebookSDKStream(Stream):
    """Base class for Facebook streams using Facebook Business SDK.

    This class provides common functionality for streams that use the
    Facebook Business SDK, including client initialization, error handling,
    and retry logic.
    """

    api_sleep_time = 60

    def _initialize_client(self) -> None:
        """Initialize the Facebook Business SDK client."""
        self.facebook_api = FacebookAdsApi.init(
            access_token=self.config["access_token"],
            timeout=300,
            api_version=self.config["api_version"],
        )
        self.facebook_id = fb_user.User(fbid="me")

        account_id = self.config["account_id"]
        self.account = AdAccount(f"act_{account_id}").api_get()
        if not self.account:
            user_logger.error(f"[{self.name}] Couldn't find account with id {account_id}")
            sys.exit(1)

    def _handle_facebook_request_error(self, fb_err: FacebookRequestError, retry_count: int, max_retries: int) -> bool:
        """Handle FacebookRequestError with common retry logic.

        Args:
            fb_err: The FacebookRequestError that occurred
            retry_count: Current retry attempt number
            max_retries: Maximum number of retries allowed

        Returns:
            True if should retry, False if should exit/raise
        """
        if fb_err.http_status() == HTTPStatus.BAD_REQUEST and fb_err.api_error_code() == RATE_LIMIT_ERROR_CODE:
            # Handle rate limiting
            if retry_count <= max_retries:
                slept = sleep_if_rate_limited(headers=fb_err.http_headers(), account_id=self.config["account_id"])
                if slept:
                    return True
                wait_time = min(60 * retry_count, 300)  # Progressive backoff, max 5 min
                user_logger.warning(
                    f"[{self.name}] Rate limit exceeded. Waiting {wait_time}s "
                    f"before retry {retry_count}/{max_retries}..."
                )
                time.sleep(wait_time)
                return True
        elif fb_err.http_status() >= HTTPStatus.INTERNAL_SERVER_ERROR:
            # Handle server errors
            if retry_count <= max_retries:
                user_logger.warning(
                    f"[{self.name}] Server error: {fb_err.api_error_message()}. "
                    f"Retry {retry_count}/{max_retries} in 60s..."
                )
                time.sleep(60)
                return True

        # Don't retry client errors or if max retries reached
        user_logger.error(
            f"[{self.name}] Error: {fb_err.api_error_message()}. "
            f"Code: {fb_err.api_error_code()}, Subcode: {fb_err.api_error_subcode()}"
        )
        return False


class IncrementalFacebookStream(FacebookStream):
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {"limit": 25}
        if next_page_token is not None:
            params["after"] = next_page_token
        if self.replication_key:
            if self.replication_method == REPLICATION_FULL_TABLE:
                ts = pendulum.parse(self.config["start_date"])
            else:
                ts = pendulum.parse(self.get_starting_replication_key_value(context))
            params["filtering"] = json.dumps(
                [
                    {
                        "field": f"{self.filter_entity}.{self.replication_key}",
                        "operator": "GREATER_THAN",
                        "value": int(ts.timestamp()),
                    },
                ],
            )

        return params

"""REST client handling, including facebookStream base class."""

from __future__ import annotations

import abc
import json
import typing as t
from http import HTTPStatus
from urllib.parse import urlparse
import random

import pendulum
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context


class FacebookStream(RESTStream):
    """facebook stream class."""

    # add account id in the url
    # path and fields will be added to this url in streams.pys

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._current_account_id = None

    @property
    def url_base(self) -> str:
        version: str = self.config["api_version"]
        account_id: str = self.current_account_id
        return f"https://graph.facebook.com/{version}/act_{account_id}"

    @property
    def current_account_id(self) -> str:
        """Get the current account ID being processed."""
        return self._current_account_id or self.config["account_id"]

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
        context: Context | None,  # noqa: ARG002
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
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response.

        Raises:
            FatalAPIError: If the request is not retriable.
            RetriableAPIError: If the request is retriable.
        """
        full_path = urlparse(response.url).path
        if response.status_code in self.tolerated_http_errors:
            msg = (
                f"{response.status_code} Tolerated Status Code "
                f"(Reason: {response.reason}) for path: {full_path}"
            )
            self.logger.info(msg)
            return

        if HTTPStatus.BAD_REQUEST <= response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            msg = (
                f"{response.status_code} Client Error: "
                f"{response.content!s} (Reason: {response.reason}) for path: {full_path}"
            )
            
            # Check for various rate limit and transient error patterns
            error_content = str(response.content).lower()
            rate_limit_patterns = [
                "too many calls",
                "request limit reached",
                "rate limit exceeded",
                "throttled",
                "quota exceeded",
                "application request limit reached",
                "user request limit reached",
                "ad account request limit reached"
            ]
            
            if any(pattern in error_content for pattern in rate_limit_patterns):
                self.logger.warning(
                    "Rate limit encountered. Will retry with exponential backoff. Error: %s",
                    msg
                )
                raise RetriableAPIError(msg, response)

            raise FatalAPIError(msg)

        if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            msg = (
                f"{response.status_code} Server Error: "
                f"{response.content!s} (Reason: {response.reason}) for path: {full_path}"
            )
            self.logger.warning(
                "Server error encountered. Will retry with exponential backoff. Error: %s",
                msg
            )
            raise RetriableAPIError(msg, response)

    def backoff_max_tries(self) -> int:
        """The number of attempts before giving up when retrying requests.

        Setting to None will retry indefinitely.

        Returns:
            int: limit
        """
        return 20

    def backoff_wait_generator(self):
        """Generate wait times for retries with exponential backoff and jitter.

        Returns:
            Generator yielding wait times in seconds
        """
        base_wait = 1  # Start with 1 second
        max_wait = 300  # Maximum wait of 5 minutes
        factor = 2  # Exponential factor
        
        for attempt in range(self.backoff_max_tries()):
            # Calculate wait time with exponential backoff
            wait_time = min(base_wait * (factor ** attempt), max_wait)
            
            # Add jitter (random variation) to prevent thundering herd
            jitter = random.uniform(0.5, 1.5)
            final_wait = wait_time * jitter
            
            self.logger.info(
                "Retry attempt %d/%d. Waiting %.2f seconds before next attempt.",
                attempt + 1,
                self.backoff_max_tries(),
                final_wait
            )
            yield final_wait

    def get_records(
        self,
        context: Context | None,
    ) -> t.Iterable[dict]:
        """Get records from the stream."""
        # Process accounts - either from account_ids or single account_id
        account_ids_str = self.config.get("account_ids", "")
        accounts_to_process = [aid.strip() for aid in account_ids_str.split(",") if aid.strip()] if account_ids_str else [self.config["account_id"]]
        
        # Remove duplicates while preserving order
        accounts_to_process = list(dict.fromkeys(accounts_to_process))
        
        self.logger.info("Processing accounts: %s", accounts_to_process)

        for account_id in accounts_to_process:
            self.logger.info("Starting to process account: %s", account_id)
            self._current_account_id = account_id
            yield from super().get_records(context)


class IncrementalFacebookStream(FacebookStream, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def filter_entity(self) -> str:
        """The entity to filter on."""

    def get_url_params(
        self,
        context: Context | None,
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
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
            ts = pendulum.parse(self.get_starting_replication_key_value(context))  # type: ignore[arg-type]
            params["filtering"] = json.dumps(
                [
                    {
                        "field": f"{self.filter_entity}.{self.replication_key}",
                        "operator": "GREATER_THAN",
                        "value": int(ts.timestamp()),  # type: ignore[union-attr]
                    },
                ],
            )

        return params

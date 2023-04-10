"""REST client handling, including facebookStream base class."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from urllib.parse import parse_qs, urlparse
from dateutil.parser import parse
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from os import environ

import requests, json
import backoff

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class facebookStream(RESTStream):
    """facebook stream class."""

    # add account id in the url
    # path and fields will be added to this url in streams.pys

    @property
    def url_base(self):
        version = self.config.get("api_version", "")
        account_id = self.config.get("account_id", "")
        if version and account_id:
            base_url = "https://graph.facebook.com/{}/act_{}".format(version, account_id)
        else:
            account_id = environ.get("account_id")
            version = environ.get("api_version")
            base_url = "https://graph.facebook.com/{}/act_{}".format(version, account_id)    
        return base_url

    records_jsonpath = "$.data[*]"  # Or override `parse_response`.
    next_page_token_jsonpath = (
        "$.paging.cursors.after"  # Or override `get_next_page_token`.
    )

    tolerated_http_errors: List[int] = []

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        Returns,
            An authenticator instance.
        """
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("access_token", ""),
        )

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        """Return a token for identifying next page or None if no more pages.

        Args,
            response: The HTTP ``requests.Response`` object.
            previous_token: The previous page token value.

        Returns,
            The next pagination token.
        """
        if self.next_page_token_jsonpath:
            all_matches = extract_jsonpath(
                self.next_page_token_jsonpath, response.json()
            )
            first_match = next(iter(all_matches), None)
            next_page_token = first_match
        else:
            next_page_token = response.headers.get("X-Next-Page", None)

        return next_page_token

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args,
            context: The stream context.
            next_page_token: The next page index or value.

        Returns,
            A dictionary of URL query parameters.
        """
        params: dict = {}
        params["limit"] = 25
        if next_page_token is not None:
            params["after"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        return params

    def prepare_request_payload(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args,
            context: The stream context.
            next_page_token: The next page index or value.

        Returns,
            A dictionary with the JSON body for a POST requests.
        """
        return None

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

        if 400 <= response.status_code < 500:
            msg = (
                f"{response.status_code} Client Error: "
                f"{str(response.content)} (Reason: {response.reason}) for path: {full_path}"
            )
            # Retry on reaching rate limit
            if (
                    response.status_code == 403
                    and "rate limit exceeded" in str(response.content).lower()
            ):
                # Update token
                self.authenticator.get_next_auth_token()
                # Raise an error to force a retry with the new token.
                raise RetriableAPIError(msg, response)

            # Retry on reaching second rate limit
            if (
                    response.status_code == 403
                    and "secondary rate limit" in str(response.content).lower()
            ):
                # Wait about a minute and retry
                time.sleep(60 + 30 * random.random())
                raise RetriableAPIError(msg, response)

            # The GitHub API randomly returns 401 Unauthorized errors, so we try again.
            if (
                    response.status_code == 401
                    # if the token is invalid, we are also told about it
                    and not "bad credentials" in str(response.content).lower()
            ):
                raise RetriableAPIError(msg, response)

            raise FatalAPIError(msg)

        elif 500 <= response.status_code < 600:
            msg = (
                f"{response.status_code} Server Error: "
                f"{str(response.content)} (Reason: {response.reason}) for path: {full_path}"
            )
            raise RetriableAPIError(msg, response)

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args,
            response: The HTTP ``requests.Response`` object.

        Yields,
            Each record from the source.
        """
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def backoff_wait_generator(self) -> Callable[..., Generator[int, Any, None]]:
        return backoff.constant(interval=1)
    


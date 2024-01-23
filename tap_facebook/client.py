"""REST client handling, including facebookStream base class."""

from __future__ import annotations

import json
import typing as t
from http import HTTPStatus
from urllib.parse import urlparse

import pendulum
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

if t.TYPE_CHECKING:
    import requests


class FacebookStream(RESTStream):
    """facebook stream class."""

    # add account id in the url
    # path and fields will be added to this url in streams.pys

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
            # Retry on reaching rate limit
            if (
                response.status_code == HTTPStatus.BAD_REQUEST
                and "too many calls" in str(response.content).lower()
            ) or (
                response.status_code == HTTPStatus.BAD_REQUEST
                and "request limit reached" in str(response.content).lower()
            ):
                raise RetriableAPIError(msg, response)

            raise FatalAPIError(msg)

        if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            msg = (
                f"{response.status_code} Server Error: "
                f"{response.content!s} (Reason: {response.reason}) for path: {full_path}"
            )
            raise RetriableAPIError(msg, response)

    def backoff_max_tries(self) -> int:
        """The number of attempts before giving up when retrying requests.

        Setting to None will retry indefinitely.

        Returns:
            int: limit
        """
        return 20


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
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
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

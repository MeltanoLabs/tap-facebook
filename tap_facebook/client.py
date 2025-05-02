"""REST client handling, including facebookStream base class."""

from __future__ import annotations

import abc
import json
import typing as t
from http import HTTPStatus
from urllib.parse import urlparse

import pendulum
import random
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

        status_code = response.status_code

        try:
            error_json = response.json().get("error", {})
            self.logger.debug("Full Facebook error JSON: %s", json.dumps(error_json, indent=2))
        except Exception:
            error_json = {}

        error_code = error_json.get("code")
        error_message = error_json.get("message", "")
        is_transient = error_json.get("is_transient", False)

        retryable_codes = {1, 2, 4, 17, 32, 341, 368, 613}

        if status_code in self.tolerated_http_errors:
            self.logger.info(
                "%s Tolerated Status Code (Reason: %s) for path: %s",
                status_code, response.reason, full_path
            )
            return

        if (
            status_code >= 500
            or error_code in retryable_codes
            or is_transient
            or "temporarily" in error_message.lower()
            or "too many calls" in error_message.lower()
            or "request limit" in error_message.lower()
        ):
            self.logger.warning(
                "Retryable Facebook error (code %s): %s",
                error_code,
                error_message,
            )
            msg = (
                f"Retriable error {status_code} (code {error_code}): "
                f"{error_message} | path: {full_path}"
            )
            raise RetriableAPIError(msg, response)

        if 400 <= status_code < 500:
            msg = (
                f"{status_code} Client Error: {error_message} "
                f"(Reason: {response.reason}) for path: {full_path}"
            )
            raise FatalAPIError(msg)

        if status_code >= 500:
            msg = (
                f"{status_code} Server Error: {error_message} "
                f"(Reason: {response.reason}) for path: {full_path}"
            )
            raise RetriableAPIError(msg, response)

    def backoff_max_tries(self) -> int:
        """The number of attempts before giving up when retrying requests.

        Setting to None will retry indefinitely.

        Returns:
            int: limit
        """
        return 20

    def backoff_wait_generator(self) -> t.Iterator[float]:
        max_retries = self.backoff_max_tries()
        base = 2
        max_sleep = 300  # 5 minutes max sleep
        for i in range(max_retries):
            wait = min(base ** i, max_sleep)
            jitter = random.uniform(0, 1)
            wait += jitter
            self.logger.warning(f"Retry attempt {i+1}/{max_retries} - sleeping for {wait} seconds")
            yield wait

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

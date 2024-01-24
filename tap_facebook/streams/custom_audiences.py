"""Stream classes for CustomAudiences."""

from __future__ import annotations

import typing as t

from singer_sdk.streams.core import REPLICATION_INCREMENTAL
from singer_sdk.typing import (
    BooleanType,
    DateTimeType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream


class CustomAudiencesInternal(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/custom-audience/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    @property
    def columns(self) -> list[str]:
        return [
            "account_id",
            "id",
            "approximate_count_lower_bound",
            "approximate_count_upper_bound",
            "time_updated",
            "time_created",
            "customer_file_source",
            "data_source",
            "delivery_status",
            "description",
        ]

    name = "customaudiencesinternal"
    tap_stream_id = "customaudiencesinternal"
    primary_keys = ["id"]  # noqa: RUF012
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "time_updated"

    schema = PropertiesList(
        Property("account_id", StringType),
        Property("id", StringType),
        Property("approximate_count_lower_bound", IntegerType),
        Property("approximate_count_upper_bound", IntegerType),
        Property("time_updated", IntegerType),
        Property("time_created", IntegerType),
        Property("time_content_updated", StringType),
        Property("customer_file_source", StringType),
        Property("data_source", ObjectType()),
        Property("delivery_status", ObjectType()),
        Property("description", StringType),
        Property("external_event_source_automatic_matching_fields", StringType),
        Property("external_event_source_can_proxy", BooleanType),
        Property("external_event_source_code", StringType),
        Property("external_event_source_creation_time", DateTimeType),
        Property("external_event_source_data_use_setting", StringType),
        Property("external_event_source_enable_automatic_matching", BooleanType),
        Property("external_event_source_first_party_cookie_status", StringType),
        Property("external_event_source_id", IntegerType),
        Property("external_event_source_is_created_by_business", BooleanType),
        Property("external_event_source_is_crm", BooleanType),
        Property("external_event_source_is_unavailable", BooleanType),
        Property("external_event_source_last_fired_time", DateTimeType),
        Property("external_event_source_name", StringType),
        Property("external_event_source", StringType),
        Property("lookalike_country", StringType),
        Property("lookalike_is_financial_service", BooleanType),
        Property("lookalike_origin_event_name", StringType),
        Property("lookalike_origin_event_source_name", StringType),
        Property("lookalike_product_set_name", StringType),
        Property("lookalike_ratio", StringType),
        Property("lookalike_starting_ratio", StringType),
        Property("lookalike_type", StringType),
        Property("is_value_based", BooleanType),
        Property("operation_status", StringType),
        Property("permission_for_actions", StringType),
        Property("pixel_id", IntegerType),
        Property("retention_days", IntegerType),
        Property("rule", StringType),
        Property("subtype", StringType),
        Property("rule_aggregation", StringType),
        Property("opt_out_link", StringType),
        Property("name", StringType),
    ).to_dict()

    @property
    def path(self) -> str:
        return f"/customaudiences?fields={self.columns}"


class CustomAudiences(CustomAudiencesInternal):
    """https://developers.facebook.com/docs/marketing-api/reference/custom-audience/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    # Add rule column
    @property
    def columns(self) -> list[str]:
        return [*super().columns, "rule"]

    name = "customaudiences"
    tap_stream_id = "customaudiences"

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

        return params

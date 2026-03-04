"""Stream classes for CustomAudiences."""

from __future__ import annotations

import typing as t

from nekt_singer_sdk.typing import (
    BooleanType,
    IntegerType,
    NumberType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream


class CustomAudiences(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/custom-audience/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    name = "customaudiences"
    primary_keys = ["id"]  # noqa: RUF012

    @property
    def path(self) -> str:
        return f"/customaudiences?fields={self.columns}"

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
            "lookalike_spec",
            "is_value_based",
            "operation_status",
            "permission_for_actions",
            "pixel_id",
            "retention_days",
            "subtype",
            "rule_aggregation",
            "opt_out_link",
            "name",
        ]

    schema = PropertiesList(
        Property(
            "account_id",
            StringType,
            description="ID of the ad account that owns the custom audience",
        ),
        Property(
            "id",
            StringType,
            description="Unique ID of the custom audience",
        ),
        Property(
            "approximate_count_lower_bound",
            IntegerType,
            description="Lower bound of approximate audience size",
        ),
        Property(
            "approximate_count_upper_bound",
            IntegerType,
            description="Upper bound of approximate audience size",
        ),
        Property(
            "time_updated",
            IntegerType,
            description="Unix timestamp when the audience was last updated",
        ),
        Property(
            "time_created",
            IntegerType,
            description="Unix timestamp when the audience was created",
        ),
        Property(
            "time_content_updated",
            StringType,
            description="When the audience content was last updated",
        ),
        Property(
            "customer_file_source",
            StringType,
            description="Source of the customer file (e.g. USER_PROVIDED_ONLY, PARTNER_PROVIDED_ONLY)",
        ),
        Property(
            "data_source",
            ObjectType(
                Property("type", StringType, description="Data source type"),
                Property("sub_type", StringType, description="Data source sub-type"),
            ),
            description="Data source type and sub-type for the audience",
        ),
        Property(
            "delivery_status",
            ObjectType(
                Property("code", IntegerType, description="Delivery status code"),
                Property("description", StringType, description="Delivery status description"),
            ),
            description="Delivery status code and description",
        ),
        Property(
            "description",
            StringType,
            description="Description of the custom audience",
        ),
        Property(
            "lookalike_spec",
            ObjectType(
                Property("country", StringType, description="Country for lookalike audience"),
                Property("is_financial_service", BooleanType, description="Whether lookalike is for financial service"),
                Property("origin_event_name", StringType, description="Origin event name for lookalike"),
                Property("origin_event_source_name", StringType, description="Origin event source name"),
                Property("product_set_name", StringType, description="Product set name for lookalike"),
                Property("ratio", NumberType, description="Lookalike audience ratio"),
                Property("starting_ratio", NumberType, description="Lookalike starting ratio"),
                Property("type", StringType, description="Lookalike spec type"),
            ),
            description="Specification for lookalike audience (country, ratio, origin)",
        ),
        Property(
            "is_value_based",
            BooleanType,
            description="Whether this is a value-based custom audience",
        ),
        Property(
            "operation_status",
            ObjectType(
                Property("code", IntegerType, description="Operation status code"),
                Property("description", StringType, description="Operation status description"),
            ),
            description="Operation status code and description",
        ),
        Property(
            "pixel_id",
            StringType,
            description="Facebook Pixel ID associated with the audience",
        ),
        Property(
            "retention_days",
            IntegerType,
            description="Number of days to retain the audience",
        ),
        Property(
            "subtype",
            StringType,
            description="Subtype of the custom audience",
        ),
        Property(
            "rule_aggregation",
            StringType,
            description="How rules are aggregated (AND or OR)",
        ),
        Property(
            "opt_out_link",
            StringType,
            description="Opt-out link for the audience",
        ),
        Property(
            "name",
            StringType,
            description="Name of the custom audience",
        ),
    ).to_dict()

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

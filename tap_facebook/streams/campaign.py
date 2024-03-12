"""Stream class for Campaigns."""

from __future__ import annotations

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.streams.core import REPLICATION_INCREMENTAL

from tap_facebook.client import IncrementalFacebookStream


class CampaignStream(IncrementalFacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = [  # noqa: RUF012
        "id",
        "account_id",
        "updated_time",
        "created_time",
        "start_time",
        "stop_time",
        "name",
        "buying_type",
        "budget_remaining",
        "can_create_brand_lift_study",
        "can_use_spend_cap",
        "configured_status",
        "effective_status",
        "has_secondary_skadnetwork_reporting",
        "is_skadnetwork_attribution",
        "objective",
        "primary_attribution",
        "smart_promotion_type",
        "source_campaign_id",
        "special_ad_categories",
        "special_ad_category",
        "special_ad_category_country",
        "spend_cap",
        "status",
        "topline_id",
        "boosted_object_id",
        "pacing_type",
        "budget_rebalance_flag",
        "bid_strategy",
        "lifetime_budget",
        "daily_budget",
        "last_budget_toggling_time",
    ]

    columns_remaining = [  # noqa: RUF012
        "adlabels",
        "issues_info",
        "recommendations",
    ]

    name = "campaigns"
    filter_entity = "campaign"

    path = f"/campaigns?fields={columns}"
    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    tap_stream_id = "campaigns"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "updated_time"

    PropertiesList = th.PropertiesList
    Property = th.Property
    ObjectType = th.ObjectType
    DateTimeType = th.DateTimeType
    StringType = th.StringType
    ArrayType = th.ArrayType(StringType)
    BooleanType = th.BooleanType
    IntegerType = th.IntegerType

    schema = PropertiesList(
        Property("name", StringType),
        Property("objective", StringType),
        Property("id", StringType),
        Property("account_id", StringType),
        Property("effective_status", StringType),
        Property("buying_type", StringType),
        Property("can_create_brand_lift_study", BooleanType),
        Property("can_use_spend_cap", BooleanType),
        Property("configured_status", StringType),
        Property("has_secondary_skadnetwork_reporting", BooleanType),
        Property("is_skadnetwork_attribution", BooleanType),
        Property("primary_attribution", StringType),
        Property("smart_promotion_type", StringType),
        Property("pacing_type", ArrayType),
        Property("source_campaign_id", StringType),
        Property("boosted_object_id", StringType),
        Property("special_ad_categories", ArrayType),
        Property("special_ad_category", StringType),
        Property("status", StringType),
        Property("topline_id", StringType),
        Property("spend_cap", StringType),
        Property("budget_remaining", StringType),
        Property("daily_budget", IntegerType),
        Property("start_time", StringType),
        Property("stop_time", StringType),
        Property("updated_time", StringType),
        Property("created_time", StringType),
        Property(
            "adlabels",
            th.ArrayType(
                Property(
                    "items",
                    ObjectType(
                        Property("id", StringType),
                        Property("name", StringType),
                        Property("created_time", DateTimeType),
                        Property("updated_time", DateTimeType),
                    ),
                ),
            ),
        ),
        Property("budget_rebalance_flag", BooleanType),
        Property("bid_strategy", StringType),
        Property("ad_strategy_group_id", IntegerType),
        Property("ad_strategy_id", IntegerType),
        Property("lifetime_budget", StringType),
        Property("last_budget_toggling_time", StringType),
        Property("daily_budget", IntegerType),
        Property("special_ad_category_country", ArrayType),
    ).to_dict()

    def post_process(
        self,
        row: dict,
        context: dict | None,  # noqa: ARG002
    ) -> dict:
        daily_budget = row.get("daily_budget")
        row["daily_budget"] = int(daily_budget) if daily_budget is not None else None
        return row

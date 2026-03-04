"""Stream class for Campaigns."""

from __future__ import annotations

from nekt_singer_sdk import typing as th  # JSON Schema typing helpers
from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL

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
        Property(
            "name",
            StringType,
            description="Name of the campaign",
        ),
        Property(
            "objective",
            StringType,
            description="Campaign objective (e.g. OUTCOME_AWARENESS, OUTCOME_ENGAGEMENT, OUTCOME_LEADS)",
        ),
        Property(
            "id",
            StringType,
            description="ID of the campaign",
        ),
        Property(
            "account_id",
            StringType,
            description="ID of the ad account",
        ),
        Property(
            "effective_status",
            StringType,
            description="Effective status considering account and child objects",
        ),
        Property(
            "buying_type",
            StringType,
            description="Buying type (e.g. AUCTION, RESERVED)",
        ),
        Property(
            "can_create_brand_lift_study",
            BooleanType,
            description="Whether a brand lift study can be created",
        ),
        Property(
            "can_use_spend_cap",
            BooleanType,
            description="Whether spend cap can be used",
        ),
        Property(
            "configured_status",
            StringType,
            description="User-configured status of the campaign",
        ),
        Property(
            "has_secondary_skadnetwork_reporting",
            BooleanType,
            description="Whether SKAdNetwork reporting is enabled",
        ),
        Property(
            "is_skadnetwork_attribution",
            BooleanType,
            description="Whether SKAdNetwork attribution is used",
        ),
        Property(
            "primary_attribution",
            StringType,
            description="Primary attribution setting",
        ),
        Property(
            "smart_promotion_type",
            StringType,
            description="Smart promotion type",
        ),
        Property(
            "pacing_type",
            ArrayType,
            description="Pacing type for campaign delivery",
        ),
        Property(
            "source_campaign_id",
            StringType,
            description="ID of the source campaign if this was copied",
        ),
        Property(
            "boosted_object_id",
            StringType,
            description="ID of the boosted object (e.g. page, post)",
        ),
        Property(
            "special_ad_categories",
            ArrayType,
            description="Special ad categories (e.g. housing, employment, credit)",
        ),
        Property(
            "special_ad_category",
            StringType,
            description="Primary special ad category",
        ),
        Property(
            "status",
            StringType,
            description="Status of the campaign (ACTIVE, PAUSED, etc.)",
        ),
        Property(
            "topline_id",
            StringType,
            description="Topline ID for the campaign",
        ),
        Property(
            "spend_cap",
            StringType,
            description="Spend cap for the campaign",
        ),
        Property(
            "budget_remaining",
            StringType,
            description="Remaining budget",
        ),
        Property(
            "daily_budget",
            IntegerType,
            description="Daily budget in smallest currency unit",
        ),
        Property(
            "start_time",
            StringType,
            description="Campaign start time",
        ),
        Property(
            "stop_time",
            StringType,
            description="Campaign stop time",
        ),
        Property(
            "updated_time",
            StringType,
            description="When the campaign was last updated",
        ),
        Property(
            "created_time",
            StringType,
            description="When the campaign was created",
        ),
        Property(
            "adlabels",
            th.ArrayType(
                Property(
                    "items",
                    ObjectType(
                        Property("id", StringType, description="Ad label ID"),
                        Property("name", StringType, description="Ad label name"),
                        Property("created_time", DateTimeType, description="Ad label created time"),
                        Property("updated_time", DateTimeType, description="Ad label updated time"),
                    ),
                ),
            ),
            description="Ad labels associated with this campaign",
        ),
        Property(
            "budget_rebalance_flag",
            BooleanType,
            description="Whether budget rebalance is enabled",
        ),
        Property(
            "bid_strategy",
            StringType,
            description="Bid strategy for the campaign",
        ),
        Property(
            "ad_strategy_group_id",
            IntegerType,
            description="Ad strategy group ID",
        ),
        Property(
            "ad_strategy_id",
            IntegerType,
            description="Ad strategy ID",
        ),
        Property(
            "lifetime_budget",
            StringType,
            description="Lifetime budget in smallest currency unit",
        ),
        Property(
            "last_budget_toggling_time",
            StringType,
            description="When budget was last toggled",
        ),
        Property(
            "daily_budget",
            IntegerType,
            description="Daily budget in smallest currency unit",
        ),
        Property(
            "special_ad_category_country",
            ArrayType,
            description="Countries for special ad category",
        ),
    ).to_dict()

    def post_process(
        self,
        row: dict,
        context: dict | None,  # noqa: ARG002
    ) -> dict:
        daily_budget = row.get("daily_budget")
        row["daily_budget"] = int(daily_budget) if daily_budget is not None else None
        return row

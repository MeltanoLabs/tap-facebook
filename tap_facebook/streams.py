"""Stream type classes for tap-facebook."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_facebook.client import facebookStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

# ads insights stream
class adsinsightStream(facebookStream):
    name = "adsinsights"
    path = "/insights"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "ads_insights.json"
    tap_stream_id = "adsinsights"
    #replication_key = "created_time"

# ads stream
class adsStream(facebookStream):
    columns = ["id",
               "account_id",
               "adset_id",
               "campaign_id",
               "bid_type",
               "status",
               "updated_time",
               "created_time",
               "name",
               "effective_status",
               "last_updated_by_app_id",
               "source_ad_id",
               "creative",
               "tracking_specs",
               "conversion_specs"]

    columns_remaining = ["adlabels", "recommendations"]

    name = "ads"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "ads.json"
    tap_stream_id = "ads"

# adsets stream
class adsetsStream(facebookStream):
    columns = ["id",
               "account_id",
               "campaign_id",
               "updated_time",
               "created_time",
               "start_time",
               "end_time",
               "name",
               "effective_status",
               "daily_budget",
               "budget_remaining",
               "lifetime_budget",
               "configured_status",
               "promoted_object",
               "attribution_spec",
               "billing_event",
               "campaign_attribution",
               "destination_type",
               "is_dynamic_creative",
               "learning_stage_info",
               "lifetime_imps",
               "multi_optimization_goal_weight",
               "optimization_goal",
               "optimization_sub_event",
               "pacing_type",
               "recurring_budget_semantics",
               "source_adset_id",
               "status",
               "targeting",
               "targeting_optimization_types",
               "use_new_app_click"]

    columns_remaining = ["adlabels",
                         "adset_schedule",
                         "asset_feed_id",
                         "attribution_spec",
                         "bid_adjustments",
                         "bid_amount",
                         "bid_constraints",
                         "bid_info",
                         "bid_strategy",
                         "contextual_bundling_spec",
                         "creative_sequence",
                         "daily_min_spend_target",
                         "spend_cap",
                         "frequency_control_specs",
                         "instagram_actor_id",
                         "issues_info",
                         "lifetime_min_spend_target",
                         "lifetime_spend_cap",
                         "recommendations",
                         "review_feedback",
                         "rf_prediction_id",
                         "time_based_ad_rotation_id_blocks",
                         "time_based_ad_rotation_intervals"]

    name = "adsets"
    path = "/adsets?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adsets.json"
    tap_stream_id = "adsets"

# campaigns stream
class campaignStream(facebookStream):
    columns = ["id",
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
               "promoted_object",
               "smart_promotion_type",
               "source_campaign_id",
               "special_ad_categories",
               "special_ad_category",
               "special_ad_category_country",
               "spend_cap",
               "status",
               "topline_id"]

    columns_remaining = ["ad_strategy_group_id",
                         "ad_strategy_id",
                         "adlabels",
                         "boosted_object_id",
                         "daily_budget",
                         "issues_info",
                         "last_budget_toggling_time",
                         "lifetime_budget",
                         "pacing_type",
                         "recommendations"]

    name = "campaigns"
    path = "/campaigns?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "campaigns.json"
    tap_stream_id = "campaigns"

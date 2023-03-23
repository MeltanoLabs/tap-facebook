"""Stream type classes for tap-facebook."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_facebook.client import facebookStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


#TODO  we need to add the streams for the below tables,
# CREATIVE_HISTORY,FIVETRAN_AUDIT, FREQUENCY_CONTROL, PACING_TYPE, REACH_FREQUENCY
# TARGETING_OPTIMIZATION_TYPES,ACCOUNT_HISTORY



# ads insights stream
class adsinsightStream(facebookStream):
    columns = ["account_id",
               "ad_id",
               "adset_id",
               "campaign_id",
               "ad_name",
               "adset_name",
               "campaign_name",
               "date_start",
               "date_stop",
               "clicks",
               "website_ctr",
               "unique_inline_link_click_ctr",
               "frequency",
               "account_name",
               "unique_inline_link_clicks",
               "cost_per_unique_action_type",
               "inline_post_engagement",
               "inline_link_clicks",
               "cpc",
               "cost_per_unique_inline_link_click",
               "cpm",
               "canvas_avg_view_time",
               "cost_per_inline_post_engagement",
               "inline_link_click_ctr",
               "cpp",
               "cost_per_action_type",
               "unique_link_clicks_ctr",
               "spend",
               "cost_per_unique_click",
               "unique_clicks",
               "social_spend",
               "reach",
               "canvas_avg_view_percent",
               "objective",
               "quality_ranking",
               "engagement_rate_ranking",
               "conversion_rate_ranking",
               "impressions",
               "unique_ctr",
               "cost_per_inline_link_click",
               "ctr"]

    columns_remaining = [
        "unique_actions",
        "actions",
        "action_values",
        "outbound_clicks",
        "unique_outbound_clicks",
        "video_30_sec_watched_actions",
        "video_p25_watched_actions",
        "video_p50_watched_actions",
        "video_p75_watched_actions",
        "video_p100_watched_actions"]

    name = "adsinsights"
    path = "/insights?level=ad&fields={}".format(columns)
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
               "bid_info",
               "status",
               "updated_time",
               "created_time",
               "name",
               "effective_status",
               "last_updated_by_app_id",
               "source_ad_id",
               "creative",
               "tracking_specs",
               "conversion_specs",
               "recommendations"]

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
               "status"]

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
               "topline_id",
               "boosted_object_id",
               "pacing_type"]

    columns_remaining = ["ad_strategy_group_id",
                         "ad_strategy_id",
                         "adlabels",
                         "daily_budget",
                         "issues_info",
                         "last_budget_toggling_time",
                         "lifetime_budget",
                         "recommendations"]

    name = "campaigns"
    path = "/campaigns?fields={}".format(columns)
    schema_filepath = SCHEMAS_DIR / "campaigns.json"
    tap_stream_id = "campaigns"

class adhistoryStream(facebookStream):
    columns = ["id",
               "account_id",
               "adset_id",
               "campaign_id",
               "creative",
               "bid_amount",
               "bid_type",
               "bid_info",
               "status",
               "conversion_domain",
               "configured_status",
               "effective_status",
               "updated_time",
               "created_time",
               "name",
               "last_updated_by_app_id",
               "source_ad_id"]

    name = "ad_history"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adhistory.json"
    tap_stream_id = "ad_history"

class campaignhistoryStream(facebookStream):
    columns = ["id",
               "account_id",
               "updated_time",
               "created_time",
               "start_time",
               "stop_time",
               "name",
               "bid_strategy",
               "boosted_object_id",
               "ad_strategy_group_id",
               "ad_strategy_id",
               "budget_rebalance_flag",
               "buying_type",
               "daily_budget",
               "lifetime_budget",
               "budget_remaining",
               "can_create_brand_lift_study",
               "can_use_spend_cap",
               "configured_status",
               "effective_status",
               "has_secondary_skadnetwork_reporting",
               "is_skadnetwork_attribution",
               "last_budget_toggling_time",
               "objective",
               "pacing_type",
               "promoted_object_application_type",
               "promoted_object_custom_conversion_id",
               "promoted_object_custom_event_str",
               "promoted_object_custom_event_type",
               "promoted_object_event_id",
               "promoted_object_object_store_url",
               "promoted_object_offer_id",
               "promoted_object_offline_conversion_data_set_id",
               "promoted_object_page_id",
               "promoted_object_pixel_aggregation_rule",
               "promoted_object_pixel_id",
               "promoted_object_pixel_rule",
               "promoted_object_place_page_set_id",
               "promoted_object_product_catalog_id",
               "promoted_object_product_set_id",
               "promoted_object_retention_days",
               "primary_attribution",
               "smart_promotion_type",
               "source_campaign_id",
               "special_ad_categories",
               "special_ad_category",
               "special_ad_category_country",
               "spend_cap",
               "promoted_object",
               "status",
               "topline_id"]

    name = "campaign_history"
    path = "/campaigns?fields={}".format(columns)
    schema_filepath = SCHEMAS_DIR / "campaignhistory.json"
    tap_stream_id = "campaign_history"

class adsethistoryStream(facebookStream):
    columns = ["id",
               "account_id",
               "campaign_id",
               "updated_time",
               "created_time",
               "start_time",
               "end_time",
               "name",
               "asset_feed_id",
               "bid_amount",
               "bid_info_actions",
               "bid_info_impressions",
               "bid_strategy",
               "billing_event",
               "budget_remaining",
               "configured_status",
               "effective_status",
               "daily_budget",
               "lifetime_budget",
               "daily_min_spend_target",
               "daily_spend_cap",
               "destination_type",
               "instagram_actor_id",
               "is_dynamic_creative",
               "learning_stage_info",
               "lifetime_imps",
               "lifetime_min_spend_target",
               "lifetime_spend_cap",
               "multi_optimization_goal_weight",
               "optimization_goal",
               "optimization_sub_event",
               "promoted_object_application_type",
               "promoted_object_custom_conversion_id",
               "promoted_object_custom_event_str",
               "promoted_object_custom_event_type",
               "promoted_object_event_id",
               "promoted_object_object_store_url",
               "promoted_object_offer_id",
               "promoted_object_offline_conversion_data_set_id",
               "promoted_object_page_id",
               "promoted_object_pixel_aggregation_rule",
               "promoted_object_pixel_id",
               "promoted_object_pixel_rule",
               "promoted_object_place_page_set_id",
               "promoted_object_product_catalog_id",
               "promoted_object_product_set_id",
               "promoted_object_retention_days",
               "recurring_budget_semantics",
               "review_feedback",
               "rf_prediction_id",
               "promoted_object",
               "attribution_spec",
               "campaign_attribution",
               "pacing_type",
               "source_adset_id",
               "status"]

    name = "ad_set_history"
    path = "/adsets?fields={}".format(columns)
    schema_filepath = SCHEMAS_DIR / "adsethistory.json"
    tap_stream_id = "ad_set_history"

class adconversionStream(facebookStream):
    columns = ["id",
               "adset_id",
               "campaign_id",
               "conversion_id"
               "application",
               "creative",
               "dataset",
               "event",
               "event_creator",
               "event_type",
               "fb_pixel",
               "fb_pixel_event",
               "index",
               "leadgen",
               "object",
               "object_domain",
               "offer",
               "offer_creator",
               "offsite_pixel",
               "page",
               "page_parent",
               "post",
               "post_object",
               "post_object_wall",
               "post_wall",
               "question",
               "question_creator",
               "response",
               "subtype",
               "updated_time",
               "created_time"]

    name = "ad_conversion"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adconversion.json"
    tap_stream_id = "ad_conversion"

class campaignlabelStream(facebookStream):
    columns = ["id",
               "account_id",
               "ad_label_id"
               "source_campaign_id",
               "adlabels"
               "updated_time",
               "created_time"]

    name = "campaign_label"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "campaignlabel.json"
    tap_stream_id = "campaign_label"

class adgroupissuesinfoStream(facebookStream):
    columns = ["id",
               "account_id",
               "error_code"
               "error_message",
               "error_summary",
               "error_type",
               "index",
               "level",
               "updated_time",
               "created_time"]

    name = "ad_group_issues_info"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adgroupissuesinfo.json"
    tap_stream_id = "ad_group_issues_info"

class adrecommendationStream(facebookStream):
    columns = ["id",
               "account_id",
               "blame_field"
               "code",
               "confidence",
               "importance",
               "index",
               "message",
               "recommendation_data",
               "title",
               "updated_time",
               "created_time"]

    name = "ad_recommendation"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adrecommendation.json"
    tap_stream_id = "ad_recommendation"

class adsetscheduleStream(facebookStream):
    columns = ["id",
               "account_id",
               "days",
               "start_minute",
               "end_minute",
               "index",
               "timezone_type",
               "updated_time",
               "created_time"]

    name = "adset_schedule"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adsetschedule.json"
    tap_stream_id = "adset_schedule"

class adcampaignissuesinfoStream(facebookStream):
    columns = ["id",
               "account_id",
               "error_code"
               "error_message",
               "error_summary",
               "error_type",
               "index",
               "level",
               "updated_time",
               "created_time"]

    name = "ad_campaign_issues_info"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adcampaignissuesinfo.json"
    tap_stream_id = "ad_campaign_issues_info"

class adsetattributionStream(facebookStream):
    columns = ["id",
               "account_id",
               "event_type",
               "index",
               "window_days",
               "updated_time",
               "created_time"]

    name = "ad_set_attribution"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adsetattribution.json"
    tap_stream_id = "ad_set_attribution"

class adtrackingStream(facebookStream):
    columns = ["id",
               "adset_id",
               "campaign_id",
               "conversion_id"
               "application",
               "creative",
               "dataset",
               "event",
               "event_creator",
               "event_type",
               "fb_pixel",
               "fb_pixel_event",
               "index",
               "leadgen",
               "object",
               "object_domain",
               "offer",
               "offer_creator",
               "offsite_pixel",
               "page",
               "page_parent",
               "post",
               "post_object",
               "post_object_wall",
               "post_wall",
               "question",
               "question_creator",
               "response",
               "subtype",
               "updated_time",
               "created_time"]

    name = "ad_tracking"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adtracking.json"
    tap_stream_id = "ad_tracking"



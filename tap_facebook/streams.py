"""Stream type classes for tap-facebook."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType

from tap_facebook.client import facebookStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

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


#   TODO: FIND OUT HOW TO GET DATA FOR THESE COLUMNS

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
    #schema_filepath = SCHEMAS_DIR / "ads_insights.json"
    # TODO: test completed SDK stream
    schema = th.PropertiesList(
        Property("clicks", StringType),
        Property("date_stop", StringType),
        Property("ad_id", StringType),

        Property("website_ctr",
                 ArrayType(
                     ObjectType(
                         Property("value", StringType),
                         Property("action_destination", StringType),
                         Property("action_target_id", StringType),
                         Property("action_type", StringType)
                     )
                 )
                 ),

        Property("unique_inline_link_click_ctr", StringType),
        Property("adset_id", StringType),
        Property("frequency", StringType),
        Property("account_name", StringType),
        Property("canvas_avg_view_time", StringType),
        Property("unique_inline_link_clicks", StringType),

        Property("cost_per_unique_action_type",
                 ArrayType(
                     ObjectType(
                         Property("value", StringType),
                         Property("action_type", StringType)
                     )
                 )
                 ),

        Property("inline_post_engagement", StringType),
        Property("campaign_name", StringType),
        Property("inline_link_clicks", StringType),
        Property("campaign_id", StringType),
        Property("cpc", StringType),
        Property("ad_name", StringType),
        Property("cost_per_unique_inline_link_click", StringType),
        Property("cpm", StringType),
        Property("cost_per_inline_post_engagement", StringType),
        Property("inline_link_click_ctr", StringType),
        Property("cpp", StringType),
        Property("cost_per_action_type", StringType),
        Property("unique_link_clicks_ctr", StringType),
        Property("spend", StringType),
        Property("cost_per_unique_click", StringType),
        Property("adset_name", StringType),
        Property("unique_clicks", StringType),
        Property("social_spend", StringType),
        Property("canvas_avg_view_percent", StringType),
        Property("account_id", StringType),
        Property("date_start", DateTimeType),
        Property("objective", StringType),
        Property("quality_ranking", StringType),
        Property("engagement_rate_ranking", StringType),
        Property("conversion_rate_ranking", StringType),
        Property("impressions", StringType),
        Property("unique_ctr", StringType),
        Property("cost_per_inline_link_click", StringType),
        Property("ctr", StringType),
        Property("reach", StringType)
    ).to_dict()

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

#   TODO: FIND OUT HOW TO GET DATA FOR THESE COLUMNS

    columns_remaining = ["adlabels", "recommendations"]

    name = "ads"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    # schema_filepath = SCHEMAS_DIR / "ads.json"

    schema = th.PropertiesList(
        Property("bid_type", StringType),
        Property("account_id", StringType),
        Property("campaign_id", StringType),
        Property("adset_id", StringType),

        Property("adlabels",
                 ArrayType(
                     ObjectType(
                         Property("id", StringType),
                         Property("created_time", DateTimeType),
                         Property("name", StringType),
                         Property("updated_time", DateTimeType),
                     )
                 )
                 ),
        Property("bid_amount", IntegerType),

        Property("bid_info",
                 ObjectType(
                    Property("CLICKS", IntegerType),
                    Property("ACTIONS", IntegerType),
                    Property("REACH", IntegerType),
                    Property("IMPRESSIONS", IntegerType),
                    Property("SOCIAL", IntegerType)
                 )
                 ),

        Property("status", StringType),

        Property("creative",
                 ObjectType(
                     Property("creative_id", StringType),
                     Property("id", StringType)
                 )
                 ),

        Property("id", StringType),
        Property("updated_time", DateTimeType),
        Property("created_time", DateTimeType),
        Property("name", StringType),
        Property("effective_status", StringType),
        Property("last_updated_by_app_id", DateTimeType),

        Property("recommendations",
                 ArrayType(
                     ObjectType(
                         Property("blame_field", StringType),
                         Property("code", IntegerType),
                         Property("confidence", StringType),
                         Property("importance", StringType),
                         Property("message", StringType),
                         Property("title", StringType)
                     )
                 )
                 ),

        Property("source_ad_id", StringType),

        Property("tracking_specs",
                 ArrayType(
                     ObjectType(
                         Property("application",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("post", StringType),
                         Property("conversion_id", StringType),
                         Property("action.type",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("post.type",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("page",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("creative",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("dataset",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("event",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("event.creator",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("event_type",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("fb_pixel",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("fb_pixel_event",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("leadgen",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("object",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("object.domain",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("offer",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("offer.creator",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("offsite_pixel",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("page.parent",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("post.object",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("post.object.wall",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("question",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("question.creator",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("response",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("subtype",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  )
                     )
                 )
                 ),
        Property("conversion_specs",
                 ArrayType(
                     ObjectType(
                         Property("application",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),
                         Property("application",
                                  ArrayType(
                                      Property("items", StringType)
                                  )
                                  ),


    ).to_dict(

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

#   TODO: FIND OUT HOW TO GET DATA FOR THESE COLUMNS

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

    #   TODO: FIND OUT HOW TO GET DATA FOR THESE COLUMNS
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
    tap_stream_id = "campaigns"
    # schema_filepath = SCHEMAS_DIR / "campaigns.json"
    # TODO: test completed SDK stream
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
        Property("start_time", StringType),
        Property("stop_time", StringType),
        Property("updated_time", StringType),
        Property("created_time", StringType),
        # TODO resolve ads object SDK schema logic withi
        Property("ads",
                 PropertiesList(
                     Property(
                         "data",
                         ArrayType(
                             ObjectType(
                                 Property("id",
                                          StringType
                                          ),
                             )
                         )
                     )
                 )
                 ),
        Property("adlabels",
                 ArrayType(
                     Property("items", ObjectType(
                       Property("id", StringType),
                       Property("name", StringType),
                       Property("created_time", DateTimeType)
                     )
                              )
                 )
                 )
    ).to_dict()


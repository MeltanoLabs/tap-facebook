"""Stream type classes for tap-facebook."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_facebook.client import facebookStream
import json

from singer_sdk.streams import RESTStream

from singer_sdk.typing import (
    PropertiesList,
    Property,
    ObjectType,
    DateTimeType,
    StringType,
    ArrayType,
    BooleanType,
    IntegerType,
)

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

## TODO: ADD ACCOUNTS STREAM AND SCHEMA

# ads insights stream
class adsinsightStream(facebookStream):
    """
    https://developers.facebook.com/docs/marketing-api/insights.
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = [
        "account_id",
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
        "ctr",
    ]

    #   TODO: CONTINUE MONITORING TARGETING COLUMNS WITHIN ADSINSIGHTS, COLUMNS ARE REPORTED AS NULL AND NOT CRITICAL TO REPORTS

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
        "video_p100_watched_actions",
    ]

    name = "adsinsights"

    path = "/insights?level=ad&fields={}".format(columns)

    replication_keys = ["date_start"]
    replication_method = "incremental"

    schema = PropertiesList(
        Property("clicks", StringType),
        Property("date_stop", StringType),
        Property("ad_id", StringType),
        Property(
            "website_ctr",
            ArrayType(
                ObjectType(
                    Property("value", StringType),
                    Property("action_destination", StringType),
                    Property("action_target_id", StringType),
                    Property("action_type", StringType),
                )
            ),
        ),
        Property("unique_inline_link_click_ctr", StringType),
        Property("adset_id", StringType),
        Property("frequency", StringType),
        Property("account_name", StringType),
        Property("canvas_avg_view_time", StringType),
        Property("unique_inline_link_clicks", StringType),
        Property(
            "cost_per_unique_action_type",
            ArrayType(
                ObjectType(
                    Property("value", StringType), Property("action_type", StringType)
                )
            ),
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
        Property("reach", StringType),
    ).to_dict()

    tap_stream_id = "adsinsights"
    # replication_key = "created_time"

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
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


# ads stream
class adsStream(facebookStream):
    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = [
        "id",
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
        "recommendations",
    ]

    #   TODO: CONTINUE MONITORING TARGETING COLUMNS WITHIN ADS, COLUMNS ARE REPORTED AS NULL AND NOT CRITICAL TO REPORTS

    columns_remaining = ["adlabels", "recommendations"]

    name = "ads"

    path = "/ads?fields={}".format(columns)

    primary_keys = ["id", "updated_time"]
    replication_keys = ["updated_time"]
    replication_method = "incremental"

    schema = PropertiesList(
        Property("bid_type", StringType),
        Property("account_id", StringType),
        Property("campaign_id", StringType),
        Property("adset_id", StringType),
        Property(
            "adlabels",
            ArrayType(
                ObjectType(
                    Property("id", StringType),
                    Property("created_time", DateTimeType),
                    Property("name", StringType),
                    Property("updated_time", DateTimeType),
                )
            ),
        ),
        Property("bid_amount", IntegerType),
        Property(
            "bid_info",
            ObjectType(
                Property("CLICKS", IntegerType),
                Property("ACTIONS", IntegerType),
                Property("REACH", IntegerType),
                Property("IMPRESSIONS", IntegerType),
                Property("SOCIAL", IntegerType),
            ),
        ),
        Property("status", StringType),
        Property(
            "creative",
            ObjectType(Property("creative_id", StringType), Property("id", StringType)),
        ),
        Property("id", StringType),
        Property("updated_time", StringType),
        Property("created_time", StringType),
        Property("name", StringType),
        Property("effective_status", StringType),
        Property("last_updated_by_app_id", StringType),
        Property(
            "recommendations",
            ArrayType(
                ObjectType(
                    Property("blame_field", StringType),
                    Property("code", IntegerType),
                    Property("confidence", StringType),
                    Property("importance", StringType),
                    Property("message", StringType),
                    Property("title", StringType),
                )
            ),
        ),
        Property("source_ad_id", StringType),
        Property(
            "tracking_specs",
            ArrayType(
                ObjectType(
                    Property("application", ArrayType(Property("items", StringType))),
                    Property("post", StringType),
                    Property("conversion_id", StringType),
                    Property("action.type", ArrayType(Property("items", StringType))),
                    Property("post.type", ArrayType(Property("items", StringType))),
                    Property("page", ArrayType(Property("items", StringType))),
                    Property("creative", ArrayType(Property("items", StringType))),
                    Property("dataset", ArrayType(Property("items", StringType))),
                    Property("event", ArrayType(Property("items", StringType))),
                    Property("event.creator", ArrayType(Property("items", StringType))),
                    Property("event_type", ArrayType(Property("items", StringType))),
                    Property("fb_pixel", ArrayType(Property("items", StringType))),
                    Property(
                        "fb_pixel_event", ArrayType(Property("items", StringType))
                    ),
                    Property("leadgen", ArrayType(Property("items", StringType))),
                    Property("object", ArrayType(Property("items", StringType))),
                    Property("object.domain", ArrayType(Property("items", StringType))),
                    Property("offer", ArrayType(Property("items", StringType))),
                    Property("offer.creator", ArrayType(Property("items", StringType))),
                    Property("offsite_pixel", ArrayType(Property("items", StringType))),
                    Property("page.parent", ArrayType(Property("items", StringType))),
                    Property("post.object", ArrayType(Property("items", StringType))),
                    Property(
                        "post.object.wall", ArrayType(Property("items", StringType))
                    ),
                    Property("question", ArrayType(Property("items", StringType))),
                    Property(
                        "question.creator", ArrayType(Property("items", StringType))
                    ),
                    Property("response", ArrayType(Property("items", StringType))),
                    Property("subtype", ArrayType(Property("items", StringType))),
                )
            ),
        ),
        Property(
            "conversion_specs",
            ArrayType(
                ObjectType(
                    Property("application", ArrayType(Property("items", StringType))),
                    Property("application", ArrayType(Property("items", StringType))),
                )
            ),
        ),

        Property("placement_specific_facebook_unsafe_substances", StringType),
        Property("placement_specific_instagram_unsafe_substances", StringType),
        Property("global_unsafe_substances", StringType),
        Property("placement_specific_instagram_personal_attributes", StringType),
        Property("global_personal_attributes", StringType),
        Property("placement_specific_facebook_personal_attributes", StringType),
        Property("placement_specific_instagram_nonexistent_functionality", StringType),
        Property("global_nonexistent_functionality", StringType),
        Property("placement_specific_facebook_nonexistent_functionality", StringType),
        Property("placement_specific_facebook_advertising_policies", StringType),
        Property("global_advertising_policies", StringType),
        Property("global_spyware_or_malware", StringType),
        Property("placement_specific_instagram_spyware_or_malware", StringType),
        Property("placement_specific_facebook_spyware_or_malware", StringType),
        Property("placement_specific_instagram_unrealistic_outcomes", StringType),
        Property("global_unrealistic_outcomes", StringType),
        Property("placement_specific_facebook_unrealistic_outcomes", StringType),
        Property("placement_specific_facebook_brand_usage_in_ads", StringType),
        Property("global_brand_usage_in_ads", StringType),
        Property("global_personal_health_and_appearance", StringType),
        Property("placement_specific_facebook_personal_health_and_appearance", StringType),
        Property("placement_specific_instagram_personal_health_and_appearance", StringType),
        Property("placement_specific_instagram_illegal_products_or_services", StringType),
        Property("global_illegal_products_or_services", StringType),
        Property("placement_specific_facebook_illegal_products_or_services", StringType),
        Property("global_non_functional_landing_page", StringType),
        Property("placement_specific_facebook_non_functional_landing_page", StringType),
        Property("placement_specific_instagram_non_functional_landing_page", StringType),
        Property("placement_specific_instagram_commercial_exploitation_of_crises_and_controversial_events", StringType),
        Property("placement_specific_facebook_commercial_exploitation_of_crises_and_controversial_events", StringType),
        Property("global_commercial_exploitation_of_crises_and_controversial_events", StringType),
        Property("global_discriminatory_practices", StringType),
        Property("placement_specific_facebook_discriminatory_practices", StringType),
        Property("global_circumventing_systems", StringType),
        Property("placement_specific_facebook_circumventing_systems", StringType),
        Property("placement_specific_instagram_circumventing_systems", StringType),
        Property("placement_specific_facebook_adult_content", StringType),
        Property("placement_specific_facebook_sensational_content", StringType),
        Property("global_adult_content", StringType),
        Property("global_sensational_content", StringType),
        Property("placement_specific_instagram_adult_content", StringType),
        Property("placement_specific_instagram_brand_usage_in_ads", StringType),
        Property("placement_specific_instagram_sensational_content", StringType),
        Property("placement_specific_facebook_ads_about_social_issues_elections_or_politics", StringType),
        Property("placement_specific_instagram_ads_about_social_issues_elections_or_politics", StringType),
        Property("global_ads_about_social_issues_elections_or_politics", StringType),
        Property("configured_status", StringType),
        Property("conversion_domain", StringType),
        Property("conversion_specs", StringType),
        Property("placement_specific_instagram_advertising_policies", StringType),

    ).to_dict()

    tap_stream_id = "ads"

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
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


# adsets stream
class adsetsStream(facebookStream):
    """
    https://developers.facebook.com/docs/marketing-api/reference/ad-campaign/
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = [
        "id",
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
    ]

    # TODO: CONTINUE MONITORING TARGETING COLUMNS WITHIN ADSETS, COLUMNS ARE REPORTED AS NULL AND NOT CRITICAL TO REPORTS

    columns_remaining = [
        "adlabels",
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
        "time_based_ad_rotation_intervals",
    ]

    name = "adsets"
    
    path = "/adsets?fields={}".format(columns)
    primary_keys = ["id", "updated_time"]
    replication_keys = ["updated_time"]
    replication_method = "incremental"

    schema = PropertiesList(
        Property("name", StringType),
        Property("end_time", StringType),
        Property("billing_event", StringType),
        Property("campaign_attribution", StringType),
        Property("destination_type", StringType),
        Property("is_dynamic_creative", StringType),
        Property("lifetime_imps", StringType),
        Property("multi_optimization_goal_weight", StringType),
        Property("optimization_goal", StringType),
        Property("optimization_sub_event", StringType),
        Property("pacing_type", StringType),
        Property("recurring_budget_semantics", StringType),
        Property("source_adset_id", StringType),
        Property("status", StringType),
        Property("targeting_optimization_types", StringType),
        Property("use_new_app_click", BooleanType),
        Property(
            "promoted_object",
            ObjectType(
                Property("custom_event_type", StringType),
                Property("pixel_id", StringType),
                Property("pixel_rule", StringType),
                Property("page_id", StringType),
                Property("object_store_url", StringType),
                Property("application_id", StringType),
                Property("product_set_id", StringType),
                Property("offer_id", StringType),
            ),
        ),
        Property("id", StringType),
        Property("account_id", StringType),
        Property("updated_time", StringType),
        Property("daily_budget", StringType),
        Property("budget_remaining", StringType),
        Property("effective_status", StringType),
        Property("campaign_id", StringType),
        Property("created_time", StringType),
        Property("start_time", StringType),
        Property("lifetime_budget", StringType),
        Property(
            "bid_info",
            ObjectType(
                Property("CLICKS", IntegerType),
                Property("ACTIONS", IntegerType),
                Property("REACH", IntegerType),
                Property("IMPRESSIONS", IntegerType),
                Property("SOCIAL", IntegerType),
            ),
        ),
        Property(
            "adlabels",
            ArrayType(
                Property(
                    "items",
                    ObjectType(
                        Property("id", StringType),
                        Property("name", StringType),
                        Property("created_time", DateTimeType),
                    ),
                )
            ),
        ),

        Property(
            "attribution_spec",
            ArrayType(
                ObjectType(
                    Property("event_type", StringType),
                    Property("window_days", IntegerType)
                )
            ),
        ),

        Property(
            "learning_stage_info",
                ObjectType(
                    Property("attribution_windows", ArrayType(StringType)),
                    Property("conversions", IntegerType),
                    Property("last_sig_edit_ts", IntegerType),
                    Property("status", StringType)
                )
        ),

        Property("configured_status", StringType),
        Property("asset_feed_id", StringType),
        Property("daily_min_spend_target", StringType),
        Property("daily_spend_cap", StringType),
        Property("instagram_actor_id", StringType),
        Property("review_feedback", StringType),
        Property("rf_prediction_id", StringType)

    ).to_dict()


    tap_stream_id = "adsets"

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
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


# campaigns stream
class campaignStream(facebookStream):
    """
    https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group.
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = [
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
        "pacing_type",
    ]

    #   TODO: CONTINUE MONITORING TARGETING COLUMNS WITHIN CAMPAIGNS, COLUMNS ARE REPORTED AS NULL AND NOT CRITICAL TO REPORTS
    columns_remaining = [
        "ad_strategy_group_id",
        "ad_strategy_id",
        "adlabels",
        "daily_budget",
        "issues_info",
        "last_budget_toggling_time",
        "lifetime_budget",
        "recommendations",
    ]

    name = "campaigns"

    path = "/campaigns?fields={}".format(columns)
    primary_keys = ["id", "updated_time"]
    tap_stream_id = "campaigns"
    replication_keys = ["updated_time"]
    replication_method = "incremental"

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
        Property("daily_budget", StringType),
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
                    ),
                )
            ),
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
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

class creativeStream(facebookStream):
    """
    https://developers.facebook.com/docs/marketing-api/reference/ad-creative/
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = ["id",
               "account_id",
               "actor_id",
               "applink_treatment",
               "asset_feed_spec",
               "authorization_category",
               "body",
               "branded_content_sponsor_page_id",
               "bundle_folder_id",
               "call_to_action_type",
               "categorization_criteria",
               "category_media_source",
               "degrees_of_freedom_spec",
               "destination_set_id",
               "dynamic_ad_voice",
               "effective_authorization_category",
               "effective_instagram_media_id",
               "effective_instagram_story_id",
               "effective_object_story_id",
               "enable_direct_install",
               "image_hash",
               "image_url",
               "instagram_actor_id",
               "instagram_permalink_url",
               "instagram_story_id",
               "link_destination_display_url",
               "link_og_id",
               "link_url",
               "messenger_sponsored_message",
               "name",
               "object_id",
               "object_store_url",
               "object_story_id",
               "object_story_spec",
               "object_type",
               "object_url",
               "page_link",
               "page_message",
               "place_page_set_id",
               "platform_customizations",
               "playable_asset_id",
               "source_instagram_media_id",
               "status",
               "template_url",
               "thumbnail_id",
               "thumbnail_url",
               "title",
               "url_tags",
               "use_page_actor_override",
               "video_id"]

    name = "creatives"
    path = "/adcreatives?fields={}".format(columns)
    tap_stream_id = "creatives"
    replication_keys = ["id"]
    replication_method = "incremental"

    schema = PropertiesList(
        Property("id", StringType),
        Property("account_id", StringType),
        Property("actor_id", StringType),
        Property("applink_treatment", StringType),
        Property("asset_feed_spec", StringType),
        Property("authorization_category", StringType),
        Property("body", BooleanType),
        Property("branded_content_sponsor_page_id", BooleanType),
        Property("bundle_folder_id", StringType),
        Property("call_to_action_type", StringType),
        Property("categorization_criteria", StringType),
        Property("category_media_source", StringType),
        Property("degrees_of_freedom_spec", StringType),
        Property("destination_set_id", StringType),
        Property("dynamic_ad_voice", StringType),
        Property("effective_authorization_category", StringType),
        Property("effective_instagram_media_id", StringType),
        Property("effective_instagram_story_id", StringType),
        Property("effective_object_story_id", StringType),
        Property("enable_direct_install", BooleanType),
        Property("image_hash", StringType),
        Property("image_url", StringType),
        Property("instagram_actor_id", StringType),
        Property("instagram_permalink_url", StringType),
        Property("instagram_story_id", StringType),
        Property("link_destination_display_url", StringType),
        Property("link_og_id", StringType),
        Property("link_url", StringType),
        Property("messenger_sponsored_message", StringType),
        Property("name", StringType),
        Property("object_id", StringType),
        Property("object_store_url", StringType),
        Property("object_story_id", StringType),
        Property("object_story_spec", StringType),
        Property("object_type", StringType),
        Property("object_url", StringType),
        Property("page_link", StringType),
        Property("page_message", StringType),
        Property("place_page_set_id", StringType),
        Property("platform_customizations", StringType),
        Property("playable_asset_id", StringType),
        Property("source_instagram_media_id", StringType),
        Property("status", StringType),
        Property("template_url", StringType),
        Property("thumbnail_id", StringType),
        Property("thumbnail_url", StringType),
        Property("title", StringType),
        Property("url_tags", StringType),
        Property("use_page_actor_override", BooleanType),
        Property("video_id", StringType)

    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
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
    
class adlabelsStream(facebookStream):
    """
    https://developers.facebook.com/docs/marketing-api/reference/ad-creative/
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = ["id",
               "account",
               "created_time",
               "updated_time"]

    name = "adlabels"
    path = "/adlabels?fields={}".format(columns)
    primary_keys = ["id", "updated_time"]
    tap_stream_id = "adlabels"
    replication_keys = ["updated_time"]
    replication_method = "incremental"

    schema = PropertiesList(
        Property("id", StringType),
        
        Property(
            "account",
                ObjectType(
                    Property("account_id", StringType),
                    Property("id", StringType),
                )
        ),

        Property("created_time", StringType),
        Property("updated_time", StringType)
        
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
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

class AdaccountsStream(facebookStream):
    """
    https://developers.facebook.com/docs/graph-api/reference/user/accounts/
    """

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    @property
    def url_base(self):
        version = self.config.get("api_version", "")
        base_url = "https://graph.facebook.com/{}/me".format(version)
        return base_url

    columns = ["account_id",
               "business_name",
               "account_status",
               "age",
               "amount_spent",
               "balance",
               "business_city",
               "business_country_code",
               "business_street",
               "business_street2",
               "can_create_brand_lift_study",
               "capabilities",
               "created_time",
               "currency",
               "disable_reason",
               "end_advertiser",
               "end_advertiser_name",
               "has_advertiser_opted_in_odax",
               "has_migrated_permissions",
               "id",
               "is_attribution_spec_system_default",
               "is_direct_deals_enabled",
               "is_in_3ds_authorization_enabled_market",
               "is_notifications_enabled",
               "is_personal",
               "is_prepay_account",
               "is_tax_id_required",
               "min_campaign_group_spend_cap",
               "min_daily_budget",
               "name",
               "offsite_pixels_tos_accepted",
               "owner",
               "spend_cap",
               "tax_id_status",
               "tax_id_type",
               "timezone_id",
               "timezone_name",
               "timezone_offset_hours_utc",
               "agency_client_declaration_agency_representing_client",
               "agency_client_declaration_client_based_in_france",
               "agency_client_declaration_client_city",
               "agency_client_declaration_client_country_code",
               "agency_client_declaration_client_email_address",
               "agency_client_declaration_client_name",
               "agency_client_declaration_client_postal_code",
               "agency_client_declaration_client_province",
               "agency_client_declaration_client_street",
               "agency_client_declaration_client_street2",
               "agency_client_declaration_has_written_mandate_from_advertiser",
               "agency_client_declaration_is_client_paying_invoices",
               "business_manager_block_offline_analytics",
               "business_manager_created_by",
               "business_manager_created_time",
               "business_manager_extended_updated_time",
               "business_manager_is_hidden",
               "business_manager_link",
               "business_manager_name",
               "business_manager_payment_account_id",
               "business_manager_primary_page",
               "business_manager_profile_picture_uri",
               "business_manager_timezone_id",
               "business_manager_two_factor_type",
               "business_manager_updated_by",
               "business_manager_update_time",
               "business_manager_verification_status",
               "business_manager_vertical",
               "business_manager_vertical_id",
               "business_manager_manager_id",
               "extended_credit_invoice_group_id",
               "extended_credit_invoice_group_auto_enroll",
               "extended_credit_invoice_group_customer_po_number",
               "extended_credit_invoice_group_email",
               "extended_credit_invoice_group_emails",
               "extended_credit_invoice_group_name",
               "business_state",
               "io_number",
               "media_agency",
               "partner",
               "salesforce_invoice_group_id",
               "business_zip",
               "tax_id"]

    name = "adaccounts"
    path = "/adaccounts?fields={}".format(columns)
    tap_stream_id = "adaccounts"
    primary_keys = ["created_time"]
    replication_keys = ["created_time"]
    replication_method = "incremental"

    schema = PropertiesList(
        Property("account_id", StringType),
        Property("timezone_id", IntegerType),
        Property("business_name", StringType),
        Property("account_status", StringType),
        Property("age", StringType),
        Property("amount_spent", IntegerType),
        Property("balance", IntegerType),
        Property("business_city", StringType),
        Property("business_country_code", StringType),
        Property("business_street", StringType),
        Property("business_street2", StringType),
        Property("can_create_brand_lift_study", BooleanType),
        Property("capabilities", ArrayType(StringType)),
        Property("created_time", StringType),
        Property("currency", StringType),
        Property("disable_reason", StringType),
        Property("end_advertiser", IntegerType),
        Property("end_advertiser_name", StringType),
        Property("has_advertiser_opted_in_odax", BooleanType),
        Property("has_migrated_permissions", BooleanType),
        Property("id", StringType),
        Property("is_attribution_spec_system_default", BooleanType),
        Property("is_direct_deals_enabled", BooleanType),
        Property("is_in_3ds_authorization_enabled_market", BooleanType),
        Property("is_notifications_enabled", BooleanType),
        Property("is_personal", StringType),
        Property("is_prepay_account", BooleanType),
        Property("is_tax_id_required", BooleanType),
        Property("min_campaign_group_spend_cap", IntegerType),
        Property("min_daily_budget", IntegerType),
        Property("name", StringType),
        Property("offsite_pixels_tos_accepted", BooleanType),
        Property("owner", StringType),
        Property("spend_cap", IntegerType),
        Property("tax_id_status", StringType),
        Property("tax_id_type", StringType),
        Property("timezone_id", StringType),
        Property("timezone_name", StringType),
        Property("timezone_offset_hours_utc", IntegerType),
        Property("agency_client_declaration_agency_representing_client", IntegerType),
        Property("agency_client_declaration_client_based_in_france", IntegerType),
        Property("agency_client_declaration_client_city", StringType),
        Property("agency_client_declaration_client_country_code", StringType),
        Property("agency_client_declaration_client_email_address", StringType),
        Property("agency_client_declaration_client_name", StringType),
        Property("agency_client_declaration_client_postal_code", StringType),
        Property("agency_client_declaration_client_province", StringType),
        Property("agency_client_declaration_client_street", StringType),
        Property("agency_client_declaration_client_street2", StringType),
        Property("agency_client_declaration_has_written_mandate_from_advertiser", IntegerType),
        Property("agency_client_declaration_is_client_paying_invoices", IntegerType),
        Property("business_manager_block_offline_analytics", BooleanType),
        Property("business_manager_created_by", StringType),
        Property("business_manager_created_time", StringType),
        Property("business_manager_extended_updated_time", StringType),
        Property("business_manager_is_hidden", BooleanType),
        Property("business_manager_link", StringType),
        Property("business_manager_name", StringType),
        Property("business_manager_payment_account_id", IntegerType),
        Property("business_manager_primary_page", StringType),
        Property("business_manager_profile_picture_uri", StringType),
        Property("business_manager_timezone_id", IntegerType),
        Property("business_manager_two_factor_type", StringType),
        Property("business_manager_updated_by", StringType),
        Property("business_manager_update_time", StringType),
        Property("business_manager_verification_status", StringType),
        Property("business_manager_vertical", StringType),
        Property("business_manager_vertical_id", IntegerType),
        Property("business_manager_manager_id", IntegerType),
        Property("extended_credit_invoice_group_id", IntegerType),
        Property("extended_credit_invoice_group_auto_enroll", BooleanType),
        Property("extended_credit_invoice_group_customer_po_number", StringType),
        Property("extended_credit_invoice_group_email", StringType),
        Property("extended_credit_invoice_group_emails", StringType),
        Property("extended_credit_invoice_group_name", StringType),
        Property("business_state", StringType),
        Property("io_number", IntegerType),
        Property("media_agency", StringType),
        Property("partner", StringType),
        Property("salesforce_invoice_group_id", StringType),
        Property("business_zip", StringType),
        Property("tax_id", StringType)
        
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
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

    
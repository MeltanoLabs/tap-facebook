"""Stream type classes for tap-facebook."""

from __future__ import annotations

import typing as t
from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.streams.core import REPLICATION_INCREMENTAL
from singer_sdk.typing import (
    ArrayType,
    BooleanType,
    DateTimeType,
    IntegerType,
    NumberType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


# ads insights stream
class AdsInsightStream(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/insights."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = [  # noqa: RUF012
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

    columns_remaining = [  # noqa: RUF012
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

    path = f"/insights?level=ad&fields={columns}"

    replication_method = REPLICATION_INCREMENTAL
    replication_key = "date_start"

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
                ),
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
                    Property("value", StringType),
                    Property("action_type", StringType),
                ),
            ),
        ),
        Property("inline_post_engagement", StringType),
        Property("campaign_name", StringType),
        Property("inline_link_clicks", IntegerType),
        Property("campaign_id", StringType),
        Property("cpc", StringType),
        Property("ad_name", StringType),
        Property("cost_per_unique_inline_link_click", StringType),
        Property("cpm", StringType),
        Property("cost_per_inline_post_engagement", StringType),
        Property("inline_link_click_ctr", StringType),
        Property("cpp", StringType),
        Property("cost_per_action_type", ArrayType(ObjectType())),
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
        Property("impressions", IntegerType),
        Property("unique_ctr", StringType),
        Property("cost_per_inline_link_click", StringType),
        Property("ctr", StringType),
        Property("reach", IntegerType),
        Property(
            "actions",
            ArrayType(
                ObjectType(
                    Property("action_type", StringType),
                    Property("value", StringType),
                ),
            ),
        ),
    ).to_dict()

    tap_stream_id = "adsinsights"

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
            params["sort"] = [f"{self.replication_key}_ascending"]
            params["order_by"] = self.replication_key

        params["action_attribution_windows"] = '["1d_view","7d_click"]'

        return params

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        row["inline_link_clicks"] = (
            int(row["inline_link_clicks"]) if "inline_link_clicks" in row else None
        )
        row["impressions"] = int(row["impressions"]) if "impressions" in row else None
        row["reach"] = int(row["reach"]) if "reach" in row else None
        return row


# ads stream
class AdsStream(FacebookStream):
    """Ads stream class.

    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id.
    """

    columns = [  # noqa: RUF012
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
        "configured_status",
        "conversion_domain",
        "bid_amount",
    ]

    columns_remaining = ["adlabels", "recommendations"]  # noqa: RUF012

    name = "ads"

    path = f"/ads?fields={columns}"

    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "updated_time"

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
                ),
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
                ),
            ),
        ),
        Property("source_ad_id", StringType),
        Property(
            "tracking_specs",
            ArrayType(
                ObjectType(
                    Property(
                        "application",
                        ArrayType(ObjectType(Property("items", StringType))),
                    ),
                    Property("post", ArrayType(StringType)),
                    Property("conversion_id", ArrayType(StringType)),
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
                        "fb_pixel_event",
                        ArrayType(Property("items", StringType)),
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
                        "post.object.wall",
                        ArrayType(Property("items", StringType)),
                    ),
                    Property("question", ArrayType(Property("items", StringType))),
                    Property(
                        "question.creator",
                        ArrayType(Property("items", StringType)),
                    ),
                    Property("response", ArrayType(Property("items", StringType))),
                    Property("subtype", ArrayType(Property("items", StringType))),
                ),
            ),
        ),
        Property(
            "conversion_specs",
            ArrayType(
                ObjectType(
                    Property("action.type", ArrayType(StringType)),
                    Property("conversion_id", ArrayType(StringType)),
                ),
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
        Property(
            "placement_specific_facebook_personal_health_and_appearance",
            StringType,
        ),
        Property(
            "placement_specific_instagram_personal_health_and_appearance",
            StringType,
        ),
        Property(
            "placement_specific_instagram_illegal_products_or_services",
            StringType,
        ),
        Property("global_illegal_products_or_services", StringType),
        Property(
            "placement_specific_facebook_illegal_products_or_services",
            StringType,
        ),
        Property("global_non_functional_landing_page", StringType),
        Property("placement_specific_facebook_non_functional_landing_page", StringType),
        Property(
            "placement_specific_instagram_non_functional_landing_page",
            StringType,
        ),
        Property(
            "placement_specific_instagram_commercial_exploitation_of_crises_and_controversial_events",
            StringType,
        ),
        Property(
            "placement_specific_facebook_commercial_exploitation_of_crises_and_controversial_events",
            StringType,
        ),
        Property(
            "global_commercial_exploitation_of_crises_and_controversial_events",
            StringType,
        ),
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
        Property(
            "placement_specific_facebook_ads_about_social_issues_elections_or_politics",
            StringType,
        ),
        Property(
            "placement_specific_instagram_ads_about_social_issues_elections_or_politics",
            StringType,
        ),
        Property("global_ads_about_social_issues_elections_or_politics", StringType),
        Property("configured_status", StringType),
        Property("conversion_domain", StringType),
        Property(
            "conversion_specs",
            ArrayType(
                ObjectType(
                    Property("action.type", ArrayType(StringType)),
                    Property("conversion_id", ArrayType(StringType)),
                ),
            ),
        ),
        Property("placement_specific_instagram_advertising_policies", StringType),
        Property("recommendation_data", ArrayType(Property("items", StringType))),
        Property("application", ArrayType(Property("items", StringType))),
        Property("dataset", ArrayType(Property("items", StringType))),
        Property("event", ArrayType(Property("items", StringType))),
        Property("event_creator", ArrayType(Property("items", StringType))),
        Property("event_type", ArrayType(Property("items", StringType))),
        Property("fb_pixel", ArrayType(Property("items", StringType))),
        Property("fb_pixel_event", ArrayType(Property("items", StringType))),
        Property("leadgen", ArrayType(Property("items", StringType))),
        Property("object", ArrayType(Property("items", StringType))),
        Property("object_domain", ArrayType(Property("items", StringType))),
        Property("offer", ArrayType(Property("items", StringType))),
        Property("offer_creator", ArrayType(Property("items", StringType))),
        Property("offsite_pixel", ArrayType(Property("items", StringType))),
        Property("page_parent", ArrayType(Property("items", StringType))),
        Property("post_object", ArrayType(Property("items", StringType))),
        Property("post_object_wall", ArrayType(Property("items", StringType))),
        Property("question", ArrayType(Property("items", StringType))),
        Property("question_creator", ArrayType(Property("items", StringType))),
        Property("response", ArrayType(Property("items", StringType))),
        Property("subtype", ArrayType(Property("items", StringType))),
    ).to_dict()

    tap_stream_id = "ads"


# adsets stream
class AdsetsStream(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-campaign/."""

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
        "bid_amount",
        "bid_strategy",
        "targeting",
        "bid_info",
    ]

    columns_remaining = [  # noqa: RUF012
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

    path = f"/adsets?fields={columns}"
    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "updated_time"

    schema = PropertiesList(
        Property("name", StringType),
        Property("end_time", StringType),
        Property("billing_event", StringType),
        Property("campaign_attribution", StringType),
        Property("destination_type", StringType),
        Property("is_dynamic_creative", BooleanType),
        Property("lifetime_imps", IntegerType),
        Property("multi_optimization_goal_weight", StringType),
        Property("optimization_goal", StringType),
        Property("optimization_sub_event", StringType),
        Property("pacing_type", ArrayType(StringType)),
        Property("recurring_budget_semantics", BooleanType),
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
                ),
            ),
        ),
        Property(
            "attribution_spec",
            ArrayType(
                ObjectType(
                    Property("event_type", StringType),
                    Property("window_days", IntegerType),
                ),
            ),
        ),
        Property(
            "learning_stage_info",
            ObjectType(
                Property("attribution_windows", ArrayType(StringType)),
                Property("conversions", IntegerType),
                Property("last_sig_edit_ts", IntegerType),
                Property("status", StringType),
            ),
        ),
        Property("configured_status", StringType),
        Property("asset_feed_id", StringType),
        Property("daily_min_spend_target", StringType),
        Property("daily_spend_cap", StringType),
        Property("instagram_actor_id", StringType),
        Property("review_feedback", StringType),
        Property("rf_prediction_id", StringType),
        Property("promoted_object_application_id", IntegerType),
        Property("promoted_object_custom_conversion_id", IntegerType),
        Property("promoted_object_custom_event_str", StringType),
        Property("promoted_object_custom_event_type", StringType),
        Property("promoted_object_event_id", IntegerType),
        Property("promoted_object_object_store_url", StringType),
        Property("promoted_object_offer_id", IntegerType),
        Property("promoted_object_offline_conversion_data_set_id", IntegerType),
        Property("promoted_object_page_id", IntegerType),
        Property("promoted_object_pixel_aggregation_rule", StringType),
        Property("promoted_object_pixel_id", IntegerType),
        Property("promoted_object_pixel_rule", StringType),
        Property("promoted_object_place_page_set_id", IntegerType),
        Property("promoted_object_product_catalog_id", IntegerType),
        Property("promoted_object_product_set_id", IntegerType),
        Property("promoted_object_retention_days", StringType),
        Property("promoted_object_application_type", StringType),
        Property("bid_amount", StringType),
        Property("bid_strategy", StringType),
        Property(
            "targeting",
            ObjectType(
                Property("age_max", IntegerType),
                Property("age_min", IntegerType),
                Property("excluded_custom_audiences", ArrayType(StringType)),
                Property(
                    "geo_locations",
                    ObjectType(
                        Property("countries", ArrayType(StringType)),
                        Property("location_types", ArrayType(StringType)),
                    ),
                ),
                Property("genders", ArrayType(IntegerType)),
                Property("brand_safety_content_filter_levels", ArrayType(StringType)),
                Property("publisher_platforms", ArrayType(StringType)),
                Property("facebook_positions", ArrayType(StringType)),
                Property("instagram_positions", ArrayType(StringType)),
                Property("device_platforms", ArrayType(StringType)),
            ),
        ),
        Property("targeting_app_install_state", StringType),
        Property("targeting_audience_network_positions", ArrayType(StringType)),
        Property("targeting_behaviors", ArrayType(StringType)),
        Property("targeting_college_years", ArrayType(StringType)),
        Property("targeting_connections", ArrayType(StringType)),
        Property("targeting_education_majors", ArrayType(StringType)),
        Property("targeting_education_schools", ArrayType(StringType)),
        Property("targeting_education_statuses", ArrayType(StringType)),
        Property(
            "targeting_effective_audience_network_positions",
            ArrayType(StringType),
        ),
        Property("targeting_excluded_connections", ArrayType(StringType)),
        Property("targeting_excluded_geo_locations_countries", ArrayType(StringType)),
        Property(
            "targeting_excluded_geo_locations_country_groups",
            ArrayType(StringType),
        ),
        Property(
            "targeting_excluded_geo_locations_custom_locations",
            ArrayType(StringType),
        ),
        Property(
            "targeting_excluded_geo_locations_electoral_district",
            ArrayType(StringType),
        ),
        Property("targeting_excluded_geo_locations_geo_markets", ArrayType(StringType)),
        Property(
            "targeting_excluded_geo_locations_location_types",
            ArrayType(StringType),
        ),
        Property("targeting_excluded_geo_locations_places", ArrayType(StringType)),
        Property("targeting_excluded_geo_locations_regions", ArrayType(StringType)),
        Property("targeting_excluded_geo_locations_cities", ArrayType(StringType)),
        Property("targeting_excluded_geo_locations_zips", ArrayType(StringType)),
        Property("targeting_excluded_publisher_categories", ArrayType(StringType)),
        Property("targeting_excluded_publisher_list_ids", ArrayType(StringType)),
        Property("targeting_excluded_user_device", ArrayType(StringType)),
        Property("targeting_exclusions", ArrayType(StringType)),
        Property("targeting_family_statuses", ArrayType(StringType)),
        Property("targeting_flexible_spec", ArrayType(StringType)),
        Property("targeting_friends_of_connections", ArrayType(StringType)),
        Property("targeting_geo_locations_cities", ArrayType(StringType)),
        Property("targeting_geo_locations_country_groups", ArrayType(StringType)),
        Property("targeting_geo_locations_custom_locations", ArrayType(StringType)),
        Property("targeting_geo_locations_electoral_district", ArrayType(StringType)),
        Property("targeting_geo_locations_geo_markets", ArrayType(StringType)),
        Property("targeting_geo_locations_places", ArrayType(StringType)),
        Property("targeting_geo_locations_regions", ArrayType(StringType)),
        Property("targeting_geo_locations_zips", ArrayType(StringType)),
        Property("targeting_income", ArrayType(StringType)),
        Property("targeting_industries", ArrayType(StringType)),
        Property("targeting_interests", ArrayType(StringType)),
        Property("targeting_life_events", ArrayType(StringType)),
        Property("targeting_locales", ArrayType(StringType)),
        Property("targeting_relationship_statuses", ArrayType(StringType)),
        Property("targeting_user_adclusters", ArrayType(StringType)),
        Property("targeting_user_device", ArrayType(StringType)),
        Property("targeting_user_os", ArrayType(StringType)),
        Property("targeting_wireless_carrier", ArrayType(StringType)),
        Property("targeting_work_employers", ArrayType(StringType)),
        Property("targeting_work_positions", ArrayType(StringType)),
        Property("lifetime_min_spend_target", StringType),
        Property("lifetime_spend_cap", StringType),
    ).to_dict()

    tap_stream_id = "adsets"


# campaigns stream
class CampaignStream(FacebookStream):
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
                    ),
                ),
            ),
        ),
        Property("budget_rebalance_flag", BooleanType),
        Property("bid_strategy", StringType),
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
        Property("promoted_object_application_id", IntegerType),
        Property("promoted_object_custom_conversion_id", IntegerType),
        Property("promoted_object_custom_event_str", StringType),
        Property("promoted_object_custom_event_type", StringType),
        Property("promoted_object_event_id", IntegerType),
        Property("promoted_object_object_store_url", StringType),
        Property("promoted_object_offer_id", IntegerType),
        Property("promoted_object_offline_conversion_data_set_id", IntegerType),
        Property("promoted_object_page_id", IntegerType),
        Property("promoted_object_pixel_aggregation_rule", StringType),
        Property("promoted_object_pixel_id", IntegerType),
        Property("promoted_object_pixel_rule", StringType),
        Property("promoted_object_place_page_set_id", IntegerType),
        Property("promoted_object_product_catalog_id", IntegerType),
        Property("promoted_object_product_set_id", IntegerType),
        Property("promoted_object_retention_days", StringType),
        Property("promoted_object_application_type", StringType),
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


class CreativeStream(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-creative/."""

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
        "video_id",
    ]

    name = "creatives"
    path = f"/adcreatives?fields={columns}"
    tap_stream_id = "creatives"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "id"

    schema = PropertiesList(
        Property("id", StringType),
        Property("account_id", StringType),
        Property("actor_id", StringType),
        Property("applink_treatment", StringType),
        Property(
            "asset_feed_spec",
            ObjectType(),
        ),
        Property("authorization_category", StringType),
        Property("body", BooleanType),
        Property("branded_content_sponsor_page_id", BooleanType),
        Property("bundle_folder_id", StringType),
        Property("call_to_action_type", StringType),
        Property("categorization_criteria", StringType),
        Property("category_media_source", StringType),
        Property("degrees_of_freedom_spec", ObjectType()),
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
        Property("instagram_story_id", IntegerType),
        Property("link_destination_display_url", StringType),
        Property("link_og_id", IntegerType),
        Property("link_url", StringType),
        Property("messenger_sponsored_message", StringType),
        Property("name", StringType),
        Property("object_id", IntegerType),
        Property("object_store_url", StringType),
        Property("object_story_id", StringType),
        Property("object_story_spec", ObjectType()),
        Property("object_type", StringType),
        Property("object_url", StringType),
        Property("page_link", StringType),
        Property("page_message", StringType),
        Property("place_page_set_id", IntegerType),
        Property("platform_customizations", StringType),
        Property("playable_asset_id", IntegerType),
        Property("source_instagram_media_id", StringType),
        Property("status", StringType),
        Property("template_url", StringType),
        Property("thumbnail_id", StringType),
        Property("thumbnail_url", StringType),
        Property("title", StringType),
        Property("url_tags", StringType),
        Property("use_page_actor_override", BooleanType),
        Property("video_id", StringType),
        Property("template_app_link_spec_android", ArrayType(StringType)),
        Property("template_app_link_spec_ios", ArrayType(StringType)),
        Property("template_app_link_spec_ipad", ArrayType(StringType)),
        Property("template_app_link_spec_iphone", ArrayType(StringType)),
        Property("template_caption", StringType),
        Property("template_child_attachments", ArrayType(StringType)),
        Property("template_description", StringType),
        Property("template_link", StringType),
        Property("template_message", StringType),
        Property("template_page_link", StringType),
        Property("template_url_spec_android_app_name", StringType),
        Property("template_url_spec_android_package", StringType),
        Property("template_url_spec_android_url", StringType),
        Property("template_url_spec_config_app_id", StringType),
        Property("template_url_spec_ios_app_name", StringType),
        Property("template_url_spec_ios_app_store_id", StringType),
        Property("template_url_spec_ios_url", StringType),
        Property("template_url_spec_ipad_app_name", StringType),
        Property("template_url_spec_ipad_app_store_id", StringType),
        Property("template_url_spec_ipad_url", StringType),
        Property("template_url_spec_iphone_app_name", StringType),
        Property("template_url_spec_iphone_app_store_id", StringType),
        Property("template_url_spec_iphone_url", StringType),
        Property("template_url_spec_web_should_fallback", StringType),
        Property("template_url_spec_web_url", StringType),
        Property("template_url_spec_windows_phone_app_id", StringType),
        Property("template_url_spec_windows_phone_app_name", StringType),
        Property("template_url_spec_windows_phone_url", StringType),
        Property(
            "platform_customizations_instagram_caption_ids",
            ArrayType(StringType),
        ),
        Property("platform_customizations_instagram_image_hash", StringType),
        Property("platform_customizations_instagram_image_url", StringType),
        Property("platform_customizations_instagram_video_id", IntegerType),
        Property("object_story_link_data_caption", StringType),
        Property("object_story_link_data_description", StringType),
        Property("product_set_id", StringType),
        Property("carousel_ad_link", StringType),
    ).to_dict()


class AdLabelsStream(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-creative/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = ["id", "account", "created_time", "updated_time", "name"]  # noqa: RUF012

    name = "adlabels"
    path = f"/adlabels?fields={columns}"
    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    tap_stream_id = "adlabels"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "updated_time"

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "account",
            ObjectType(
                Property("account_id", StringType),
                Property("id", StringType),
            ),
        ),
        Property("created_time", StringType),
        Property("updated_time", StringType),
        Property("name", StringType),
    ).to_dict()


class AdAccountsStream(FacebookStream):
    """https://developers.facebook.com/docs/graph-api/reference/user/accounts/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version", "")
        return f"https://graph.facebook.com/{version}/me"

    columns = [  # noqa: RUF012
        "account_id",
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
        "tax_id",
    ]

    name = "adaccounts"
    path = f"/adaccounts?fields={columns}"
    tap_stream_id = "adaccounts"
    primary_keys = ["created_time"]  # noqa: RUF012
    replication_key = "created_time"
    replication_method = REPLICATION_INCREMENTAL

    schema = PropertiesList(
        Property("account_id", StringType),
        Property("timezone_id", IntegerType),
        Property("business_name", StringType),
        Property("account_status", IntegerType),
        Property("age", NumberType),
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
        Property("disable_reason", IntegerType),
        Property("end_advertiser", StringType),
        Property("end_advertiser_name", StringType),
        Property("has_migrated_permissions", BooleanType),
        Property("id", StringType),
        Property("is_attribution_spec_system_default", BooleanType),
        Property("is_direct_deals_enabled", BooleanType),
        Property("is_in_3ds_authorization_enabled_market", BooleanType),
        Property("is_notifications_enabled", BooleanType),
        Property("is_personal", IntegerType),
        Property("is_prepay_account", BooleanType),
        Property("is_tax_id_required", BooleanType),
        Property("min_campaign_group_spend_cap", IntegerType),
        Property("min_daily_budget", IntegerType),
        Property("name", StringType),
        Property("offsite_pixels_tos_accepted", BooleanType),
        Property("owner", StringType),
        Property("spend_cap", IntegerType),
        Property("tax_id_status", IntegerType),
        Property("tax_id_type", StringType),
        Property("timezone_id", IntegerType),
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
        Property(
            "agency_client_declaration_has_written_mandate_from_advertiser",
            IntegerType,
        ),
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
        Property("tax_id", StringType),
    ).to_dict()

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        row["amount_spent"] = (
            int(row["amount_spent"]) if "amount_spent" in row else None
        )
        row["balance"] = int(row["balance"]) if "balance" in row else None
        row["min_campaign_group_spend_cap"] = (
            int(row["min_campaign_group_spend_cap"])
            if "min_campaign_group_spend_cap" in row
            else None
        )
        row["spend_cap"] = int(row["spend_cap"]) if "spend_cap" in row else None
        return row

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


class CustomConversions(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/custom-audience/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = [  # noqa: RUF012
        "account_id",
        "id",
        "creation_time",
        "name",
        "business",
        "is_archived",
        "is_unavailable",
        "last_fired_time",
    ]

    name = "customconversions"
    path = f"/customconversions?fields={columns}"
    tap_stream_id = "customconversions"
    primary_keys = ["id"]  # noqa: RUF012
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "creation_time"

    schema = PropertiesList(
        Property("account_id", StringType),
        Property("id", StringType),
        Property("name", StringType),
        Property("creation_time", StringType),
        Property("business", ObjectType()),
        Property("is_archived", BooleanType),
        Property("is_unavailable", BooleanType),
        Property("last_fired_time", StringType),
    ).to_dict()


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
        Property("time_updated", StringType),
        Property("time_created", StringType),
        Property("time_content_updated", StringType),
        Property("customer_file_source", StringType),
        Property("data_source", StringType),
        Property("delivery_status", StringType),
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


class AdImages(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-image/."""

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
        "created_time",
        "creatives",
        "hash",
        "height",
        "is_associated_creatives_in_adgroups",
        "name",
        "original_height",
        "original_width",
        "permalink_url",
        "status",
        "updated_time",
        "url",
        "url_128",
        "width",
    ]

    name = "adimages"
    path = f"/adimages?fields={columns}"
    tap_stream_id = "images"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "id"

    schema = PropertiesList(
        Property("id", StringType),
        Property("account_id", StringType),
        Property("created_time", StringType),
        Property("creatives", ArrayType(StringType)),
        Property("hash", StringType),
        Property("height", IntegerType),
        Property("is_associated_creatives_in_adgroups", BooleanType),
        Property("name", StringType),
        Property("original_height", IntegerType),
        Property("original_width", IntegerType),
        Property("permalink_url", StringType),
        Property("status", StringType),
        Property("updated_time", StringType),
        Property("url", StringType),
        Property("url_128", StringType),
        Property("width", IntegerType),
    ).to_dict()


class AdVideos(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-image/."""

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
        "updated_time",
        "account_id",
        "ad_breaks",
        "backdated_time",
        "backdated_time_granularity",
        "content_category",
        "content_tags",
        "created_time",
        "custom_labels",
        "description",
        "embed_html",
        "embeddable",
        "event",
        "format",
        "from_object",
        "icon",
        "is_crosspost_video",
        "is_crossposting_eligible",
        "is_episode",
        "is_instagram_eligible",
        # "is_reference_only",
        "length",
        "live_status",
        # "music_video_copyright",
        "permalink_url",
        "place",
        "post_views",
        "premiere_living_room_status",
        "privacy",
        "published",
        "scheduled_publish_time",
        "source",
        "status_processing_progress",
        "status_value",
        "title",
        "universal_video_id",
        "views",
    ]

    name = "advideos"
    path = f"/advideos?fields={columns}"
    tap_stream_id = "videos"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "id"

    schema = PropertiesList(
        Property("id", StringType),
        Property("account_id", StringType),
        Property("ad_breaks", StringType),
        Property("backdated_time", DateTimeType),
        Property("backdated_time_granularity", StringType),
        Property("content_category", StringType),
        Property("content_tags", StringType),
        Property("created_time", StringType),
        Property("custom_labels", StringType),
        Property("description", StringType),
        Property("embed_html", StringType),
        Property("embeddable", BooleanType),
        Property("event", StringType),
        Property("format", ArrayType(ObjectType())),
        Property("from_object", StringType),
        Property("icon", StringType),
        Property("is_crosspost_video", BooleanType),
        Property("is_crossposting_eligible", BooleanType),
        Property("is_episode", BooleanType),
        Property("is_instagram_eligible", BooleanType),
        Property("is_reference_only", BooleanType),
        Property("length", NumberType),
        Property("live_status", StringType),
        Property("music_video_copyright", StringType),
        Property("permalink_url", StringType),
        Property("place", StringType),
        Property("post_views", IntegerType),
        Property("premiere_living_room_status", StringType),
        Property("privacy", ObjectType()),
        Property("published", BooleanType),
        Property("scheduled_publish_time", DateTimeType),
        Property("source", StringType),
        Property("status_processing_progress", IntegerType),
        Property("status_value", StringType),
        Property("title", StringType),
        Property("universal_video_id", StringType),
        Property("updated_time", StringType),
        Property("views", IntegerType),
    ).to_dict()

"""Stream class for Adsets."""

from __future__ import annotations

from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL
from nekt_singer_sdk.typing import (
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

from tap_facebook.client import IncrementalFacebookStream


class AdsetsStream(IncrementalFacebookStream):
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
    filter_entity = "adset"

    path = f"/adsets?fields={columns}"
    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    replication_key = "updated_time"

    schema = PropertiesList(
        Property(
            "name",
            StringType,
            description="Name of the ad set",
        ),
        Property(
            "end_time",
            StringType,
            description="End time for the ad set schedule",
        ),
        Property(
            "billing_event",
            StringType,
            description="Billing event (e.g. IMPRESSIONS, LINK_CLICKS, APP_INSTALLS)",
        ),
        Property(
            "campaign_attribution",
            StringType,
            description="Campaign attribution setting",
        ),
        Property(
            "destination_type",
            StringType,
            description="Type of destination for the ad set",
        ),
        Property(
            "is_dynamic_creative",
            BooleanType,
            description="Whether dynamic creative is enabled",
        ),
        Property(
            "lifetime_imps",
            IntegerType,
            description="Lifetime impressions for the ad set",
        ),
        Property(
            "multi_optimization_goal_weight",
            StringType,
            description="Weights for multi-optimization goal",
        ),
        Property(
            "optimization_goal",
            StringType,
            description="Optimization goal (e.g. REACH, LINK_CLICKS, CONVERSIONS)",
        ),
        Property(
            "optimization_sub_event",
            StringType,
            description="Sub-event for optimization",
        ),
        Property(
            "pacing_type",
            ArrayType(StringType),
            description="Pacing type for ad delivery",
        ),
        Property(
            "recurring_budget_semantics",
            BooleanType,
            description="Whether recurring budget semantics are used",
        ),
        Property(
            "source_adset_id",
            StringType,
            description="ID of the source ad set if this was copied",
        ),
        Property(
            "status",
            StringType,
            description="Status of the ad set (ACTIVE, PAUSED, etc.)",
        ),
        Property(
            "targeting_optimization_types",
            StringType,
            description="Targeting optimization types",
        ),
        Property(
            "use_new_app_click",
            BooleanType,
            description="Whether to use new app click tracking",
        ),
        Property(
            "promoted_object",
            ObjectType(
                Property("custom_event_type", StringType, description="Custom event type for promotion"),
                Property("pixel_id", StringType, description="Facebook Pixel ID"),
                Property("pixel_rule", StringType, description="Pixel aggregation rule"),
                Property("page_id", StringType, description="Facebook Page ID"),
                Property("object_store_url", StringType, description="App store or object URL"),
                Property("application_id", StringType, description="Application ID"),
                Property("product_set_id", StringType, description="Product set ID"),
                Property("offer_id", StringType, description="Offer ID"),
                Property("custom_conversion_id", StringType, description="Custom conversion ID"),
                Property("custom_event_str", StringType, description="Custom event string"),
                Property("event_id", IntegerType, description="Event ID"),
                Property("offline_conversion_data_set_id", IntegerType, description="Offline conversion dataset ID"),
                Property("pixel_aggregation_rule", StringType, description="Pixel aggregation rule"),
                Property("place_page_set_id", IntegerType, description="Place page set ID"),
                Property("product_catalog_id", IntegerType, description="Product catalog ID"),
                Property("retention_days", StringType, description="Retention days"),
                Property("application_type", StringType, description="Application type"),
            ),
            description="Object describing what is being promoted (page_id, pixel_id, app_id, etc.)",
        ),
        Property(
            "id",
            StringType,
            description="ID of the ad set",
        ),
        Property(
            "account_id",
            StringType,
            description="ID of the ad account",
        ),
        Property(
            "updated_time",
            StringType,
            description="When the ad set was last updated",
        ),
        Property(
            "daily_budget",
            StringType,
            description="Daily budget in smallest currency unit",
        ),
        Property(
            "budget_remaining",
            StringType,
            description="Remaining budget for the ad set",
        ),
        Property(
            "effective_status",
            StringType,
            description="Effective status considering parent campaign",
        ),
        Property(
            "campaign_id",
            StringType,
            description="ID of the parent campaign",
        ),
        Property(
            "created_time",
            StringType,
            description="When the ad set was created",
        ),
        Property(
            "start_time",
            StringType,
            description="Start time for the ad set schedule",
        ),
        Property(
            "lifetime_budget",
            StringType,
            description="Lifetime budget in smallest currency unit",
        ),
        Property(
            "bid_info",
            ObjectType(
                Property("CLICKS", IntegerType, description="Bid value for CLICKS optimization"),
                Property("ACTIONS", IntegerType, description="Bid value for ACTIONS optimization"),
                Property("REACH", IntegerType, description="Bid value for REACH optimization"),
                Property("IMPRESSIONS", IntegerType, description="Bid value for IMPRESSIONS optimization"),
                Property("SOCIAL", IntegerType, description="Bid value for SOCIAL optimization"),
            ),
            description="Map of optimization objective to bid value",
        ),
        Property(
            "adlabels",
            ArrayType(
                Property(
                    "items",
                    ObjectType(
                        Property("id", StringType, description="Ad label ID"),
                        Property("name", StringType, description="Ad label name"),
                        Property("created_time", DateTimeType, description="Ad label created time"),
                    ),
                ),
            ),
            description="Ad labels associated with this ad set",
        ),
        Property(
            "attribution_spec",
            ArrayType(
                ObjectType(
                    Property("event_type", StringType, description="Conversion event type"),
                    Property("window_days", IntegerType, description="Attribution window in days"),
                ),
            ),
            description="Conversion attribution spec (event_type, window_days)",
        ),
        Property(
            "learning_stage_info",
            ObjectType(
                Property("attribution_windows", ArrayType(StringType), description="Attribution windows"),
                Property("conversions", IntegerType, description="Number of conversions"),
                Property("last_sig_edit_ts", IntegerType, description="Last significant edit timestamp"),
                Property("status", StringType, description="Learning stage status"),
            ),
            description="Learning stage info (attribution windows, conversions, status)",
        ),
        Property(
            "configured_status",
            StringType,
            description="User-configured status of the ad set",
        ),
        Property(
            "asset_feed_id",
            StringType,
            description="ID of the asset feed for ad content",
        ),
        Property(
            "daily_min_spend_target",
            StringType,
            description="Daily minimum spend target",
        ),
        Property(
            "daily_spend_cap",
            StringType,
            description="Daily spend cap",
        ),
        Property(
            "instagram_actor_id",
            StringType,
            description="Instagram actor (business) ID",
        ),
        Property(
            "review_feedback",
            StringType,
            description="Feedback from ad review",
        ),
        Property(
            "rf_prediction_id",
            StringType,
            description="Reach and frequency prediction ID",
        ),
        Property(
            "bid_amount",
            IntegerType,
            description="Bid cap or target cost in smallest currency unit",
        ),
        Property(
            "bid_strategy",
            StringType,
            description="Bid strategy (e.g. LOWEST_COST_WITHOUT_CAP, LOWEST_COST_WITH_BID_CAP, COST_CAP)",
        ),
        Property(
            "targeting",
            ObjectType(
                Property("age_max", IntegerType, description="Maximum age for targeting"),
                Property("age_min", IntegerType, description="Minimum age for targeting"),
                Property(
                    "custom_audiences",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType, description="Custom audience ID"),
                            Property("name", StringType, description="Custom audience name"),
                            Property("primary_city_id", IntegerType, description="Primary city ID"),
                            Property("country", StringType, description="Country"),
                            Property("region_id", StringType, description="Region ID"),
                        ),
                    ),
                    description="Custom audiences to target",
                ),
                Property(
                    "excluded_custom_audiences",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType, description="Custom audience ID"),
                            Property("name", StringType, description="Custom audience name"),
                            Property("primary_city_id", IntegerType, description="Primary city ID"),
                            Property("country", StringType, description="Country"),
                            Property("region_id", StringType, description="Region ID"),
                        ),
                    ),
                    description="Custom audiences to exclude",
                ),
                Property(
                    "geo_locations",
                    ObjectType(
                        Property("countries", ArrayType(StringType), description="Target countries"),
                        Property("location_types", ArrayType(StringType), description="Location types"),
                    ),
                    description="Geographic targeting",
                ),
                Property("genders", ArrayType(IntegerType), description="Target genders"),
                Property("brand_safety_content_filter_levels", ArrayType(StringType), description="Brand safety filter levels"),
                Property("publisher_platforms", ArrayType(StringType), description="Publisher platforms (facebook, instagram, etc.)"),
                Property("facebook_positions", ArrayType(StringType), description="Facebook ad positions"),
                Property("instagram_positions", ArrayType(StringType), description="Instagram ad positions"),
                Property("device_platforms", ArrayType(StringType), description="Device platforms"),
                Property("app_install_state", StringType, description="App install state targeting"),
                Property("audience_network_positions", ArrayType(StringType), description="Audience Network positions"),
                Property(
                    "behaviors",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType, description="Behavior ID"),
                            Property("name", StringType, description="Behavior name"),
                        )
                    ),
                    description="Behavior targeting",
                ),
                Property("college_years", ArrayType(IntegerType), description="College years targeting"),
                Property("connections", ArrayType(ObjectType()), description="Connections targeting"),
                Property(
                    "education_majors",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType, description="Education major ID"),
                            Property("name", StringType, description="Education major name"),
                        )
                    ),
                    description="Education majors targeting",
                ),
                Property(
                    "education_schools",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType, description="Education school ID"),
                            Property("name", StringType, description="Education school name"),
                        )
                    ),
                    description="Education schools targeting",
                ),
                Property("education_statuses", ArrayType(IntegerType), description="Education statuses targeting"),
                Property(
                    "effective_audience_network_positions",
                    ArrayType(StringType),
                    description="Effective Audience Network positions",
                ),
                Property("excluded_connections", ArrayType(ObjectType()), description="Excluded connections"),
                Property(
                    "excluded_geo_locations",
                    ObjectType(
                        Property("countries", ArrayType(StringType), description="Excluded countries"),
                        Property("country_groups", ArrayType(StringType), description="Excluded country groups"),
                        Property(
                            "custom_locations",
                            ArrayType(
                                ObjectType(
                                    Property("address_string", StringType, description="Address string"),
                                    Property("radius", IntegerType, description="Radius"),
                                    Property("latitude", NumberType, description="Latitude"),
                                    Property("longitude", NumberType, description="Longitude"),
                                    Property("radius", IntegerType, description="Radius in distance_unit"),
                                    Property("distance_unit", StringType, description="Distance unit (e.g. mile, km)"),
                                )
                            ),
                            description="Excluded custom locations",
                        ),
                        Property("electoral_district", ArrayType(ObjectType(Property("key", StringType, description="District key"))), description="Excluded electoral districts"),
                        Property(
                            "geo_markets",
                            ArrayType(ObjectType(Property("key", StringType, description="Market key"), Property("name", StringType, description="Market name"))),
                            description="Excluded geo markets",
                        ),
                        Property("location_types", ArrayType(StringType), description="Excluded location types"),
                        Property(
                            "places",
                            ArrayType(
                                ObjectType(
                                    Property("key", StringType, description="Place key"),
                                    Property("country", StringType, description="Country"),
                                    Property("latitude", NumberType, description="Latitude"),
                                    Property("longitude", NumberType, description="Longitude"),
                                    Property("name", StringType, description="Place name"),
                                    Property("radius", IntegerType, description="Radius"),
                                    Property("primary_city_id", IntegerType, description="Primary city ID"),
                                    Property("region_id", IntegerType, description="Region ID"),
                                    Property("distance_unit", StringType, description="Distance unit"),
                                )
                            ),
                            description="Excluded places",
                        ),
                        Property("regions", ArrayType(ObjectType(Property("key", StringType, description="Region key"))), description="Excluded regions"),
                        Property(
                            "cities",
                            ArrayType(
                                ObjectType(
                                    Property("key", StringType, description="City key"),
                                    Property("country", StringType, description="Country"),
                                    Property("name", StringType, description="City name"),
                                    Property("radius", IntegerType, description="Radius"),
                                    Property("region_id", StringType, description="Region ID"),
                                    Property("distance_unit", StringType, description="Distance unit"),
                                )
                            ),
                            description="Excluded cities",
                        ),
                        Property("zips", ArrayType(ObjectType(Property("key", StringType, description="ZIP key"))), description="Excluded ZIP codes"),
                    ),
                    description="Excluded geographic locations",
                ),
                Property("excluded_publisher_categories", ArrayType(StringType), description="Excluded publisher categories"),
                Property("excluded_publisher_list_ids", ArrayType(StringType), description="Excluded publisher list IDs"),
                Property("excluded_user_device", ArrayType(StringType), description="Excluded user devices"),
                Property(
                    "exclusions",
                    ObjectType(
                        Property(
                            "work_employers",
                            ArrayType(ObjectType(Property("id", StringType, description="Employer ID"), Property("name", StringType, description="Employer name"))),
                            description="Excluded work employers",
                        ),
                        Property(
                            "work_positions",
                            ArrayType(ObjectType(Property("id", StringType, description="Position ID"), Property("name", StringType, description="Position name"))),
                            description="Excluded work positions",
                        ),
                        Property(
                            "income",
                            ArrayType(ObjectType(Property("id", StringType, description="Income ID"), Property("name", StringType, description="Income name"))),
                            description="Excluded income ranges",
                        ),
                        Property(
                            "industries",
                            ArrayType(ObjectType(Property("id", StringType, description="Industry ID"), Property("name", StringType, description="Industry name"))),
                            description="Excluded industries",
                        ),
                        Property(
                            "interests",
                            ArrayType(ObjectType(Property("id", StringType, description="Interest ID"), Property("name", StringType, description="Interest name"))),
                            description="Excluded interests",
                        ),
                        Property(
                            "life_events",
                            ArrayType(ObjectType(Property("id", StringType, description="Life event ID"), Property("name", StringType, description="Life event name"))),
                            description="Excluded life events",
                        ),
                        Property(
                            "education_majors",
                            ArrayType(ObjectType(Property("id", StringType, description="Education major ID"), Property("name", StringType, description="Education major name"))),
                            description="Excluded education majors",
                        ),
                        Property(
                            "education_schools",
                            ArrayType(ObjectType(Property("id", StringType, description="School ID"), Property("name", StringType, description="School name"))),
                            description="Excluded education schools",
                        ),
                        Property("education_statuses", ArrayType(IntegerType), description="Excluded education statuses"),
                        Property(
                            "family_statuses",
                            ArrayType(ObjectType(Property("id", StringType, description="Family status ID"), Property("name", StringType, description="Family status name"))),
                            description="Excluded family statuses",
                        ),
                        Property("college_years", ArrayType(IntegerType), description="Excluded college years"),
                        Property(
                            "behaviors",
                            ArrayType(ObjectType(Property("id", StringType, description="Behavior ID"), Property("name", StringType, description="Behavior name"))),
                            description="Excluded behaviors",
                        ),
                    ),
                    description="Targeting exclusions (demographics, interests, etc.)",
                ),
                Property(
                    "family_statuses",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType, description="Family status ID"),
                            Property("name", StringType, description="Family status name"),
                        )
                    ),
                    description="Family statuses targeting",
                ),
                # Property("flexible_spec", ArrayType(ObjectType())), # not enough documentation or examples
                Property("friends_of_connections", ArrayType(ObjectType()), description="Friends of connections targeting"),
                Property(
                    "geo_locations",
                    ObjectType(
                        Property("countries", ArrayType(StringType), description="Target countries"),
                        Property("country_groups", ArrayType(StringType), description="Target country groups"),
                        Property(
                            "custom_locations",
                            ArrayType(
                                ObjectType(
                                    Property("address_string", StringType, description="Address string"),
                                    Property("radius", IntegerType, description="Radius"),
                                    Property("latitude", NumberType, description="Latitude"),
                                    Property("longitude", NumberType, description="Longitude"),
                                    Property("radius", IntegerType, description="Radius in distance_unit"),
                                    Property("distance_unit", StringType, description="Distance unit"),
                                )
                            ),
                            description="Custom geographic locations",
                        ),
                        Property("electoral_district", ArrayType(ObjectType(Property("key", StringType, description="District key"))), description="Electoral districts"),
                        Property(
                            "geo_markets",
                            ArrayType(ObjectType(Property("key", StringType, description="Market key"), Property("name", StringType, description="Market name"))),
                            description="Geo markets",
                        ),
                        Property("location_types", ArrayType(StringType), description="Location types"),
                        Property(
                            "places",
                            ArrayType(
                                ObjectType(
                                    Property("key", StringType, description="Place key"),
                                    Property("country", StringType, description="Country"),
                                    Property("latitude", NumberType, description="Latitude"),
                                    Property("longitude", NumberType, description="Longitude"),
                                    Property("name", StringType, description="Place name"),
                                    Property("radius", IntegerType, description="Radius"),
                                    Property("primary_city_id", IntegerType, description="Primary city ID"),
                                    Property("region_id", IntegerType, description="Region ID"),
                                    Property("distance_unit", StringType, description="Distance unit"),
                                )
                            ),
                            description="Target places",
                        ),
                        Property("regions", ArrayType(ObjectType(Property("key", StringType, description="Region key"))), description="Target regions"),
                        Property(
                            "cities",
                            ArrayType(
                                ObjectType(
                                    Property("key", StringType, description="City key"),
                                    Property("country", StringType, description="Country"),
                                    Property("name", StringType, description="City name"),
                                    Property("radius", IntegerType, description="Radius"),
                                    Property("region_id", StringType, description="Region ID"),
                                    Property("distance_unit", StringType, description="Distance unit"),
                                )
                            ),
                            description="Target cities",
                        ),
                        Property("zips", ArrayType(ObjectType(Property("key", StringType, description="ZIP key"))), description="Target ZIP codes"),
                    ),
                    description="Geographic targeting (countries, regions, cities, etc.)",
                ),
                Property(
                    "income",
                    ArrayType(ObjectType(Property("id", StringType, description="Income range ID"), Property("name", StringType, description="Income range name"))),
                    description="Income targeting",
                ),
                Property(
                    "industries",
                    ArrayType(ObjectType(Property("id", StringType, description="Industry ID"), Property("name", StringType, description="Industry name"))),
                    description="Industries targeting",
                ),
                Property(
                    "interests",
                    ArrayType(ObjectType(Property("id", StringType, description="Interest ID"), Property("name", StringType, description="Interest name"))),
                    description="Interests targeting",
                ),
                Property(
                    "life_events",
                    ArrayType(ObjectType(Property("id", StringType, description="Life event ID"), Property("name", StringType, description="Life event name"))),
                    description="Life events targeting",
                ),
                Property("locales", ArrayType(IntegerType), description="Locales targeting"),
                Property("relationship_statuses", ArrayType(IntegerType), description="Relationship statuses targeting"),
                Property("user_adclusters", ArrayType(ObjectType()), description="User ad clusters"),
                Property("user_device", ArrayType(StringType), description="User device targeting"),
                Property("user_os", ArrayType(StringType), description="User OS targeting"),
                Property("wireless_carrier", ArrayType(StringType), description="Wireless carrier targeting"),
                Property(
                    "work_employers",
                    ArrayType(ObjectType(Property("id", StringType, description="Employer ID"), Property("name", StringType, description="Employer name"))),
                    description="Work employers targeting",
                ),
                Property(
                    "work_positions",
                    ArrayType(ObjectType(Property("id", StringType, description="Position ID"), Property("name", StringType, description="Position name"))),
                    description="Work positions targeting",
                ),
            ),
            description="Targeting specification (geo, age, interests, placements, etc.)",
        ),
        Property(
            "lifetime_min_spend_target",
            StringType,
            description="Lifetime minimum spend target",
        ),
        Property(
            "lifetime_spend_cap",
            StringType,
            description="Lifetime spend cap",
        ),
    ).to_dict()

    tap_stream_id = "adsets"

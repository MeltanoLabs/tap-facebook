"""Stream class for AdsStream."""

from __future__ import annotations

from singer_sdk.streams.core import REPLICATION_INCREMENTAL
from singer_sdk.typing import (
    ArrayType,
    DateTimeType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import IncrementalFacebookStream


class AdsStream(IncrementalFacebookStream):
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
    filter_entity = "ad"

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

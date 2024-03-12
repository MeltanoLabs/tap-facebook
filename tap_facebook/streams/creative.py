"""Stream class for Creative."""

from __future__ import annotations

from singer_sdk.streams.core import REPLICATION_INCREMENTAL
from singer_sdk.typing import (
    BooleanType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream


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
        Property("body", StringType),
        Property("branded_content_sponsor_page_id", StringType),
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
        Property("instagram_story_id", StringType),
        Property("link_destination_display_url", StringType),
        Property("link_og_id", StringType),
        Property("link_url", StringType),
        Property("messenger_sponsored_message", StringType),
        Property("name", StringType),
        Property("object_id", StringType),
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
        Property(
            "template_url_spec",
            ObjectType(
                Property(
                    "android",
                    ObjectType(
                        Property("app_name", StringType),
                        Property("package", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "config",
                    ObjectType(
                        Property("app_id", StringType),
                    ),
                ),
                Property(
                    "ios",
                    ObjectType(
                        Property("app_name", StringType),
                        Property("app_store_id", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "ipad",
                    ObjectType(
                        Property("app_name", StringType),
                        Property("app_store_id", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "iphone",
                    ObjectType(
                        Property("app_name", StringType),
                        Property("app_store_id", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "web",
                    ObjectType(
                        Property("should_fallback", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "windows_phone",
                    ObjectType(
                        Property("app_id", StringType),
                        Property("app_name", StringType),
                        Property("url", StringType),
                    ),
                ),
            ),
        ),
        Property("product_set_id", StringType),
        Property("carousel_ad_link", StringType),
    ).to_dict()

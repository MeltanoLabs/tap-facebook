"""Stream class for Creative."""

from __future__ import annotations

import typing as t

from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL, Stream
from nekt_singer_sdk.typing import (
    BooleanType,
    DateTimeType,
    IntegerType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.streams.ads import AdsStream

# Field sets for different extraction modes
BASIC_FIELDS = [
    "account_id",
    "body",
    "id",
    "name",
    "status",
    "title",
    "actor_id",
    "authorization_category",
    "call_to_action_type",
    "enable_direct_install",
    "link_url",
    "object_id",
    "object_type",
    "object_url",
    "use_page_actor_override",
]

ADVANCED_FIELDS = [
    *BASIC_FIELDS,
    "applink_treatment",
    "branded_content_sponsor_page_id",
    "bundle_folder_id",
    "categorization_criteria",
    "category_media_source",
    "degrees_of_freedom_spec",
    "destination_set_id",
    "dynamic_ad_voice",
    "effective_authorization_category",
    "effective_instagram_media_id",
    "effective_instagram_story_id",
    "effective_object_story_id",
    "image_hash",
    "image_url",
    "instagram_user_id",
    "instagram_permalink_url",
    "instagram_story_id",
    "link_destination_display_url",
    "link_og_id",
    "object_store_url",
    "object_story_id",
    "place_page_set_id",
    "playable_asset_id",
    "source_instagram_media_id",
    "template_url",
    "thumbnail_id",
    "thumbnail_url",
    "url_tags",
    "video_id",
]


class CreativeStream(Stream):
    """Facebook Ad Creative stream using child context from AdsStream.

    This stream extracts creative data from the ads stream without making
    additional API calls, providing true incremental sync and avoiding
    rate limiting issues.
    """

    name = "creatives"
    tap_stream_id = "creatives"
    replication_key = "ad_updated_time"
    primary_keys = ["id"]  # noqa: RUF012
    parent_stream_type = AdsStream
    state_partitioning_keys = []

    @property
    def columns(self) -> list[str]:
        """Get columns based on creative_fields_mode configuration."""
        fields_mode = self.config.get("creative_fields_mode", "basic")

        if fields_mode == "basic":
            return BASIC_FIELDS
        if fields_mode == "advanced":
            return ADVANCED_FIELDS
        return BASIC_FIELDS

    schema = PropertiesList(
        Property("id", StringType),
        Property("account_id", StringType),
        Property("actor_id", StringType),
        Property("applink_treatment", StringType),
        Property("authorization_category", StringType),
        Property("body", StringType),
        Property("branded_content_sponsor_page_id", StringType),
        Property("bundle_folder_id", StringType),
        Property("call_to_action_type", StringType),
        Property("categorization_criteria", StringType),
        Property("category_media_source", StringType),
        Property("destination_set_id", StringType),
        Property("dynamic_ad_voice", StringType),
        Property("effective_authorization_category", StringType),
        Property("effective_instagram_media_id", StringType),
        Property("effective_instagram_story_id", StringType),
        Property("effective_object_story_id", StringType),
        Property("enable_direct_install", BooleanType),
        Property("image_hash", StringType),
        Property("image_url", StringType),
        Property("instagram_user_id", StringType),
        Property("instagram_permalink_url", StringType),
        Property("instagram_story_id", StringType),
        Property("link_destination_display_url", StringType),
        Property("link_og_id", StringType),
        Property("link_url", StringType),
        Property("name", StringType),
        Property("object_id", StringType),
        Property("object_store_url", StringType),
        Property("object_story_id", StringType),
        Property("object_type", StringType),
        Property("object_url", StringType),
        Property("place_page_set_id", IntegerType),
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
        # Additional fields from parent ad context
        Property("ad_id", StringType),
        Property("ad_updated_time", DateTimeType),
    ).to_dict()

    def get_records(
        self,
        context: dict | None,
    ) -> t.Iterable[dict | tuple[dict, dict | None]]:
        """Get creative records from parent ads stream context.

        Args:
            context: Context from parent AdsStream containing creative data.

        Yields:
            Individual creative record dictionaries.
        """
        if not context or "creative" not in context:
            return

        creative_data = {
            **context["creative"],
            "ad_id": context.get("ad_id"),
            "ad_updated_time": context.get("ad_updated_time"),
        }

        yield creative_data

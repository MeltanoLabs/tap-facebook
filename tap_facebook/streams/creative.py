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
        Property(
            "id",
            StringType,
            description="Unique ID for the ad creative",
        ),
        Property(
            "account_id",
            StringType,
            description="Ad account ID this creative belongs to",
        ),
        Property(
            "actor_id",
            StringType,
            description="The actor ID (Page ID) of this creative",
        ),
        Property(
            "applink_treatment",
            StringType,
            description="For Dynamic Ads: action when app is not installed (e.g. open webpage or app store)",
        ),
        Property(
            "authorization_category",
            StringType,
            description="Whether ad is labeled as political (e.g. POLITICAL, POLITICAL_WITH_DIGITALLY_CREATED_MEDIA)",
        ),
        Property(
            "body",
            StringType,
            description="The body text of the ad; not supported for video post creatives",
        ),
        Property(
            "branded_content_sponsor_page_id",
            StringType,
            description="Page ID representing business that runs Branded Content ads",
        ),
        Property(
            "bundle_folder_id",
            StringType,
            description="Dynamic Ad bundle folder ID",
        ),
        Property(
            "call_to_action_type",
            StringType,
            description="Type of CTA button (e.g. SHOP_NOW, LEARN_MORE, INSTALL_APP)",
        ),
        Property(
            "categorization_criteria",
            StringType,
            description="Dynamic Category Ad categorization field (e.g. brand)",
        ),
        Property(
            "category_media_source",
            StringType,
            description="Dynamic Ad rendering mode for category ads",
        ),
        Property(
            "destination_set_id",
            StringType,
            description="Destination set ID for the creative",
        ),
        Property(
            "dynamic_ad_voice",
            StringType,
            description="Voice setting for dynamic ads",
        ),
        Property(
            "effective_authorization_category",
            StringType,
            description="Effective authorization category applied to the creative",
        ),
        Property(
            "effective_instagram_media_id",
            StringType,
            description="Effective Instagram media ID when using Instagram content",
        ),
        Property(
            "effective_instagram_story_id",
            StringType,
            description="Effective Instagram story ID",
        ),
        Property(
            "effective_object_story_id",
            StringType,
            description="ID of the page post or story used in the creative",
        ),
        Property(
            "enable_direct_install",
            BooleanType,
            description="Whether direct install is enabled for app ads",
        ),
        Property(
            "image_hash",
            StringType,
            description="Hash of the image from ad account image library",
        ),
        Property(
            "image_url",
            StringType,
            description="URL of the image used in the creative",
        ),
        Property(
            "instagram_user_id",
            StringType,
            description="Instagram user ID when creative uses Instagram content",
        ),
        Property(
            "instagram_permalink_url",
            StringType,
            description="Permanent link to the Instagram content",
        ),
        Property(
            "instagram_story_id",
            StringType,
            description="Instagram story ID",
        ),
        Property(
            "link_destination_display_url",
            StringType,
            description="Display URL for the link destination",
        ),
        Property(
            "link_og_id",
            StringType,
            description="Open Graph object ID for the link",
        ),
        Property(
            "link_url",
            StringType,
            description="URL the ad links to",
        ),
        Property(
            "name",
            StringType,
            description="Name of the creative",
        ),
        Property(
            "object_id",
            StringType,
            description="ID of the object (e.g. link, video) in the creative",
        ),
        Property(
            "object_store_url",
            StringType,
            description="App store or destination URL for the object",
        ),
        Property(
            "object_story_id",
            StringType,
            description="ID of the story (page post) used in the creative",
        ),
        Property(
            "object_type",
            StringType,
            description="Type of object (SHARE, PHOTO, VIDEO, etc.)",
        ),
        Property(
            "object_url",
            StringType,
            description="URL of the object",
        ),
        Property(
            "place_page_set_id",
            IntegerType,
            description="Place page set ID for location-based creatives",
        ),
        Property(
            "playable_asset_id",
            IntegerType,
            description="Playable asset ID for playable ad creatives",
        ),
        Property(
            "source_instagram_media_id",
            StringType,
            description="Source Instagram media ID when repurposing Instagram content",
        ),
        Property(
            "status",
            StringType,
            description="Status of the creative (ACTIVE, DELETED, etc.)",
        ),
        Property(
            "template_url",
            StringType,
            description="URL of the template for dynamic creatives",
        ),
        Property(
            "thumbnail_id",
            StringType,
            description="ID of the thumbnail image",
        ),
        Property(
            "thumbnail_url",
            StringType,
            description="URL of the thumbnail for the creative",
        ),
        Property(
            "title",
            StringType,
            description="Title of the ad",
        ),
        Property(
            "url_tags",
            StringType,
            description="URL parameters for tracking",
        ),
        Property(
            "use_page_actor_override",
            BooleanType,
            description="Whether to use page actor override for the creative",
        ),
        Property(
            "video_id",
            StringType,
            description="ID of the video used in the creative",
        ),
        Property(
            "ad_id",
            StringType,
            description="ID of the parent ad (from context)",
        ),
        Property(
            "ad_updated_time",
            DateTimeType,
            description="When the parent ad was last updated (from context)",
        ),
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

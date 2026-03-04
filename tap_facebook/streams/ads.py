"""Stream class for AdsStream."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict

from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL
from nekt_singer_sdk.typing import (
    ArrayType,
    DateTimeType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import IncrementalFacebookStream

if TYPE_CHECKING:
    from tap_facebook.streams.creative import CreativeStream


class AdsStream(IncrementalFacebookStream):
    """Ads stream class.

    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id.
    """

    name = "ads"
    filter_entity = "ad"

    @cached_property
    def path(self) -> str:
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
            "tracking_specs",
            "conversion_specs",
            "recommendations",
            "configured_status",
            "conversion_domain",
            "bid_amount",
        ]

        if "creatives" in self._tap.streams:
            creative_stream: CreativeStream = self._tap.streams["creatives"]
            thumbnail_width = self.config.get("creative_thumbnail_width", 1024)
            thumbnail_height = self.config.get("creative_thumbnail_height", 1024)
            return (
                f"/ads?fields={','.join(columns)},"
                f"creative.thumbnail_width({thumbnail_width}).thumbnail_height({thumbnail_height}){{{','.join(creative_stream.columns)}}}"
            )
        return f"/ads?fields={','.join([*columns, 'creative'])}"

    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    replication_key = "updated_time"

    schema = PropertiesList(
        Property(
            "bid_type",
            StringType,
            description="The bid type for this ad (e.g. CPC, CPM)",
        ),
        Property(
            "account_id",
            StringType,
            description="ID of the ad account this ad belongs to",
        ),
        Property(
            "ad_acive_time",
            StringType,
            description="Time the ad was active",
        ),
        Property(
            "ad_schedule_end_time",
            DateTimeType,
            description="Scheduled end time for the ad",
        ),
        Property(
            "ad_schedule_start_time",
            DateTimeType,
            description="Scheduled start time for the ad",
        ),
        Property(
            "campaign_id",
            StringType,
            description="ID of the campaign this ad belongs to",
        ),
        Property(
            "adset_id",
            StringType,
            description="ID of the ad set this ad belongs to",
        ),
        Property(
            "bid_amount",
            IntegerType,
            description="Bid amount in the smallest currency unit (e.g. cents)",
        ),
        Property(
            "status",
            StringType,
            description="Configured status of the ad (ACTIVE, PAUSED, etc.)",
        ),
        Property(
            "creative",
            ObjectType(
                Property("creative_id", StringType, description="ID of the creative"),
                Property("id", StringType, description="Creative node ID"),
            ),
            description="Creative object defining the ad's appearance and content",
        ),
        Property(
            "id",
            StringType,
            description="Unique ID for the ad",
        ),
        Property(
            "updated_time",
            StringType,
            description="When the ad was last updated (ISO 8601)",
        ),
        Property(
            "created_time",
            StringType,
            description="When the ad was created (ISO 8601)",
        ),
        Property(
            "conversion_domain",
            StringType,
            description="Domain for conversion tracking",
        ),
        Property(
            "name",
            StringType,
            description="Name of the ad",
        ),
        Property(
            "effective_status",
            StringType,
            description="Effective status considering parent campaign/ad set status",
        ),
        Property(
            "last_updated_by_app_id",
            StringType,
            description="ID of the app that last updated the ad",
        ),
        Property(
            "recommendations",
            ArrayType(
                ObjectType(
                    Property("blame_field", StringType, description="Field the recommendation blames"),
                    Property("code", IntegerType, description="Recommendation code"),
                    Property("confidence", StringType, description="Confidence level of the recommendation"),
                    Property("importance", StringType, description="Importance of the recommendation"),
                    Property("message", StringType, description="Recommendation message"),
                    Property("title", StringType, description="Recommendation title"),
                ),
            ),
            description="Recommendations to improve ad performance",
        ),
        Property(
            "source_ad_id",
            StringType,
            description="ID of the source ad if this ad was copied",
        ),
        Property(
            "tracking_specs",
            ArrayType(
                ObjectType(
                    Property(
                        "application",
                        ArrayType(Property("items", StringType, description="Application tracking item")),
                        description="Application tracking spec",
                    ),
                    Property("post", ArrayType(StringType), description="Post tracking spec"),
                    Property("conversion_id", ArrayType(StringType), description="Conversion ID tracking spec"),
                    Property("action_type", ArrayType(StringType), description="Action type tracking spec"),
                    Property("post_type", ArrayType(StringType), description="Post type tracking spec"),
                    Property("page", ArrayType(StringType), description="Page tracking spec"),
                    Property("creative", ArrayType(StringType), description="Creative tracking spec"),
                    Property("dataset", ArrayType(StringType), description="Dataset tracking spec"),
                    Property("event", ArrayType(StringType), description="Event tracking spec"),
                    Property("event_creator", ArrayType(StringType), description="Event creator tracking spec"),
                    Property("event_type", ArrayType(StringType), description="Event type tracking spec"),
                    Property("fb_pixel", ArrayType(StringType), description="Facebook Pixel tracking spec"),
                    Property(
                        "fb_pixel_event",
                        ArrayType(StringType),
                        description="Facebook Pixel event tracking spec",
                    ),
                    Property("leadgen", ArrayType(StringType), description="Lead gen tracking spec"),
                    Property("object", ArrayType(StringType), description="Object tracking spec"),
                    Property("object_domain", ArrayType(StringType), description="Object domain tracking spec"),
                    Property("offer", ArrayType(StringType), description="Offer tracking spec"),
                    Property("offer_creator", ArrayType(StringType), description="Offer creator tracking spec"),
                    Property("offsite_pixel", ArrayType(StringType), description="Offsite pixel tracking spec"),
                    Property("page_parent", ArrayType(StringType), description="Page parent tracking spec"),
                    Property("post_object", ArrayType(StringType), description="Post object tracking spec"),
                    Property("question", ArrayType(StringType), description="Question tracking spec"),
                    Property(
                        "post_object_wall",
                        ArrayType(StringType),
                        description="Post object wall tracking spec",
                    ),
                    Property(
                        "post_wall",
                        ArrayType(StringType),
                        description="Post wall tracking spec",
                    ),
                    Property(
                        "question_creator",
                        ArrayType(StringType),
                        description="Question creator tracking spec",
                    ),
                    Property("response", ArrayType(StringType), description="Response tracking spec"),
                    Property("subtype", ArrayType(StringType), description="Subtype tracking spec"),
                ),
            ),
            description="Tracking specifications for conversion attribution",
        ),
        Property(
            "conversion_specs",
            ArrayType(
                ObjectType(
                    Property("action_type", ArrayType(StringType), description="Conversion action type"),
                    Property("conversion_id", ArrayType(StringType), description="Conversion ID"),
                ),
            ),
            description="Conversion specifications for optimization",
        ),
        Property(
            "configured_status",
            StringType,
            description="User-configured status of the ad",
        ),
    ).to_dict()

    tap_stream_id = "ads"

    def sanitize_field_names(self, record):
        if isinstance(record, dict):
            updated_record = {}
            for key, value in record.items():
                new_key = key.replace(".", "_")
                updated_record[new_key] = self.sanitize_field_names(value)
            return updated_record
        elif isinstance(record, list):
            return [self.sanitize_field_names(item) for item in record]
        else:
            return record

    def get_child_context(self, record: dict, context: dict | None) -> dict | None:
        """Provide context for child streams (creatives)."""
        creative_data = record.get("creative")
        if creative_data and isinstance(creative_data, dict):
            return {
                "creative": creative_data,
                "ad_id": record.get("id"),
                "ad_updated_time": record.get("updated_time"),
            }
        return None

    def post_process(self, row: Dict[str, Any], context: Dict | None = None) -> dict | None:
        return super().post_process(self.sanitize_field_names(row), context)

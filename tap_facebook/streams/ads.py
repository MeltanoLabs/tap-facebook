"""Stream class for AdsStream."""

from __future__ import annotations

from typing import Any, Dict

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

    columns_remaining = ["adlabels"]  # noqa: RUF012

    name = "ads"
    filter_entity = "ad"

    path = f"/ads?fields={columns}"

    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "updated_time"

    schema = PropertiesList(
        Property("bid_type", StringType),
        Property("account_id", StringType),
        Property("ad_acive_time", StringType),
        Property("ad_schedule_end_time", DateTimeType),
        Property("ad_schedule_start_time", DateTimeType),
        Property("campaign_id", StringType),
        Property("adset_id", StringType),
        Property("bid_amount", IntegerType),
        Property("status", StringType),
        Property(
            "creative",
            ObjectType(Property("creative_id", StringType), Property("id", StringType)),
        ),
        Property("id", StringType),
        Property("updated_time", StringType),
        Property("created_time", StringType),
        Property("conversion_domain", StringType),
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
                        ArrayType(Property("items", StringType)),
                    ),
                    Property("post", ArrayType(StringType)),
                    Property("conversion_id", ArrayType(StringType)),
                    Property("action_type", ArrayType(StringType)),
                    Property("post_type", ArrayType(StringType)),
                    Property("page", ArrayType(StringType)),
                    Property("creative", ArrayType(StringType)),
                    Property("dataset", ArrayType(StringType)),
                    Property("event", ArrayType(StringType)),
                    Property("event_creator", ArrayType(StringType)),
                    Property("event_type", ArrayType(StringType)),
                    Property("fb_pixel", ArrayType(StringType)),
                    Property(
                        "fb_pixel_event",
                        ArrayType(StringType),
                    ),
                    Property("leadgen", ArrayType(StringType)),
                    Property("object", ArrayType(StringType)),
                    Property("object_domain", ArrayType(StringType)),
                    Property("offer", ArrayType(StringType)),
                    Property("offer_creator", ArrayType(StringType)),
                    Property("offsite_pixel", ArrayType(StringType)),
                    Property("page_parent", ArrayType(StringType)),
                    Property("post_object", ArrayType(StringType)),
                    Property("question", ArrayType(StringType)),
                    Property(
                        "post_object_wall",
                        ArrayType(StringType),
                    ),
                    Property(
                        "post_wall",
                        ArrayType(StringType),
                    ),
                    Property(
                        "question_creator",
                        ArrayType(StringType),
                    ),
                    Property("response", ArrayType(StringType)),
                    Property("subtype", ArrayType(StringType)),
                ),
            ),
        ),
        Property(
            "conversion_specs",
            ArrayType(
                ObjectType(
                    Property("action_type", ArrayType(StringType)),
                    Property("conversion_id", ArrayType(StringType)),
                ),
            ),
        ),
        Property("configured_status", StringType),
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

    def post_process(self, row: Dict[str, Any], context: Dict | None = None) -> dict | None:
        return super().post_process(self.sanitize_field_names(row), context)

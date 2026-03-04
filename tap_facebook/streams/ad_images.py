"""Stream class for AdImages."""

from __future__ import annotations

from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL
from nekt_singer_sdk.typing import (
    ArrayType,
    BooleanType,
    IntegerType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream


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
    tap_stream_id = "adimages"
    replication_key = "id"

    schema = PropertiesList(
        Property(
            "id",
            StringType,
            description="The ID of the image",
        ),
        Property(
            "account_id",
            StringType,
            description="The ad account that owns the image",
        ),
        Property(
            "created_time",
            StringType,
            description="Time the image was created",
        ),
        Property(
            "creatives",
            ArrayType(StringType),
            description="List of ad creative IDs that use this image",
        ),
        Property(
            "hash",
            StringType,
            description="Hash which uniquely identifies the image",
        ),
        Property(
            "height",
            IntegerType,
            description="The height of the image in pixels",
        ),
        Property(
            "is_associated_creatives_in_adgroups",
            BooleanType,
            description="Whether this image is associated with creatives in ad groups",
        ),
        Property(
            "name",
            StringType,
            description="The filename of the image (max 100 characters)",
        ),
        Property(
            "original_height",
            IntegerType,
            description="The height of the image as originally uploaded",
        ),
        Property(
            "original_width",
            IntegerType,
            description="The width of the image as originally uploaded",
        ),
        Property(
            "permalink_url",
            StringType,
            description="Permanent URL of the image for use in story creatives",
        ),
        Property(
            "status",
            StringType,
            description="Status of the image (ACTIVE, INTERNAL, DELETED)",
        ),
        Property(
            "updated_time",
            StringType,
            description="Time the image was last updated",
        ),
        Property(
            "url",
            StringType,
            description="Temporary URL to retrieve the image; do not use in ad creative creation",
        ),
        Property(
            "url_128",
            StringType,
            description="Temporary URL for version resized to fit within 128x128 pixels",
        ),
        Property(
            "width",
            IntegerType,
            description="The width of the image in pixels",
        ),
    ).to_dict()

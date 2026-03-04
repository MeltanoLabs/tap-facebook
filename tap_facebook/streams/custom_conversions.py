"""Stream class for CustomConversions."""

from __future__ import annotations

from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL
from nekt_singer_sdk.typing import (
    BooleanType,
    DateTimeType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream


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
    replication_key = "creation_time"

    schema = PropertiesList(
        Property(
            "account_id",
            StringType,
            description="ID of the ad account that owns the custom conversion",
        ),
        Property(
            "id",
            StringType,
            description="Unique ID of the custom conversion",
        ),
        Property(
            "name",
            StringType,
            description="Name of the custom conversion",
        ),
        Property(
            "creation_time",
            StringType,
            description="When the custom conversion was created",
        ),
        Property(
            "business",
            ObjectType(
                Property("id", StringType, description="Business ID"),
                Property("block_offline_analytics", BooleanType, description="Whether offline analytics is blocked"),
                Property("created_time", DateTimeType, description="Business creation time"),
                Property("extended_updated_time", DateTimeType, description="Business extended updated time"),
                Property("is_hidden", BooleanType, description="Whether business is hidden"),
                Property("link", StringType, description="Business link"),
                Property("name", StringType, description="Business name"),
                Property("payment_account_id", StringType, description="Business payment account ID"),
                Property("profile_picture_uri", StringType, description="Business profile picture URI"),
                Property("timezone_id", IntegerType, description="Business timezone ID"),
                Property("two_factor_type", StringType, description="Business two-factor type"),
                Property("updated_time", DateTimeType, description="Business updated time"),
                Property("verification_status", StringType, description="Business verification status"),
                Property("vertical", StringType, description="Business vertical"),
                Property("vertical_id", IntegerType, description="Business vertical ID"),
            ),
            description="Business (Business Manager) that owns this custom conversion",
        ),
        Property(
            "is_archived",
            BooleanType,
            description="Whether the custom conversion is archived",
        ),
        Property(
            "is_unavailable",
            BooleanType,
            description="Whether the custom conversion is unavailable",
        ),
        Property(
            "last_fired_time",
            StringType,
            description="When the custom conversion last fired",
        ),
    ).to_dict()

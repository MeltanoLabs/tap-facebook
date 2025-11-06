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
        Property("account_id", StringType),
        Property("id", StringType),
        Property("name", StringType),
        Property("creation_time", StringType),
        Property(
            "business",
            ObjectType(
                Property("id", StringType),
                Property("block_offline_analytics", BooleanType),
                Property("created_time", DateTimeType),
                Property("extended_updated_time", DateTimeType),
                Property("is_hidden", BooleanType),
                Property("link", StringType),
                Property("name", StringType),
                Property("payment_account_id", StringType),
                Property("profile_picture_uri", StringType),
                Property("timezone_id", IntegerType),
                Property("two_factor_type", StringType),
                Property("updated_time", DateTimeType),
                Property("verification_status", StringType),
                Property("vertical", StringType),
                Property("vertical_id", IntegerType),
            ),
        ),
        Property("is_archived", BooleanType),
        Property("is_unavailable", BooleanType),
        Property("last_fired_time", StringType),
    ).to_dict()

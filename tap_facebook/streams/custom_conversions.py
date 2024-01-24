"""Stream class for CustomConversions."""

from __future__ import annotations

from singer_sdk.streams.core import REPLICATION_INCREMENTAL
from singer_sdk.typing import (
    BooleanType,
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
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "creation_time"

    schema = PropertiesList(
        Property("account_id", StringType),
        Property("id", StringType),
        Property("name", StringType),
        Property("creation_time", StringType),
        Property("business", ObjectType()),
        Property("is_archived", BooleanType),
        Property("is_unavailable", BooleanType),
        Property("last_fired_time", StringType),
    ).to_dict()

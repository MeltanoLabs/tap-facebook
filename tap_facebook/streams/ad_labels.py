"""Stream class for AdLabels."""

from singer_sdk.streams.core import REPLICATION_INCREMENTAL
from singer_sdk.typing import (
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream


class AdLabelsStream(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-creative/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = ["id", "account", "created_time", "updated_time", "name"]  # noqa: RUF012

    name = "adlabels"
    path = f"/adlabels?fields={columns}"
    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    tap_stream_id = "adlabels"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "updated_time"

    schema = PropertiesList(
        Property("id", StringType),
        Property(
            "account",
            ObjectType(
                Property("account_id", StringType),
                Property("id", StringType),
            ),
        ),
        Property("created_time", StringType),
        Property("updated_time", StringType),
        Property("name", StringType),
    ).to_dict()

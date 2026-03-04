"""Stream class for AdLabels."""

from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL
from nekt_singer_sdk.typing import ObjectType, PropertiesList, Property, StringType

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
    replication_key = "updated_time"

    schema = PropertiesList(
        Property(
            "id",
            StringType,
            description="Unique ID of the ad label",
        ),
        Property(
            "account",
            ObjectType(
                Property("account_id", StringType, description="Ad account ID"),
                Property("id", StringType, description="Ad account node ID"),
            ),
            description="Ad account this label belongs to",
        ),
        Property(
            "created_time",
            StringType,
            description="When the label was created",
        ),
        Property(
            "updated_time",
            StringType,
            description="When the label was last updated",
        ),
        Property(
            "name",
            StringType,
            description="Name of the ad label",
        ),
    ).to_dict()

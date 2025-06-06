"""Stream class for AdImages."""

from __future__ import annotations

import typing as t

from singer_sdk.streams.core import REPLICATION_INCREMENTAL
from singer_sdk.typing import (
    ArrayType,
    BooleanType,
    DateTimeType,
    IntegerType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


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
    tap_stream_id = "images"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "updated_time"

    schema = PropertiesList(
        Property("id", StringType),
        Property("account_id", StringType),
        Property("created_time", DateTimeType),
        Property("creatives", ArrayType(StringType)),
        Property("hash", StringType),
        Property("height", IntegerType),
        Property("is_associated_creatives_in_adgroups", BooleanType),
        Property("name", StringType),
        Property("original_height", IntegerType),
        Property("original_width", IntegerType),
        Property("permalink_url", StringType),
        Property("status", StringType),
        Property("updated_time", DateTimeType),
        Property("url", StringType),
        Property("url_128", StringType),
        Property("width", IntegerType),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        params = super().get_url_params(context, next_page_token)
        params.pop("sort")
        return params

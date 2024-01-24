"""facebook tap class."""

from __future__ import annotations

import typing as t

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

if t.TYPE_CHECKING:
    from tap_facebook.client import FacebookStream

from tap_facebook.streams import (
    AdAccountsStream,
    AdImages,
    AdLabelsStream,
    AdsetsStream,
    AdsInsightStream,
    AdsStream,
    AdVideos,
    CampaignStream,
    CreativeStream,
    CustomAudiences,
    CustomConversions,
)

STREAM_TYPES = [
    AdsetsStream,
    AdsInsightStream,
    AdsStream,
    CampaignStream,
    CreativeStream,
    AdLabelsStream,
    AdAccountsStream,
    CustomConversions,
    CustomAudiences,
    AdImages,
    AdVideos,
]


class TapFacebook(Tap):
    """Singer tap for extracting data from the Facebook Marketing API."""

    name = "tap-facebook"

    # add parameters you have in config.json
    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            description="The token to authenticate against the API service",
            required=True,
        ),
        th.Property(
            "api_version",
            th.StringType,
            description="The API version to request data from.",
            default="v18.0",
        ),
        th.Property(
            "account_id",
            th.StringType,
            description="Your Facebook Account ID.",
            required=True,
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "end_date",
            th.DateTimeType,
            description="The latest record date to sync",
        ),
    ).to_dict()

    def discover_streams(self) -> list[FacebookStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapFacebook.cli()

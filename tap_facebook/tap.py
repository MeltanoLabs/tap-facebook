"""facebook tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_facebook import streams
from tap_facebook.streams import ( 
  adsinsightStream,
  adsStream,
  facebookStream
)

STREAM_TYPES = [
    adsinsightStream,
    adsStream
]



class Tapfacebook(Tap):
    """facebook tap class."""

    name = "tap-facebook"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "account_id",
            th.StringType,
            description="Account ID"
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync"
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.facebookStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        adstream = [streams.adsStream(self)]
        stream_list = [stream_class(tap=self) for stream_class in STREAM_TYPES]

        return stream_list


if __name__ == "__main__":
    Tapfacebook.cli()

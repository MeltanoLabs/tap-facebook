"""facebook tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# streams
from tap_facebook import streams

#TODO:  We need to add the CREATIVE_HISTORY,FIVETRAN_AUDIT, FREQUENCY_CONTROL, PACING_TYPE, REACH_FREQUENCY
# TARGETING_OPTIMIZATION_TYPES,ACCOUNT_HISTORY in  streams  and STREAM_TYPES.

from tap_facebook.streams import ( 
  adsinsightStream,
  adsStream,
  adsetsStream,
  facebookStream,
  campaignStream,
  adhistoryStream,
  campaignhistoryStream,
  adsethistoryStream,
  adconversionStream,
  campaignlabelStream,
  adgroupissuesinfoStream,
  adrecommendationStream,
  adsetscheduleStream,
  adcampaignissuesinfoStream,
  adsetattributionStream,
  adtrackingStream
)

STREAM_TYPES = [
    adsinsightStream,
    adsStream,
    adsetsStream,
    campaignStream,
    adhistoryStream,
    campaignhistoryStream,
    adsethistoryStream,
    adconversionStream,
    campaignlabelStream,
    adgroupissuesinfoStream,
    adrecommendationStream,
    adsetscheduleStream,
    adcampaignissuesinfoStream,
    adsetattributionStream,
    adtrackingStream
]



class Tapfacebook(Tap):
    """facebook tap class."""

    name = "tap-facebook"

    # add parameters you have in config.json
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
        adstream = [streams.adtrackingStream(self)]
        stream_list = [stream_class(tap=self) for stream_class in STREAM_TYPES]

        return stream_list


if __name__ == "__main__":
    Tapfacebook.cli()

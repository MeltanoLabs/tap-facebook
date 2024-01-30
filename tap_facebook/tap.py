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

DEFAULT_INSIGHT_REPORT = {
    "name": "default",
    "level": "ad",
    "action_breakdowns": [],
    "breakdowns": [],
    "time_increment_days": 1,
    "action_attribution_windows_view": "1d_view",
    "action_attribution_windows_click": "7d_click",
    "action_report_time": "mixed",
    "lookback_window": 28,
}


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
            "insight_reports_list",
            th.ArrayType(
                th.ObjectType(
                    th.Property(
                        "name",
                        th.StringType,
                        description=(
                            "A name used to define your custom report. "
                            "This will included in the stream name. "
                            "Changing this name will affect incremental bookmark values.",
                        ),
                        required=True,
                    ),
                    th.Property(
                        "level",
                        th.StringType,
                        description="Represents the level of result aggregation.",
                        default="ad",
                    ),
                    th.Property(
                        "action_breakdowns",
                        th.ArrayType(th.StringType),
                        description=(
                            "How to break down action results. "
                            "Supports more than one breakdowns.",
                        ),
                        default=[],
                    ),
                    th.Property(
                        "breakdowns",
                        th.ArrayType(th.StringType),
                        description=(
                            "How to break down the result. "
                            "For more than one breakdown, only certain combinations are available: "
                            "See 'Combining Breakdowns' in the "
                            "[Breakdowns page](https://developers.facebook.com/docs/marketing-api/insights/breakdowns). "  # noqa: E501
                            "The option impression_device cannot be used by itself"
                        ),
                        default=[],
                    ),
                    th.Property(
                        "time_increment_days",
                        th.IntegerType,
                        description=(
                            "The amount of days to aggregate your stats by, in days. "
                            "A value of 1 will return a daily aggregation of your stats."
                        ),
                        default=1,
                    ),
                    th.Property(
                        "action_attribution_windows_view",
                        th.StringType,
                        description=(
                            "The attribution window for the actions. For example, "
                            "28d_view means the API returns all actions that happened "
                            "28 days after someone viewed the ad."
                        ),
                        default="1d_view",
                    ),
                    th.Property(
                        "action_attribution_windows_click",
                        th.StringType,
                        description=(
                            "The attribution window for the actions. "
                            "For example, 28d_click means the API returns "
                            "all actions that happened 28 days after someone clicked on the ad."
                        ),
                        default="7d_click",
                    ),
                    th.Property(
                        "action_report_time",
                        th.StringType,
                        description=(
                            "Determines the report time of action stats. "
                            "For example, if a person saw the ad on Jan 1st but converted on Jan "
                            "2nd, when you query the API with action_report_time=impression, you "
                            "see a conversion on Jan 1st. When you query the API with "
                            "action_report_time=conversion, you see a conversion on Jan 2nd."
                        ),
                        default="mixed",
                    ),
                    th.Property(
                        "lookback_window",
                        th.IntegerType,
                        description=(
                            "Facebook freezes insight data 28 days after it was generated, which "
                            "means that all data from the past 28 days may have changed since we "
                            "last emitted it, so we attempt to retrieve it again."
                        ),
                        default=28,
                    ),
                ),
            ),
            description=(
                "A list of insight report definitions. See the "
                "[Ad Insights docs](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights) "  # noqa: E501
                "for more details."
            ),
            default=[],
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
        streams = [stream_class(tap=self) for stream_class in STREAM_TYPES]
        report_configs = [
            DEFAULT_INSIGHT_REPORT,
            *self.config.get("insight_reports_list"),
        ]
        insight_streams = [
            AdsInsightStream(
                tap=self,
                report_definition=insight_report_definition,
            )
            for insight_report_definition in report_configs
        ]
        return [*streams, *insight_streams]


if __name__ == "__main__":
    TapFacebook.cli()

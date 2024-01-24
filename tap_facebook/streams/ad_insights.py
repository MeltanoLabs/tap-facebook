"""Stream class for AdInsights."""

from __future__ import annotations

import typing as t

from singer_sdk.streams.core import REPLICATION_INCREMENTAL
from singer_sdk.typing import (
    ArrayType,
    DateTimeType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream


class AdsInsightStream(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/insights."""

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
        "ad_id",
        "adset_id",
        "campaign_id",
        "ad_name",
        "adset_name",
        "campaign_name",
        "date_start",
        "date_stop",
        "clicks",
        "website_ctr",
        "unique_inline_link_click_ctr",
        "frequency",
        "account_name",
        "unique_inline_link_clicks",
        "cost_per_unique_action_type",
        "inline_post_engagement",
        "inline_link_clicks",
        "cpc",
        "cost_per_unique_inline_link_click",
        "cpm",
        "canvas_avg_view_time",
        "cost_per_inline_post_engagement",
        "inline_link_click_ctr",
        "cpp",
        "cost_per_action_type",
        "unique_link_clicks_ctr",
        "spend",
        "cost_per_unique_click",
        "unique_clicks",
        "social_spend",
        "reach",
        "canvas_avg_view_percent",
        "objective",
        "quality_ranking",
        "engagement_rate_ranking",
        "conversion_rate_ranking",
        "impressions",
        "unique_ctr",
        "cost_per_inline_link_click",
        "ctr",
    ]

    columns_remaining = [  # noqa: RUF012
        "unique_actions",
        "actions",
        "action_values",
        "outbound_clicks",
        "unique_outbound_clicks",
        "video_30_sec_watched_actions",
        "video_p25_watched_actions",
        "video_p50_watched_actions",
        "video_p75_watched_actions",
        "video_p100_watched_actions",
    ]

    name = "adsinsights"

    path = f"/insights?level=ad&fields={columns}"

    replication_method = REPLICATION_INCREMENTAL
    replication_key = "date_start"

    schema = PropertiesList(
        Property("clicks", StringType),
        Property("date_stop", StringType),
        Property("ad_id", StringType),
        Property(
            "website_ctr",
            ArrayType(
                ObjectType(
                    Property("value", StringType),
                    Property("action_destination", StringType),
                    Property("action_target_id", StringType),
                    Property("action_type", StringType),
                ),
            ),
        ),
        Property("unique_inline_link_click_ctr", StringType),
        Property("adset_id", StringType),
        Property("frequency", StringType),
        Property("account_name", StringType),
        Property("canvas_avg_view_time", StringType),
        Property("unique_inline_link_clicks", StringType),
        Property(
            "cost_per_unique_action_type",
            ArrayType(
                ObjectType(
                    Property("value", StringType),
                    Property("action_type", StringType),
                ),
            ),
        ),
        Property("inline_post_engagement", StringType),
        Property("campaign_name", StringType),
        Property("inline_link_clicks", IntegerType),
        Property("campaign_id", StringType),
        Property("cpc", StringType),
        Property("ad_name", StringType),
        Property("cost_per_unique_inline_link_click", StringType),
        Property("cpm", StringType),
        Property("cost_per_inline_post_engagement", StringType),
        Property("inline_link_click_ctr", StringType),
        Property("cpp", StringType),
        Property("cost_per_action_type", ArrayType(ObjectType())),
        Property("unique_link_clicks_ctr", StringType),
        Property("spend", StringType),
        Property("cost_per_unique_click", StringType),
        Property("adset_name", StringType),
        Property("unique_clicks", StringType),
        Property("social_spend", StringType),
        Property("canvas_avg_view_percent", StringType),
        Property("account_id", StringType),
        Property("date_start", DateTimeType),
        Property("objective", StringType),
        Property("quality_ranking", StringType),
        Property("engagement_rate_ranking", StringType),
        Property("conversion_rate_ranking", StringType),
        Property("impressions", IntegerType),
        Property("unique_ctr", StringType),
        Property("cost_per_inline_link_click", StringType),
        Property("ctr", StringType),
        Property("reach", IntegerType),
        Property(
            "actions",
            ArrayType(
                ObjectType(
                    Property("action_type", StringType),
                    Property("value", StringType),
                ),
            ),
        ),
    ).to_dict()

    tap_stream_id = "adsinsights"

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {"limit": 25}
        if next_page_token is not None:
            params["after"] = next_page_token
        if self.replication_key:
            params["sort"] = [f"{self.replication_key}_ascending"]
            params["order_by"] = self.replication_key

        params["action_attribution_windows"] = '["1d_view","7d_click"]'

        return params

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        row["inline_link_clicks"] = (
            int(row["inline_link_clicks"]) if "inline_link_clicks" in row else None
        )
        row["impressions"] = int(row["impressions"]) if "impressions" in row else None
        row["reach"] = int(row["reach"]) if "reach" in row else None
        return row

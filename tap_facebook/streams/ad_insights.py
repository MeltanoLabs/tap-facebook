"""Stream class for AdInsights."""

from __future__ import annotations

import typing as t

import facebook_business.adobjects.user as fb_user
import pendulum
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi
from singer_sdk.streams.core import REPLICATION_INCREMENTAL, Stream
from singer_sdk.typing import (
    ArrayType,
    DateTimeType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)


class AdsInsightStream(Stream):
    name = "adsinsights"
    tap_stream_id = "adsinsights"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "date_start"

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

    # @property
    # def schema(self) -> dict:
    #     properties: List[th.Property] = []
    # from facebook_business.adobjects.adsinsights import AdsInsights
    # from facebook_business.adobjects.adsactionstats import AdsActionStats
    # AdsInsights._field_types
    # AdsActionStats._field_types
    # ValidFields = Enum("ValidEnums", AdsInsights.Field.__dict__)
    # ValidBreakdowns = Enum("ValidBreakdowns", AdsInsights.Breakdowns.__dict__)
    # ValidActionBreakdowns = Enum("ValidActionBreakdowns", AdsInsights.ActionBreakdowns.__dict__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FacebookAdsApi.init(access_token=self.config["access_token"], timeout=300)
        user = fb_user.User(fbid="me")

        account_id = self.config["account_id"]
        self.account = AdAccount(f"act_{account_id}").api_get()
        if not self.account:
            msg = f"Couldn't find account with id {account_id}"
            raise Exception(msg)

    def _run_job_to_completion(self, params):
        import time

        job = self.account.get_insights(
            params=params,
            is_async=True,
        )
        status = None
        time_start = time.time()
        sleep_time = 10
        INSIGHTS_MAX_WAIT_TO_START_SECONDS = 5 * 60
        INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS = 30 * 60
        INSIGHTS_MAX_ASYNC_SLEEP_SECONDS = 5 * 60
        while status != "Job Completed":
            duration = time.time() - time_start
            job = job.api_get()
            status = job["async_status"]
            percent_complete = job["async_percent_completion"]

            job_id = job["id"]
            self.logger.info("%s, %d%% done", status, percent_complete)

            if status == "Job Completed":
                return job

            if duration > INSIGHTS_MAX_WAIT_TO_START_SECONDS and percent_complete == 0:
                pretty_error_message = (
                    "Insights job {} did not start after {} seconds. "
                    + "This is an intermittent error and may resolve itself on subsequent queries to the Facebook API. "
                    + "You should deselect fields from the schema that are not necessary, "
                    + "as that may help improve the reliability of the Facebook API."
                )
                raise InsightsJobTimeout(
                    pretty_error_message.format(job_id, INSIGHTS_MAX_WAIT_TO_START_SECONDS)
                )
            elif duration > INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS and status != "Job Completed":
                pretty_error_message = (
                    "Insights job {} did not complete after {} seconds. "
                    + "This is an intermittent error and may resolve itself on subsequent queries to the Facebook API. "
                    + "You should deselect fields from the schema that are not necessary, "
                    + "as that may help improve the reliability of the Facebook API."
                )
                raise InsightsJobTimeout(
                    pretty_error_message.format(job_id, INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS // 60)
                )

            self.logger.info("sleeping for %d seconds until job is done", sleep_time)
            time.sleep(sleep_time)
            if sleep_time < INSIGHTS_MAX_ASYNC_SLEEP_SECONDS:
                sleep_time = 2 * sleep_time

    def get_records(
        self,
        context: dict | None,
    ) -> t.Iterable[dict | tuple[dict, dict | None]]:
        # Aggregation window of 1 day
        # TODO: if we allow this to be configurable we need to increase the time range accordingly
        time_increment = 1

        # Facebook freezes insight data 28 days after it was generated, which means that all data
        # from the past 28 days may have changed since we last emitted it, so we retrieve it again.
        # But in some cases users my have define their own lookback window, thats
        # why the value for `insights_lookback_window` is set throught config.
        lookback_window = 28

        # Facebook store metrics maximum of 37 months old. Any time range that
        # older that 37 months from current date would result in 400 Bad request
        # HTTP response.
        # https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
        INSIGHTS_RETENTION_PERIOD = pendulum.duration(months=37)

        today = pendulum.today().date()
        # TODO: handle these edge cases
        # oldest_date = today - INSIGHTS_RETENTION_PERIOD
        # refresh_date = today - lookback_window
        report_start = (
            pendulum.parse(self.get_starting_replication_key_value(context))
            .subtract(days=lookback_window)
            .date()
        )

        action_breakdowns = []
        breakdowns = []
        while report_start <= today:
            params = {
                "level": "ad",
                "action_breakdowns": action_breakdowns,
                # AdsInsights.ActionReportTime.__dict__
                # "conversion", "impression", "mixed"
                "action_report_time": "mixed",
                "breakdowns": breakdowns,
                "fields": self.columns,
                # Ignore time increment and just split it manually
                # We can define increment as 1 for daily agg but then chose a larger
                # time range to get multiple reports back in one async jobs
                "time_increment": time_increment,
                "limit": 100,
                "action_attribution_windows": ["1d_view", "7d_click"],
                "time_range": {
                    "since": report_start.to_date_string(),
                    "until": report_start.to_date_string(),
                },
            }
            job = self._run_job_to_completion(params)
            for obj in job.get_result():
                yield obj.export_all_data()
            # Bump to the next increment
            report_start = report_start.add(days=time_increment)

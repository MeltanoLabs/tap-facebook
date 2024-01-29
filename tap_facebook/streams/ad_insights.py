"""Stream class for AdInsights."""

from __future__ import annotations

import typing as t
from functools import lru_cache

import facebook_business.adobjects.user as fb_user
import pendulum
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsactionstats import AdsActionStats
from facebook_business.adobjects.adshistogramstats import AdsHistogramStats
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from singer_sdk import typing as th
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

    @staticmethod
    def _get_datatype(field):
        d_type = AdsInsights._field_types[field]
        if d_type == "string":
            return th.StringType()
        elif d_type.startswith("list"):
            if "AdsActionStats" in d_type:
                sub_props = [
                    th.Property(
                        field.replace("field_", ""),
                        th.StringType()
                    )
                    for field in list(AdsActionStats.Field.__dict__)
                    if field not in ["__module__", "__doc__", "__dict__"]
                ]
                return th.ArrayType(
                    th.ObjectType(
                        *sub_props
                    )
                )
            if "AdsHistogramStats" in d_type:
                sub_props = []
                for field in list(AdsHistogramStats.Field.__dict__):
                    if field not in ["__module__", "__doc__", "__dict__"]:
                        clean_field = field.replace("field_", "")
                        if AdsHistogramStats._field_types[clean_field] == "string":
                            sub_props.append(
                                th.Property(clean_field, th.StringType())
                            )
                        else:
                            sub_props.append(
                                th.Property(clean_field, th.ArrayType(th.IntegerType()))
                            )
                return th.ArrayType(th.ObjectType(*sub_props))
            return th.ArrayType(th.ObjectType())

    @property
    @lru_cache
    def schema(self) -> dict:
        properties: List[th.Property] = []
        columns = list(AdsInsights.Field.__dict__)[1:]
        for field in columns:
            if field in ["__module__", "__doc__", "__dict__"]:
                continue
            properties.append(
                th.Property(field, self._get_datatype(field))
            )
        return th.PropertiesList(*properties).to_dict()
    
    def _initialize_client(self):
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

    def _get_selected_columns(self):
        return [
            keys[1]
            for keys, data in self.metadata.items()
            if data.selected
            and len(keys) > 0
        ]

    def get_records(
        self,
        context: dict | None,
    ) -> t.Iterable[dict | tuple[dict, dict | None]]:
        self._initialize_client()
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
        columns = self._get_selected_columns()
        while report_start <= today:
            params = {
                "level": "ad",
                "action_breakdowns": action_breakdowns,
                # AdsInsights.ActionReportTime.__dict__
                # "conversion", "impression", "mixed"
                "action_report_time": "mixed",
                "breakdowns": breakdowns,
                "fields": columns,
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

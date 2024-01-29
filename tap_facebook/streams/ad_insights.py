"""Stream class for AdInsights."""

from __future__ import annotations

import time
import typing as t
from functools import lru_cache

import facebook_business.adobjects.user as fb_user
import pendulum
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adreportrun import AdReportRun
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

EXCLUDED_FIELDS = [
    "total_postbacks",
    "adset_end",
    "adset_start",
    "conversion_lead_rate",
    "cost_per_conversion_lead",
    "cost_per_dda_countby_convs",
    "cost_per_one_thousand_ad_impression",
    "cost_per_unique_conversion",
    "creative_media_type",
    "dda_countby_convs",
    "dda_results",
    "instagram_upcoming_event_reminders_set",
    "interactive_component_tap",
    "marketing_messages_cost_per_delivered",
    "marketing_messages_cost_per_link_btn_click",
    "marketing_messages_spend",
    "place_page_name",
    "total_postbacks",
    "total_postbacks_detailed",
    "total_postbacks_detailed_v4",
    "unique_conversions",
    "unique_video_continuous_2_sec_watched_actions",
    "unique_video_view_15_sec",
    "video_thruplay_watched_actions",
    "__module__",
    "__doc__",
    "__dict__",
]

SLEEP_TIME_INCREMENT = 5
INSIGHTS_MAX_WAIT_TO_START_SECONDS = 5 * 60
INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS = 30 * 60

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
                    if field not in EXCLUDED_FIELDS
                ]
                return th.ArrayType(
                    th.ObjectType(
                        *sub_props
                    )
                )
            if "AdsHistogramStats" in d_type:
                sub_props = []
                for field in list(AdsHistogramStats.Field.__dict__):
                    if field not in EXCLUDED_FIELDS:
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
            if field in EXCLUDED_FIELDS:
                continue
            properties.append(
                th.Property(field, self._get_datatype(field))
            )
        return th.PropertiesList(*properties).to_dict()
    
    def _initialize_client(self):
        FacebookAdsApi.init(
            access_token=self.config["access_token"],
            timeout=300,
            api_version=self.config["api_version"],
        )
        user = fb_user.User(fbid="me")

        account_id = self.config["account_id"]
        self.account = AdAccount(f"act_{account_id}").api_get()
        if not self.account:
            msg = f"Couldn't find account with id {account_id}"
            raise Exception(msg)

    def _run_job_to_completion(self, params):
        job = self.account.get_insights(
            params=params,
            is_async=True,
        )
        status = None
        time_start = time.time()
        while status != "Job Completed":
            duration = time.time() - time_start
            job = job.api_get()
            status = job["async_status"]
            percent_complete = job[AdReportRun.Field.async_percent_completion]

            job_id = job["id"]
            self.logger.info(f"{status}, {percent_complete}% done")

            if status == "Job Completed":
                return job
            if status == "Job Failed":
                raise Exception(dict(job))
            if duration > INSIGHTS_MAX_WAIT_TO_START_SECONDS and percent_complete == 0:
                error_message = (
                    f"Insights job {job_id} did not start after {INSIGHTS_MAX_WAIT_TO_START_SECONDS} seconds. "
                    + "This is an intermittent error and may resolve itself on subsequent queries to the Facebook API. "
                    + "You should deselect fields from the schema that are not necessary, "
                    + "as that may help improve the reliability of the Facebook API."
                )
                raise Exception(error_message)
            elif duration > INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS and status != "Job Completed":
                error_message = (
                    f"Insights job {job_id} did not complete after {INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS // 60} seconds. "
                    + "This is an intermittent error and may resolve itself on subsequent queries to the Facebook API. "
                    + "You should deselect fields from the schema that are not necessary, "
                    + "as that may help improve the reliability of the Facebook API."
                )
                raise Exception(error_message)

            self.logger.info(f"Sleeping for {SLEEP_TIME_INCREMENT} seconds until job is done")
            time.sleep(SLEEP_TIME_INCREMENT)

    def _get_selected_columns(self):
        return [
            keys[1]
            for keys, data in self.metadata.items()
            if data.selected
            and len(keys) > 0
        ]

    def _get_start_date(
        self,
        context: dict | None,
    ) -> pendulum.Date:
        # Facebook freezes insight data 28 days after it was generated, which means that all data
        # from the past 28 days may have changed since we last emitted it, so we retrieve it again.
        # But in some cases users my have define their own lookback window, thats
        # why the value for `insights_lookback_window` is set throught config.
        lookback_window = 28

        config_start_date = pendulum.parse(self.config["start_date"]).date()
        incremental_start_date = pendulum.parse(self.get_starting_replication_key_value(context)).date()
        lookback_start_date = incremental_start_date.subtract(days=lookback_window)

        # Don't use lookback if this is the first sync. Just start where the user requested.
        if config_start_date >= incremental_start_date:
            report_start = config_start_date
            self.logger.info(f"Using configured start_date as report start filter.")
        else:
            self.logger.info(f"Incremental sync, applying lookback '{lookback_window}' to the bookmark start_date '{incremental_start_date}'. Syncing reports starting on '{lookback_start_date}'.")
            report_start = lookback_start_date

        # Facebook store metrics maximum of 37 months old. Any time range that
        # older that 37 months from current date would result in 400 Bad request
        # HTTP response.
        # https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
        today = pendulum.today().date()
        oldest_allowed_start_date = today.subtract(months=37)
        if report_start < oldest_allowed_start_date:
            report_start = oldest_allowed_start_date
            self.logger.info(f"Report start date '{report_start}' is older than 37 months. Using oldest allowed start date '{oldest_allowed_start_date}' instead.")
        return report_start

    def get_records(
        self,
        context: dict | None,
    ) -> t.Iterable[dict | tuple[dict, dict | None]]:
        self._initialize_client()

        time_increment = 1

        today = pendulum.today().date()
        report_start = self._get_start_date(context)
        report_end = (
            report_start
            .add(days=time_increment)
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
                "time_increment": time_increment,
                "limit": 100,
                "action_attribution_windows": ["1d_view", "7d_click"],
                "time_range": {
                    "since": report_start.to_date_string(),
                    "until": report_end.to_date_string(),
                },
            }
            job = self._run_job_to_completion(params)
            for obj in job.get_result():
                yield obj.export_all_data()
            # Bump to the next increment
            report_start = report_start.add(days=time_increment)
            report_end = report_end.add(days=time_increment)

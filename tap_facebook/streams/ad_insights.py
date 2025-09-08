"""Stream class for AdInsights."""

from __future__ import annotations

import sys
import time
import typing as t
from functools import lru_cache
from hashlib import md5
from http import HTTPStatus

import facebook_business.adobjects.user as fb_user
import pendulum
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.adobjects.adsactionstats import AdsActionStats
from facebook_business.adobjects.adshistogramstats import AdsHistogramStats
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi, FacebookRequest
from facebook_business.exceptions import FacebookRequestError
from nekt_singer_sdk import typing as th
from nekt_singer_sdk.custom_logger import internal_logger, user_logger
from nekt_singer_sdk.streams.core import (
    REPLICATION_FULL_TABLE,
    REPLICATION_INCREMENTAL,
    Stream,
)

from tap_facebook.api_helper import CALL_THRESHOLD_PERCENTAGE, has_reached_api_limit

EXCLUDED_FIELDS = [
    "account_currency",
    # "account_id",
    # "account_name",
    "action_values",
    # "actions",
    "ad_click_actions",
    # "ad_id",
    "ad_impression_actions",
    # "ad_name",
    "adset_end",
    # "adset_id",
    # "adset_name",
    "adset_start",
    "age_targeting",
    "attribution_setting",
    "auction_bid",
    "auction_competitiveness",
    "auction_max_competitor_bid",
    "buying_type",
    # "campaign_id",
    # "campaign_name",
    "canvas_avg_view_percent",
    "canvas_avg_view_time",
    "catalog_segment_actions",
    "catalog_segment_value",
    "catalog_segment_value_mobile_purchase_roas",
    "catalog_segment_value_omni_purchase_roas",
    "catalog_segment_value_website_purchase_roas",
    # "clicks",
    "conversion_lead_rate",
    # "conversion_rate_ranking",
    # "conversion_values",
    # "conversions",
    "converted_product_quantity",
    "converted_product_value",
    "cost_per_15_sec_video_view",
    "cost_per_2_sec_continuous_video_view",
    # "cost_per_action_type",
    "cost_per_ad_click",
    # "cost_per_conversion",
    "cost_per_conversion_lead",
    "cost_per_dda_countby_convs",
    "cost_per_estimated_ad_recallers",
    "cost_per_inline_link_click",
    "cost_per_inline_post_engagement",
    "cost_per_one_thousand_ad_impression",
    "cost_per_outbound_click",
    "cost_per_thruplay",
    "cost_per_unique_action_type",
    "cost_per_unique_click",
    "cost_per_unique_conversion",
    "cost_per_unique_inline_link_click",
    "cost_per_unique_outbound_click",
    # "cpc",
    # "cpm",
    # "cpp",
    "created_time",
    "creative_media_type",
    # "ctr",
    # "date_start",
    # "date_stop",
    "dda_countby_convs",
    "dda_results",
    # "engagement_rate_ranking",
    # "estimated_ad_recall_rate",
    "estimated_ad_recall_rate_lower_bound",
    "estimated_ad_recall_rate_upper_bound",
    # "estimated_ad_recallers",
    "estimated_ad_recallers_lower_bound",
    "estimated_ad_recallers_upper_bound",
    # "frequency",
    "full_view_impressions",
    "full_view_reach",
    "gender_targeting",
    # "impressions",
    # "inline_link_click_ctr",
    # "inline_link_clicks",
    # "inline_post_engagement",
    "instagram_upcoming_event_reminders_set",
    "instant_experience_clicks_to_open",
    "instant_experience_clicks_to_start",
    "instant_experience_outbound_clicks",
    "interactive_component_tap",
    "labels",
    "location",
    "marketing_messages_cost_per_delivered",
    "marketing_messages_cost_per_link_btn_click",
    "marketing_messages_spend",
    "marketing_messages_website_purchase_values",
    "mobile_app_purchase_roas",
    "objective",
    "optimization_goal",
    # "outbound_clicks",
    # "outbound_clicks_ctr",
    "place_page_name",
    # "purchase_roas",
    "qualifying_question_qualify_answer_rate",
    # "quality_ranking",
    # "reach",
    "social_spend",
    # "spend",
    "total_postbacks",
    "total_postbacks_detailed",
    "total_postbacks_detailed_v4",
    # "unique_actions",
    # "unique_clicks",
    # "unique_conversions",
    # "unique_ctr",
    "unique_inline_link_click_ctr",
    "unique_inline_link_clicks",
    "unique_link_clicks_ctr",
    "unique_outbound_clicks",
    "unique_outbound_clicks_ctr",
    "unique_video_continuous_2_sec_watched_actions",
    "unique_video_view_15_sec",
    "updated_time",
    # "video_15_sec_watched_actions",
    # "video_30_sec_watched_actions",
    # "video_avg_time_watched_actions",
    "video_continuous_2_sec_watched_actions",
    # "video_p100_watched_actions",
    "video_p25_watched_actions",
    "video_p50_watched_actions",
    "video_p75_watched_actions",
    "video_p95_watched_actions",
    "video_play_actions",
    "video_play_curve_actions",
    "video_play_retention_0_to_15s_actions",
    "video_play_retention_20_to_60s_actions",
    "video_play_retention_graph_actions",
    "video_thruplay_watched_actions",
    "video_time_watched_actions",
    "website_ctr",
    "website_purchase_roas",
    "wish_bid",
    "__module__",
    "__doc__",
    "__dict__",
]

POLL_JOB_SLEEP_TIME = 5
AD_REPORT_RETRY_TIME = 2 * 60
AD_REPORT_INCREMENT_SLEEP_TIME = 1
INSIGHTS_MAX_WAIT_TO_START_SECONDS = 5 * 60
INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS = 10 * 60
JOB_STALE_ERROR_MESSAGE = (
    "This is an intermittent error and may resolve itself on "
    "subsequent queries to the Facebook API. "
    "You should deselect fields from the schema that are not necessary, "
    "as that may help improve the reliability of the Facebook API."
)


class AdsInsightStream(Stream):
    name = "adsinsights"
    replication_key = "date_start"
    api_sleep_time = 60

    @property
    def report_breakdowns(self) -> list[str] | None:
        return self.config.get("report_definition", {}).get("breakdowns")

    @property
    def primary_keys(self) -> list[str] | None:
        return ["id"]

    @primary_keys.setter
    def primary_keys(self, new_value: list[str] | None) -> None:
        """Set primary key(s) for the stream.

        Args:
            new_value: TODO
        """
        self._primary_keys = new_value

    @staticmethod
    def _get_datatype(field: str) -> th.Type | None:
        d_type = AdsInsights._field_types[field]  # noqa: SLF001
        if d_type == "string":
            return th.StringType()
        if d_type.startswith("list"):
            if "AdsActionStats" in d_type:
                sub_props = [
                    th.Property(field.replace("field_", ""), th.StringType())
                    for field in list(AdsActionStats.Field.__dict__)
                    if field not in EXCLUDED_FIELDS
                ]
                return th.ArrayType(th.ObjectType(*sub_props))
            if "AdsHistogramStats" in d_type:
                sub_props = []
                for field in list(AdsHistogramStats.Field.__dict__):
                    if field not in EXCLUDED_FIELDS:
                        clean_field = field.replace("field_", "")
                        if AdsHistogramStats._field_types[clean_field] == "string":  # noqa: SLF001
                            sub_props.append(th.Property(clean_field, th.StringType()))
                        else:
                            sub_props.append(
                                th.Property(
                                    clean_field,
                                    th.ArrayType(th.IntegerType()),
                                ),
                            )
                return th.ArrayType(th.ObjectType(*sub_props))
            return th.ArrayType(th.ObjectType())
        user_logger.error(f"Type not found for field: {field}")
        sys.exit(1)

    @property
    @lru_cache  # noqa: B019
    def schema(self) -> dict:
        properties: th.List[th.Property] = []
        properties.append(th.Property("id", th.StringType()))
        columns = list(AdsInsights.Field.__dict__)[1:]
        for field in columns:
            if field in EXCLUDED_FIELDS:
                continue
            properties.append(th.Property(field, self._get_datatype(field)))
        for breakdown in self.report_breakdowns:
            properties.append(th.Property(breakdown, th.StringType()))
        return th.PropertiesList(*properties).to_dict()

    def _initialize_client(self) -> None:
        self.facebook_api = FacebookAdsApi.init(
            access_token=self.config["access_token"],
            timeout=300,
            api_version=self.config["api_version"],
        )
        self.facebook_id = fb_user.User(fbid="me")

        account_id = self.config["account_id"]
        self.account = AdAccount(f"act_{account_id}").api_get()
        if not self.account:
            user_logger.error(f"[{self.name}] Couldn't find account with id {account_id}")
            sys.exit(1)

    def _check_facebook_api_usage(self, headers: str) -> None:
        should_sleep = has_reached_api_limit(
            headers=headers,
            account_id=self.config.get("account_id"),
        )
        if should_sleep:
            user_logger.warning(
                f"[{self.name}]Call count limit nearing threshold of {CALL_THRESHOLD_PERCENTAGE}%, sleeping for {self.api_sleep_time} seconds..."
            )
            time.sleep(self.api_sleep_time)
            self.api_sleep_time = min(self.api_sleep_time * 2, 300)  # Double the sleep time, but cap it at 5min
        else:
            # Reset sleep time
            self.api_sleep_time = 60

    def _trigger_async_insight_report_creation(self, account_id: str, params: dict) -> th.Any:

        request = FacebookRequest(
            node_id=f"act_{account_id}",
            method="POST",
            endpoint="/insights",
            api_type="EDGE",
            include_summary=False,
            api=FacebookAdsApi.get_default_api(),
        )

        request.add_params(params)

        return request.execute()

    def _run_job_to_completion(self, report_instance: AdReportRun, report_date: str) -> th.Any:
        status = None
        time_start = time.time()

        while status != "Job Completed":
            duration = time.time() - time_start
            job = report_instance.api_get()
            status = job[AdReportRun.Field.async_status]
            percent_complete = job[AdReportRun.Field.async_percent_completion]

            job_id = job["id"]
            user_logger.info(f"[{self.name}] ID: {job_id} - {status} for {report_date} - {percent_complete}% done. ")

            if status == "Job Completed":
                return job
            if status == "Job Failed":
                user_logger.error(
                    f"[{self.name}] Insights job {job_id} failed, trying again in a minute." + JOB_STALE_ERROR_MESSAGE
                )
                return
            if duration > INSIGHTS_MAX_WAIT_TO_START_SECONDS and percent_complete == 0:
                user_logger.warning(
                    f"[{self.name}] Insights job {job_id} did not start after {duration} seconds."
                    + JOB_STALE_ERROR_MESSAGE
                )
                return
            if duration > INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS:
                user_logger.warning(
                    f"[{self.name}] Insights job {job_id} did not complete after {INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS} seconds"
                )
                return

            internal_logger.info(f"[{self.name}] Sleeping for {POLL_JOB_SLEEP_TIME} seconds until job is done")
            time.sleep(POLL_JOB_SLEEP_TIME)
        user_logger.error(f"[{self.name}] Job failed to complete for unknown reason")
        sys.exit(1)

    def _get_selected_columns(self) -> list[str]:
        columns = [keys[1] for keys, data in self.metadata.items() if data.selected and len(keys) > 0]
        if not columns:
            columns = list(self.schema["properties"])

        # pop ID, since it's auto-generated
        if "id" in columns:
            columns.remove("id")

        # don't pass along columns that are part of breakdowns
        return [column for column in columns if column not in self.report_breakdowns]

    def _get_start_date(
        self,
        context: dict | None,
    ) -> pendulum.Date:
        lookback_window = self.config.get("report_definition", {}).get("lookback_window")
        config_start_date = pendulum.parse(self.config["start_date"]).date()
        if incremental_start_date := self.get_starting_replication_key_value(context):
            incremental_start_date = pendulum.parse(incremental_start_date).date()
        else:
            incremental_start_date = config_start_date

        if self.replication_method == REPLICATION_FULL_TABLE or config_start_date == incremental_start_date:
            report_start = config_start_date
            user_logger.info(f"[{self.name}] Using configured start date as report start filter {report_start}.")
        else:
            lookback_start_date = incremental_start_date.subtract(days=lookback_window)
            user_logger.info(
                f"[{self.name}] Incremental sync, applying lookback '{lookback_window}' to the "
                f"bookmark start date '{incremental_start_date}'. Syncing "
                f"reports starting on '{lookback_start_date}'."
            )
            report_start = lookback_start_date

        # Facebook store metrics maximum of 37 months old. Any time range that
        # older that 37 months from current date would result in 400 Bad request
        # HTTP response.
        # https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
        today = pendulum.today().date()
        oldest_allowed_start_date = today.subtract(months=37)
        if report_start < oldest_allowed_start_date:
            report_start = oldest_allowed_start_date
            user_logger.warning(
                f"[{self.name}] Report start date '{report_start}' is older than 37 months. "
                f"Using oldest allowed start date '{oldest_allowed_start_date}' instead."
            )
        return report_start

    def _generate_hash_id(self, adinsight: AdsInsights, report_breakdowns: list[str]):
        # Extract the relevant properties from the AdsInsights object
        date_start = adinsight.get("date_start", "")
        campaign_id = adinsight.get("campaign_id", "")
        adset_id = adinsight.get("adset_id", "")
        ad_id = adinsight.get("ad_id", "")

        # Get breakdown values for each breakdown field
        breakdown_values = []
        for breakdown in report_breakdowns:
            breakdown_values.append(str(adinsight.get(breakdown, "")))
        breakdown_string = "-".join(breakdown_values)

        hash_object = md5(f"{date_start}-{campaign_id}-{adset_id}-{ad_id}-{breakdown_string}".encode())
        return hash_object.hexdigest()

    def get_records(
        self,
        context: dict | None,
    ) -> t.Iterable[dict | tuple[dict, dict | None]]:
        self._initialize_client()
        time_increment = self.config.get("report_definition", {}).get("time_increment_days")

        sync_end_date = pendulum.parse(
            self.config.get("end_date", pendulum.today().to_date_string()),
        ).date()

        report_date = self._get_start_date(context)
        columns = self._get_selected_columns()

        retry_count = 0

        while report_date <= sync_end_date:
            if retry_count > 10:
                user_logger.error(f"[{self.name}] Failed to get insights after 10 retries. Stopping execution.")
                sys.exit(1)

            params = {
                "level": self.config.get("report_definition", {}).get("level"),
                "action_breakdowns": self.config.get("report_definition", {}).get("action_breakdowns"),
                "action_report_time": self.config.get("report_definition", {}).get("action_report_time"),
                "breakdowns": self.report_breakdowns,
                "fields": columns,
                "time_increment": time_increment,
                "limit": 100,
                "action_attribution_windows": [
                    self.config.get("report_definition", {}).get("action_attribution_windows_view"),
                    self.config.get("report_definition", {}).get("action_attribution_windows_click"),
                ],
                "time_range": {
                    "since": report_date.to_date_string(),
                    "until": report_date.to_date_string(),
                },
            }

            try:
                response = self._trigger_async_insight_report_creation(
                    params=params, account_id=self.config["account_id"]
                )

                self._check_facebook_api_usage(headers=response._headers)
                if response._http_status != HTTPStatus.OK:
                    continue

                report_run_id = response.json()["report_run_id"]
                job = self._run_job_to_completion(
                    report_instance=AdReportRun(report_run_id),
                    report_date=report_date.to_date_string(),
                )

                if not isinstance(job, AdReportRun):
                    # retry if facebook job report generation got stuck
                    time.sleep(AD_REPORT_RETRY_TIME)
                    retry_count += 1
                    continue

                for obj in job.get_result():
                    if isinstance(obj, AdsInsights):
                        obj["id"] = self._generate_hash_id(adinsight=obj, report_breakdowns=self.report_breakdowns)
                        yield obj.export_all_data()
                    else:
                        # stop the for loop and retry the same date after a while
                        time.sleep(AD_REPORT_RETRY_TIME)
                        retry_count += 1
                        break
                else:
                    # successfully got the insights data, bump to the next date increment
                    time.sleep(AD_REPORT_INCREMENT_SLEEP_TIME)
                    report_date = report_date.add(days=time_increment)

            except FacebookRequestError as fb_err:
                if fb_err.api_error_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                    user_logger.warning(f"[{self.name}] API Error: {fb_err.api_error_message()}. Trying again..")
                    time.sleep(60)
                    retry_count += 1
                    continue

                if fb_err.api_error_code == HTTPStatus.BAD_REQUEST and "unsupported get request" in str(
                    fb_err.api_error_message.lower()
                ):
                    user_logger.warning(f"[{self.name}] API Error: {fb_err.api_error_message()}. Trying again..")
                    retry_count += 1
                    continue

                user_logger.error(f"[{self.name}] An unhandled error occurred: {fb_err}. Stopping execution.")
                user_logger.exception(f"[{self.name}] An unhandled error occurred: {fb_err}. Stopping execution.")
                sys.exit(1)


class AdsInsightByAgeAndGenderStream(AdsInsightStream):
    name = "adsinsights_by_age_and_gender"

    @property
    def report_breakdowns(self) -> list[str] | None:
        return ["age", "gender"]


class AdsInsightByCountryStream(AdsInsightStream):
    name = "adsinsights_by_country"

    @property
    def report_breakdowns(self) -> list[str] | None:
        return ["country"]


class AdsInsightByDevicePlatformStream(AdsInsightStream):
    name = "adsinsights_by_device_platform"

    @property
    def report_breakdowns(self) -> list[str] | None:
        return ["device_platform"]


class AdsInsightByRegionStream(AdsInsightStream):
    name = "adsinsights_by_region"

    @property
    def report_breakdowns(self) -> list[str] | None:
        return ["region"]

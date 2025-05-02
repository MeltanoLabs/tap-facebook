"""Stream class for AdInsights."""

from __future__ import annotations

import time
import typing as t
from functools import lru_cache

import facebook_business.adobjects.user as fb_user
import pendulum
import json
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.adobjects.adsactionstats import AdsActionStats
from facebook_business.adobjects.adshistogramstats import AdsHistogramStats
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.exceptions import FacebookRequestError
from facebook_business.api import FacebookAdsApi

from singer_sdk import typing as th

from singer_sdk.streams.core import REPLICATION_INCREMENTAL, Stream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

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
    "__module__",
    "__doc__",
    "__dict__",
    "__firstlineno__",  # Python 3.13+
    "__static_attributes__",  # Python 3.13+
    # No longer available >= v19.0: https://developers.facebook.com/docs/marketing-api/marketing-api-changelog/version19.0/
    "age_targeting",
    "gender_targeting",
    "labels",
    "location",
    "estimated_ad_recall_rate_lower_bound",
    "estimated_ad_recall_rate_upper_bound",
    "estimated_ad_recallers_lower_bound",
    "estimated_ad_recallers_upper_bound",
]

SLEEP_TIME_INCREMENT = 5
INSIGHTS_MAX_WAIT_TO_START_SECONDS = 5 * 60
INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS = 30 * 60


class AdsInsightStream(Stream):
    name = "adsinsights"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "date_start"

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Initialize the stream."""
        self._report_definition = kwargs.pop("report_definition")
        kwargs["name"] = f"{self.name}_{self._report_definition['name']}"
        super().__init__(*args, **kwargs)
        self._current_account_id = None

    @property
    def primary_keys(self) -> t.Sequence[str] | None:
        level = self._report_definition["level"]
        base_keys = ["date_start", "account_id"]
        
        # Add the appropriate ID field based on the level
        if level == "campaign":
            base_keys.append("campaign_id")
        elif level == "adset":
            base_keys.append("adset_id")
        elif level == "ad":
            base_keys.append("ad_id")
        
        return base_keys + self._report_definition["breakdowns"]

    @primary_keys.setter
    def primary_keys(self, new_value: list[str] | None) -> None:
        """Set primary key(s) for the stream.

        Args:
            new_value: TODO
        """
        self._primary_keys = new_value

    @property
    def current_account_id(self) -> str:
        """Get the current account ID being processed.

        Returns:
            The current account ID, falling back to the configured account_id.
        """
        return self._current_account_id or self.config["account_id"]

    @staticmethod
    def _get_datatype(field: str) -> th.JSONTypeHelper | None:
        d_type = AdsInsights._field_types[field]  # noqa: SLF001
        if d_type == "string":
            return th.StringType()
        if d_type.startswith("list"):
            sub_props: list[th.Property]
            if "AdsActionStats" in d_type:
                sub_props = [
                    th.Property(field.replace("field_", ""), th.StringType())
                    for field in list(AdsActionStats.Field.__dict__)
                    if field not in EXCLUDED_FIELDS
                ]
                return th.ArrayType(th.ObjectType(*sub_props))
            if "AdsHistogramStats" in d_type:
                sub_props = []
                for f in list(AdsHistogramStats.Field.__dict__):
                    if f not in EXCLUDED_FIELDS:
                        clean_field = f.replace("field_", "")
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
        msg = f"Type not found for field: {field}"
        raise RuntimeError(msg)

    @property
    @lru_cache  # noqa: B019
    def schema(self) -> dict:
        properties: list[th.Property] = []
        columns = list(AdsInsights.Field.__dict__)[1:]
        for field in columns:
            if field in EXCLUDED_FIELDS:
                continue
            if data_type := self._get_datatype(field):
                properties.append(th.Property(field, data_type))

        properties.extend(
            [
                th.Property(breakdown, th.StringType())
                for breakdown in self._report_definition["breakdowns"]
            ],
        )

        return th.PropertiesList(*properties).to_dict()

    def _initialize_client(self) -> None:
        FacebookAdsApi.init(
            access_token=self.config["access_token"],
            timeout=300,
            api_version=self.config["api_version"],
        )
        fb_user.User(fbid="me")

        account_id = self.current_account_id
        self.account = AdAccount(f"act_{account_id}").api_get()
        if not self.account:
            msg = f"Couldn't find account with id {account_id}"
            raise RuntimeError(msg)

    def _run_job_to_completion(self, params: dict) -> None:
        max_retries = 5
        base_backoff = 2
        retry_count = 0
        retryable_codes = {1, 2, 4, 17, 32, 341, 368, 613}

        while retry_count < max_retries:
            try:
                job = self.account.get_insights(
                    params=params,
                    is_async=True,
                )
                status = None
                time_start = time.time()

                while status != "Job Completed":
                    duration = time.time() - time_start
                    try:
                        job = job.api_get()
                    except FacebookRequestError as fb_err:
                        error_body = getattr(fb_err, "body", {})
                        error_info = error_body.get("error", {})
                        code = error_info.get("code")
                        is_transient = error_info.get("is_transient", False)
                        message = error_info.get("message", "Unknown")

                        self.logger.warning("Facebook API error: %s", json.dumps(error_info))

                        if is_transient or code in retryable_codes:
                            retry_count += 1
                            sleep_time = min(base_backoff ** retry_count, 300)
                            self.logger.warning(
                                "Retryable Facebook error (code %s): %s. Retrying %d/%d after %s seconds.",
                                code, message, retry_count, max_retries, sleep_time
                            )
                            time.sleep(sleep_time)
                            break  # Retry outer job loop
                        else:
                            raise  # Fatal Facebook error

                    except TypeError as e:
                        retry_count += 1
                        sleep_time = min(base_backoff ** retry_count, 300)
                        self.logger.warning(
                            "TypeError during job.api_get(): %s. Retrying %d/%d after %s seconds.",
                            str(e), retry_count, max_retries, sleep_time
                        )
                        time.sleep(sleep_time)
                        break

                    status = job[AdReportRun.Field.async_status]
                    percent_complete = job[AdReportRun.Field.async_percent_completion]
                    job_id = job["id"]

                    self.logger.info(
                        "%s for %s - %s. %s%% done.",
                        status,
                        params["time_range"]["since"],
                        params["time_range"]["until"],
                        percent_complete,
                    )

                    if status == "Job Completed":
                        return job
                    if status == "Job Failed":
                        raise RuntimeError(f"Job {job_id} failed: {dict(job)}")

                    if duration > INSIGHTS_MAX_WAIT_TO_START_SECONDS and percent_complete == 0:
                        raise RuntimeError(
                            f"Insights job {job_id} did not start after {INSIGHTS_MAX_WAIT_TO_START_SECONDS} seconds."
                        )
                    if duration > INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS:
                        raise RuntimeError(
                            f"Insights job {job_id} did not complete after {INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS // 60} minutes."
                        )

                    self.logger.info("Sleeping for %s seconds...", SLEEP_TIME_INCREMENT)
                    time.sleep(SLEEP_TIME_INCREMENT)

            except (RuntimeError, FacebookRequestError) as e:
                retry_count += 1
                if retry_count >= max_retries:
                    self.logger.error("Job failed after all retries. Error: %s", str(e))
                    raise
                sleep_time = min(base_backoff ** retry_count, 300)
                self.logger.warning("Outer retry after error: %s. Retrying %d/%d after %s seconds.",
                                    str(e), retry_count, max_retries, sleep_time)
                time.sleep(sleep_time)

        raise RuntimeError("Job failed to complete after all retries.")


    def _get_selected_columns(self) -> list[str]:
        self.logger.info("********** METADATA CONTENT **********")
        self.logger.info("%s", self.metadata.items())
        self.logger.info("************************************")
        columns = [
            keys[1] for keys, data in self.metadata.items() if data.selected and len(keys) > 0
        ]
        self.logger.info("********** COLUMNS FROM METADATA **********")
        self.logger.info("%s", columns)
        self.logger.info("****************************************")
        if not columns and self.name == "adsinsights_default":
            columns = list(self.schema["properties"])
            self.logger.info("********** USING ALL SCHEMA PROPERTIES **********")
            self.logger.info("%s", columns)
            self.logger.info("********************************************")
        return columns

    def _get_start_date(
        self,
        context: Context | None,
    ) -> pendulum.Date:
        lookback_window = self._report_definition["lookback_window"]

        config_start_date = pendulum.parse(self.config["start_date"]).date()  # type: ignore[union-attr]
        incremental_start_date = pendulum.parse(  # type: ignore[union-attr]
            self.get_starting_replication_key_value(context),  # type: ignore[arg-type]
        ).date()
        lookback_start_date = incremental_start_date.subtract(days=lookback_window)

        # Don't use lookback if this is the first sync. Just start where the user requested.
        if config_start_date >= incremental_start_date:
            report_start = config_start_date
            self.logger.info("Using configured start_date as report start filter.")
        else:
            self.logger.info(
                "Incremental sync, applying lookback '%s' to the "
                "bookmark start_date '%s'. Syncing "
                "reports starting on '%s'.",
                lookback_window,
                incremental_start_date,
                lookback_start_date,
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
            self.logger.info(
                "Report start date '%s' is older than 37 months. "
                "Using oldest allowed start date '%s' instead.",
                report_start,
                oldest_allowed_start_date,
            )
        return report_start

    def get_records(
        self,
        context: Context | None,
    ) -> t.Iterable[dict | tuple[dict, dict | None]]:
        """Get records from the stream.

        Args:
            context: The stream context.

        Yields:
            A record from the stream.
        """
        # Process accounts - either from account_ids or single account_id
        account_ids_str = self.config.get("account_ids", "")
        accounts_to_process = [aid.strip() for aid in account_ids_str.split(",") if aid.strip()] if account_ids_str else [self.config["account_id"]]
        
        self.logger.info("********** ACCOUNTS TO PROCESS **********")
        self.logger.info("%s", accounts_to_process)
        self.logger.info("************************************")

        for account_id in accounts_to_process:
            self.logger.info("********** PROCESSING ACCOUNT **********")
            self.logger.info("%s", account_id)
            self.logger.info("************************************")
            self._current_account_id = account_id
            self._initialize_client()

            # Handle time increment - can be either days or 'monthly'
            time_increment = self._report_definition.get("time_increment", "daily")
            time_increment_days = self._report_definition.get("time_increment_days", 1)
            
            is_monthly = time_increment == "monthly"

            # Handle end_date being None
            config_end_date = self.config.get("end_date")
            if config_end_date is None:
                self.logger.info("********** END DATE CONFIG **********")
                self.logger.info("end_date is None, using today's date")
                self.logger.info("************************************")
                sync_end_date = pendulum.today().date()
            else:
                sync_end_date = pendulum.parse(config_end_date).date()

            report_start = self._get_start_date(context)
            if is_monthly:
                report_start = report_start.start_of('month')
                report_end = report_start.end_of('month').add(days=1)
            else:
                report_end = report_start.add(days=time_increment_days)

            self.logger.info("********** DATE RANGE FOR ACCOUNT **********")
            self.logger.info(
                "Account: %s\nFrom: %s\nTo: %s", 
                account_id,
                report_start.to_date_string(),
                sync_end_date.to_date_string()
            )
            self.logger.info("************************************")

            columns = self._get_selected_columns()

            # >>> FIX: Remove breakdowns from columns
            columns = [col for col in columns if col not in self._report_definition["breakdowns"]]

            while report_start <= sync_end_date:
                actual_until = min(report_end.subtract(days=1), sync_end_date)
                self.logger.info("********** FETCHING DATE RANGE **********")
                self.logger.info("From: %s\nTo: %s", report_start, actual_until)
                self.logger.info("************************************")

                params = {
                    "level": self._report_definition["level"],
                    "action_breakdowns": self._report_definition["action_breakdowns"],
                    "action_report_time": self._report_definition["action_report_time"],
                    "breakdowns": self._report_definition["breakdowns"],
                    "fields": columns,
                    "time_increment": "monthly" if is_monthly else time_increment_days,
                    "limit": 100,
                    "action_attribution_windows": [
                        self._report_definition["action_attribution_windows_view"],
                        self._report_definition["action_attribution_windows_click"],
                    ],
                    "use_unified_attribution_setting": True,
                    "time_range": {
                        "since": report_start.to_date_string(),
                        "until": actual_until.to_date_string(),
                    },
                }
                self.logger.info("********** API REQUEST PARAMS **********")
                self.logger.info("%s", params)
                self.logger.info("************************************")
                job = self._run_job_to_completion(params)  # type: ignore[func-returns-value]
                for obj in job.get_result():
                    yield obj.export_all_data()
                # Bump to the next increment
                if is_monthly:
                    report_start = report_start.add(months=1).start_of('month')
                    report_end = report_start.end_of('month').add(days=1)
                else:
                    report_start = report_start.add(days=time_increment_days)
                    report_end = report_end.add(days=time_increment_days)

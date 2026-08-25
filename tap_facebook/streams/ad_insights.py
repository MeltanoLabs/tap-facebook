"""Stream class for AdInsights."""

from __future__ import annotations

import time
import typing as t
from functools import lru_cache
from http import HTTPStatus

import facebook_business.adobjects.user as fb_user
import pendulum
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.adobjects.adsactionstats import AdsActionStats
from facebook_business.adobjects.adshistogramstats import AdsHistogramStats
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
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
    "video_thruplay_watched_actions",
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
    "marketing_messages_media_view_rate",
    "marketing_messages_phone_call_btn_click_rate",
    "marketing_messages_website_purchase_values",
    "wish_bid",
]

SLEEP_TIME_INCREMENT = 5
INSIGHTS_MAX_WAIT_TO_START_SECONDS = 5 * 60
INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS = 30 * 60
MAX_PAGINATION_RETRIES = 5
PAGINATION_RETRY_DELAY = 10


class AdsInsightStream(Stream):
    name = "adsinsights"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "date_start"

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Initialize the stream."""
        self._report_definition = kwargs.pop("report_definition")
        kwargs["name"] = f"{self.name}_{self._report_definition['name']}"
        super().__init__(*args, **kwargs)

    @property
    def primary_keys(self) -> t.Sequence[str]:
        # The id field is level-dependent: an adset-level report never returns ad_id.
        level = self._report_definition["level"]
        keys = ["date_start", "account_id"]
        if level != "account":
            keys.append(f"{level}_id")
        # Breakdowns are deliberately NOT included. They belong to the real grain, but
        # target-bigquery marks key properties REQUIRED, and BigQuery cannot widen an
        # existing NULLABLE column to REQUIRED. Deduping happens in dbt on the full grain.
        # A report with an explicit `fields` list may not include every key, and a key
        # absent from the schema would be declared but never populated.
        available = self.schema["properties"]
        return [key for key in keys if key in available]

    @primary_keys.setter
    def primary_keys(self, new_value: t.Sequence[str] | None) -> None:
        """Set primary key(s) for the stream.

        Args:
            new_value: TODO
        """
        self._primary_keys = new_value

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
        # Selection prunes records but not the emitted SCHEMA message, so a report that
        # requests a handful of fields would still declare every available one. An
        # explicit `fields` list bounds the schema to what the report actually returns.
        allowed = self._report_definition.get("fields")
        columns = list(AdsInsights.Field.__dict__)[1:]
        for field in columns:
            # Field.__dict__ also carries class dunders, and which ones exist varies by
            # Python version. Anything without a declared type is not a real API field.
            if field not in AdsInsights._field_types:  # noqa: SLF001
                continue
            if allowed and field not in allowed:
                continue
            if data_type := self._get_datatype(field):
                properties.append(th.Property(field, data_type))

        properties.extend(
            [
                th.Property(breakdown, th.StringType())
                for breakdown in self._report_definition["breakdowns"]
            ],
        )
        properties.append(th.Property("extracted_at", th.DateTimeType()))

        return th.PropertiesList(*properties).to_dict()

    def _initialize_client(self) -> None:
        FacebookAdsApi.init(
            access_token=self.config["access_token"],
            timeout=300,
            api_version=self.config["api_version"],
        )
        fb_user.User(fbid="me")

        account_id = self.config["account_id"]
        self.account = AdAccount(f"act_{account_id}").api_get()
        if not self.account:
            msg = f"Couldn't find account with id {account_id}"
            raise RuntimeError(msg)

    def _run_job_to_completion(self, params: dict) -> None:
        job = self.account.get_insights(
            params=params,
            is_async=True,
        )
        status = None
        time_start = time.time()
        while status != "Job Completed":
            duration = time.time() - time_start
            job = job.api_get()
            status = job[AdReportRun.Field.async_status]
            percent_complete = job[AdReportRun.Field.async_percent_completion]

            job_id = job["id"]
            self.logger.info(
                "%s for %s - %s. %s%% done. ",
                status,
                params["time_range"]["since"],
                params["time_range"]["until"],
                percent_complete,
            )

            if status == "Job Completed":
                return job
            if status == "Job Failed":
                raise RuntimeError(dict(job))
            if duration > INSIGHTS_MAX_WAIT_TO_START_SECONDS and percent_complete == 0:
                error_message = (
                    f"Insights job {job_id} did not start after "
                    f"{INSIGHTS_MAX_WAIT_TO_START_SECONDS} seconds. "
                    "This is an intermittent error and may resolve itself on subsequent "
                    "queries to the Facebook API. "
                    "You should deselect fields from the schema that are not necessary, "
                    "as that may help improve the reliability of the Facebook API."
                )
                raise RuntimeError(error_message)

            if duration > INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS:
                error_message = (
                    f"Insights job {job_id} did not complete after "
                    f"{INSIGHTS_MAX_WAIT_TO_FINISH_SECONDS // 60} seconds. "
                    "This is an intermittent error and may resolve itself on "
                    "subsequent queries to the Facebook API. "
                    "You should deselect fields from the schema that are not necessary, "
                    "as that may help improve the reliability of the Facebook API."
                )
                raise RuntimeError(error_message)

            self.logger.info(
                "Sleeping for %s seconds until job is done",
                SLEEP_TIME_INCREMENT,
            )
            time.sleep(SLEEP_TIME_INCREMENT)
        msg = "Job failed to complete for unknown reason"
        raise RuntimeError(msg)

    def _get_selected_columns(self) -> list[str]:
        columns = [
            keys[1] for keys, data in self.metadata.items() if data.selected and len(keys) > 0
        ]
        if not columns and self.name == "adsinsights_default":
            columns = list(self.schema["properties"])
        return columns

    def _get_records_with_retry(self, params: dict) -> t.Iterable[dict]:
        """Run one insights job, retrying on transient Facebook 500s.

        Records are buffered rather than streamed straight out: a 500 raised partway
        through pagination would otherwise leave a partial window already emitted,
        which the retry would then emit again as duplicates.
        """
        extracted_at = pendulum.now("UTC").to_iso8601_string()
        for attempt in range(MAX_PAGINATION_RETRIES + 1):
            try:
                job = self._run_job_to_completion(params)
                records = []
                for obj in job.get_result():  # type: ignore[attr-defined]
                    record = obj.export_all_data()
                    record["extracted_at"] = extracted_at
                    records.append(record)
                yield from records
                return  # noqa: TRY300
            except FacebookRequestError as e:  # noqa: PERF203
                if (
                    e.http_status() == HTTPStatus.INTERNAL_SERVER_ERROR
                    and attempt < MAX_PAGINATION_RETRIES
                ):
                    self.logger.warning(
                        "Facebook API 500 error during pagination. Retry %s/%s in %s seconds.",
                        attempt + 1,
                        MAX_PAGINATION_RETRIES,
                        PAGINATION_RETRY_DELAY,
                    )
                    time.sleep(PAGINATION_RETRY_DELAY)
                    continue
                raise

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
        self._initialize_client()

        time_increment = self._report_definition["time_increment_days"]

        sync_end_date = pendulum.parse(  # type: ignore[union-attr]
            self.config.get("end_date", pendulum.today().to_date_string()),
        ).date()

        report_start = self._get_start_date(context)
        report_end = report_start.add(days=time_increment)

        columns = self._report_definition.get("fields") or self._get_selected_columns()
        # Breakdowns (and extracted_at) live in the schema but are not AdsInsights fields;
        # passing them in `fields` makes Facebook reject the job.
        columns = [c for c in columns if c in AdsInsights.Field.__dict__]
        while report_start <= sync_end_date:
            params = {
                "level": self._report_definition["level"],
                "action_breakdowns": self._report_definition["action_breakdowns"],
                "action_report_time": self._report_definition["action_report_time"],
                "breakdowns": self._report_definition["breakdowns"],
                "fields": columns,
                "time_increment": time_increment,
                "limit": 100,
                "action_attribution_windows": [
                    self._report_definition["action_attribution_windows_view"],
                    self._report_definition["action_attribution_windows_click"],
                ],
                "time_range": {
                    "since": report_start.to_date_string(),
                    "until": report_end.to_date_string(),
                },
            }
            yield from self._get_records_with_retry(params)
            # Bump to the next increment
            report_start = report_start.add(days=time_increment)
            report_end = report_end.add(days=time_increment)

"""Stream class for Adsets."""

from __future__ import annotations

from pathlib import Path

from singer_sdk.streams.core import REPLICATION_INCREMENTAL

from tap_facebook.client import IncrementalFacebookStream

SCHEMAS_DIR = Path(__file__).parents[1] / Path("./schemas")


class AdsetsStream(IncrementalFacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-campaign/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema_filepath: path to json schema file
    tap_stream_id = stream id
    """

    schema_filepath = SCHEMAS_DIR / "adsets.json"

    columns = [  # noqa: RUF012
        "id",
        "campaign_id",
        "updated_time",
        "created_time",
        "start_time",
        "end_time",
        "name",
        "daily_budget",
        "lifetime_budget",
        "status",
        "optimization_goal",
        "targeting",
    ]

    columns_remaining = [  # noqa: RUF012
        "adlabels",
        "adset_schedule",
        "asset_feed_id",
        "attribution_spec",
        "bid_adjustments",
        "bid_amount",
        "bid_constraints",
        "bid_info",
        "bid_strategy",
        "contextual_bundling_spec",
        "creative_sequence",
        "daily_min_spend_target",
        "spend_cap",
        "frequency_control_specs",
        "instagram_actor_id",
        "issues_info",
        "lifetime_min_spend_target",
        "lifetime_spend_cap",
        "recommendations",
        "review_feedback",
        "rf_prediction_id",
        "time_based_ad_rotation_id_blocks",
        "time_based_ad_rotation_intervals",
    ]

    name = "adsets"
    filter_entity = "adset"

    path = f"/adsets?fields={columns}"
    primary_keys = ["id", "updated_time"]  # noqa: RUF012
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "updated_time"

    tap_stream_id = "adsets"

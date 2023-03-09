"""Stream type classes for tap-facebook."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_facebook.client import facebookStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

# ads insights stream
class adsinsightStream(facebookStream):
    name = "adsinsights"
    path = "/insights"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "ads_insights.json"
    tap_stream_id = "adsinsights"
    #replication_key = "created_time"

# ads stream
class adsStream(facebookStream):
    columns = ["id",
               "account_id",
               "adset_id",
               "campaign_id",
               "bid_type",
               "status",
               "updated_time",
               "created_time",
               "name",
               "effective_status",
               "last_updated_by_app_id",
               "source_ad_id",
               "creative",
               "tracking_specs",
               "conversion_specs"]

    columns_remaining = ["adlabels", "recommendations"]

    name = "ads"
    path = "/ads?fields={}".format(columns)
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "ads.json"
    tap_stream_id = "ads"

# adsets stream
class adsetsStream(facebookStream):

    name = "adsets"
    path = "/insights?level=adset"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "adsets.json"
    tap_stream_id = "adsets"

# campaigns stream
class campaignStream(facebookStream):
    name = "campaigns"
    path = "/insights?level=campaign"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "campaigns.json"
    tap_stream_id = "campaigns"

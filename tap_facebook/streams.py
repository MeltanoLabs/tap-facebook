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
    name = "ads"
    path = "/insights?level=ad"
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

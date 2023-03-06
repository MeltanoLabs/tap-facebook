"""Stream type classes for tap-facebook."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_facebook.client import facebookStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class adsinsightStream(facebookStream):
    """Define custom stream."""

    name = "ads"
    path = "/ads"
    primary_keys = ["id"]
    replication_key = "created_time"
    schema_filepath = SCHEMAS_DIR / "ads.json"

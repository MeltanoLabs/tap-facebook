"""Stream type classes for tap-facebook."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_facebook.client import facebookStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class adsinsightStream(facebookStream):
    """Define custom stream."""
    name = "adsinsight"
    path = "/insights"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "insight.json"

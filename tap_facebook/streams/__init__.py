"""Stream classes for tap-facebook."""

from tap_facebook.streams.ad_insights import AdsInsightStream
from tap_facebook.streams.adsets import AdsetsStream

__all__ = [
    "AdsInsightStream",
    "AdsetsStream",
]

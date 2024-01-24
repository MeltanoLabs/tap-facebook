"""Stream classes for tap-facebook."""
from tap_facebook.streams.ad_accounts import AdAccountsStream
from tap_facebook.streams.ad_images import AdImages
from tap_facebook.streams.ad_insights import AdsInsightStream
from tap_facebook.streams.ad_labels import AdLabelsStream
from tap_facebook.streams.ad_videos import AdVideos
from tap_facebook.streams.ads import AdsStream
from tap_facebook.streams.adsets import AdsetsStream
from tap_facebook.streams.campaign import CampaignStream
from tap_facebook.streams.creative import CreativeStream
from tap_facebook.streams.custom_audiences import CustomAudiences
from tap_facebook.streams.custom_conversions import CustomConversions

__all__ = [
    "AdAccountsStream",
    "AdImages",
    "AdLabelsStream",
    "AdsetsStream",
    "AdsInsightStream",
    "AdsStream",
    "AdVideos",
    "CampaignStream",
    "CreativeStream",
    "CustomAudiences",
    "CustomConversions",
]

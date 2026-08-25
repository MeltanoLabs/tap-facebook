"""Tests standard tap features using the built-in SDK tests library."""

import os

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_facebook.tap import TapFacebook

SAMPLE_CONFIG = {
    "start_date": "2021-03-01T00:00:00Z",
    "access_token": os.environ["TAP_FACEBOOK_ACCESS_TOKEN"],
    "account_id": os.environ["TAP_FACEBOOK_ACCOUNT_ID"],
    "insight_reports_list": [
        {
            "name": "adset",
            "level": "adset",
            "fields": ["adset_id", "date_start", "date_stop", "impressions", "clicks", "spend"],
            "breakdowns": ["country", "region"],
        },
    ],
}

TestTapFacebook = get_tap_test_class(
    TapFacebook,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(max_records_limit=20),
)

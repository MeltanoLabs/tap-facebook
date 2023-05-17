"""Tests standard tap features using the built-in SDK tests library."""


from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_facebook.tap import Tapfacebook

SAMPLE_CONFIG = {
    "start_date": "2023-03-01T00:00:00Z",
    "api_version": "v16.0",
}

TestTapFacebook = get_tap_test_class(
    Tapfacebook,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        max_records_limit=20,
    ),
)

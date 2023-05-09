"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_standard_tap_tests

from tap_facebook.tap import Tapfacebook

SAMPLE_CONFIG = {
    "start_date": "2023-03-01T00:00:00Z",
    "access_token": "abc123",
    "account_id":  "1000",
    "api_version":"v16.0"
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(Tapfacebook, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your tap.

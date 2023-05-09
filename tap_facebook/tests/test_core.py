"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_standard_tap_tests

from tap_facebook.tap import Tapfacebook

import os
from dotenv import load_dotenv

load_dotenv()

facebook_config = {
    "start_date": os.getenv("TAP_FACEBOOK_START_DATE"),
    "access_token":os.getenv("TAP_FACEBOOK_ACCESS_TOKEN"),
    "account_id":os.getenv("TAP_FACEBOOK_ACCOUNT_ID"),
    "api_version":"v16.0"
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(Tapfacebook, config=facebook_config)
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your tap.

"""Tests standard tap features using the built-in SDK tests library."""

import os

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_facebook.streams import AdAccountsStream, AdsInsightStream
from tap_facebook.tap import TapFacebook

SAMPLE_CONFIG = {
    "start_date": "2021-03-01T00:00:00Z",
    "access_token": os.environ["TAP_FACEBOOK_ACCESS_TOKEN"],
    "account_id": os.environ["TAP_FACEBOOK_ACCOUNT_ID"],
}

TestTapFacebook = get_tap_test_class(
    TapFacebook,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        max_records_limit=20,
        ignore_no_records_for_streams=[
            "adlabels",
            "adsinsights",
            "customconversions",
        ],
    ),
)


def test_ads_insights_post_process():
    row = {"reach": "0", "impressions": "1"}

    ads_insights_stream = AdsInsightStream(tap=TapFacebook(config=SAMPLE_CONFIG))

    post_processed_row = ads_insights_stream.post_process(row)

    assert post_processed_row["inline_link_clicks"] is None
    assert post_processed_row["reach"] == 0
    assert post_processed_row["impressions"] == 1


def test_ads_accounts_post_process():
    row = {"amount_spent": "0", "balance": "1", "min_campaign_group_spend_cap": "2"}

    ads_accounts_stream = AdAccountsStream(tap=TapFacebook(config=SAMPLE_CONFIG))

    post_processed_row = ads_accounts_stream.post_process(row)

    assert post_processed_row["spend_cap"] is None
    assert post_processed_row["amount_spent"] == 0
    assert post_processed_row["balance"] == 1
    assert post_processed_row["min_campaign_group_spend_cap"] == 2

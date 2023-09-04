"""Tests standard tap features using the built-in SDK tests library."""


from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_facebook.streams import AdAccountsStream, AdsInsightStream
from tap_facebook.tap import TapFacebook

SAMPLE_CONFIG = {
    "start_date": "2023-03-01T00:00:00Z",
    "api_version": "v16.0",
    "access_token": "xxx",
    "account_id": "xxx",
}

TestTapFacebook = get_tap_test_class(
    TapFacebook,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        max_records_limit=20,
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

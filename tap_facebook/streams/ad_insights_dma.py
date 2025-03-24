"""Stream class for AdInsights with DMA breakdown."""

from __future__ import annotations

from tap_facebook.streams.ad_insights import AdsInsightStream


class AdInsightsDMAStream(AdsInsightStream):
    """Stream class for AdInsights with DMA breakdown."""

    name = "adsinsights_dma"
    tap_stream_id = "adsinsights_dma"

    def __init__(self, *args, **kwargs) -> None:
        report_definition = {
          "name": "default",
          "level": "ad",
          "action_breakdowns": [],
          "breakdowns": ["dma"],
          "time_increment_days": 1,
          "action_attribution_windows_view": "1d_view",
          "action_attribution_windows_click": "7d_click",
          "action_report_time": "mixed",
          "lookback_window": 28,
        }
        super().__init__(*args, report_definition=report_definition, **kwargs)
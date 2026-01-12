"""Stream class for Ad Account Activities including Billing Charges."""

from __future__ import annotations

import json
import typing as t

from nekt_singer_sdk.custom_logger import user_logger
from nekt_singer_sdk.helpers import types
from nekt_singer_sdk.typing import NumberType, PropertiesList, Property, StringType

from tap_facebook.client import FacebookStream


class ActivitiesStream(FacebookStream):
    """Fetch account activities from Facebook Ads, including billing charges.

    API Reference:
    https://developers.facebook.com/docs/marketing-api/reference/ad-account/activities/

    This stream returns account activities. Billing-related event types include:
    - ad_account_billing_charge (charges made to credit card)
    - ad_account_billing_charge_failed
    - ad_account_billing_refund

    To get billing data, we fetch all activities and the event_type field will
    contain billing event types. The extra_data field contains transaction details.
    """

    columns = [  # noqa: RUF012
        "event_time",
        "event_type",
        "extra_data",
        "actor_id",
        "actor_name",
    ]

    name = "activities"
    path = f"/activities?fields={','.join(columns)}"
    tap_stream_id = "activities"
    primary_keys = ["event_time", "event_type", "actor_id"]  # noqa: RUF012
    replication_key = "event_time"

    schema = PropertiesList(
        Property(
            "event_time",
            StringType,
            description="The time when the event occurred (ISO 8601 format)",
        ),
        Property(
            "event_type",
            StringType,
            description="The type of event (e.g., ad_account_billing_charge, ad_account_billing_refund)",
        ),
        Property(
            "extra_data",
            StringType,
            description="Additional data about the event, typically includes transaction value in JSON format",
        ),
        Property(
            "actor_id",
            StringType,
            description="ID of the user/entity who triggered the activity",
        ),
        Property(
            "actor_name",
            StringType,
            description="Name of the user/entity who triggered the activity",
        ),
        Property(
            "charge_amount",
            NumberType,
            description="Extracted charge amount from extra_data (if available and event is billing-related)",
        ),
        Property(
            "currency",
            StringType,
            description="Currency code extracted from extra_data (if available)",
        ),
        Property(
            "is_billing_event",
            StringType,
            description="Boolean flag indicating if this is a billing-related event",
        ),
    ).to_dict()

    def sync(self, context: types.Context | None = None) -> None:
        user_logger.info(f"[{self.name}] Retrieving activities from the last 7 days.")
        return super().sync(context)

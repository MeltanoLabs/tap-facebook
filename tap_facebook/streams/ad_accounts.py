"""Stream class for AdAccounts."""

from __future__ import annotations

import typing as t

from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL
from nekt_singer_sdk.typing import (
    ArrayType,
    BooleanType,
    IntegerType,
    NumberType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)
from singer_sdk.typing import DateTimeType

from tap_facebook.client import FacebookStream

# Basic columns - core fields that work with limited permissions
BASIC_COLUMNS = [
    "account_id",
    "account_status",
    "age",
    "amount_spent",
    "balance",
    "business_city",
    "business_country_code",
    "business_name",
    "business_street",
    "business_street2",
    "business_state",
    "business_zip",
    "can_create_brand_lift_study",
    "capabilities",
    "created_time",
    "currency",
    "disable_reason",
    "end_advertiser",
    "end_advertiser_name",
    "has_migrated_permissions",
    "id",
    "is_attribution_spec_system_default",
    "is_direct_deals_enabled",
    "is_in_3ds_authorization_enabled_market",
    "is_notifications_enabled",
    "is_personal",
    "is_prepay_account",
    "is_tax_id_required",
    "min_campaign_group_spend_cap",
    "min_daily_budget",
    "name",
    "offsite_pixels_tos_accepted",
    "spend_cap",
    "timezone_id",
    "timezone_name",
    "timezone_offset_hours_utc",
]

# Extended columns - require elevated permissions (admin/finance access)
# These may fail if user doesn't have sufficient permissions on all ad accounts
EXTENDED_COLUMNS = [
    # Owner and tax info
    "owner",
    "tax_id",
    "tax_id_status",
    "tax_id_type",
    # Agency client declaration fields
    "agency_client_declaration_agency_representing_client",
    "agency_client_declaration_client_based_in_france",
    "agency_client_declaration_client_city",
    "agency_client_declaration_client_country_code",
    "agency_client_declaration_client_email_address",
    "agency_client_declaration_client_name",
    "agency_client_declaration_client_postal_code",
    "agency_client_declaration_client_province",
    "agency_client_declaration_client_street",
    "agency_client_declaration_client_street2",
    "agency_client_declaration_has_written_mandate_from_advertiser",
    "agency_client_declaration_is_client_paying_invoices",
    # Business manager fields
    "business_manager_block_offline_analytics",
    "business_manager_created_by",
    "business_manager_created_time",
    "business_manager_extended_updated_time",
    "business_manager_is_hidden",
    "business_manager_link",
    "business_manager_name",
    "business_manager_payment_account_id",
    "business_manager_primary_page",
    "business_manager_profile_picture_uri",
    "business_manager_timezone_id",
    "business_manager_two_factor_type",
    "business_manager_updated_by",
    "business_manager_update_time",
    "business_manager_verification_status",
    "business_manager_vertical",
    "business_manager_vertical_id",
    "business_manager_manager_id",
    # Extended credit and invoice fields
    "extended_credit_invoice_group_id",
    "extended_credit_invoice_group_auto_enroll",
    "extended_credit_invoice_group_customer_po_number",
    "extended_credit_invoice_group_email",
    "extended_credit_invoice_group_emails",
    "extended_credit_invoice_group_name",
    # Other extended fields
    "io_number",
    "media_agency",
    "partner",
    "salesforce_invoice_group_id",
    "funding_source_details",
]

# Basic schema properties
BASIC_SCHEMA_PROPERTIES = [
    Property("account_id", StringType, description="The ID of the ad account"),
    Property("account_status", IntegerType, description="Status of the account (1=ACTIVE, 2=DISABLED, etc.)"),
    Property("age", NumberType, description="Amount of time the ad account has been open, in days"),
    Property("amount_spent", IntegerType, description="Current amount spent by the account"),
    Property("balance", IntegerType, description="Bill amount due for this ad account"),
    Property("business_city", StringType, description="City for business address"),
    Property("business_country_code", StringType, description="Country code for the business address"),
    Property("business_name", StringType, description="The business name for the account"),
    Property("business_street", StringType, description="First line of the business street address"),
    Property("business_street2", StringType, description="Second line of the business street address"),
    Property("business_state", StringType, description="State abbreviation for business address"),
    Property("business_zip", StringType, description="Zip code for business address"),
    Property("can_create_brand_lift_study", BooleanType, description="If a new brand lift study can be created"),
    Property("capabilities", ArrayType(StringType), description="List of capabilities the ad account has"),
    Property("created_time", StringType, description="When the account was created (ISO 8601)"),
    Property("currency", StringType, description="Currency used for the account"),
    Property("disable_reason", IntegerType, description="Reason the account was disabled (0=NONE, 1=ADS_INTEGRITY_POLICY, etc.)"),
    Property("end_advertiser", StringType, description="Entity the ads will target (Page ID or App ID)"),
    Property("end_advertiser_name", StringType, description="Name of the entity the ads will target"),
    Property("has_migrated_permissions", BooleanType, description="Whether this account has migrated permissions"),
    Property("id", StringType, description="The string act_{ad_account_id}"),
    Property("is_attribution_spec_system_default", BooleanType, description="If attribution spec is system default"),
    Property("is_direct_deals_enabled", BooleanType, description="Whether Direct Deals are enabled"),
    Property("is_in_3ds_authorization_enabled_market", BooleanType, description="If account is in 3DS authorization market"),
    Property("is_notifications_enabled", BooleanType, description="Whether notifications are enabled for this account"),
    Property("is_personal", IntegerType, description="If account is for private non-business use (affects VAT)"),
    Property("is_prepay_account", BooleanType, description="If this is a prepay account"),
    Property("is_tax_id_required", BooleanType, description="If tax ID is required for this account"),
    Property("min_campaign_group_spend_cap", IntegerType, description="Minimum campaign group spend cap"),
    Property("min_daily_budget", IntegerType, description="Minimum daily budget"),
    Property("name", StringType, description="Name of the ad account"),
    Property("offsite_pixels_tos_accepted", BooleanType, description="Whether offsite pixels ToS are accepted"),
    Property("spend_cap", IntegerType, description="Spend cap for the account"),
    Property("timezone_id", IntegerType, description="Timezone ID for the account"),
    Property("timezone_name", StringType, description="Timezone name"),
    Property("timezone_offset_hours_utc", NumberType, description="Timezone offset from UTC in hours"),
]

# Extended schema properties
EXTENDED_SCHEMA_PROPERTIES = [
    Property("owner", StringType, description="Owner of the ad account"),
    Property("tax_id", StringType, description="Tax ID for the account"),
    Property("tax_id_status", IntegerType, description="Status of the tax ID"),
    Property("tax_id_type", StringType, description="Type of tax ID"),
    Property(
        "agency_client_declaration_agency_representing_client",
        IntegerType,
        description="Agency representing client declaration",
    ),
    Property(
        "agency_client_declaration_client_based_in_france",
        IntegerType,
        description="Whether client is based in France",
    ),
    Property(
        "agency_client_declaration_client_city",
        StringType,
        description="Client city for agency declaration",
    ),
    Property(
        "agency_client_declaration_client_country_code",
        StringType,
        description="Client country code for agency declaration",
    ),
    Property(
        "agency_client_declaration_client_email_address",
        StringType,
        description="Client email for agency declaration",
    ),
    Property(
        "agency_client_declaration_client_name",
        StringType,
        description="Client name for agency declaration",
    ),
    Property(
        "agency_client_declaration_client_postal_code",
        StringType,
        description="Client postal code for agency declaration",
    ),
    Property(
        "agency_client_declaration_client_province",
        StringType,
        description="Client province for agency declaration",
    ),
    Property(
        "agency_client_declaration_client_street",
        StringType,
        description="Client street for agency declaration",
    ),
    Property(
        "agency_client_declaration_client_street2",
        StringType,
        description="Client street line 2 for agency declaration",
    ),
    Property(
        "agency_client_declaration_has_written_mandate_from_advertiser",
        IntegerType,
        description="Whether agency has written mandate from advertiser",
    ),
    Property(
        "agency_client_declaration_is_client_paying_invoices",
        IntegerType,
        description="Whether client is paying invoices",
    ),
    Property(
        "business_manager_block_offline_analytics",
        BooleanType,
        description="Whether Business Manager blocks offline analytics",
    ),
    Property(
        "business_manager_created_by",
        StringType,
        description="Business Manager created by user ID",
    ),
    Property(
        "business_manager_created_time",
        StringType,
        description="Business Manager creation time",
    ),
    Property(
        "business_manager_extended_updated_time",
        StringType,
        description="Business Manager extended updated time",
    ),
    Property(
        "business_manager_is_hidden",
        BooleanType,
        description="Whether Business Manager is hidden",
    ),
    Property(
        "business_manager_link",
        StringType,
        description="Business Manager link",
    ),
    Property(
        "business_manager_name",
        StringType,
        description="Business Manager name",
    ),
    Property(
        "business_manager_payment_account_id",
        IntegerType,
        description="Business Manager payment account ID",
    ),
    Property(
        "business_manager_primary_page",
        StringType,
        description="Business Manager primary page ID",
    ),
    Property(
        "business_manager_profile_picture_uri",
        StringType,
        description="Business Manager profile picture URI",
    ),
    Property(
        "business_manager_timezone_id",
        IntegerType,
        description="Business Manager timezone ID",
    ),
    Property(
        "business_manager_two_factor_type",
        StringType,
        description="Business Manager two-factor type",
    ),
    Property(
        "business_manager_updated_by",
        StringType,
        description="Business Manager updated by user ID",
    ),
    Property(
        "business_manager_update_time",
        StringType,
        description="Business Manager update time",
    ),
    Property(
        "business_manager_verification_status",
        StringType,
        description="Business Manager verification status",
    ),
    Property(
        "business_manager_vertical",
        StringType,
        description="Business Manager vertical",
    ),
    Property(
        "business_manager_vertical_id",
        IntegerType,
        description="Business Manager vertical ID",
    ),
    Property(
        "business_manager_manager_id",
        IntegerType,
        description="Business Manager manager ID",
    ),
    Property(
        "extended_credit_invoice_group_id",
        IntegerType,
        description="Extended credit invoice group ID",
    ),
    Property(
        "extended_credit_invoice_group_auto_enroll",
        BooleanType,
        description="Extended credit invoice group auto-enroll",
    ),
    Property(
        "extended_credit_invoice_group_customer_po_number",
        StringType,
        description="Extended credit invoice group customer PO number",
    ),
    Property(
        "extended_credit_invoice_group_email",
        StringType,
        description="Extended credit invoice group email",
    ),
    Property(
        "extended_credit_invoice_group_emails",
        StringType,
        description="Extended credit invoice group emails",
    ),
    Property(
        "extended_credit_invoice_group_name",
        StringType,
        description="Extended credit invoice group name",
    ),
    Property(
        "io_number",
        IntegerType,
        description="Insertion order number",
    ),
    Property(
        "media_agency",
        StringType,
        description="Media agency",
    ),
    Property(
        "partner",
        StringType,
        description="Partner",
    ),
    Property(
        "salesforce_invoice_group_id",
        StringType,
        description="Salesforce invoice group ID",
    ),
    Property(
        "funding_source_details",
        ObjectType(
            Property("id", StringType, description="Payment method ID"),
            Property("type", IntegerType, description="Funding source type (e.g. CREDIT_CARD, INVOICE)"),
            Property("display_string", StringType, description="How the payment method is displayed"),
            Property(
                "coupons",
                ArrayType(
                    ObjectType(
                        Property("coupon_id", StringType, description="Facebook Ads coupon ID"),
                        Property("amount", IntegerType, description="Coupon amount"),
                        Property("currency", StringType, description="Coupon currency"),
                        Property("display_amount", StringType, description="Coupon display amount"),
                        Property("original_amount", IntegerType, description="Coupon original amount"),
                        Property("original_display_amount", StringType, description="Coupon original display amount"),
                        Property("expiration_date", DateTimeType, description="Coupon expiration date"),
                        Property("start_date", DateTimeType, description="Coupon start date"),
                    )
                ),
                description="List of active Facebook Ads coupons from the payment method",
            ),
        ),
        description="Payment method details (ID, type, display string, coupons)",
    ),
]


class AdAccountsStream(FacebookStream):
    """https://developers.facebook.com/docs/graph-api/reference/user/accounts/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    @property
    def url_base(self) -> str:
        version = self.config.get("api_version", "")
        return f"https://graph.facebook.com/{version}/me"

    @property
    def fields_mode(self) -> str:
        """Get the fields mode from config (basic or extended)."""
        return self.config.get("ad_accounts_fields_mode", "extended")

    @property
    def columns(self) -> list[str]:  # noqa: RUF012
        """Get columns based on the configured fields mode."""
        if self.fields_mode == "basic":
            return BASIC_COLUMNS
        return BASIC_COLUMNS + EXTENDED_COLUMNS

    @property
    def path(self) -> str:
        """Build the path with fields based on the configured mode."""
        return f"/adaccounts?fields={self.columns}"

    name = "adaccounts"
    tap_stream_id = "adaccounts"
    primary_keys = ["account_id"]  # noqa: RUF012
    replication_key = None

    @property
    def schema(self) -> dict:
        """Build schema based on the configured fields mode."""
        if self.fields_mode == "basic":
            properties = BASIC_SCHEMA_PROPERTIES
        else:
            properties = BASIC_SCHEMA_PROPERTIES + EXTENDED_SCHEMA_PROPERTIES
        return PropertiesList(*properties).to_dict()

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        row["amount_spent"] = int(row["amount_spent"]) if "amount_spent" in row else None
        row["balance"] = int(row["balance"]) if "balance" in row else None
        row["min_campaign_group_spend_cap"] = (
            int(row["min_campaign_group_spend_cap"]) if "min_campaign_group_spend_cap" in row else None
        )
        row["spend_cap"] = int(row["spend_cap"]) if "spend_cap" in row else None
        return row

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {"limit": 25}
        if next_page_token is not None:
            params["after"] = next_page_token

        return params

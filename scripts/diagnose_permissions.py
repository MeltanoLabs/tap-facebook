#!/usr/bin/env python3
"""
Facebook API Permission Diagnostic Script.

This script helps diagnose permission issues when accessing Facebook Marketing API endpoints.
It checks OAuth scopes, Business Manager access, and Ad Account permissions.

Usage:
    python diagnose_permissions.py <access_token>

    Or set the environment variable:
    export FACEBOOK_ACCESS_TOKEN=<your_token>
    python diagnose_permissions.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests

API_VERSION = "v24.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def make_request(endpoint: str, token: str, params: dict | None = None) -> dict[str, Any]:
    """Make a GET request to the Facebook Graph API."""
    url = f"{BASE_URL}{endpoint}"
    request_params = {"access_token": token}
    if params:
        request_params.update(params)

    response = requests.get(url, params=request_params, timeout=30)
    return response.json()


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"  ✓ {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"  ⚠ {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"  ✗ {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"  ℹ {message}")


def check_token_validity(token: str) -> dict | None:
    """Check if the token is valid and get basic user info."""
    print_section("1. TOKEN VALIDITY CHECK")

    result = make_request("/me", token, {"fields": "id,name,email"})

    if "error" in result:
        print_error(f"Token is invalid: {result['error'].get('message', 'Unknown error')}")
        return None

    print_success(f"Token is valid")
    print_info(f"User ID: {result.get('id')}")
    print_info(f"Name: {result.get('name', 'N/A')}")
    print_info(f"Email: {result.get('email', 'N/A')}")

    return result


def check_oauth_permissions(token: str) -> list[dict]:
    """Check granted OAuth permissions/scopes."""
    print_section("2. OAUTH PERMISSIONS (App-level scopes)")

    result = make_request("/me/permissions", token)

    if "error" in result:
        print_error(f"Could not fetch permissions: {result['error'].get('message')}")
        return []

    permissions = result.get("data", [])

    # Key permissions for ads/business
    # Note: ads_read OR ads_management is needed, not both
    required_permissions = {
        "ads_read": "Read-only access to ad accounts and insights (sufficient for /me/adaccounts)",
        "ads_management": "Full read/write access to ads (alternative to ads_read, not required if ads_read is granted)",
        "business_management": "Required to access ad accounts owned by a Business Manager",
    }

    granted = []
    declined = []

    for perm in permissions:
        perm_name = perm.get("permission")
        status = perm.get("status")

        if status == "granted":
            granted.append(perm_name)
        else:
            declined.append(perm_name)

    print("  Granted permissions:")
    for perm in granted:
        marker = "**" if perm in required_permissions else ""
        print(f"    - {perm} {marker}")

    if declined:
        print("\n  Declined permissions:")
        for perm in declined:
            print(f"    - {perm}")

    print("\n  Required permissions status:")

    # Check ads permissions (only one is needed)
    has_ads_read = "ads_read" in granted
    has_ads_management = "ads_management" in granted

    if has_ads_read or has_ads_management:
        if has_ads_read:
            print_success("ads_read: GRANTED (sufficient for reading ad accounts)")
        if has_ads_management:
            print_success("ads_management: GRANTED (includes read access)")
    else:
        ads_read_declined = "ads_read" in declined
        ads_mgmt_declined = "ads_management" in declined
        if ads_read_declined or ads_mgmt_declined:
            print_error("ads_read/ads_management: DECLINED - One of these is required")
        else:
            print_warning("ads_read/ads_management: NOT REQUESTED - One of these is required")

    # Check business_management
    if "business_management" in granted:
        print_success("business_management: GRANTED")
    elif "business_management" in declined:
        print_error("business_management: DECLINED - Required for Business Manager ad accounts")
    else:
        print_warning("business_management: NOT REQUESTED - Required for Business Manager ad accounts")

    return permissions


def check_business_access(token: str) -> list[dict]:
    """Check which Business Managers the user has access to."""
    print_section("3. BUSINESS MANAGER ACCESS")

    result = make_request("/me/businesses", token, {"fields": "id,name,permitted_roles"})

    if "error" in result:
        print_error(f"Could not fetch businesses: {result['error'].get('message')}")
        print_info("This might indicate the user is not part of any Business Manager")
        return []

    businesses = result.get("data", [])

    if not businesses:
        print_warning("User is not associated with any Business Manager")
        print_info("This could be why /me/adaccounts fails - ad accounts might be")
        print_info("owned by a Business Manager the user doesn't have access to.")
        return []

    print_success(f"User has access to {len(businesses)} Business Manager(s):\n")

    for biz in businesses:
        print(f"  Business: {biz.get('name')}")
        print(f"    ID: {biz.get('id')}")
        roles = biz.get("permitted_roles", [])
        print(f"    Roles: {', '.join(roles) if roles else 'N/A'}")
        print()

    return businesses


def check_ad_accounts_direct(token: str) -> list[dict]:
    """Try to access ad accounts directly via /me/adaccounts."""
    print_section("4. DIRECT AD ACCOUNT ACCESS (/me/adaccounts)")

    result = make_request("/me/adaccounts", token, {"fields": "id,name,account_status,account_id"})

    if "error" in result:
        error = result["error"]
        print_error(f"Failed to access /me/adaccounts")
        print_info(f"Error code: {error.get('code')}")
        print_info(f"Error type: {error.get('type')}")
        print_info(f"Message: {error.get('message')}")

        if error.get("code") == 200:
            print()
            print_warning("Error code 200 indicates insufficient permissions on the resource")
            print_info("The user likely needs to be assigned to ad accounts in Business Manager")

        return []

    ad_accounts = result.get("data", [])

    if not ad_accounts:
        print_warning("No ad accounts found")
        print_info("The user might not be assigned to any ad accounts")
        return []

    print_success(f"User has access to {len(ad_accounts)} ad account(s):\n")

    status_map = {
        1: "ACTIVE",
        2: "DISABLED",
        3: "UNSETTLED",
        7: "PENDING_RISK_REVIEW",
        8: "PENDING_SETTLEMENT",
        9: "IN_GRACE_PERIOD",
        100: "PENDING_CLOSURE",
        101: "CLOSED",
        201: "ANY_ACTIVE",
        202: "ANY_CLOSED",
    }

    for account in ad_accounts:
        status_code = account.get("account_status", 0)
        status = status_map.get(status_code, f"UNKNOWN ({status_code})")
        print(f"  Account: {account.get('name', 'N/A')}")
        print(f"    ID: {account.get('id')}")
        print(f"    Account ID: {account.get('account_id')}")
        print(f"    Status: {status}")
        print()

    return ad_accounts


def check_business_ad_accounts(token: str, businesses: list[dict]) -> dict[str, list]:
    """Check ad accounts accessible via each Business Manager."""
    print_section("5. BUSINESS MANAGER AD ACCOUNTS")

    if not businesses:
        print_info("No Business Managers to check")
        return {}

    all_accounts = {}

    for biz in businesses:
        biz_id = biz.get("id")
        biz_name = biz.get("name")

        print(f"  Checking Business Manager: {biz_name} ({biz_id})")

        # Check owned ad accounts
        owned_result = make_request(
            f"/{biz_id}/owned_ad_accounts", token, {"fields": "id,name,account_status,account_id"}
        )

        # Check client ad accounts
        client_result = make_request(
            f"/{biz_id}/client_ad_accounts", token, {"fields": "id,name,account_status,account_id"}
        )

        owned_accounts = []
        client_accounts = []

        if "error" in owned_result:
            print_warning(f"    Could not fetch owned ad accounts: {owned_result['error'].get('message')}")
        else:
            owned_accounts = owned_result.get("data", [])

        if "error" in client_result:
            print_warning(f"    Could not fetch client ad accounts: {client_result['error'].get('message')}")
        else:
            client_accounts = client_result.get("data", [])

        total = len(owned_accounts) + len(client_accounts)

        if total > 0:
            print_success(f"    Found {len(owned_accounts)} owned + {len(client_accounts)} client ad accounts")

            if owned_accounts:
                print("    Owned accounts:")
                for acc in owned_accounts[:5]:  # Limit output
                    print(f"      - {acc.get('name', 'N/A')} ({acc.get('id')})")
                if len(owned_accounts) > 5:
                    print(f"      ... and {len(owned_accounts) - 5} more")

            if client_accounts:
                print("    Client accounts:")
                for acc in client_accounts[:5]:  # Limit output
                    print(f"      - {acc.get('name', 'N/A')} ({acc.get('id')})")
                if len(client_accounts) > 5:
                    print(f"      ... and {len(client_accounts) - 5} more")
        else:
            print_warning(f"    No ad accounts found via this Business Manager")

        all_accounts[biz_id] = {
            "name": biz_name,
            "owned": owned_accounts,
            "client": client_accounts,
        }
        print()

    return all_accounts


def print_diagnosis(
    token_valid: bool,
    permissions: list,
    businesses: list,
    direct_accounts: list,
    business_accounts: dict,
) -> None:
    """Print a diagnosis summary based on all checks."""
    print_section("DIAGNOSIS SUMMARY")

    if not token_valid:
        print_error("Token is invalid. Please obtain a new access token.")
        return

    granted_perms = {p["permission"] for p in permissions if p.get("status") == "granted"}

    has_ads_perm = "ads_management" in granted_perms or "ads_read" in granted_perms
    has_business_perm = "business_management" in granted_perms

    issues = []
    recommendations = []

    if not has_ads_perm:
        issues.append("Missing ads_read or ads_management permission")
        recommendations.append(
            "Re-authenticate and grant ads_read permission (ads_management also works but grants more than needed)"
        )

    if not has_business_perm:
        issues.append("Missing business_management permission")
        recommendations.append("Re-authenticate and grant business_management permission")
        recommendations.append("Note: This is required if ad accounts are owned by a Business Manager")

    if not businesses:
        issues.append("User is not associated with any Business Manager")
        recommendations.append("Add the user to a Business Manager or use a personal ad account")

    if not direct_accounts and businesses:
        issues.append("Cannot access ad accounts via /me/adaccounts despite being in Business Manager(s)")
        recommendations.append("Ensure the user is assigned to ad accounts within Business Manager Settings")
        recommendations.append("The user needs at least 'Analyst' permission on the ad accounts")

    # Check if accounts are accessible via business but not directly
    total_business_accounts = sum(len(data["owned"]) + len(data["client"]) for data in business_accounts.values())

    if total_business_accounts > 0 and not direct_accounts:
        issues.append("Ad accounts exist in Business Manager but user cannot access them directly")
        recommendations.append("The user's role in Business Manager may not include ad account access")
        recommendations.append("Ask a Business Manager admin to assign the user to specific ad accounts")

    if issues:
        print("  Issues found:")
        for issue in issues:
            print_error(issue)

        print("\n  Recommendations:")
        for rec in recommendations:
            print_info(rec)
    else:
        print_success("No obvious permission issues detected")
        print_info("If you're still experiencing issues, the problem might be:")
        print_info("  - Token has expired (check token expiry)")
        print_info("  - Rate limiting (try again later)")
        print_info("  - API version incompatibility")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Diagnose Facebook API permission issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "token",
        nargs="?",
        help="Facebook access token (or set FACEBOOK_ACCESS_TOKEN env var)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON results",
    )

    args = parser.parse_args()

    token = args.token or os.environ.get("FACEBOOK_ACCESS_TOKEN")

    if not token:
        print("Error: No access token provided")
        print("Usage: python diagnose_permissions.py <access_token>")
        print("   Or: export FACEBOOK_ACCESS_TOKEN=<token>")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  FACEBOOK API PERMISSION DIAGNOSTIC")
    print("=" * 60)

    # Run all checks
    user_info = check_token_validity(token)
    token_valid = user_info is not None

    if not token_valid:
        print("\nCannot continue diagnostics with invalid token.")
        sys.exit(1)

    permissions = check_oauth_permissions(token)
    businesses = check_business_access(token)
    direct_accounts = check_ad_accounts_direct(token)
    business_accounts = check_business_ad_accounts(token, businesses)

    # Print diagnosis
    print_diagnosis(
        token_valid=token_valid,
        permissions=permissions,
        businesses=businesses,
        direct_accounts=direct_accounts,
        business_accounts=business_accounts,
    )

    if args.json:
        print_section("RAW JSON OUTPUT")
        output = {
            "user": user_info,
            "permissions": permissions,
            "businesses": businesses,
            "direct_ad_accounts": direct_accounts,
            "business_ad_accounts": business_accounts,
        }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

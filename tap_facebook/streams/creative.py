"""Stream class for Creative."""

from __future__ import annotations

import sys
import time
import typing as t
from http import HTTPStatus

import facebook_business.adobjects.user as fb_user
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi, FacebookRequest
from facebook_business.exceptions import FacebookRequestError
from nekt_singer_sdk.custom_logger import user_logger
from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL, Stream
from nekt_singer_sdk.typing import (
    BooleanType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.api_helper import CALL_THRESHOLD_PERCENTAGE, has_reached_api_limit

# Error subcodes for specific issues
PROBLEMATIC_CREATIVE_ERROR_SUBCODE = 2446289
RATE_LIMIT_ERROR_CODE = 80004

# Optimal page size for creative extraction
OPTIMAL_PAGE_SIZE = 100


class CreativeStream(Stream):
    """Facebook Ad Creative stream using Facebook Business SDK.

    This stream fetches ad creatives using the official Facebook Business SDK
    with comprehensive retry logic for rate limits, server errors, and
    problematic creatives.
    """

    name = "creatives"
    tap_stream_id = "creatives"
    replication_method = REPLICATION_INCREMENTAL
    replication_key = "id"
    api_sleep_time = 60

    columns = [
        "id",
        "account_id",
        "actor_id",
        "applink_treatment",
        "asset_feed_spec",
        "authorization_category",
        "body",
        "branded_content_sponsor_page_id",
        "bundle_folder_id",
        "call_to_action_type",
        "categorization_criteria",
        "category_media_source",
        "degrees_of_freedom_spec",
        "destination_set_id",
        "dynamic_ad_voice",
        "effective_authorization_category",
        "effective_instagram_media_id",
        "effective_instagram_story_id",
        "effective_object_story_id",
        "enable_direct_install",
        "image_hash",
        "image_url",
        "instagram_actor_id",
        "instagram_permalink_url",
        "instagram_story_id",
        "link_destination_display_url",
        "link_og_id",
        "link_url",
        "name",
        "object_id",
        "object_store_url",
        "object_story_id",
        "object_story_spec",
        "object_type",
        "object_url",
        "page_link",
        "page_message",
        "place_page_set_id",
        "platform_customizations",
        "playable_asset_id",
        "source_instagram_media_id",
        "status",
        "template_url",
        "thumbnail_id",
        "thumbnail_url",
        "title",
        "url_tags",
        "use_page_actor_override",
        "video_id",
    ]

    schema = PropertiesList(
        Property("id", StringType),
        Property("account_id", StringType),
        Property("actor_id", StringType),
        Property("applink_treatment", StringType),
        Property("authorization_category", StringType),
        Property("body", StringType),
        Property("branded_content_sponsor_page_id", StringType),
        Property("bundle_folder_id", StringType),
        Property("call_to_action_type", StringType),
        Property("categorization_criteria", StringType),
        Property("category_media_source", StringType),
        Property("destination_set_id", StringType),
        Property("dynamic_ad_voice", StringType),
        Property("effective_authorization_category", StringType),
        Property("effective_instagram_media_id", StringType),
        Property("effective_instagram_story_id", StringType),
        Property("effective_object_story_id", StringType),
        Property("enable_direct_install", BooleanType),
        Property("image_hash", StringType),
        Property("image_url", StringType),
        Property("instagram_actor_id", StringType),
        Property("instagram_permalink_url", StringType),
        Property("instagram_story_id", StringType),
        Property("link_destination_display_url", StringType),
        Property("link_og_id", StringType),
        Property("link_url", StringType),
        Property("name", StringType),
        Property("object_id", StringType),
        Property("object_store_url", StringType),
        Property("object_story_id", StringType),
        Property("object_type", StringType),
        Property("object_url", StringType),
        Property("page_link", StringType),
        Property("page_message", StringType),
        Property("place_page_set_id", IntegerType),
        Property("platform_customizations", StringType),
        Property("playable_asset_id", IntegerType),
        Property("source_instagram_media_id", StringType),
        Property("status", StringType),
        Property("template_url", StringType),
        Property("thumbnail_id", StringType),
        Property("thumbnail_url", StringType),
        Property("title", StringType),
        Property("url_tags", StringType),
        Property("use_page_actor_override", BooleanType),
        Property("video_id", StringType),
        Property(
            "template_url_spec",
            ObjectType(
                Property(
                    "android",
                    ObjectType(
                        Property("app_name", StringType),
                        Property("package", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "config",
                    ObjectType(
                        Property("app_id", StringType),
                    ),
                ),
                Property(
                    "ios",
                    ObjectType(
                        Property("app_name", StringType),
                        Property("app_store_id", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "ipad",
                    ObjectType(
                        Property("app_name", StringType),
                        Property("app_store_id", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "iphone",
                    ObjectType(
                        Property("app_name", StringType),
                        Property("app_store_id", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "web",
                    ObjectType(
                        Property("should_fallback", StringType),
                        Property("url", StringType),
                    ),
                ),
                Property(
                    "windows_phone",
                    ObjectType(
                        Property("app_id", StringType),
                        Property("app_name", StringType),
                        Property("url", StringType),
                    ),
                ),
            ),
        ),
        Property("product_set_id", StringType),
        Property("carousel_ad_link", StringType),
    ).to_dict()

    @property
    def primary_keys(self) -> list[str] | None:
        """Return the primary key(s) for the stream."""
        return ["id"]

    def _initialize_client(self) -> None:
        """Initialize the Facebook Business SDK client."""
        self.facebook_api = FacebookAdsApi.init(
            access_token=self.config["access_token"],
            timeout=300,
            api_version=self.config["api_version"],
        )
        self.facebook_id = fb_user.User(fbid="me")

        account_id = self.config["account_id"]
        self.account = AdAccount(f"act_{account_id}").api_get()
        if not self.account:
            user_logger.error(f"[{self.name}] Couldn't find account with id {account_id}")
            sys.exit(1)

    def get_records(
        self,
        context: dict | None,  # noqa: ARG002
    ) -> t.Iterable[dict | tuple[dict, dict | None]]:
        """Get ad creative records with comprehensive retry logic.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            Individual creative record dictionaries.
        """
        retry_count = 0
        max_retries = 10

        while retry_count <= max_retries:
            try:
                self._initialize_client()

                user_logger.info(f"[{self.name}] Starting creative extraction...")

                after_cursor = None
                record_count = 0
                page_size = OPTIMAL_PAGE_SIZE

                while True:
                    params = {
                        "fields": self.columns,
                        "limit": page_size,
                    }
                    if after_cursor:
                        params["after"] = after_cursor

                    try:
                        request = FacebookRequest(
                            node_id=f"act_{self.config['account_id']}",
                            method="GET",
                            endpoint="/adcreatives",
                            api=self.facebook_api,
                        )
                        request.add_params(params)
                        response = request.execute()

                        data = response.json() if hasattr(response, "json") else response
                        creatives = data.get("data", [])

                        if not creatives:
                            user_logger.info(f"[{self.name}] No more creatives to process")
                            break

                        # Process each creative
                        for creative_data in creatives:
                            record_count += 1
                            if record_count % 1000 == 0:
                                user_logger.info(f"[{self.name}] Processed {record_count} creatives...")
                            yield creative_data

                        # Get next page cursor
                        paging = data.get("paging", {})
                        cursors = paging.get("cursors", {})
                        after_cursor = cursors.get("after")

                        if not after_cursor:
                            user_logger.info(f"[{self.name}] Reached end of pagination")
                            break

                        # Reset page size after successful page
                        if page_size < OPTIMAL_PAGE_SIZE:
                            page_size = OPTIMAL_PAGE_SIZE
                            user_logger.info(f"[{self.name}] Reset page size to {page_size}")

                    except FacebookRequestError as page_err:
                        if (
                            page_err.http_status() == HTTPStatus.BAD_REQUEST
                            and page_err.api_error_subcode() == PROBLEMATIC_CREATIVE_ERROR_SUBCODE
                        ):
                            # Handle problematic creative with adaptive page size
                            if page_size > 1:
                                new_page_size = max(1, page_size // 2)
                                user_logger.warning(
                                    f"[{self.name}] Problematic creative at cursor {after_cursor}. "
                                    f"Reducing page size from {page_size} to {new_page_size}..."
                                )
                                page_size = new_page_size
                                continue
                            else:
                                user_logger.warning(
                                    f"[{self.name}] Skipping problematic creative at cursor {after_cursor}"
                                )
                                break
                        elif (
                            page_err.http_status() >= HTTPStatus.INTERNAL_SERVER_ERROR
                            and "reduce the amount of data" in page_err.api_error_message().lower()
                        ):
                            # Handle "reduce data" server error
                            if page_size > 1:
                                new_page_size = max(1, page_size // 2)
                                user_logger.warning(
                                    f"[{self.name}] Server requested data reduction. "
                                    f"Reducing page size from {page_size} to {new_page_size}..."
                                )
                                page_size = new_page_size
                                continue
                            else:
                                user_logger.warning(
                                    f"[{self.name}] Server still requesting data reduction at page size 1"
                                )
                                break
                        else:
                            # Re-raise to be handled by outer retry loop
                            raise

                user_logger.info(f"[{self.name}] Successfully processed {record_count} total creatives")
                return  # Success - exit retry loop

            except FacebookRequestError as fb_err:
                retry_count += 1

                if fb_err.http_status() == HTTPStatus.BAD_REQUEST and fb_err.api_error_code() == RATE_LIMIT_ERROR_CODE:
                    # Handle rate limiting
                    if retry_count <= max_retries:
                        wait_time = min(60 * retry_count, 300)  # Progressive backoff, max 5 min
                        user_logger.warning(
                            f"[{self.name}] Rate limit exceeded. Waiting {wait_time}s "
                            f"before retry {retry_count}/{max_retries}..."
                        )
                        time.sleep(wait_time)
                        continue
                elif fb_err.http_status() >= HTTPStatus.INTERNAL_SERVER_ERROR:
                    # Handle server errors
                    if retry_count <= max_retries:
                        user_logger.warning(
                            f"[{self.name}] Server error: {fb_err.api_error_message()}. "
                            f"Retry {retry_count}/{max_retries} in 60s..."
                        )
                        time.sleep(60)
                        continue

                # Don't retry client errors or if max retries reached
                user_logger.error(
                    f"[{self.name}] Error: {fb_err.api_error_message()}. "
                    f"Code: {fb_err.api_error_code()}, Subcode: {fb_err.api_error_subcode()}"
                )
                raise

        user_logger.error(f"[{self.name}] Failed after {max_retries} retries")
        sys.exit(1)

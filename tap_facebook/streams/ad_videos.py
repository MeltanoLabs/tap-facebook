"""Stream class for AdVideos."""

from __future__ import annotations

from http import HTTPStatus
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests
from nekt_singer_sdk.custom_logger import user_logger
from nekt_singer_sdk.streams.core import REPLICATION_INCREMENTAL
from nekt_singer_sdk.typing import (
    ArrayType,
    BooleanType,
    DateTimeType,
    IntegerType,
    NumberType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_facebook.client import FacebookStream


class AdVideos(FacebookStream):
    """https://developers.facebook.com/docs/marketing-api/reference/ad-image/."""

    """
    columns: columns which will be added to fields parameter in api
    name: stream name
    account_id: facebook account
    path: path which will be added to api url in client.py
    schema: instream schema
    tap_stream_id = stream id
    """

    columns = [  # noqa: RUF012
        "id",
        "updated_time",
        "account_id",
        "ad_breaks",
        # "backdated_time",
        # "backdated_time_granularity",
        "content_category",
        "content_tags",
        "created_time",
        "custom_labels",
        "description",
        # "embed_html",
        "embeddable",
        "event",
        "format",
        "from_object",
        "icon",
        "is_crosspost_video",
        "is_crossposting_eligible",
        "is_episode",
        "is_instagram_eligible",
        # "is_reference_only",
        "length",
        "live_status",
        # "music_video_copyright",
        "permalink_url",
        "place",
        "post_views",
        "premiere_living_room_status",
        # "privacy",
        "published",
        "scheduled_publish_time",
        "source",
        "status_processing_progress",
        "status_value",
        "title",
        "universal_video_id",
        "views",
    ]

    name = "advideos"
    path = f"/advideos?fields={columns}"
    tap_stream_id = "advideos"
    replication_key = "id"

    schema = PropertiesList(
        Property(
            "id",
            StringType,
            description="The ID of the video",
        ),
        Property(
            "account_id",
            StringType,
            description="The ad account that owns the video",
        ),
        Property(
            "ad_breaks",
            StringType,
            description="Ad break configuration for the video",
        ),
        Property(
            "backdated_time",
            DateTimeType,
            description="Backdated time for the video",
        ),
        Property(
            "backdated_time_granularity",
            StringType,
            description="Granularity of backdated time",
        ),
        Property(
            "content_category",
            StringType,
            description="Content category of the video",
        ),
        Property(
            "content_tags",
            StringType,
            description="Tags applied to the video content",
        ),
        Property(
            "created_time",
            StringType,
            description="When the video was created",
        ),
        Property(
            "custom_labels",
            StringType,
            description="Custom labels for the video",
        ),
        Property(
            "description",
            StringType,
            description="Description of the video",
        ),
        Property(
            "embed_html",
            StringType,
            description="HTML for embedding the video",
        ),
        Property(
            "embeddable",
            BooleanType,
            description="Whether the video can be embedded",
        ),
        Property(
            "event",
            StringType,
            description="Event associated with the video",
        ),
        Property(
            "format",
            ArrayType(
                ObjectType(
                    Property("embed_html", StringType, description="Embed HTML for this format"),
                    Property("filter", StringType, description="Format filter"),
                    Property("height", IntegerType, description="Format height in pixels"),
                    Property("width", IntegerType, description="Format width in pixels"),
                    Property("picture", StringType, description="Picture URL for this format"),
                )
            ),
            description="Available formats (dimensions, thumbnail) for the video",
        ),
        Property(
            "from_object",
            StringType,
            description="Object (page, user) that owns or uploaded the video",
        ),
        Property(
            "icon",
            StringType,
            description="Icon URL for the video",
        ),
        Property(
            "is_crosspost_video",
            BooleanType,
            description="Whether this is a crosspost video",
        ),
        Property(
            "is_crossposting_eligible",
            BooleanType,
            description="Whether the video is eligible for crossposting",
        ),
        Property(
            "is_episode",
            BooleanType,
            description="Whether the video is an episode",
        ),
        Property(
            "is_instagram_eligible",
            BooleanType,
            description="Whether the video is eligible for Instagram",
        ),
        Property(
            "is_reference_only",
            BooleanType,
            description="Whether the video is reference-only",
        ),
        Property(
            "length",
            NumberType,
            description="Length of the video in seconds",
        ),
        Property(
            "live_status",
            StringType,
            description="Live status if the video is a live broadcast",
        ),
        Property(
            "music_video_copyright",
            StringType,
            description="Music video copyright information",
        ),
        Property(
            "permalink_url",
            StringType,
            description="Permanent URL to the video",
        ),
        Property(
            "place",
            StringType,
            description="Place associated with the video",
        ),
        Property(
            "post_views",
            IntegerType,
            description="Number of post views",
        ),
        Property(
            "premiere_living_room_status",
            StringType,
            description="Premiere living room status",
        ),
        Property(
            "published",
            BooleanType,
            description="Whether the video is published",
        ),
        Property(
            "scheduled_publish_time",
            DateTimeType,
            description="Scheduled publish time for the video",
        ),
        Property(
            "source",
            StringType,
            description="Source URL of the video file",
        ),
        Property(
            "status_processing_progress",
            IntegerType,
            description="Video processing progress percentage",
        ),
        Property(
            "status_value",
            StringType,
            description="Processing status of the video",
        ),
        Property(
            "title",
            StringType,
            description="Title of the video",
        ),
        Property(
            "universal_video_id",
            StringType,
            description="Universal video ID across Facebook properties",
        ),
        Property(
            "updated_time",
            StringType,
            description="When the video was last updated",
        ),
        Property(
            "views",
            IntegerType,
            description="Number of views",
        ),
    ).to_dict()

    def validate_response(self, response: requests.Response) -> None:
        if response.status_code == HTTPStatus.OK:
            self.page_size = min(self.page_size + 5, 25)
        elif (
            response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            and "reduce the amount of data" in response.text.lower()
        ):
            self.page_size = max(self.page_size - 5, 1)
            user_logger.warning(
                f"[{self.name}] Reducing page size to {self.page_size} due to reaching API limit on the amount of data being requested."
            )
        return super().validate_response(response)

    def _request(
        self,
        prepared_request: requests.PreparedRequest,
        context: dict | None,
    ) -> requests.Response:
        # Parse URL to get parameters
        parsed = urlparse(prepared_request.url)
        params = parse_qs(parsed.query)
        params["limit"] = [str(self.page_size)]
        # Update limit parameter and rebuild URL
        new_query = urlencode(params, doseq=True)
        prepared_request.url = urlunparse(parsed._replace(query=new_query))
        return super()._request(prepared_request, context)

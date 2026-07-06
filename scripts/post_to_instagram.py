"""Publish a post (single image or multi-image carousel) to an Instagram
Business account via the Graph API. Requires the IG Business account to be
linked to the same Facebook Page whose access token we use.
"""
import os
import time

import requests

GRAPH_VERSION = "v20.0"


def _create_media_container(ig_user_id: str, access_token: str, **fields) -> str:
    resp = requests.post(
        f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_user_id}/media",
        data={**fields, "access_token": access_token},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def _publish(ig_user_id: str, access_token: str, creation_id: str) -> dict:
    resp = requests.post(
        f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def post(image_urls: list, caption: str) -> dict:
    ig_user_id = os.environ["IG_BUSINESS_ACCOUNT_ID"]
    access_token = os.environ["FB_PAGE_ACCESS_TOKEN"]

    if len(image_urls) == 1:
        creation_id = _create_media_container(
            ig_user_id, access_token, image_url=image_urls[0], caption=caption
        )
    else:
        child_ids = [
            _create_media_container(
                ig_user_id, access_token, image_url=url, is_carousel_item="true"
            )
            for url in image_urls
        ]
        # Give Instagram a moment to finish processing each child before referencing them.
        time.sleep(2)
        creation_id = _create_media_container(
            ig_user_id,
            access_token,
            media_type="CAROUSEL",
            caption=caption,
            children=",".join(child_ids),
        )

    return _publish(ig_user_id, access_token, creation_id)

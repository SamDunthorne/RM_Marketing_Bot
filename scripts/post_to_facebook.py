"""Publish a multi-photo post to a Facebook Page via the Graph API.

Technique: upload each photo unpublished to get a media_fbid, then create one
feed post that attaches all of them -- this is how the Graph API does
"multiple images, one post" (there's no single multi-photo endpoint).
"""
import json
import os

import requests

GRAPH_VERSION = "v20.0"


def _upload_unpublished_photo(page_id: str, access_token: str, image_url: str) -> str:
    resp = requests.post(
        f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/photos",
        data={
            "url": image_url,
            "published": "false",
            "access_token": access_token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def post(image_urls: list, caption: str) -> dict:
    """Create the Facebook feed post. Returns the Graph API response (includes post id)."""
    page_id = os.environ["FB_PAGE_ID"]
    access_token = os.environ["FB_PAGE_ACCESS_TOKEN"]

    media_fbids = [
        _upload_unpublished_photo(page_id, access_token, url) for url in image_urls
    ]

    attached_media = [{"media_fbid": fbid} for fbid in media_fbids]
    resp = requests.post(
        f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/feed",
        data={
            "message": caption,
            "attached_media": json.dumps(attached_media),
            "access_token": access_token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

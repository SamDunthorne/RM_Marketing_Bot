"""Publish an "Update" local post to a Google Business Profile location.

Notes / known API limits (as of API v4):
- A local post accepts multiple `media` entries, but Google's UI/apps typically
  only surface the first image -- treat this as "1 photo reliably, extras best-effort".
- Local Post CallToAction only supports a fixed set of actionType values. There's
  no generic "EMAIL" type. We map our cta.type -> actionType as:
    call    -> CALL            (uses the phone number already on the listing; no url)
    website -> LEARN_MORE      (url = cta.value)
    email   -> LEARN_MORE      (url = "mailto:<value>" -- best effort, not officially documented)
"""
import os

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
API_BASE = "https://mybusiness.googleapis.com/v4"


def _get_access_token() -> str:
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "refresh_token": os.environ["GOOGLE_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _call_to_action(cta: dict) -> dict:
    if cta["type"] == "call":
        return {"actionType": "CALL"}
    if cta["type"] == "email":
        return {"actionType": "LEARN_MORE", "url": f"mailto:{cta['value']}"}
    return {"actionType": "LEARN_MORE", "url": cta["value"]}  # website


def post(image_urls: list, caption: str, cta: dict = None) -> dict:
    access_token = _get_access_token()
    account_id = os.environ["GBP_ACCOUNT_ID"]
    location_id = os.environ["GBP_LOCATION_ID"]

    body = {
        "languageCode": "en-US",
        "summary": caption,
        "topicType": "STANDARD",
        "media": [{"mediaFormat": "PHOTO", "sourceUrl": url} for url in image_urls],
    }
    if cta:
        body["callToAction"] = _call_to_action(cta)

    resp = requests.post(
        f"{API_BASE}/accounts/{account_id}/locations/{location_id}/localPosts",
        headers={"Authorization": f"Bearer {access_token}"},
        json=body,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

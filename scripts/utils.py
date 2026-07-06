"""Shared helpers used by the platform posting scripts and the scheduler."""
import os
import urllib.parse
from pathlib import Path

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(REPO_ROOT / ".env")


def load_config():
    with open(REPO_ROOT / "config" / "config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def image_urls_for_post(post_dir: Path, post: dict) -> list:
    """Turn a post's relative image paths into publicly-fetchable URLs."""
    base_url = os.environ["IMAGE_BASE_URL"].rstrip("/")
    urls = []
    for rel_path in post["images"]:
        abs_path = (post_dir / rel_path).resolve()
        rel_to_repo = abs_path.relative_to(REPO_ROOT).as_posix()
        urls.append(f"{base_url}/{urllib.parse.quote(rel_to_repo)}")
    return urls


def build_caption(post: dict, config: dict) -> str:
    """Caption text, with a CTA line appended for 'cta' posts (Facebook/Instagram
    have no native CTA button on organic photo posts, so we spell it out)."""
    caption = post["caption"]
    cta = post.get("cta")
    if cta:
        if cta["type"] == "call":
            line = f"\U0001F4DE Call us: {cta['value']}"
        elif cta["type"] == "email":
            line = f"\U0001F4E7 Email us: {cta['value']}"
        else:  # website
            line = f"\U0001F310 {cta.get('label', 'Visit our website')}: {cta['value']}"
        caption = f"{caption}\n\n{line}"

    hashtags_file = REPO_ROOT / "assets" / "shared" / "boilerplate" / "hashtags.txt"
    if hashtags_file.exists():
        hashtags = hashtags_file.read_text(encoding="utf-8").strip()
        if hashtags:
            caption = f"{caption}\n\n{hashtags}"
    return caption

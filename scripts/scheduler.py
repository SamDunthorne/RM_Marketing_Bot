"""Scan posts/*/post.json, publish anything due, and write back status/results.

Meant to be run periodically (see .github/workflows/publish-scheduled-posts.yml).
A post that partially fails stays "pending" -- platforms already posted are
recorded under `posted` and are skipped on the next run; only the platforms
that failed (or haven't run yet) are retried.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import post_to_facebook
import post_to_google_business
import post_to_instagram
from utils import REPO_ROOT, build_caption, image_urls_for_post, load_config

POSTERS = {
    "facebook": lambda urls, caption, cta: post_to_facebook.post(urls, caption),
    "instagram": lambda urls, caption, cta: post_to_instagram.post(urls, caption),
    "google_business": lambda urls, caption, cta: post_to_google_business.post(urls, caption, cta),
}


def _now():
    return datetime.now(timezone.utc)


def process_post(post_dir: Path, config: dict) -> bool:
    """Returns True if the post.json changed and needs to be saved."""
    post_file = post_dir / "post.json"
    post = json.loads(post_file.read_text(encoding="utf-8"))

    if post.get("status") == "posted":
        return False

    scheduled_time = datetime.fromisoformat(post["scheduled_time"])
    if scheduled_time > _now():
        return False  # not due yet

    caption = build_caption(post, config)
    image_urls = image_urls_for_post(post_dir, post)
    posted = post.setdefault("posted", {})
    changed = False

    for platform in post["platforms"]:
        existing = posted.get(platform)
        if isinstance(existing, dict) and existing.get("ok"):
            continue  # already succeeded on a previous run

        try:
            result = POSTERS[platform](image_urls, caption, post.get("cta"))
            posted[platform] = {"ok": True, "result": result, "at": _now().isoformat()}
            print(f"[{post['id']}] {platform}: posted OK")
        except Exception as exc:  # noqa: BLE001 - we want to record and continue
            posted[platform] = {"ok": False, "error": str(exc), "at": _now().isoformat()}
            print(f"[{post['id']}] {platform}: FAILED - {exc}", file=sys.stderr)
        changed = True

    if all(isinstance(posted.get(p), dict) and posted[p].get("ok") for p in post["platforms"]):
        post["status"] = "posted"
        changed = True

    if changed:
        post_file.write_text(json.dumps(post, indent=2) + "\n", encoding="utf-8")
    return changed


def main():
    config = load_config()
    posts_root = REPO_ROOT / "posts"
    any_changed = False

    for post_dir in sorted(p for p in posts_root.iterdir() if p.is_dir()):
        if not (post_dir / "post.json").exists():
            continue
        if process_post(post_dir, config):
            any_changed = True

    # Exit code 0 always; GitHub Actions step checks git diff to decide whether to commit.
    print("changed" if any_changed else "no changes")


if __name__ == "__main__":
    main()

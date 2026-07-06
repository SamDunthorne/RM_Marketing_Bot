# Scheduled Posts

Each subfolder is one post: `posts/post-01/`, `posts/post-02/`, etc. A post has:

```
posts/post-01/
  post.json     <- required: schedule, caption, platforms, CTA
  images/       <- required: 1-4 images for this post
```

## `post.json` schema

```jsonc
{
  "id": "post-01",
  "scheduled_time": "2026-07-08T09:00:00-04:00",   // ISO 8601, include the -04:00/-05:00 offset for America/Toronto
  "platforms": ["facebook", "instagram", "google_business"],
  "post_type": "basic",                             // "basic" or "cta"
  "caption": "Main post text. Hashtags can go here or be appended from assets/shared/boilerplate/hashtags.txt",
  "images": [
    "images/photo1.jpg",
    "images/photo2.jpg"
  ],
  "cta": {                                          // omit or leave value blank for a plain "basic" post
    "type": "website",                              // "call" | "email" | "website"
    "label": "Get a Free Quote",
    "value": "https://roofmasterottawa.com"
  },
  "status": "pending",                              // set to "posted" automatically once published
  "posted": {                                        // filled in automatically by scheduler.py per platform
    "facebook": null,
    "instagram": null,
    "google_business": null
  }
}
```

## Rules the scheduler follows

- A post is only published once `scheduled_time` has passed (in the timezone set in
  `config/config.yaml`) AND `status` is still `"pending"`.
- The scheduler posts to every platform listed in `platforms` and records a timestamp (or an
  error) per-platform under `posted`. `status` only flips to `"posted"` once every listed
  platform has succeeded; if one platform fails, the others still go out and the scheduler
  retries the failed one on the next run.
- Facebook/Instagram don't support real CTA buttons on organic (non-ad) photo posts, so for
  `cta` posts the scheduler appends the call/email/website line to the caption. Google
  Business Profile *does* support a real CTA button, so `cta.type`/`cta.value` map directly to
  its `callToAction` field.
- Images must be reachable at a public URL for the Facebook/Instagram/Google APIs to fetch them
  server-side. By default this repo assumes images are committed here and served via
  `raw.githubusercontent.com`, which requires the **repo to be public**. See the main README for
  alternatives if you'd rather keep the repo private.

## Adding more posts

Copy an existing `post-XX` folder, rename it, drop in new images, edit `post.json`. IDs don't
need to be sequential or contiguous -- the scheduler just reads every folder under `posts/`.

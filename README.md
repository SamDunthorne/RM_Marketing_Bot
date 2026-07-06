# Roofmaster Ottawa Marketing Bot

Automates scheduled posting to Facebook, Instagram, and Google Business Profile for
**Roofmaster Ottawa Inc.** Posts (caption + images + optional call/email/website CTA) are
authored ahead of time as plain files in this repo, and a GitHub Actions workflow checks every
30 minutes for anything due and publishes it.

## Repo layout

```
assets/shared/     - reusable logos, brand graphics, boilerplate text (see its README)
posts/post-01../10 - one folder per scheduled post: post.json + images/ (see posts/README.md)
scripts/           - the actual posting logic (Facebook, Instagram, Google Business, scheduler)
docs/              - step-by-step setup guides for each platform's API access
config/config.yaml - non-secret business info & settings
.env.example       - template for local testing credentials (never commit a real .env)
.github/workflows/ - the scheduled GitHub Action that runs the bot
```

## How it works

1. You (or I) create/edit posts under `posts/`, each with a `scheduled_time`, images, caption,
   and optional CTA (call / email / website).
2. A GitHub Actions workflow (`.github/workflows/publish-scheduled-posts.yml`) runs on a cron
   schedule, calls `scripts/scheduler.py`, which:
   - finds posts whose `scheduled_time` has passed and aren't marked `"posted"` yet,
   - publishes to each platform listed in that post's `platforms`,
   - writes the result back into `post.json` and commits it, so you get a permanent record of
     what went out and when (and so it never double-posts).
3. Facebook/Instagram get a multi-photo post with the CTA folded into the caption text (they
   don't support real CTA buttons on organic posts). Google Business Profile gets a real CTA
   button via its Local Post API.

## Image hosting

Facebook, Instagram, and Google's APIs all fetch each image server-side from a URL you give
them -- they can't read a private repo, and Synology NAS hotlinks require exposing the NAS to
the public internet 24/7, and Google Drive share links don't reliably serve as direct image URLs
(Google shows an interstitial page instead for many files). So this repo
(`SamDunthorne/RM_Marketing_Bot`) is now **public**, and images are served straight from it via
`raw.githubusercontent.com`. No credentials live in the repo -- those are GitHub Actions secrets.

## Setting up each platform

- **Facebook & Instagram:** see [docs/SETUP_FACEBOOK_INSTAGRAM.md](docs/SETUP_FACEBOOK_INSTAGRAM.md)
- **Google Business Profile:** see [docs/SETUP_GOOGLE_BUSINESS.md](docs/SETUP_GOOGLE_BUSINESS.md)

Once you have the credentials, add them as **repository secrets**
(Settings > Secrets and variables > Actions > New repository secret):

`FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN`, `IG_BUSINESS_ACCOUNT_ID`,
`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`,
`GBP_ACCOUNT_ID`, `GBP_LOCATION_ID`

And one **repository variable** (same screen, "Variables" tab -- not secret):
`IMAGE_BASE_URL` (defaults suggested value: `https://raw.githubusercontent.com/SamDunthorne/RM_Marketing_Bot/main`)

## Adding real content

The 10 example posts under `posts/` use placeholder image filenames
(e.g. `images/roof-inspection-1.jpg`). Real business contact info (phone `(613) 521-0088`,
email `admin@roofmaster.ca`, website `https://roofmaster.ca`) is already filled in across
`config/config.yaml` and each post's CTA. Before going live:

1. Drop your logo and any reusable graphics into `assets/shared/` (see its README).
2. Replace the placeholder images in each `posts/post-XX/images/` folder with real photos
   (same filenames referenced in that post's `post.json`, or update the filenames).
3. Adjust `scheduled_time` values to whenever you actually want each post to go out.

## Running locally (optional, for testing before it's all wired into Actions)

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in real values
cd scripts
python scheduler.py
```

## Questions worth answering before this goes live

- Whether you want Google Business Profile posting now, or to add it once API access is
  approved (Facebook/Instagram can go live independently in the meantime).

# Setting up Facebook + Instagram

Since you already have a Facebook Page and/or Instagram account, this walks through what the
bot specifically needs: a Meta developer app, the Page linked to an Instagram **Business**
account, and a long-lived Page access token.

## 1. Confirm Instagram is a Business (or Creator) account, linked to the Page

- On Instagram: Settings > Account type and tools > confirm it's set to "Professional account" /
  "Business".
- Instagram Settings > "Linked accounts" (or via Meta Business Suite) > make sure it's linked to
  the correct Facebook Page. The Graph API posts to Instagram *through* the linked Page's
  permissions, not directly with an Instagram login.

## 2. Create a Meta developer app

1. Go to https://developers.facebook.com/apps and click **Create App**.
2. App type: **Business**.
3. Once created, add the **Facebook Login for Business** and the app should automatically have
   access to the Graph API. You don't need any special "product" beyond that for Page/Instagram
   publishing.

## 3. Get a Page access token with the right permissions

The bot needs a token with:
- `pages_manage_posts`
- `pages_read_engagement`
- `instagram_basic`
- `instagram_content_publish`

Easiest path:
1. Go to https://developers.facebook.com/tools/explorer
2. Select your app, then "Get Token" > "Get Page Access Token", and choose your Roofmaster
   Ottawa Page. Grant the permissions listed above when prompted.
3. This short-lived token needs to be exchanged for a **long-lived token** (~60 days, and Page
   tokens derived from a long-lived user token don't expire): use the
   [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) or call:

   ```
   GET https://graph.facebook.com/v20.0/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id=<APP_ID>
     &client_secret=<APP_SECRET>
     &fb_exchange_token=<SHORT_LIVED_USER_TOKEN>
   ```

   Then use that long-lived user token to fetch the Page token again via
   `GET /me/accounts` -- Page tokens obtained this way don't expire as long as the app stays
   active and the user remains an admin of the Page.
4. For submission review: Meta requires **App Review** for `instagram_content_publish` and
   `pages_manage_posts` before the app can post for anyone other than the app's own
   admins/developers/testers. If you (the business owner) are added as an admin/developer on the
   app, you can post to your own Page/Instagram without waiting on review -- this is enough to
   run the bot for your own account. Only pursue App Review if you plan to publish through this
   app for *other* businesses too.

## 4. Find your Page ID and Instagram Business Account ID

```
GET https://graph.facebook.com/v20.0/me/accounts?access_token=<USER_TOKEN>
```
Returns your Pages and their `id` (this is `FB_PAGE_ID`) and Page-specific access token
(`FB_PAGE_ACCESS_TOKEN`).

```
GET https://graph.facebook.com/v20.0/<FB_PAGE_ID>?fields=instagram_business_account&access_token=<FB_PAGE_ACCESS_TOKEN>
```
Returns the linked `instagram_business_account.id` (this is `IG_BUSINESS_ACCOUNT_ID`).

## 5. Add the values as GitHub Actions secrets

In the repo: **Settings > Secrets and variables > Actions > New repository secret**, add:
- `FB_PAGE_ID`
- `FB_PAGE_ACCESS_TOKEN`
- `IG_BUSINESS_ACCOUNT_ID`

(For local testing you can instead put these in a `.env` file copied from `.env.example` --
`.env` is git-ignored.)

## Notes / gotchas

- Instagram photo posts require the image to be reachable at a plain public URL when the
  container is created -- this is why the repo needs to be public (or images hosted elsewhere).
  See the main [README](../README.md) for the image-hosting decision.
- Page tokens can still get invalidated if the Page's admin roles change, the app is unpublished,
  or the token is manually revoked in Business Settings. If posts start failing with `OAuthException`,
  regenerate the token via steps 3-4.

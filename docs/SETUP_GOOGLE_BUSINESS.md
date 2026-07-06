# Setting up Google Business Profile

Google Business Profile ("GBP", formerly Google My Business) posting uses OAuth 2.0 with a
refresh token, plus the older "My Business" v4 API which still hosts the Local Posts
functionality. Access to this API for new projects is gated behind an approval process, so this
is the most involved of the three integrations.

## 1. Confirm you're an Owner/Manager of the Roofmaster Ottawa listing

Go to https://business.google.com and confirm you can see and edit the Roofmaster Ottawa Inc.
listing. You'll need this access level to authorize the API.

## 2. Create a Google Cloud project and OAuth credentials

1. Go to https://console.cloud.google.com and create a new project (e.g. "roofmaster-marketing-bot").
2. Enable the **My Business Business Information API** and **My Business Account Management API**
   under "APIs & Services > Library" (search "My Business").
3. **Request access to the Business Profile Performance/Local Posts APIs**: Google restricts the
   Local Posts endpoints (part of the legacy "My Business API v4") to approved applications. Fill
   out the request form linked from
   https://developers.google.com/my-business/content/prereqs -- approval can take a few days.
   Until approved, calls to the Local Posts endpoint will fail even with valid OAuth credentials.
4. Under "APIs & Services > Credentials", create an **OAuth client ID** of type "Desktop app" (or
   "Web application" if you prefer a redirect URI you control).

## 3. Get a refresh token (one-time, manual step)

Using the OAuth client ID/secret from step 2, run through the standard OAuth consent flow once
to get a refresh token. The simplest way without writing a script:

1. Build the consent URL (replace `CLIENT_ID` and `REDIRECT_URI`, e.g.
   `http://localhost` for a Desktop app client):
   ```
   https://accounts.google.com/o/oauth2/v2/auth?
     client_id=CLIENT_ID&
     redirect_uri=REDIRECT_URI&
     response_type=code&
     access_type=offline&
     prompt=consent&
     scope=https://www.googleapis.com/auth/business.manage
   ```
2. Open it in a browser, sign in with the Google account that manages the Roofmaster Ottawa
   listing, and approve. You'll be redirected with a `?code=...` in the URL.
3. Exchange that code for tokens:
   ```
   curl -X POST https://oauth2.googleapis.com/token \
     -d client_id=CLIENT_ID \
     -d client_secret=CLIENT_SECRET \
     -d redirect_uri=REDIRECT_URI \
     -d grant_type=authorization_code \
     -d code=THE_CODE_FROM_STEP_2
   ```
4. The JSON response includes `refresh_token` -- save it, this is `GOOGLE_REFRESH_TOKEN`. It does
   not expire under normal use (only if revoked or unused for 6 months).

## 4. Find your Account ID and Location ID

```
GET https://mybusinessaccountmanagement.googleapis.com/v1/accounts
Authorization: Bearer <ACCESS_TOKEN>
```
Returns your account resource, e.g. `accounts/1234567890` -- the numeric part is `GBP_ACCOUNT_ID`.

```
GET https://mybusinessbusinessinformation.googleapis.com/v1/accounts/GBP_ACCOUNT_ID/locations
Authorization: Bearer <ACCESS_TOKEN>
```
Find the Roofmaster Ottawa location in the results; the numeric id in its resource name
(`locations/9876543210`) is `GBP_LOCATION_ID`.

(You can get a one-off `ACCESS_TOKEN` for these lookups the same way `scripts/post_to_google_business.py`
does -- POST to `https://oauth2.googleapis.com/token` with your refresh token.)

## 5. Add the values as GitHub Actions secrets

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`
- `GBP_ACCOUNT_ID`
- `GBP_LOCATION_ID`

## Notes / gotchas

- If your API access request (step 2.3) isn't approved yet, the bot's `google_business` platform
  calls will fail with a 403 -- Facebook/Instagram posting is unaffected since it's independent
  per-platform. You can leave `"google_business"` out of a post's `platforms` list until access
  is approved.
- Local Posts only reliably display **one photo** even if you send more; the CTA button types are
  limited to a fixed set (`CALL`, `LEARN_MORE`, `BOOK`, `ORDER`, `SHOP`, `SIGN_UP`) -- see the
  comments in `scripts/post_to_google_business.py` for how our `call`/`email`/`website` CTA types
  map onto those.

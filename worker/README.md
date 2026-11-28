# Sign-in worker (optional)

Bungie's public sign-in lasts one hour, so the site quietly sends you back through bungie.net to renew it. With this worker, Bungie gives the site a refresh token that lasts 90 days, and renewal happens in the background with no page change.

The worker holds the Bungie app's client secret, so the secret never goes into the website. It answers only your site's address and stores nothing.

Everything keeps working without it. Set it up only if the hourly renewal bothers you.

## What you need

- A free Cloudflare account
- Node.js (for the `wrangler` command)
- Access to your Bungie app settings at bungie.net/en/Application

## Steps

Do steps 1 to 3 together. Between switching the Bungie app and finishing step 3, sign-in on the site won't work.

1. **Switch the Bungie app to Confidential.** Open your app at bungie.net/en/Application, set OAuth Client Type to Confidential, save, and copy the client secret it shows. The client_id stays the same.

2. **Deploy the worker.** In PowerShell, from the repo folder:

   ```powershell
   npm install -g wrangler
   wrangler login
   cd worker
   wrangler secret put BUNGIE_CLIENT_ID
   wrangler secret put BUNGIE_CLIENT_SECRET
   wrangler secret put BUNGIE_API_KEY
   wrangler deploy
   cd ..
   ```

   Each `secret put` asks you to paste the value. `wrangler deploy` prints the worker address, something like `https://d2rc-signin.yourname.workers.dev`.

3. **Point the site at it and redeploy.**

   ```powershell
   "https://d2rc-signin.yourname.workers.dev".Trim() | gh secret set BUNGIE_TOKEN_PROXY
   gh workflow run "Deploy site"
   ```

4. **Sign out and sign in once** on the site. From then on you stay signed in for up to 90 days of use.

## If your site address changes

Edit `ALLOWED_ORIGIN` in `wrangler.toml` and run `wrangler deploy` again.

## To turn it off

Run `gh secret delete BUNGIE_TOKEN_PROXY`, then `gh workflow run "Deploy site"`, and set the Bungie app back to Public. The site goes back to the hourly renewal.

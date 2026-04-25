# Optional: live.andrewdiaz.io custom domain setup

**Status**: OPTIONAL — `panopticon-live.vercel.app` is the canonical demo URL and works publicly. This file documents the steps to ALSO add `live.andrewdiaz.io` as a name-neutral branded URL.

## Why this is optional

After the prod deploy on 2026-04-25 ~02:51 EDT, Vercel auto-aliased `panopticon-live.vercel.app` (the unscoped subdomain) to the deployment. That URL is:

- Publicly accessible (no SSO redirect)
- Bound to every future prod deploy (the alias persists)
- Already printed on the B5 closing card

So we DON'T need a custom domain for v1 submission. The custom-domain setup below is purely for personal-branding aesthetics ("live.andrewdiaz.io" reads cleaner than "panopticon-live.vercel.app").

## If you want live.andrewdiaz.io anyway

The Vercel side is already done — I added the domain to the project (`mcp__vercel__addProjectDomain`). It came back `verified: true` because Vercel detected your apex `andrewdiaz.io` is already managed in the same team. But Vercel doesn't host your DNS — GoDaddy does (per `dig +short NS andrewdiaz.io`: `ns55.domaincontrol.com.` / `ns56.domaincontrol.com.`). So the actual DNS record needs to be added at GoDaddy.

### Steps (yours)

1. Log in to **GoDaddy.com**
2. Go to **My Products → Domains → andrewdiaz.io → DNS** (or **Manage DNS**)
3. Click **Add Record** (or **Add New Record**)
4. Configure:
   - **Type**: `CNAME`
   - **Name** (or **Host**): `live`
   - **Value** (or **Points to**): `cname.vercel-dns.com.` (note the trailing dot)
   - **TTL**: 1 hour (or default)
5. **Save**
6. Wait ~5–15 minutes for DNS propagation (GoDaddy is usually fast)
7. Verify with: `dig +short live.andrewdiaz.io` — should return Vercel IPs
8. Visit `https://live.andrewdiaz.io` in a browser — should serve the PANOPTICON LIVE dashboard

### Alternative: A record (if CNAME doesn't work)

Some registrars don't allow CNAMEs at certain subdomains. If GoDaddy rejects the CNAME, use TWO A records instead:

- Type: `A` | Name: `live` | Value: `216.150.1.1`
- Type: `A` | Name: `live` | Value: `216.150.16.1`

(These are Vercel's recommended IPv4 addresses for the apex per `mcp__vercel__getDomainConfig` on andrewdiaz.io.)

## If you want to ALSO update the B5 closing card to show live.andrewdiaz.io

After DNS propagates and the URL works:

1. Edit `demo-presentation/remotion/src/compositions/B5Closing.tsx` line ~135:
   ```tsx
   panopticon-live.vercel.app  →  live.andrewdiaz.io
   ```
2. Re-render: `cd demo-presentation/remotion && ./node_modules/.bin/remotion render b5-closing out/b5-closing.mp4`
3. The DaVinci composite uses the new MP4 automatically.

## If you want to remove the custom domain later

```
mcp__vercel__removeProjectDomain (projectId=prj_wYNC4mSDtJFsckhW9cFTS5JPfZHb, domain=live.andrewdiaz.io)
```

OR via Vercel dashboard: project → Settings → Domains → ⋯ → Remove.

The CNAME at GoDaddy can stay (harmless once Vercel no longer claims it; would just resolve to Vercel without serving anything).

---

**Bottom line**: skip this entirely if you just want to ship the demo. `panopticon-live.vercel.app` is your URL.

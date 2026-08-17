# 🌸 Jasmine Store — Complete Launch, Monetization & AI Automation Guide

Everything below is **free of cost** and works with the files already in this project:

| File | Purpose |
|---|---|
| `index.html` | The complete website (single file, logo embedded) |
| `server.py` | 🆕 **Dynamic server** — password-protected admin panel at `/admin` that updates `index.html` live (zero dependencies, pure Python) |
| `templates/admin_login.html` | 🆕 Login page for the admin panel |
| `templates/admin_panel.html` | 🆕 The live admin panel UI (Method 1: form · Method 2: products.json) |
| `admin.html` | Offline Product Manager (for the static GitHub Pages workflow) |
| `products.json` | Master product list (the single source of truth) |
| `tools/update_products.py` | Injects `products.json` into `index.html` + validates everything |
| `.github/workflows/deploy.yml` | Auto-rebuild + auto-deploy on every change (GitHub Pages) |

---

# PART 0 — 🆕 Dynamic Admin Panel (password-protected)

Run the site with a real backend so `index.html` updates itself:

```bash
ADMIN_PASSWORD="your-secret-password" python3 server.py     # http://localhost:8000
```

- **Website** → `http://<host>/`
- **Admin panel** → `http://<host>/admin` (asks for your password)

### Two ways to update index.html — both live instantly:

**METHOD 1 — The form.** Log in at `/admin`, fill the product form, click
*"Save → publish to index.html"*. The server validates the product, saves it to
`products.json` AND rewrites the `PRODUCTS` array inside `index.html` in the same
second. Edit ✏️ and delete ✕ buttons work the same way.

**METHOD 2 — products.json.** Three options, all end with `index.html` re-injected:
1. `/admin` → **⬆️ Upload products.json** (replaces the whole catalog)
2. Edit `products.json` on the server directly → click **🔄 Re-inject** in the panel
3. Command line: `python3 tools/update_products.py`

### Security built in
- Session cookies (HttpOnly, random 256-bit, 8-hour expiry)
- Constant-time password check, 5 failed logins → 5-minute IP lockout
- Every write makes an automatic `index.html.bak` backup
- Same validation engine on every path — a broken product can never reach the live site

### Free hosting for the DYNAMIC version
GitHub Pages is static-only, so for the live admin panel use one of these free tiers:
| Host | Free plan | How |
|---|---|---|
| **PythonAnywhere** | ✅ forever-free | Upload files → Web tab → manual config → point to `server.py` |
| **Render.com** | ✅ free web service | Connect repo → Start command: `python3 server.py` → add `ADMIN_PASSWORD` env var |
| **Replit** | ✅ free | Import repo → Run `python3 server.py` |

> 💡 **Hybrid setup (best of both):** host the public site free on GitHub Pages, and
> run `server.py` only when *you* are adding products (locally or on Replit) — then
> commit the updated `products.json`/`index.html` and Pages redeploys automatically.
> ⚠️ Always set a strong `ADMIN_PASSWORD` env var before exposing `/admin` to the internet.

---

# PART 1 — Deploy the Website 100% Free

## ⭐ Option A: GitHub Pages (recommended — enables full automation)

**Cost: $0 forever. You get `https://yourname.github.io/jasmine-store/`**

1. Create a free account at **github.com**.
2. Click **➕ → New repository** → name it `jasmine-store` → Public → Create.
3. Click **uploading an existing file** and drag in ALL project files/folders:
   `index.html`, `admin.html`, `products.json`, `tools/`, `.github/`
   *(To upload the `.github` folder you may need "Add file → Create new file" and type `.github/workflows/deploy.yml` as the filename, then paste its contents.)*
4. Commit the upload.
5. Go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
6. Wait ~1 minute. Your site is live at:
   `https://YOUR-USERNAME.github.io/jasmine-store/`

From now on, **any change you commit automatically redeploys the site** thanks to the included workflow.

## Option B: Netlify Drop (fastest — 60 seconds, no account needed to test)

1. Go to **app.netlify.com/drop**
2. Drag the folder containing `index.html` onto the page.
3. Done — you get a live URL like `https://jasmine-store.netlify.app` (free account lets you rename it).

## Option C: Cloudflare Pages / Vercel

Both free: connect the same GitHub repo → click Deploy → done. Useful later if you want Cloudflare's free analytics.

## 🇵🇰 Free custom domain feel (optional)

- Free subdomains: `jasmine-store.netlify.app`, `.github.io`, `.pages.dev` — all fine to start.
- When you earn your first commissions, buy `jasminestore.pk` (~Rs. 2,500/yr) and attach it free on any of the hosts above.

---

# PART 2 — Post REAL Affiliate Products (step-by-step)

## Step 1: Join the affiliate programs (all free)

### 🟠 Daraz (best starting point in Pakistan — instant approval)
1. Go to the **Daraz Affiliate Program**: `https://www.daraz.pk/affiliate/` (runs on partner networks like Involve Asia — sign up at `involve.asia`, it's free).
2. Register → add your website URL (your new GitHub Pages link) → get approved.
3. In the dashboard, paste any Daraz product URL → it generates your **tracked deep link**.
4. Commissions: typically **3–12%** depending on category, paid via bank transfer/Payoneer.

### 🔴 AliExpress Portals
1. Sign up free at **portals.aliexpress.com**.
2. Add your website URL under Ad Zones.
3. Use the **Deep Link tool**: paste any AliExpress product URL → get an `s.click.aliexpress.com/e/_XXXX` tracked link.
4. Commissions: **3–9%**, paid monthly (bank/Payoneer, $16 minimum payout).

### 🟡 Amazon Associates
1. Sign up free at **affiliate-program.amazon.com**.
2. ⚠️ Rule: you must make **3 qualifying sales within 180 days** or reapply (easy — just share links honestly).
3. Use **SiteStripe** (toolbar shown on every Amazon page once logged in) → "Get Link" → copy your `amzn.to/XXXX` short link.
4. Note for Pakistan: receive payments via **Payoneer** (free account) as the bank option.

## Step 2: Add products with the Admin Panel (no coding!)

1. Open **`admin.html`** in your browser (double-click it, or visit `/admin.html` on your live site).
2. For each product you found on Daraz/AliExpress/Amazon:
   - Copy the **title & details** from the product page → click **"✨ Copy AI prompt"** → paste into free ChatGPT/Gemini → get an elegant on-brand title + description back.
   - **Image**: right-click the product photo → *Copy image address* → paste into the Image URL field.
   - **Prices**: enter the deal price and the original (crossed-out) price.
   - **Affiliate link**: paste YOUR tracked link from Step 1 (never the plain product URL — plain links earn you nothing!).
3. Click **Add product** → repeat.
4. Click **⬇️ Download products.json**.

## Step 3: Publish

**If you deployed with GitHub Pages (Option A):**
1. On github.com, open your repo → click `products.json` → ✏️ Edit → paste the new JSON → **Commit**.
2. The GitHub Action automatically rebuilds `index.html` and redeploys. **Live in ~60 seconds.** ✅

**If you deployed with Netlify Drop:**
```bash
python3 tools/update_products.py     # injects products.json into index.html
```
Then drag the folder onto Netlify Drop again.

> The script validates everything: missing fields, price ≥ original price, non-https links, duplicate IDs — and warns about leftover EXAMPLE links, so you can't accidentally publish a broken card.

## ⚖️ Compliance checklist (protects your accounts)

- ✅ Affiliate disclosure — already in the site footer (required by all 3 programs).
- ✅ `rel="sponsored nofollow"` on buy buttons — already implemented.
- ⚠️ Amazon-specific: do NOT show stale Amazon prices. Either update prices regularly or write "Check price on Amazon" style copy. Never fake ratings for Amazon products — use the real ones.
- ⚠️ Never say "Amazon partner pricing guaranteed" etc. Keep the disclosure honest.

---

# PART 3 — Use AI to Automate the Site & Earn Commissions

## Level 1 — AI as your content team (start today, $0)

Free tools: **ChatGPT** (chat.openai.com), **Gemini** (gemini.google.com), **Claude** (claude.ai).

**a) Product copy at scale** — the admin panel's "✨ AI prompt" button generates this automatically, but the master version:

```
You are the copywriter for "Jasmine Store" (tagline: "Affordable elegance for
everyday living"; voice: elegant, feminine, warm, never salesy).
I will paste raw product data for N products. For EACH, return JSON with:
title (max 8 words), description (max 20 words, benefit-driven).
Return a single JSON array only.
```
Paste 10 raw product listings → get 10 polished entries → paste into `products.json`.

**b) Weekly product research:**
```
Act as an e-commerce trend researcher. List 10 trending, giftable,
elegant/feminine products under $25 on AliExpress right now in home décor,
beauty and jewellery that a curated deals site should feature this week.
For each: product keyword to search, why it's trending, target buyer.
```

**c) Free-traffic content (this is what actually earns commissions):**
```
Write a 60-second Instagram Reel script + caption + 20 hashtags for this
product: [paste product]. Hook in first 2 seconds. Elegant, feminine tone.
CTA: "Link on our site — Jasmine Store".
```
Post 1 Reel/TikTok per day per product → each links to your site → clicks → commissions. AI writes every script; Canva (free) makes the visuals.

**d) The Jasmine Edit newsletter:** collect emails via your form (connect it to **Brevo** — free for 300 emails/day) and let AI draft the weekly email from your `products.json`.

## Level 2 — Semi-automated pipeline (already built for you ✅)

Your repo now works like this:

```
find product → AI writes copy → paste into admin.html → download products.json
      → commit to GitHub → Action rebuilds & redeploys automatically
```

Total time per product: **~3 minutes**, zero code.

## Level 3 — Fully automated product feed (when you're approved)

Once your AliExpress Portals account is active, request **API access** (free) at portals.aliexpress.com → API Settings. Then a scheduled GitHub Action can refresh your catalog **while you sleep**:

```python
# tools/fetch_aliexpress.py  (sketch — requires your API key + approval)
# 1. Call aliexpress.affiliate.product.query with keywords like
#    "ceramic vase", "silk pillowcase", sorted by commission rate
# 2. For each result: title, price, image, YOUR tracked promotion link
# 3. (Optional) pass titles through a free AI API to rewrite in brand voice
# 4. Write products.json  →  the deploy workflow does the rest
```

Add a schedule to `.github/workflows/deploy.yml`:
```yaml
on:
  schedule:
    - cron: "0 6 * * 1"   # every Monday 6:00 UTC — fresh deals weekly
```

**Honest notes (so you don't waste time):**
- AliExpress API approval usually needs a live site with some traffic — launch first, apply after 2–4 weeks.
- Amazon's Product Advertising API unlocks only **after your first 3 sales** — until then use SiteStripe links manually.
- Daraz/Involve Asia provides deep-link generation; bulk feeds vary by account level.
- No AI can *guarantee* commissions. The proven loop is: **consistent traffic (Reels/TikTok/Pinterest/SEO) → honest curation → clicks → sales.** AI removes 90% of the labor; it doesn't remove the need for traffic.

## 📈 Your first-30-days plan

| Week | Action |
|---|---|
| 1 | Deploy to GitHub Pages · join Daraz affiliate + AliExpress Portals · replace all 12 EXAMPLE products with real linked ones via `admin.html` |
| 2 | Apply for Amazon Associates · create Instagram + TikTok + Pinterest for "Jasmine Store" · post 1 AI-scripted Reel daily |
| 3 | Connect newsletter form to Brevo · send first "Jasmine Edit" · add 12 more products |
| 4 | Check affiliate dashboards for first clicks/commissions · double down on whichever platform converts · apply for AliExpress API access |

---

*Every price/commission figure above is typical at the time of writing — always confirm current rates in each affiliate dashboard.*

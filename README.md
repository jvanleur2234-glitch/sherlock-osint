# Sherlock OSINT Suite

> Find anyone across 500+ social platforms — by username, phone, or IP address.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow)
![Python 3](https://img.shields.io/badge/Python-3.12+-blue)
![Platforms](https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-green)

## What It Does

Sherlock OSINT Suite combines three powerful OSINT tools into one:

| Tool | Searches | Speed |
|------|----------|-------|
| **Maigret** (Sherlock fork) | 500+ social platforms by username | ~50s for full scan |
| **GhostTrack** | Phone number info (carrier, region, validity) | Instant |
| **IPGeo** | IP address location (city, ISP, coordinates) | Instant |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/jvanleur2234-glitch/sherlock-osint.git
cd sherlock-osint

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API server
python3 api.py

# 4. Open index.html in your browser
# (or serve it with: python3 -m http.server 8000)
```

## API Endpoints

```bash
# Scan a username (async - returns job_id)
curl -X POST http://localhost:5012/api/sherlock/scan \
  -H "Content-Type: application/json" \
  -d '{"type":"username","value":"elonmusk"}'

# Check job status
curl http://localhost:5012/api/sherlock/status/<job_id>

# Lookup phone (instant)
curl -X POST http://localhost:5012/api/sherlock/scan \
  -H "Content-Type: application/json" \
  -d '{"type":"phone","value":"+14155551212"}'

# Lookup IP (instant)
curl -X POST http://localhost:5012/api/sherlock/scan \
  -H "Content-Type: application/json" \
  -d '{"type":"ip","value":"8.8.8.8"}'
```

## Pricing Tiers

| Tier | Price | Includes |
|------|-------|----------|
| **Free** | $0 | 10 scans/day, basic results |
| **Pro** | $19/mo | Unlimited scans, full reports, export CSV |
| **Agency** | $49/mo | Everything + API access + whitelist features |

**Setup fee:** $49 one-time (required — establishes value)

## Example Results

**Username scan on "zuck":** Found 175 accounts across Facebook, Instagram, Twitter/X, LinkedIn, GitHub, and 170+ other platforms in 47 seconds.

**Phone lookup on +14155551212:** Valid ✅ | Region: San Francisco, CA | Timezone: America/Los_Angeles

**IP lookup on 8.8.8.8:** Google LLC | Ashburn, Virginia, United States | Lat: 39.03, Lon: -77.5

## Use Cases

- **Journalists & Researchers** — verify online identities
- **Recruiters** — check candidate social presence
- **Security Researchers** — footprinting and OSINT
- **Law Enforcement** — digital forensics support
- **Dating App Verification** — confirm who someone says they are

## Live Demo

Try it now: **[https://josephv.zo.space/sherlock](https://josephv.zo.space/sherlock)**

## Tech Stack

- **Backend:** Python 3 + Flask API
- **Scanning:** Maigret (507 sites), GhostTrack, IPGeo
- **Frontend:** Vanilla HTML/CSS/JS (no framework dependencies)
- **Deploy:** Runs anywhere — laptop, server, or Raspberry Pi

## Legal Notice

**For authorized use only.** This tool is provided for ethical OSINT research, security testing, and legitimate identity verification. Unauthorized scanning of websites may violate their Terms of Service. You are responsible for complying with all applicable laws.

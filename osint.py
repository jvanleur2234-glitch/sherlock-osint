#!/usr/bin/env python3
"""
Sherlock OSINT Suite — Combines Sherlock (Maigret) + GhostTrack
Usage:
  python3 osint.py phone +14155551212
  python3 osint.py ip 8.8.8.8
  python3 osint.py username elonmusk
"""
import sys, os, re, csv, io, json, subprocess, uuid, requests
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

# ── GhostTrack phone tracker ─────────────────────────────────
def track_phone(number):
    try:
        n = phonenumbers.parse(number, None)
        if not phonenumbers.is_valid_number(n):
            return {"error": "Invalid phone number"}
        return {
            "number": number,
            "region": geocoder.description_for_number(n, "en"),
            "carrier": carrier.name_for_number(n, "en"),
            "timezone": str(timezone.time_zones_for_number(n)),
            "valid": phonenumbers.is_valid_number(n),
            "type": str(phonenumbers.number_type(n)).split(".")[-1],
        }
    except Exception as e:
        return {"error": str(e)}

# ── GhostTrack IP tracker ─────────────────────────────────────
def track_ip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,isp,org,as,query", timeout=10)
        d = r.json()
        if d.get("status") == "fail":
            return {"error": d.get("message", "IP lookup failed")}
        return {
            "ip": d["query"],
            "city": d["city"],
            "region": d["regionName"],
            "country": d["country"],
            "isp": d["isp"],
            "org": d["org"],
            "lat": d["lat"],
            "lon": d["lon"],
            "zip": d.get("zip", ""),
        }
    except Exception as e:
        return {"error": str(e)}

# ── Sherlock (Maigret) username scan ─────────────────────────
def scan_username(username, timeout_sec=60):
    job_id = str(uuid.uuid4())[:8]
    out_dir = f"/home/workspace/sherlock-app/results/{job_id}"
    os.makedirs(out_dir, exist_ok=True)
    
    cmd = ["maigret", username, "-T", "-C", "--folderoutput", out_dir]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
        csv_file = f"{out_dir}/report_{username}.csv"
        if os.path.exists(csv_file):
            accounts = []
            with open(csv_file) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("exists") == "Claimed":
                        accounts.append({
                            "site": row.get("name", ""),
                            "url": row.get("url_user", ""),
                            "status": "Claimed",
                            "http_status": row.get("http_status", ""),
                        })
            return {"username": username, "job_id": job_id, "found": len(accounts), "accounts": accounts}
        return {"error": "No CSV output"}
    except subprocess.TimeoutExpired:
        return {"error": f"Timeout after {timeout_sec}s", "job_id": job_id}
    except Exception as e:
        return {"error": str(e)}

# ── CLI ──────────────────────────────────────────────────────
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "phone" and len(sys.argv) > 2:
        print(json.dumps(track_phone(sys.argv[2]), indent=2))
    elif cmd == "ip" and len(sys.argv) > 2:
        print(json.dumps(track_ip(sys.argv[2]), indent=2))
    elif cmd == "username" and len(sys.argv) > 2:
        print(json.dumps(scan_username(sys.argv[2]), indent=2))
    else:
        print(__doc__)

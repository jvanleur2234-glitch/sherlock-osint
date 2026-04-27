#!/usr/bin/env python3
"""
Sherlock OSINT API — Fast, non-blocking wrapper for all 3 tools.
POST /api/sherlock/scan  {"type": "username|phone|ip", "value": "..."}
GET  /api/sherlock/status/:jobId
"""
import sys, os, csv, json, subprocess, uuid, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import requests
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

BASE = "/home/workspace/sherlock-app/results"
os.makedirs(BASE, exist_ok=True)

# ── Tools ────────────────────────────────────────────────
def track_phone(number):
    try:
        n = phonenumbers.parse(number, None)
        if not phonenumbers.is_valid_number(n):
            return {"found": False, "error": "Invalid phone number"}
        return {
            "found": True,
            "number": number,
            "region": geocoder.description_for_number(n, "en"),
            "carrier": carrier.name_for_number(n, "en") or "Unknown",
            "timezone": str(timezone.time_zones_for_number(n)),
            "valid": phonenumbers.is_valid_number(n),
            "type": str(phonenumbers.number_type(n)).split(".")[-1],
        }
    except Exception as e:
        return {"found": False, "error": str(e)}

def track_ip(ip):
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,isp,org,query",
            timeout=10
        )
        d = r.json()
        if d.get("status") == "fail":
            return {"found": False, "error": d.get("message", "IP lookup failed")}
        return {"found": True, "ip": d["query"], "city": d["city"], "region": d["regionName"],
                "country": d["country"], "isp": d["isp"], "org": d["org"],
                "lat": d["lat"], "lon": d["lon"], "zip": d.get("zip","")}
    except Exception as e:
        return {"found": False, "error": str(e)}

def scan_username(username, timeout=60):
    job_id = str(uuid.uuid4())[:8]
    out_dir = f"{BASE}/{job_id}"
    os.makedirs(out_dir, exist_ok=True)

    # Background the maigret scan
    log_file = f"{out_dir}/log.txt"
    cmd = f"cd {out_dir} && maigret {username} -T -C --folderoutput . > log.txt 2>&1; echo $? > .exitcode"
    
    with open(f"{out_dir}/status.json", "w") as f:
        json.dump({"job_id": job_id, "type": "username", "value": username, "status": "running", "found": 0, "accounts": []}, f)
    
    subprocess.Popen(cmd, shell=True)
    return job_id

def get_status(job_id):
    job_dir = f"{BASE}/{job_id}"
    status_file = f"{job_dir}/status.json"
    
    if not os.path.exists(job_dir):
        return {"error": "Job not found"}
    
    if os.path.exists(f"{job_dir}/.exitcode"):
        exitcode_file = f"{job_dir}/.exitcode"
    else:
        exitcode_file = None
    
    # Read maigret CSV if exists
    csv_files = [f for f in os.listdir(job_dir) if f.startswith("report_") and f.endswith(".csv")]
    accounts = []
    if csv_files:
        with open(os.path.join(job_dir, csv_files[0])) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("exists") == "Claimed":
                    accounts.append({
                        "site": row.get("name",""),
                        "url": row.get("url_user",""),
                        "http_status": row.get("http_status",""),
                    })
        status = "done"
    elif exitcode_file:
        status = "done"
    else:
        status = "running"
    
    result = {
        "job_id": job_id,
        "status": status,
        "found": len(accounts),
        "accounts": accounts,
    }
    
    # Add phone/ip results if stored
    if os.path.exists(status_file):
        with open(status_file) as f:
            stored = json.load(f)
            if stored.get("type") in ("phone", "ip"):
                result.update(stored)
    
    return result

# ── HTTP API ──────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/sherlock/scan":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
            except:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            
            scan_type = data.get("type")
            value = data.get("value", "").strip()
            
            if scan_type == "phone":
                result = track_phone(value)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            elif scan_type == "ip":
                result = track_ip(value)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            elif scan_type == "username":
                job_id = scan_username(value)
                self.send_response(202)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"job_id": job_id, "status": "running", "message": "Scan started"}).encode())
                return
            
            else:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "type must be username, phone, or ip"}).encode())
                return
        
        self.send_response(404)
        self.end_headers()
    
    def do_GET(self):
        if self.path.startswith("/api/sherlock/status/"):
            job_id = self.path.split("/")[-1]
            result = get_status(job_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            return
        
        self.send_response(404)
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 5012
    print(f"Sherlock OSINT API running on port {port}")
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

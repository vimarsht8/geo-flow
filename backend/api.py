# api.py

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import dns.resolver
import requests
from typing import List

app = FastAPI()

# serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# in-memory storage
events: List[dict] = []

# tracker classification
TRACKER_KEYWORDS = {
    "ads": ["doubleclick", "adservice", "adsystem", "criteo"],
    "analytics": ["analytics", "google-analytics", "gtag"],
    "cdn": ["cloudflare", "akamai", "fastly"]
}

# -------------------------------
# Helpers
# -------------------------------

def resolve_ip(domain: str):
    try:
        return dns.resolver.resolve(domain, "A")[0].to_text()
    except:
        return None

def geo_lookup(ip: str):
    if not ip:
        return {}
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,city,org"
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

def calculate_risk(category: str, country: str):
    score = 0

    if category == "ads":
        score += 3
    elif category == "analytics":
        score += 2
    elif category == "cdn":
        score += 1

    if country != "India":
        score += 1

    if score >= 4:
        return "HIGH"
    elif score >= 2:
        return "MEDIUM"
    else:
        return "LOW"

def calculate_site_privacy_score(events):
    score = 100
    for e in events:
        if e.get("risk") == "HIGH":
            score -= 10
        elif e.get("risk") == "MEDIUM":
            score -= 5
    return max(score, 0)

# -------------------------------
# Routes
# -------------------------------

@app.post("/track")
def track(payload: dict):
    page = payload.get("page")
    resources = payload.get("resources", [])
    timestamp = payload.get("timestamp")

    domains = set([page] + resources)

    for domain in domains:
        ip = resolve_ip(domain)
        geo = geo_lookup(ip)

        category = "first-party"
        for cat, keys in TRACKER_KEYWORDS.items():
            if any(k in domain for k in keys):
                category = cat

        risk = calculate_risk(category, geo.get("country", "Unknown"))

        events.append({
            "domain": domain,
            "category": category,
            "risk": risk,
            "country": geo.get("country", "Unknown"),
            "city": geo.get("city", "Unknown"),
            "org": geo.get("org", "Unknown"),
            "timestamp": timestamp
        })

    return {"status": "ok"}

@app.get("/events")
def get_events():
    return events

@app.get("/privacy-score")
def privacy_score():
    return {
        "score": calculate_site_privacy_score(events)
    }

@app.get("/export")
def export_data():
    return JSONResponse(content=events)

@app.get("/dashboard")
def dashboard():
    return FileResponse("templates/dashboard.html")

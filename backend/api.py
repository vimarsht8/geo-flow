# api.py

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from datetime import datetime

import dns.resolver
import requests

app = FastAPI(title="GeoFlow Backend")

# -------------------------------
# Static files (CSS / JS)
# -------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------------------
# In-memory storage
# -------------------------------
events: List[dict] = []

# -------------------------------
# Tracker classification
# -------------------------------
TRACKER_KEYWORDS = {
    "ads": ["doubleclick", "adservice", "adsystem"],
    "analytics": ["analytics", "google-analytics", "gtag"],
    "cdn": ["cloudflare", "akamai", "fastly"]
}

# -------------------------------
# Utils
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


def calculate_risk(category: str):
    if category == "ads":
        return "HIGH"
    if category == "analytics":
        return "MEDIUM"
    return "LOW"


def calculate_site_privacy_score(events):
    score = 100
    for e in events:
        if e["risk"] == "HIGH":
            score -= 10
        elif e["risk"] == "MEDIUM":
            score -= 5
    return max(score, 0)

# -------------------------------
# ROUTES
# -------------------------------

# 🔹 Landing Page (Friend UI)
@app.get("/")
def landing_page():
    return FileResponse("templates/landing.html")


# 🔹 Dashboard Page (Your UI)
@app.get("/dashboard")
def dashboard():
    return FileResponse("templates/dashboard.html")


# 🔹 Track endpoint (used by extension / demo)
@app.post("/track")
def track(payload: dict):
    page = payload.get("page")
    resources = payload.get("resources", [])
    timestamp = payload.get("timestamp", datetime.utcnow().isoformat())

    domains = set([page] + resources)

    for domain in domains:
        if not domain:
            continue

        ip = resolve_ip(domain)
        geo = geo_lookup(ip)

        category = "first-party"
        for cat, keys in TRACKER_KEYWORDS.items():
            if any(k in domain for k in keys):
                category = cat

        risk = calculate_risk(category)

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


# 🔹 Dashboard data
@app.get("/events")
def get_events():
    return events


# 🔹 Privacy score
@app.get("/privacy-score")
def privacy_score():
    return {
        "score": calculate_site_privacy_score(events)
    }

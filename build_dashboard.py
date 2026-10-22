#!/usr/bin/env python3
"""Master script: runs all collectors, dedupes, filters paywalls, adds scores, writes HTML."""

import json
import re
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from collectors import (
    college_baseball,
    college_basketball,
    college_football,
    current_events,
    daily_story,
    entertainment,
    letterboxd,
    mlb,
    movie_releases,
    nba,
    nfl,
    quote,
    scores,
)
from collectors.base import parse_date

CONFIG_FILE = Path("sources.json")
TEMPLATE_FILE = Path("template.html")
OUTPUT_FILE = Path("dashboard.html")


# ── Paywall blocklist ──────────────────────────────────────────────
PAYWALL_DOMAINS = {
    "nytimes.com",
    "wsj.com",
    "washingtonpost.com",
    "theathletic.com",
    "bloomberg.com",
    "ft.com",
    "economist.com",
    "newyorker.com",
    "thetimes.co.uk",
    "telegraph.co.uk",
    "latimes.com",
    "bostonglobe.com",
    "seattletimes.com",
    "chicagotribune.com",
    "sfchronicle.com",
    "denverpost.com",
    "dallasnews.com",
    "star-telegram.com",
    "theatlantic.com",
    "wired.com",
    "businessinsider.com",
    "hbr.org",
    "science.org",
    "nature.com",
    "foreignaffairs.com",
}


def is_paywalled(item):
    """Return True if the item's link points to a known paywalled domain."""
    link = item.get("link", "")
    if not link:
        return False
    try:
        domain = urllib.parse.urlparse(link).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain in PAYWALL_DOMAINS
    except (ValueError, AttributeError):
        return False


# ── Global dedupe helper ───────────────────────────────────────────
def normalize_title(title):
    """Lowercase, strip punctuation, collapse whitespace for comparison."""
    t = title.lower()
    t = re.sub(r"[^\w\s]", "", t)
    return re.sub(r"\s+", " ", t).strip()


# ── Filtering helper (paywall + date + dedupe) ─────────────────────
def filter_stream(items, cutoff, seen):
    """Apply paywall, date, and global dedupe filters to a list of items."""
    clean = []
    for it in items:
        if is_paywalled(it):
            continue
        dt = parse_date(it.get("published"))
        if dt and dt < cutoff:
            continue
        key = normalize_title(it["title"])
        if key in seen:
            continue
        seen.add(key)
        clean.append(it)
    return clean


# ── Main build ─────────────────────────────────────────────────────
def build():
    cfg = json.loads(CONFIG_FILE.read_text())
    global_max = cfg["dashboard"]["max_items_per_section"]
    window = timedelta(hours=cfg["dashboard"]["time_window_hours"])
    cutoff = datetime.now(timezone.utc) - window

    all_sections = []
    for collector in (
        quote,
        college_football,
        college_basketball,
        college_baseball,
        nba,
        nfl,
        mlb,
        entertainment,
        movie_releases,
        current_events,
        daily_story,
        letterboxd,
    ):
        print(f"Running collector: {collector.__name__}")
        result = collector.collect()
        print(f"  -> returned {len(result)} sections")
        all_sections.extend(result)

    print(f"Total sections collected: {len(all_sections)}")

    seen = set()
    output = []
    for sec in all_sections:
        # Main items: paywall + date + dedupe
        clean = filter_stream(sec["items"], cutoff, seen)

        # Per-section sort mode
        sort_mode = sec.get("sort", "chronological")
        if sort_mode == "chronological":
            clean.sort(
                key=lambda it: parse_date(it.get("published"))
                or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
        # else: leave in feed order (Google News relevance)

        # Injury items (optional per-section)
        injury_clean = filter_stream(sec.get("injury_items", []), cutoff, seen)
        injury_clean.sort(
            key=lambda it: parse_date(it.get("published"))
            or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )

        # Next-game lookup for team-specific sections
        game = None
        if "espn" in sec:
            e = sec["espn"]
            print(f"  Fetching game: {sec['name']} with params {e}")
            game = scores.next_game(e["sport"], e["league"], e["team_id"])
            print(f"  Got game: {game}")

        # Use section-specific max_items if provided, otherwise global default
        section_max = sec.get("max_items", global_max)

        output.append({
            "name": sec["name"],
            "icon": sec.get("icon", ""),
            "game": game,
            "items": clean[:section_max],
            "injury_items": injury_clean[:5],
        })

    return {
        "title": cfg["dashboard"]["title"],
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "sections": output,
    }


# ── Render HTML ────────────────────────────────────────────────────
def render(data):
    html = TEMPLATE_FILE.read_text()
    payload = json.dumps(data, ensure_ascii=False)
    payload = payload.replace("</script>", "<\\/script>")
    return html.replace(
        "<script>",
        f"<script>window.__DASHBOARD_DATA__ = {payload};</script>\n<script>",
        1,
    )


if __name__ == "__main__":
    print("Building dashboard...")
    data = build()
    OUTPUT_FILE.write_text(render(data), encoding="utf-8")
    print(f"Done -> {OUTPUT_FILE}")
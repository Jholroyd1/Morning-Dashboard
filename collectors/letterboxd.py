"""Pick a random high-rated film from your Letterboxd diary via RSS."""

import os
import random
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from dotenv import load_dotenv

from .base import SSL_CTX, USER_AGENT

load_dotenv()
LETTERBOXD_USERNAME = os.getenv("LETTERBOXD_USERNAME", "YOUR_USERNAME_HERE")

RSS_URL = f"https://letterboxd.com/{LETTERBOXD_USERNAME}/rss/"

# Minimum rating to include (4 stars or better)
MIN_RATING = 4.0

# Letterboxd uses a custom XML namespace
NAMESPACES = {
    "letterboxd": "https://letterboxd.com",
    "tmdb": "https://themoviedb.org",
}


def _fetch_feed():
    """Fetch and parse the Letterboxd RSS feed."""
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        print(f"  [letterboxd] http error -> {e}")
        return None
    except urllib.error.URLError as e:
        print(f"  [letterboxd] url error -> {e}")
        return None
    except TimeoutError as e:
        print(f"  [letterboxd] timeout -> {e}")
        return None

    try:
        return ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"  [letterboxd] parse error -> {e}")
        return None


def _parse_rating(item):
    """Extract the member rating as a float, or None if unrated."""
    rating_el = item.find("letterboxd:memberRating", NAMESPACES)
    if rating_el is None or not rating_el.text:
        return None
    try:
        return float(rating_el.text)
    except ValueError:
        return None


def _parse_year(item):
    """Extract the film year as a string, or empty string if missing."""
    year_el = item.find("letterboxd:filmYear", NAMESPACES)
    if year_el is None or not year_el.text:
        return ""
    return year_el.text.strip()


def _parse_film_title(item):
    """Extract the film title without the rating suffix."""
    title_el = item.find("letterboxd:filmTitle", NAMESPACES)
    if title_el is not None and title_el.text:
        return title_el.text.strip()

    # Fallback: strip rating glyphs from the main title
    title_el = item.find("title")
    if title_el is not None and title_el.text:
        title = title_el.text.strip()
        # Letterboxd appends rating like ", 2025 - ★★★★"
        if " - " in title:
            title = title.rsplit(" - ", 1)[0]
        return title
    return ""


def _parse_tmdb_id(item):
    """Extract the TMDB movie ID if present."""
    tmdb_el = item.find("tmdb:movieId", NAMESPACES)
    if tmdb_el is not None and tmdb_el.text:
        return tmdb_el.text.strip()
    return ""


def collect():
    """Return a section with a random 4+ star film from your Letterboxd diary."""
    root = _fetch_feed()
    if root is None:
        return [{
            "name": "Letterboxd Pick",
            "icon": "🎬",
            "sort": "chronological",
            "max_items": 1,
            "items": [],
        }]

    items = root.findall(".//item")

    # Filter to entries rated 4.0 or higher
    high_rated = []
    for item in items:
        rating = _parse_rating(item)
        if rating is not None and rating >= MIN_RATING:
            high_rated.append(item)

    if not high_rated:
        print(f"  [letterboxd] no entries rated {MIN_RATING}+ found")
        return [{
            "name": "Letterboxd Pick",
            "icon": "🎬",
            "sort": "chronological",
            "max_items": 1,
            "items": [],
        }]

    # Pick one at random
    pick = random.choice(high_rated)

    title = _parse_film_title(pick)
    year = _parse_year(pick)
    rating = _parse_rating(pick)
    tmdb_id = _parse_tmdb_id(pick)

    # Get the link to the diary entry
    link_el = pick.find("link")
    link = link_el.text.strip() if link_el is not None and link_el.text else ""

    # Build a formatted title with year
    display_title = f"{title} ({year})" if year else title

    # Build summary with rating and TMDB reference
    summary_parts = [f"Your rating: {'★' * int(rating)}"]
    if tmdb_id:
        summary_parts.append(f"TMDB ID: {tmdb_id}")
    summary = " · ".join(summary_parts)

    return [{
        "name": "Letterboxd Pick",
        "icon": "🎬",
        "sort": "chronological",
        "max_items": 1,
        "items": [{
            "title": display_title,
            "link": link,
            "published": "",
            "summary": summary,
            "source": "Letterboxd",
        }],
    }]
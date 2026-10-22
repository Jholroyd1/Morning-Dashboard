"""Collect major upcoming theatrical movie releases from TMDB using Discover."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

from dotenv import load_dotenv

from .base import SSL_CTX, USER_AGENT

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def _fetch_upcoming():
    """Fetch upcoming theatrical movies for the US using Discover endpoint."""
    today = date.today()
    future = today + timedelta(days=365)

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "region": "US",
        "release_date.gte": today.isoformat(),
        "release_date.lte": future.isoformat(),
        "with_release_type": "2|3",
        "sort_by": "popularity.desc",
        "page": "1",
    }
    url = f"{TMDB_DISCOVER}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  [movie releases] http error -> {e}")
    except urllib.error.URLError as e:
        print(f"  [movie releases] url error -> {e}")
    except TimeoutError as e:
        print(f"  [movie releases] timeout -> {e}")
    except json.JSONDecodeError as e:
        print(f"  [movie releases] json error -> {e}")
    return None


def _format_release_date(iso_str):
    """Convert '2026-11-15' to 'Nov 15, 2026'."""
    try:
        d = date.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return iso_str
    return d.strftime("%b %-d, %Y")


def _fetch_upcoming():
    """Fetch multiple pages of upcoming theatrical movies for the US."""
    today = date.today()
    future = today + timedelta(days=180)  # Look 180 days ahead

    all_results = []
    
    # Fetch up to 5 pages (100 movies) to get a broader pool
    for page in range(1, 6):
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "region": "US",
            "release_date.gte": today.isoformat(),
            "release_date.lte": future.isoformat(),
            "with_release_type": "2|3",  # Theatrical releases only
            "sort_by": "popularity.desc",  # Start with popularity
            "page": str(page),
        }
        url = f"{TMDB_DISCOVER}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
                data = json.loads(resp.read())
                if data and "results" in data:
                    all_results.extend(data["results"])
                else:
                    break  # No more results
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"  [movie releases] error on page {page} -> {e}")
            break

    return {"results": all_results}


"""Collect upcoming theatrical movie releases from TMDB (next 7 days)."""

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

from .base import SSL_CTX, USER_AGENT

TMDB_API_KEY = "2714dcf81372f70b7c703942330b67ce"

TMDB_DISCOVER = "https://api.themoviedb.org/3/discover/movie"


def _fetch_upcoming():
    """Fetch upcoming theatrical movies for the US in the next 7 days."""
    today = date.today()
    future = today + timedelta(days=7)

    all_results = []

    # Fetch up to 3 pages to make sure we catch all releases in the window
    for page in range(1, 4):
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "region": "US",
            "release_date.gte": today.isoformat(),
            "release_date.lte": future.isoformat(),
            "with_release_type": "2|3",
            "sort_by": "popularity.desc",
            "page": str(page),
        }
        url = f"{TMDB_DISCOVER}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
                data = json.loads(resp.read())
                if data and "results" in data:
                    all_results.extend(data["results"])
                else:
                    break
        except urllib.error.HTTPError as e:
            print(f"  [movie releases] http error page {page} -> {e}")
            break
        except urllib.error.URLError as e:
            print(f"  [movie releases] url error page {page} -> {e}")
            break
        except TimeoutError as e:
            print(f"  [movie releases] timeout page {page} -> {e}")
            break
        except json.JSONDecodeError as e:
            print(f"  [movie releases] json error page {page} -> {e}")
            break

    return {"results": all_results}


def _format_release_date(iso_str):
    """Convert '2026-11-15' to 'Nov 15, 2026'."""
    try:
        d = date.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return iso_str
    return d.strftime("%b %-d, %Y")


def collect():
    """Return a section with movies releasing in the next 7 days."""
    data = _fetch_upcoming()
    if not data or not data.get("results"):
        return [{
            "name": "Upcoming Movies",
            "icon": "🍿",
            "sort": "chronological",
            "max_items": 10,
            "items": [],
        }]

    today = date.today()
    items = []

    for movie in data["results"]:
        title = movie.get("title", "").strip()
        release_str = movie.get("release_date", "")

        if not title or not release_str:
            continue

        # Only keep movies that haven't released yet
        try:
            release_date = date.fromisoformat(release_str)
        except ValueError:
            continue
        if release_date < today:
            continue

        formatted_date = _format_release_date(release_str)

        items.append({
            "title": f"{formatted_date} — {title}",
            "link": f"https://www.themoviedb.org/movie/{movie.get('id', '')}",
            "published": release_str,
            "summary": movie.get("overview", "")[:200] or "Upcoming theatrical release",
            "source": "TMDB",
        })

    # Sort by date, soonest first
    items.sort(key=lambda x: x["published"])

    return [{
        "name": "Upcoming Movies",
        "icon": "🍿",
        "sort": "chronological",
        "max_items": 10,
        "items": items[:10],
    }]
"""Collect the daily quote from API Ninjas."""

import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

from .base import SSL_CTX, USER_AGENT

load_dotenv()
API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")

QUOTE_URL = "https://api.api-ninjas.com/v2/quoteoftheday"


def collect():
    """Return a section with today's quote."""
    req = urllib.request.Request(
        QUOTE_URL,
        headers={
            "X-Api-Key": API_NINJAS_KEY,
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  [quote] http error -> {e}")
        return [{
            "name": "Quote of the Day",
            "icon": "💭",
            "sort": "chronological",
            "items": [],
        }]
    except urllib.error.URLError as e:
        print(f"  [quote] url error -> {e}")
        return [{
            "name": "Quote of the Day",
            "icon": "💭",
            "sort": "chronological",
            "items": [],
        }]
    except TimeoutError as e:
        print(f"  [quote] timeout -> {e}")
        return [{
            "name": "Quote of the Day",
            "icon": "💭",
            "sort": "chronological",
            "items": [],
        }]
    except json.JSONDecodeError as e:
        print(f"  [quote] json error -> {e}")
        return [{
            "name": "Quote of the Day",
            "icon": "💭",
            "sort": "chronological",
            "items": [],
        }]

    # API returns an array with a single quote object
    if not data or not isinstance(data, list) or not data:
        return [{
            "name": "Quote of the Day",
            "icon": "💭",
            "sort": "chronological",
            "items": [],
        }]

    quote_obj = data[0]
    quote_text = quote_obj.get("quote", "").strip()
    author = quote_obj.get("author", "").strip()
    work = quote_obj.get("work", "").strip()

    if not quote_text:
        return [{
            "name": "Quote of the Day",
            "icon": "💭",
            "sort": "chronological",
            "items": [],
        }]

    # Build a summary that includes the source if available
    summary_parts = []
    if work:
        summary_parts.append(work)
    summary = " — ".join(summary_parts) if summary_parts else ""

    items = [{
        "title": f"“{quote_text}”",
        "link": "",
        "published": "",
        "summary": author if not summary else f"{author}. {summary}",
        "source": "API Ninjas",
    }]

    return [{
        "name": "Quote of the Day",
        "icon": "💭",
        "sort": "chronological",
        "items": items,
    }]
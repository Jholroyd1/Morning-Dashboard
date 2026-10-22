"""Shared helpers for all collectors."""

import json
import re
import ssl
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def fetch_rss(url, timeout=10):
    """Fetch an RSS feed. Returns list of item dicts."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        print(f"  [rss http error] {url[:70]}... -> {e}")
        return []
    except urllib.error.URLError as e:
        print(f"  [rss url error] {url[:70]}... -> {e}")
        return []
    except TimeoutError as e:
        print(f"  [rss timeout] {url[:70]}... -> {e}")
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"  [parse error] {url[:70]}... -> {e}")
        return []

    results = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        desc = re.sub(r"<[^>]+>", "", (item.findtext("description") or "")).strip()
        if title and link:
            results.append({
                "title": title,
                "link": link,
                "published": pub,
                "summary": desc[:300],
            })
    return results


def fetch_json(url, timeout=10):
    """Fetch a JSON endpoint. Returns the parsed object, or None on failure."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        print(f"  [json http error] {url[:70]}... -> {e}")
        return None
    except urllib.error.URLError as e:
        print(f"  [json url error] {url[:70]}... -> {e}")
        return None
    except TimeoutError as e:
        print(f"  [json timeout] {url[:70]}... -> {e}")
        return None

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [json decode error] {url[:70]}... -> {e}")
        return None


def parse_date(date_str):
    """Return a timezone-aware datetime, or None."""
    if not date_str:
        return None

    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue
    return None


def filter_items(items, keywords=None, excludes=None):
    """Apply keyword / exclude filters to a list of items."""
    keywords = [k.lower() for k in (keywords or [])]
    excludes = [x.lower() for x in (excludes or [])]
    out = []
    for it in items:
        haystack = (it["title"] + " " + it.get("summary", "")).lower()
        if keywords and not any(k in haystack for k in keywords):
            continue
        if excludes and any(x in haystack for x in excludes):
            continue
        out.append(it)
    return out
"""Collect key current events from Google News."""

from .base import fetch_rss

GOOGLE_WORLD = (
    "https://news.google.com/rss/search"
    "?q=world+news&hl=en-US&gl=US&ceid=US:en"
)


def collect():
    return [{
        "name": "Key Current Events",
        "icon": "🌍",
        "sort": "relevance",
        "items": fetch_rss(GOOGLE_WORLD),
    }]
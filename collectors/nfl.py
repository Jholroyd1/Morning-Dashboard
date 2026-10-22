"""Collect broad NFL news from Google News."""

from .base import fetch_rss

GOOGLE_NFL = (
    "https://news.google.com/rss/search"
    "?q=NFL&hl=en-US&gl=US&ceid=US:en"
)


def collect():
    return [{
        "name": "NFL",
        "icon": "🏈",
        "sort": "relevance",
        "items": fetch_rss(GOOGLE_NFL),
    }]
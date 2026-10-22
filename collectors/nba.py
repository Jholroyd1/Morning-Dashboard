"""Collect NBA news."""

from .base import fetch_rss

NBA_FEED = (
    "https://news.google.com/rss/search"
    "?q=NBA&hl=en-US&gl=US&ceid=US:en"
)


def collect():
    return [{
        "name": "NBA",
        "icon": "🏀",
        "sort": "relevance",
        "items": fetch_rss(NBA_FEED),
    }]
"""Collect broad entertainment news plus movie-specific news from Google News."""

from .base import fetch_rss

GOOGLE_ENTERTAINMENT = (
    "https://news.google.com/rss/search"
    "?q=entertainment&hl=en-US&gl=US&ceid=US:en"
)
GOOGLE_MOVIES = (
    "https://news.google.com/rss/search"
    "?q=movies&hl=en-US&gl=US&ceid=US:en"
)


def collect():
    sections = []

    sections.append({
        "name": "Entertainment",
        "icon": "🎬",
        "sort": "relevance",
        "items": fetch_rss(GOOGLE_ENTERTAINMENT),
    })

    sections.append({
        "name": "Movies",
        "icon": "🎥",
        "sort": "relevance",
        "items": fetch_rss(GOOGLE_MOVIES),
    })

    return sections
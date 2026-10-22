"""Collect broad MLB news plus Chicago Cubs team news."""

from .base import fetch_rss, filter_items

MLB_COM = "https://www.mlb.com/feeds/news/rss.xml"
CUBS_FEED = (
    "https://news.google.com/rss/search"
    "?q=Chicago+Cubs&hl=en-US&gl=US&ceid=US:en"
)
CUBS_INJURIES = (
    "https://news.google.com/rss/search"
    "?q=%22Chicago+Cubs%22+injury&hl=en-US&gl=US&ceid=US:en"
)


def collect():
    sections = []

    broad = fetch_rss(MLB_COM)
    sections.append({
        "name": "MLB",
        "icon": "⚾",
        "sort": "relevance",
        "items": broad,
    })

    cubs = filter_items(fetch_rss(CUBS_FEED), keywords=["cubs"])
    sections.append({
        "name": "MLB – Chicago Cubs",
        "icon": "⚾",
        "espn": {"sport": "baseball", "league": "mlb", "team_id": "112"},
        "items": cubs,
        "injury_items": fetch_rss(CUBS_INJURIES),
    })

    return sections
"""Collect broad college baseball news."""

from .base import fetch_rss

GOOGLE_COLLEGE_BASEBALL = (
    "https://news.google.com/rss/search"
    "?q=college+baseball&hl=en-US&gl=US&ceid=US:en"
)
UNC_INJURIES = (
    "https://news.google.com/rss/search"
    "?q=%22North+Carolina%22+baseball+injury&hl=en-US&gl=US&ceid=US:en"
)


def collect():
    sections = []

    sections.append({
        "name": "College Baseball",
        "icon": "⚾",
        "sort": "relevance",
        "items": fetch_rss(GOOGLE_COLLEGE_BASEBALL),
    })

    # UNC-specific injury sub-section on the broad card
    # (kept here so the injury block shows up on the baseball card)
    sections.append({
        "name": "College Baseball – UNC Injuries",
        "icon": "🏥",
        "sort": "chronological",
        "max_items": 5,
        "items": fetch_rss(UNC_INJURIES),
    })

    return sections
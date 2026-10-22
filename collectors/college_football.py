"""Collect broad college football news plus UNC and Ohio State team news."""

from .base import fetch_rss, filter_items

GOOGLE_BROAD = (
    "https://news.google.com/rss/search"
    "?q=college+football&hl=en-US&gl=US&ceid=US:en"
)
UNC_FEED = (
    "https://news.google.com/rss/search"
    "?q=%22North+Carolina+Tar+Heels%22+football&hl=en-US&gl=US&ceid=US:en"
)
OSU_FEED = (
    "https://news.google.com/rss/search"
    "?q=%22Ohio+State+Buckeyes%22+football&hl=en-US&gl=US&ceid=US:en"
)
UNC_INJURIES = (
    "https://news.google.com/rss/search"
    "?q=%22North+Carolina%22+football+injury&hl=en-US&gl=US&ceid=US:en"
)
OSU_INJURIES = (
    "https://news.google.com/rss/search"
    "?q=%22Ohio+State%22+football+injury&hl=en-US&gl=US&ceid=US:en"
)


def collect():
    sections = []

    broad = fetch_rss(GOOGLE_BROAD)
    sections.append({
        "name": "College Football",
        "icon": "🏈",
        "sort": "relevance",
        "items": broad,
    })

    unc = filter_items(fetch_rss(UNC_FEED), keywords=["football"])
    sections.append({
        "name": "College Football – UNC",
        "icon": "🏈",
        "espn": {"sport": "football", "league": "college-football", "team_id": "153"},
        "items": unc,
        "injury_items": fetch_rss(UNC_INJURIES),
    })

    osu = filter_items(fetch_rss(OSU_FEED), keywords=["football"])
    sections.append({
        "name": "College Football – Ohio State",
        "icon": "🏈",
        "espn": {"sport": "football", "league": "college-football", "team_id": "194"},
        "items": osu,
        "injury_items": fetch_rss(OSU_INJURIES),
    })

    return sections
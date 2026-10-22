"""Collect broad men's college basketball news plus UNC and Ohio State team news."""

from .base import fetch_rss, filter_items

GOOGLE_BROAD = (
    "https://news.google.com/rss/search"
    "?q=%22men%27s+college+basketball%22&hl=en-US&gl=US&ceid=US:en"
)
UNC_FEED = (
    "https://news.google.com/rss/search"
    "?q=%22North+Carolina+Tar+Heels%22+basketball&hl=en-US&gl=US&ceid=US:en"
)
OSU_FEED = (
    "https://news.google.com/rss/search"
    "?q=%22Ohio+State+Buckeyes%22+basketball&hl=en-US&gl=US&ceid=US:en"
)
UNC_INJURIES = (
    "https://news.google.com/rss/search"
    "?q=%22North+Carolina%22+basketball+injury&hl=en-US&gl=US&ceid=US:en"
)
OSU_INJURIES = (
    "https://news.google.com/rss/search"
    "?q=%22Ohio+State%22+basketball+injury&hl=en-US&gl=US&ceid=US:en"
)


def collect():
    sections = []

    broad = fetch_rss(GOOGLE_BROAD)
    sections.append({
        "name": "College Basketball",
        "icon": "🏀",
        "sort": "relevance",
        "items": broad,
    })

    unc = filter_items(fetch_rss(UNC_FEED), keywords=["basketball", "hoops"])
    sections.append({
        "name": "College Basketball – UNC",
        "icon": "🏀",
        "espn": {
            "sport": "basketball",
            "league": "mens-college-basketball",
            "team_id": "153",
        },
        "items": unc,
        "injury_items": fetch_rss(UNC_INJURIES),
    })

    osu = filter_items(fetch_rss(OSU_FEED), keywords=["basketball", "hoops"])
    sections.append({
        "name": "College Basketball – Ohio State",
        "icon": "🏀",
        "espn": {
            "sport": "basketball",
            "league": "mens-college-basketball",
            "team_id": "194",
        },
        "items": osu,
        "injury_items": fetch_rss(OSU_INJURIES),
    })

    return sections
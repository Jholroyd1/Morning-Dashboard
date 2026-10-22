"""Fetch the next scheduled game for a team. Used by team-specific sections."""

import traceback
from datetime import date, timedelta


def next_game(sport, league, team_id):
    """Return the next scheduled game for a team, or None if none is found."""
    try:
        if league == "college-football":
            return _college_football(team_id)
        if league == "mens-college-basketball":
            return _college_basketball(team_id)
        if league == "mlb":
            return _mlb(team_id)
        print(f"  [scores] unknown league: {league}")
        return None
    except Exception as e:
        print(f"  [scores error] {sport}/{league}/{team_id} -> {e}")
        traceback.print_exc()
        return None


# ── College Football ───────────────────────────────────────────────
def _college_football(team_id):
    """Fetch the next CFB game using ESPN's scoreboard endpoint."""
    from datetime import date, timedelta
    from collectors.base import fetch_json

    today = date.today()
    today_str = today.isoformat()

    # Scan up to 14 days ahead to find the next game
    for offset in range(0, 14):
        check_date = today + timedelta(days=offset)
        date_str = check_date.strftime("%Y%m%d")

        url = (
            f"https://site.api.espn.com/apis/site/v2/sports/football/"
            f"college-football/scoreboard?dates={date_str}"
            f"&groups=80&limit=500"
        )

        data = fetch_json(url)
        if not data:
            continue

        events = data.get("events", [])
        if not events:
            continue

        for event in events:
            comp = (event.get("competitions") or [{}])[0]
            competitors = comp.get("competitors") or []
            ids = [str(c.get("team", {}).get("id", "")) for c in competitors]
            if str(team_id) not in ids:
                continue

            home = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away = next((c for c in competitors if c.get("homeAway") == "away"), {})
            return {
                "status": "scheduled",
                "label": "Next game",
                "home_team": home.get("team", {}).get("abbreviation", ""),
                "away_team": away.get("team", {}).get("abbreviation", ""),
                "detail": event.get("name", ""),
                "date": event.get("date", ""),
            }

    return None


# ── Men's College Basketball ───────────────────────────────────────
def _college_basketball(team_id):
    """Fetch the next MBB game using ESPN's scoreboard endpoint with a date range."""
    from datetime import date, timedelta
    from collectors.base import fetch_json

    today = date.today()
    today_str = today.isoformat()

    # Scan up to 30 days ahead to find the next game
    for offset in range(0, 30):
        check_date = today + timedelta(days=offset)
        date_str = check_date.strftime("%Y%m%d")

        url = (
            f"https://site.api.espn.com/apis/site/v2/sports/basketball/"
            f"mens-college-basketball/scoreboard?dates={date_str}"
            f"&groups=50&limit=500"
        )

        data = fetch_json(url)
        if not data:
            continue

        events = data.get("events", [])
        if not events:
            continue

        for event in events:
            comp = (event.get("competitions") or [{}])[0]
            competitors = comp.get("competitors") or []
            ids = [str(c.get("team", {}).get("id", "")) for c in competitors]
            if str(team_id) not in ids:
                continue

            home = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away = next((c for c in competitors if c.get("homeAway") == "away"), {})
            return {
                "status": "scheduled",
                "label": "Next game",
                "home_team": home.get("team", {}).get("abbreviation", ""),
                "away_team": away.get("team", {}).get("abbreviation", ""),
                "detail": event.get("name", ""),
                "date": event.get("date", ""),
            }

    return None


# ── MLB ────────────────────────────────────────────────────────────
def _mlb(team_id):
    from sportsdataverse.mlb import mlb_schedule

    today = date.today()
    today_str = today.isoformat()

    # Try current season, then next season
    for season in (today.year, today.year + 1):
        try:
            schedule_data = mlb_schedule(
                team_id=int(team_id), sport_id=1, season=season
            )
            if not schedule_data or "dates" not in schedule_data:
                continue

            for date_entry in schedule_data.get("dates", []):
                for game in date_entry.get("games", []):
                    game_date = game.get("gameDate", "")[:10]
                    if game_date >= today_str:
                        teams = game.get("teams", {})
                        away = teams.get("away", {}).get("team", {})
                        home = teams.get("home", {}).get("team", {})
                        return {
                            "status": "scheduled",
                            "label": "Next game",
                            "home_team": home.get("abbreviation", ""),
                            "away_team": away.get("abbreviation", ""),
                            "detail": f"{away.get('name', '')} at {home.get('name', '')}",
                            "date": game.get("gameDate", ""),
                        }
        except Exception as e:
            print(f"  [scores] MLB season {season} error: {e}")
            continue

    return None
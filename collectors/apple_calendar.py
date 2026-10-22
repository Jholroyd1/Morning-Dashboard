"""Collect today's Apple Calendar events via mac-calendar-mcp."""
import json
import subprocess
from datetime import date, timedelta

def collect():
    """Return a section with today's calendar events."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Call the MCP CLI to get events for today
    try:
        result = subprocess.run(
            ["mac-calendar-mcp", "events", today.isoformat(), tomorrow.isoformat()],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"  [calendar] error: {result.stderr[:200]}")
            return [{"name": "Today's Schedule", "icon": "📅", "items": []}]
        
        events = json.loads(result.stdout) if result.stdout.strip() else []
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"  [calendar] {e}")
        return [{"name": "Today's Schedule", "icon": "📅", "items": []}]

    items = []
    for ev in events[:10]:
        title = ev.get("title", "").strip()
        if not title:
            continue
        
        start = ev.get("start", "")
        end = ev.get("end", "")
        location = ev.get("location", "")
        
        # Format time for display
        time_str = ""
        if start:
            time_str = start[11:16] if len(start) > 11 else start
        if end:
            end_time = end[11:16] if len(end) > 11 else end
            if end_time != time_str:
                time_str += f" – {end_time}"
        
        summary_parts = []
        if time_str:
            summary_parts.append(time_str)
        if location:
            summary_parts.append(location)
        
        items.append({
            "title": title,
            "link": "",
            "published": "",
            "summary": " · ".join(summary_parts),
            "source": "Apple Calendar",
        })
    
    return [{
        "name": "Today's Schedule",
        "icon": "📅",
        "sort": "chronological",
        "max_items": 10,
        "items": items,
    }]
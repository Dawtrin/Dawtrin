#!/usr/bin/env python3
"""Fetch the public contribution calendar - no token needed.

GitHub serves the calendar as public HTML at
https://github.com/users/<username>/contributions.
Parse day cells + tooltips, derive stats, write data/contributions.json.
"""
import datetime as dt
import json
import os
import re
import sys

USERNAME = os.environ.get("GITHUB_USERNAME", "Dawtrin")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_html(url: str) -> str:
    try:
        import requests
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        resp.raise_for_status()
        return resp.text
    except ImportError:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")


def main() -> None:
    html_text = fetch_html(URL)

    # Tooltips carry the counts: "3 contributions on July 4th." / "No contributions on ..."
    counts = {}
    for m in re.finditer(r'<tool-tip[^>]*for=["\']([^"\']+)["\'][^>]*>(.*?)</tool-tip>', html_text, re.DOTALL):
        target = m.group(1)
        tip_text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        cm = re.match(r"(\d+|No)\s+contribution", tip_text)
        if cm and target:
            counts[target] = 0 if cm.group(1) == "No" else int(cm.group(1))

    days = []
    # Match td day cells
    td_matches = re.finditer(r'<td[^>]*class=["\'][^"\']*ContributionCalendar-day[^"\']*["\'][^>]*>', html_text)
    for m in td_matches:
        tag = m.group(0)
        date_m = re.search(r'data-date=["\']([^"\']+)["\']', tag)
        level_m = re.search(r'data-level=["\']([^"\']+)["\']', tag)
        id_m = re.search(r'id=["\']([^"\']+)["\']', tag)

        if date_m and level_m:
            date = date_m.group(1)
            level = int(level_m.group(1))
            td_id = id_m.group(1) if id_m else ""
            count = counts.get(td_id, 0)
            if count == 0 and level > 0:
                count = level
            days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    if not days:
        sys.exit("Error: No day cells parsed - GitHub markup may have changed or username is invalid")

    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    # streaks
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] > 0 else 0
        longest = max(longest, cur)

    current = 0
    today = dt.date.today().isoformat()
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["count"] > 0:
            current += 1
        elif d["date"] != today:
            break

    monthly = {}
    for d in days:
        month_key = d["date"][:7]
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    out = {
        "username": USERNAME,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "total": total,
        "best_day": {"date": best["date"], "count": best["count"]},
        "current_streak": current,
        "longest_streak": longest,
        "monthly": monthly,
        "days": days,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"wrote data/contributions.json -> {total} contributions across {len(days)} days for {USERNAME}")


if __name__ == "__main__":
    main()

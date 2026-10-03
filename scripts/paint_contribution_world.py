#!/usr/bin/env python3
"""Draw a year of public GitHub contributions as a ridge.

Uses the authenticated GitHub GraphQL API (GITHUB_TOKEN / GH_TOKEN,
or `gh auth token` locally). No third-party services. The SVGs are
SMIL-animated and keep a finished still state if animation is ignored.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import urllib.request
from datetime import date
from pathlib import Path

LOGIN = "BinayakJha"
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

LIGHT = {
    "bg": "#FBF8F4",
    "ink": "#1C1915",
    "teal": "#0F6E56",
    "teal_soft": "#D7EBE3",
    "coral": "#E15A3A",
    "line": "#E4DCD0",
    "under": "#FFFDF8",
}
DARK = {
    "bg": "#0D1117",
    "ink": "#F4EFE6",
    "teal": "#6EE0B8",
    "teal_soft": "#14342C",
    "coral": "#FF8B6A",
    "line": "#24313A",
    "under": "#04140F",
}


def token() -> str:
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        value = os.environ.get(key)
        if value:
            return value
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def fetch_weeks(login: str) -> list[tuple[date, int]]:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token()}",
            "Content-Type": "application/json",
            "User-Agent": "contribution-world",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.load(res)
    if payload.get("errors"):
        raise SystemExit(payload["errors"])
    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    rows = []
    for week in weeks:
        days = week["contributionDays"]
        if not days:
            continue
        total = sum(day["contributionCount"] for day in days)
        start = date.fromisoformat(days[0]["date"])
        rows.append((start, total))
    if len(rows) < 2:
        raise SystemExit("No contribution weeks returned.")
    return rows


def ridge_path(points: list[tuple[float, float]]) -> str:
    """Quadratic ridge that stays inside the data's vertical range."""
    parts = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        parts.append(f"Q {x1:.1f} {y1:.1f} {mx:.1f} {my:.1f}")
    last = points[-1]
    parts.append(f"L {last[0]:.1f} {last[1]:.1f}")
    return " ".join(parts)


def build(weeks: list[tuple[date, int]], palette: dict) -> str:
    width, height = 960, 248
    left, right = 48, 912
    baseline = 196
    amplitude = 124
    peak = max(total for _, total in weeks) or 1
    span = max(len(weeks) - 1, 1)
    points = []
    for index, (_, total) in enumerate(weeks):
        x = left + (right - left) * index / span
        y = baseline - (math.log1p(total) / math.log1p(peak)) * amplitude
        points.append((x, y))
    ridge = ridge_path(points)
    area = f"{ridge} L {points[-1][0]:.1f} {baseline:.1f} L {points[0][0]:.1f} {baseline:.1f} Z"

    ticks = []
    seen = set()
    for index, (start, _) in enumerate(weeks):
        if start.month in seen:
            continue
        seen.add(start.month)
        x = left + (right - left) * index / span
        ticks.append(
            f'<line x1="{x:.1f}" y1="{baseline}" x2="{x:.1f}" y2="{baseline + 8}" '
            f'stroke="{palette["line"]}" stroke-width="1.25" stroke-linecap="round"/>'
        )

    p = palette
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <title>A year of public GitHub contributions, drawn as a ridge</title>
  <desc>Weekly public contributions over the last year, as a landscape. No totals are printed.</desc>
  <rect width="{width}" height="{height}" fill="{p["bg"]}"/>
  <defs>
    <clipPath id="field">
      <rect x="24" y="16" width="912" height="216"/>
    </clipPath>
  </defs>
  <line x1="{left}" y1="{baseline}" x2="{right}" y2="{baseline}" stroke="{p["line"]}" stroke-width="1.25" stroke-linecap="round"/>
  {"".join(ticks)}
  <path d="{area}" fill="{p["teal_soft"]}" opacity="1">
    <animate attributeName="opacity" values="0;0;1" keyTimes="0;0.28;0.62" dur="3.2s" fill="freeze"/>
  </path>
  <path d="{ridge}" fill="none" stroke="{p["under"]}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"
        pathLength="100" stroke-dasharray="100" stroke-dashoffset="0">
    <animate attributeName="stroke-dashoffset" values="100;100;0" keyTimes="0;0.12;0.7" dur="3.2s" fill="freeze"/>
  </path>
  <path d="{ridge}" fill="none" stroke="{p["teal"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"
        pathLength="100" stroke-dasharray="100" stroke-dashoffset="0">
    <animate attributeName="stroke-dashoffset" values="100;100;0" keyTimes="0;0.12;0.7" dur="3.2s" fill="freeze"/>
  </path>
  <g clip-path="url(#field)">
    <circle r="9" fill="none" stroke="{p["coral"]}" stroke-width="1.4" opacity="0.55"/>
    <circle r="4" fill="{p["coral"]}"/>
    <animateMotion dur="16s" repeatCount="indefinite" rotate="0" path="{ridge}"/>
  </g>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default="assets")
    parser.add_argument("--login", default=LOGIN)
    args = parser.parse_args()
    weeks = fetch_weeks(args.login)
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    for name, palette in (
        ("contribution-world-light.svg", LIGHT),
        ("contribution-world-dark.svg", DARK),
    ):
        path = dest / name
        path.write_text(build(weeks, palette).strip() + "\n", encoding="utf-8")
        print(f"{name:32} {path.stat().st_size:6} bytes  weeks={len(weeks)}")


if __name__ == "__main__":
    main()

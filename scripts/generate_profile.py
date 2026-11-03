"""Draws the whole profile as one panel, from me.sql and live GitHub data, into assets/profile.svg. Standard library only.

Run with a token in GITHUB_TOKEN: python scripts/generate_profile.py
"""
import json
import os
import re
import sqlite3
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from type_svg import Sheet, width, wrap

LOGIN = "developedByAshu"
EMAIL = "ashutoshanandworkmail@gmail.com"
WAKATIME_BADGE = "https://wakatime.com/badge/user/e553e66b-4ac1-40d7-a4f3-f28f49793dba.svg"
WAKATIME_STATS = "https://wakatime.com/api/v1/users/ashutoshanand139/stats/all_time"
VIEWS_COUNTER = f"https://komarev.com/ghpvc/?username={LOGIN}"
ROOT = Path(__file__).resolve().parent.parent
API_URL = "https://api.github.com/graphql"
TOP_LANGUAGES = 6
ALWAYS_SHOWN = {"Rust": 0.01}
NOT_LANGUAGES = {"Markdown", "JSON", "Text", "Other", "Java Properties", "YAML", "TOML", "XML", "Log", "Git Config", "Ignore List"}
WIDTH, PAD = 1000, 44
INNER = WIDTH - PAD * 2
ORANGE, INK, BODY, MUTED, LINE, PANEL, EMPTY = "#FF7A1A", "#F4F2EE", "#B9BCC2", "#7E828A", "#26292F", "#0B0D11", "#181B20"
HEAT = ["#6B2E0A", "#B24A0E", "#EE6A14", "#FF8F33"]
BLENDS = ["#FF7A1A", "#CF6216", "#A04C13", "#7A3A10", "#58290C", "#3D1D09"]

PROFILE_QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 1) {
      totalCount
    }
  }
}"""

YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def run_query(query, variables):
    """Runs one GitHub GraphQL query and returns its data."""
    body = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(API_URL, body, {"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": LOGIN})
    with urllib.request.urlopen(request, timeout=30) as response:
        reply = json.load(response)
    if reply.get("errors"):
        raise RuntimeError(reply["errors"])
    return reply["data"]


def read_contributions(start_year, today):
    """Returns every day's contribution count from the account's first year to today."""
    days = {}
    for year in range(start_year, today.year + 1):
        variables = {"login": LOGIN, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"}
        calendar = run_query(YEAR_QUERY, variables)["user"]["contributionsCollection"]["contributionCalendar"]
        for week in calendar["weeks"]:
            for day in week["contributionDays"]:
                days[date.fromisoformat(day["date"])] = day["contributionCount"]
    return {day: count for day, count in days.items() if day <= today}


def read_public_text(url):
    """Returns the text labels of a public SVG badge."""
    request = urllib.request.Request(url, headers={"User-Agent": LOGIN})
    with urllib.request.urlopen(request, timeout=30) as response:
        return re.findall(r">([^<>]+)</text>", response.read().decode("utf-8", "ignore"))


def coding_hours():
    """Returns total hours coded, like 3,884, from the public WakaTime badge."""
    return next(match.group(1) for text in read_public_text(WAKATIME_BADGE) if (match := re.match(r"([\d,]+) hrs?", text.strip())))


def profile_views():
    """Returns the profile view count, like 228. Reading the public counter adds 1 view, so this runs once a day."""
    return next(text.strip() for text in reversed(read_public_text(VIEWS_COUNTER)) if re.fullmatch(r"[\d,.]+[kKmM]?", text.strip()))


def longest_streak(days):
    """Returns the longest run of active days."""
    longest = run = 0
    for day in sorted(days):
        run = run + 1 if days[day] else 0
        longest = max(longest, run)
    return longest


def coding_languages():
    """Returns the top programming languages by real editor time from public WakaTime stats, as (name, share)."""
    request = urllib.request.Request(WAKATIME_STATS, headers={"User-Agent": LOGIN})
    with urllib.request.urlopen(request, timeout=30) as response:
        languages = json.load(response)["data"]["languages"]
    kept = [(item["name"], item["percent"] / 100) for item in languages if item["name"] not in NOT_LANGUAGES]
    shares = dict(kept[:TOP_LANGUAGES - len(ALWAYS_SHOWN)]) | ALWAYS_SHOWN
    return sorted(shares.items(), key=lambda item: -item[1])


def section(sheet, y, label, end=WIDTH - PAD):
    """Starts a section: an orange label followed by a hairline up to the given end."""
    sheet.text(PAD, y, label.upper(), 13, ORANGE, "mono", tracking=1.8)
    start = PAD + width(label.upper(), "mono", 13, 1.8) + 16
    sheet.raw(f'<rect x="{start:.0f}" y="{y - 5}" width="{end - start:.0f}" height="1" fill="{LINE}"/>')
    return y + 36


def heatmap(sheet, y, days, today):
    """Draws the last 53 weeks of real contributions, the busiest days glowing."""
    pitch = INNER / 53
    size = pitch - 3.2
    start = today - timedelta(days=(today.weekday() + 1) % 7 + 52 * 7)
    active = sorted(count for count in days.values() if count)
    def level(count):
        if not active:
            return 0
        rank = sum(1 for value in active if value <= count) / len(active)
        return min(3, int(rank * 4 - 0.001))
    plain, bright, seen = [], [], None
    for week in range(53):
        first = start + timedelta(days=week * 7)
        if first.month != seen and week < 51:
            if seen is not None:
                sheet.text(PAD + week * pitch, y - 8, first.strftime("%b"), 12, MUTED, "mono")
            seen = first.month
        for weekday in range(7):
            day = first + timedelta(days=weekday)
            if day > today:
                continue
            x, cell_y = PAD + week * pitch, y + weekday * pitch
            count = days.get(day, 0)
            colour = HEAT[level(count)] if count else EMPTY
            rect = f'<rect x="{x:.1f}" y="{cell_y:.1f}" width="{size:.1f}" height="{size:.1f}" rx="2.5" fill="{colour}"/>'
            (bright if count and level(count) >= 2 else plain).append(rect)
    sheet.raw("".join(plain))
    sheet.raw(f'<g filter="url(#glow)">{"".join(bright)}</g>')
    return y + 7 * pitch


def draw(connection, facts, days, languages, today):
    """Lays out the whole page on one grid."""
    engineer = connection.execute("SELECT * FROM engineer").fetchone()
    sheet = Sheet(WIDTH, f"{engineer['name']}, {engineer['role']}")
    sheet.defs.append(
        '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3.2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="neon" x="-5%" y="-900%" width="110%" height="1900%"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="0.55" stop-color="{ORANGE}" stop-opacity="0.35"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></linearGradient>'
        f'<radialGradient id="wash" cx="1" cy="0" r="0.75"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0.13"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>'
        '<clipPath id="panel"><rect width="1000" height="%HEIGHT%" rx="16"/></clipPath>'
    )
    sheet.raw('<g clip-path="url(#panel)">')
    sheet.raw(f'<rect width="{WIDTH}" height="%HEIGHT%" fill="{PANEL}"/><rect width="{WIDTH}" height="520" fill="url(#wash)"/>')
    sheet.raw('<rect x="0" y="1" width="1000" height="2" fill="url(#edge)" filter="url(#neon)"/>')
    sheet.raw("</g>")
    sheet.raw(f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="%INNER%" rx="16" fill="none" stroke="{LINE}"/>')

    # Who.
    sheet.text(PAD, 92, engineer["name"], 54, INK, "semibold", tracking=-0.8)
    sheet.text(PAD, 126, f"{engineer['role']} / {engineer['city']}".lower(), 16, ORANGE, "mono")
    sheet.text(PAD, 152, EMAIL, 15, BODY, "mono")
    y = 194
    for line in wrap(engineer["intro"], "regular", 20, INNER):
        sheet.text(PAD, y, line, 20, BODY)
        y += 30

    # Live GitHub data: the page's centrepiece.
    stamp = f"updated {datetime.now(timezone(timedelta(hours=5, minutes=30))):%d %b %Y}"
    stamp_x = WIDTH - PAD - width(stamp, "mono", 12.5)
    y = section(sheet, y + 22, "Live", stamp_x - 34)
    sheet.raw(f'<circle cx="{stamp_x - 14:.1f}" cy="{y - 41}" r="3.5" fill="{ORANGE}" filter="url(#glow)"><animate attributeName="opacity" values="1;0.3;1" dur="2.4s" repeatCount="indefinite"/></circle>')
    sheet.text(stamp_x, y - 37, stamp, 12.5, MUTED, "mono")
    figures = [
        (f"{facts['all_time']:,}", "total contributions"), (facts["coding_hours"], "hours coded"), (f"{facts['this_year']:,}", f"{today.year} contributions"),
        (facts["views"], "profile views"), (f"{facts['repositories']}", "public repos"), (f"{facts['longest']}", "day best streak"),
    ]
    cell = INNER / len(figures)
    for position, (value, label) in enumerate(figures):
        centre = PAD + cell * (position + 0.5)
        sheet.text(centre - width(value, "medium", 36, -0.5) / 2, y + 26, value, 36, INK, "medium", tracking=-0.5)
        sheet.text(centre - width(label, "regular", 14) / 2, y + 52, label, 14, MUTED)
        if position:
            sheet.raw(f'<rect x="{PAD + cell * position:.1f}" y="{y - 6}" width="1" height="64" fill="{LINE}"/>')
    y = heatmap(sheet, y + 100, days, today) + 24
    left, listed = PAD, sum(share for _, share in languages) or 1
    for index, (name, share) in enumerate(languages):
        segment = share / listed * INNER
        sheet.raw(f'<rect x="{left:.1f}" y="{y}" width="{max(segment - 2, 1.5):.1f}" height="7" fill="{BLENDS[index]}"/>')
        left += segment
    x = PAD
    for index, (name, share) in enumerate(languages):
        label = f"{name} {share * 100:.0f}%"
        sheet.raw(f'<rect x="{x:.1f}" y="{y + 25}" width="9" height="9" rx="2" fill="{BLENDS[index]}"/>')
        sheet.text(x + 15, y + 34, label, 14, BODY)
        x += 15 + width(label, "regular", 14) + 26
    y += 76

    # What I have built.
    note = "figures from test runs"
    note_x = WIDTH - PAD - width(note, "mono", 12.5)
    sheet.text(note_x, y, note, 12.5, MUTED, "mono")
    y = section(sheet, y, "Selected work", note_x - 18)
    rows = connection.execute("SELECT title, what FROM work ORDER BY id").fetchall()
    column = (INNER - 40) / 2
    for start in range(0, len(rows), 2):
        tallest = 0
        for offset, row in enumerate(rows[start:start + 2]):
            x = PAD + offset * (column + 40)
            sheet.text(x, y, row["title"], 18.5, INK, "semibold")
            lines = wrap(row["what"], "regular", 16, column)
            for number, line in enumerate(lines):
                sheet.text(x, y + 26 + number * 23, line, 16, BODY)
            tallest = max(tallest, len(lines))
        y += 26 + tallest * 23 + 16
    y += 16

    # Skills.
    y = section(sheet, y, "Skills")
    for kind, names in connection.execute("SELECT kind, group_concat(name, ', ') FROM skill GROUP BY kind ORDER BY min(id)"):
        sheet.text(PAD, y, kind, 16, INK, "medium")
        for line in wrap(names, "regular", 16, INNER - 140):
            sheet.text(PAD + 140, y, line, 16, BODY)
            y += 25
        y += 6
    y += 22

    # What I am on right now.
    y = section(sheet, y, "Now")
    for row in connection.execute("SELECT label, what FROM now ORDER BY id"):
        sheet.text(PAD, y, row["label"], 16, INK, "medium")
        for line in wrap(row["what"], "regular", 16, INNER - 140):
            sheet.text(PAD + 140, y, line, 16, BODY)
            y += 25
        y += 6
    sheet.save(ROOT / "assets" / "profile.svg", y + 22)


def main():
    today = datetime.now(timezone.utc).date()
    user = run_query(PROFILE_QUERY, {"login": LOGIN})["user"]
    days = read_contributions(int(user["createdAt"][:4]), today)
    facts = {
        "this_year": sum(count for day, count in days.items() if day.year == today.year),
        "all_time": sum(days.values()), "longest": longest_streak(days), "repositories": user["repositories"]["totalCount"],
        "coding_hours": coding_hours(), "views": profile_views(),
    }
    languages = coding_languages()
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript((ROOT / "me.sql").read_text(encoding="utf-8"))
    (ROOT / "assets").mkdir(exist_ok=True)
    draw(connection, facts, days, languages, today)
    print(json.dumps(facts), languages)


if __name__ == "__main__":
    main()

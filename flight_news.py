#!/usr/bin/env python3
"""
Fetches the latest news about flight attendants and airlines using NewsAPI.org
(free tier) and saves the results to flight_news.txt.

Setup:
    1. Get a free API key at https://newsapi.org/register
    2. Set it as an environment variable:
         Windows (PowerShell):  $env:NEWSAPI_KEY = "your_key_here"
         macOS/Linux (bash):    export NEWSAPI_KEY="your_key_here"
    3. Run:  python flight_news.py
"""

import os
import sys
import urllib.parse
import urllib.request
import json
from datetime import datetime, timedelta, timezone

API_URL = "https://newsapi.org/v2/everything"
OUTPUT_FILE = "flight_news.txt"
QUERY = '"flight attendant" OR "flight attendants" OR airline'
PAGE_SIZE = 20


def fetch_news(api_key: str) -> dict:
    params = {
        "q": QUERY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": PAGE_SIZE,
        "from": (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d"),
        "apiKey": api_key,
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={"User-Agent": "flight-news-script/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} error from NewsAPI: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error reaching NewsAPI: {e.reason}") from e


def format_articles(data: dict) -> str:
    articles = data.get("articles", [])
    if not articles:
        return "No articles found.\n"

    lines = []
    for i, article in enumerate(articles, start=1):
        title = article.get("title") or "Untitled"
        source = (article.get("source") or {}).get("name", "Unknown source")
        published = article.get("publishedAt", "Unknown date")
        description = article.get("description") or ""
        url = article.get("url") or ""

        lines.append(f"{i}. {title}")
        lines.append(f"   Source:      {source}")
        lines.append(f"   Published:   {published}")
        if description:
            lines.append(f"   Summary:     {description}")
        lines.append(f"   URL:         {url}")
        lines.append("")

    return "\n".join(lines)


def main():
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key:
        print(
            "ERROR: NEWSAPI_KEY environment variable is not set.\n"
            "Get a free key at https://newsapi.org/register and set it, e.g.:\n"
            '  PowerShell: $env:NEWSAPI_KEY = "your_key_here"\n'
            '  bash:       export NEWSAPI_KEY="your_key_here"',
            file=sys.stderr,
        )
        sys.exit(1)

    print("Fetching latest flight attendant / airline news...")
    try:
        data = fetch_news(api_key)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if data.get("status") != "ok":
        print(f"ERROR: NewsAPI returned an error: {data}", file=sys.stderr)
        sys.exit(1)

    header = (
        f"Flight Attendant & Airline News\n"
        f"Fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Query: {QUERY}\n"
        f"Total results: {data.get('totalResults', 0)}\n"
        + "=" * 60
        + "\n\n"
    )

    body = format_articles(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + body)

    print(f"Saved {len(data.get('articles', []))} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

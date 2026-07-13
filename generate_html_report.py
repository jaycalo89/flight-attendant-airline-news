#!/usr/bin/env python3
"""
Converts flight_news.txt into an HTML report (flight_news.html) styled as an
airport departures board: a lit signage masthead above a manifest of
boarding-pass-style entries, one per article.

Usage:
    python generate_html_report.py
"""

import re
import html
import sys

INPUT_FILE = "flight_news.txt"
OUTPUT_FILE = "flight_news.html"


def parse_report(text: str):
    lines = text.splitlines()

    meta = {"fetched": "", "query": "", "total": ""}
    for line in lines[:5]:
        if line.startswith("Fetched:"):
            meta["fetched"] = line.split("Fetched:", 1)[1].strip()
        elif line.startswith("Query:"):
            meta["query"] = line.split("Query:", 1)[1].strip()
        elif line.startswith("Total results:"):
            meta["total"] = line.split("Total results:", 1)[1].strip()

    body = text.split("=" * 60, 1)[-1]

    blocks = re.split(r"\n(?=\d+\.\s)", body.strip())
    articles = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        title_match = re.match(r"\d+\.\s*(.+)", block)
        title = title_match.group(1).strip() if title_match else "Untitled"

        source_match = re.search(r"Source:\s*(.+)", block)
        published_match = re.search(r"Published:\s*(.+)", block)
        url_match = re.search(r"URL:\s*(.+)", block)

        summary_match = re.search(
            r"Summary:\s*(.+?)(?=\n\s*URL:)", block, re.DOTALL
        )

        source = source_match.group(1).strip() if source_match else "Unknown"
        published = published_match.group(1).strip() if published_match else ""
        url = url_match.group(1).strip() if url_match else "#"
        summary = (
            re.sub(r"\s+", " ", summary_match.group(1)).strip()
            if summary_match
            else ""
        )

        articles.append(
            {
                "title": title,
                "source": source,
                "published": published,
                "summary": summary,
                "url": url,
            }
        )

    return meta, articles


MONTHS = ["", "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def format_board_time(raw: str) -> str:
    """Compact departure-board style: '11 JUL · 22:00Z'."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", raw)
    if not m:
        return raw
    _, mo, d, hh, mm = m.groups()
    return f"{int(d):02d} {MONTHS[int(mo)]} · {hh}:{mm}Z"


TICKET_TEMPLATE = """      <article class="ticket">
        <div class="ticket-meta">
          <span class="ticket-no">{no:02d}</span>
          <span class="ticket-time">{published}</span>
          <span class="ticket-gate">{source}</span>
        </div>
        <div class="ticket-perf" aria-hidden="true"></div>
        <div class="ticket-content">
          <h2><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h2>
          <p>{summary}</p>
          <a class="ticket-link" href="{url}" target="_blank" rel="noopener noreferrer">Read article <span aria-hidden="true">&#8594;</span></a>
        </div>
      </article>"""


def build_html(meta, articles) -> str:
    tickets = []
    for i, a in enumerate(articles, start=1):
        tickets.append(
            TICKET_TEMPLATE.format(
                no=i,
                source=html.escape(a["source"]),
                title=html.escape(a["title"]),
                summary=html.escape(a["summary"]) or "No summary available.",
                url=html.escape(a["url"], quote=True),
                published=format_board_time(a["published"]),
            )
        )
    tickets_html = "\n".join(tickets)

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flight Attendant &amp; Airline News</title>
<style>
  :root {{
    --bg: #E9EBE7;
    --surface: #FFFFFF;
    --ink: #1C1E1F;
    --muted: #5B6168;
    --border: #D8DBD5;
    --beacon: #C97A1E;
    --taxiway: #256B78;
    --focus: #C97A1E;
  }}

  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #101215;
      --surface: #1B1E22;
      --ink: #ECE7DC;
      --muted: #9CA2A6;
      --border: #2C3034;
      --beacon: #F2A93C;
      --taxiway: #5FB8C9;
      --focus: #F2A93C;
    }}
  }}

  :root[data-theme="light"] {{
    --bg: #E9EBE7;
    --surface: #FFFFFF;
    --ink: #1C1E1F;
    --muted: #5B6168;
    --border: #D8DBD5;
    --beacon: #C97A1E;
    --taxiway: #256B78;
    --focus: #C97A1E;
  }}

  :root[data-theme="dark"] {{
    --bg: #101215;
    --surface: #1B1E22;
    --ink: #ECE7DC;
    --muted: #9CA2A6;
    --border: #2C3034;
    --beacon: #F2A93C;
    --taxiway: #5FB8C9;
    --focus: #F2A93C;
  }}

  * {{ box-sizing: border-box; }}

  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}

  a {{ color: inherit; }}
  a:focus-visible {{
    outline: 2px solid var(--focus);
    outline-offset: 2px;
  }}

  /* ---- Masthead: a lit departures board, deliberately fixed-dark
     regardless of page theme, like real airport signage. ---- */
  header.board {{
    background: #101215;
    background-image:
      repeating-linear-gradient(180deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 3px);
    color: #ECE7DC;
    border-bottom: 3px solid #F2A93C;
    padding: 2.25rem 1.5rem 1.5rem;
  }}

  .board-inner {{
    max-width: 960px;
    margin: 0 auto;
  }}

  .board-title-row {{
    display: flex;
    align-items: baseline;
    gap: 0.85rem;
    flex-wrap: wrap;
  }}

  .board-tag {{
    font-family: ui-monospace, "SFMono-Regular", "IBM Plex Mono", Menlo, Consolas, monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: #101215;
    background: #F2A93C;
    padding: 0.2rem 0.5rem;
  }}

  header.board h1 {{
    font-family: ui-monospace, "SFMono-Regular", "IBM Plex Mono", Menlo, Consolas, monospace;
    text-transform: uppercase;
    letter-spacing: 0.045em;
    font-size: clamp(1.25rem, 3.4vw, 1.9rem);
    font-weight: 700;
    margin: 0;
    text-wrap: balance;
    color: #F2A93C;
    text-shadow: 0 0 18px rgba(242, 169, 60, 0.35);
  }}

  .board-status {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem 2rem;
    margin-top: 1.35rem;
    font-family: ui-monospace, "SFMono-Regular", "IBM Plex Mono", Menlo, Consolas, monospace;
    font-variant-numeric: tabular-nums;
    font-size: 0.8rem;
  }}

  .status-item {{ display: flex; flex-direction: column; gap: 0.2rem; }}

  .status-label {{
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.65rem;
    color: #8A8F86;
  }}

  .status-value {{ color: #ECE7DC; }}

  /* ---- Manifest ---- */
  main {{
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
  }}

  .manifest {{
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }}

  .ticket {{
    background: var(--surface);
    border: 1px solid var(--border);
    display: grid;
    grid-template-columns: 128px 1px 1fr;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}

  @media (prefers-reduced-motion: no-preference) {{
    .ticket:hover {{
      transform: translateY(-2px);
      box-shadow: 0 10px 24px rgba(16, 18, 21, 0.12);
    }}
  }}

  .ticket-meta {{
    padding: 1.1rem 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    font-family: ui-monospace, "SFMono-Regular", "IBM Plex Mono", Menlo, Consolas, monospace;
    font-variant-numeric: tabular-nums;
  }}

  .ticket-no {{
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.05em;
  }}

  .ticket-time {{
    font-size: 0.82rem;
    color: var(--ink);
  }}

  .ticket-gate {{
    align-self: flex-start;
    font-size: 0.68rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--taxiway);
    border: 1px solid var(--taxiway);
    padding: 0.15rem 0.4rem;
  }}

  /* Perforation: dashed tear-line with punched notches top & bottom */
  .ticket-perf {{
    position: relative;
    border-left: 2px dashed var(--border);
  }}

  .ticket-perf::before,
  .ticket-perf::after {{
    content: "";
    position: absolute;
    left: -7px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--bg);
    border: 1px solid var(--border);
  }}

  .ticket-perf::before {{ top: -8px; }}
  .ticket-perf::after {{ bottom: -8px; }}

  .ticket-content {{
    padding: 1.1rem 1.35rem;
  }}

  .ticket-content h2 {{
    font-family: Georgia, "Iowan Old Style", "Palatino Linotype", "Times New Roman", serif;
    font-size: 1.15rem;
    font-weight: 700;
    line-height: 1.38;
    margin: 0 0 0.55rem;
    text-wrap: balance;
  }}

  .ticket-content h2 a {{
    text-decoration: none;
  }}

  .ticket-content h2 a:hover {{
    color: var(--beacon);
  }}

  .ticket-content p {{
    font-size: 0.92rem;
    line-height: 1.62;
    color: var(--muted);
    margin: 0 0 0.85rem;
    max-width: 62ch;
  }}

  .ticket-link {{
    display: inline-block;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--beacon);
    text-decoration: none;
    border-bottom: 1px solid transparent;
  }}

  .ticket-link:hover {{
    border-bottom-color: var(--beacon);
  }}

  @media (max-width: 620px) {{
    .ticket {{
      grid-template-columns: 1fr;
      grid-template-rows: auto 1px auto;
    }}

    .ticket-meta {{
      flex-direction: row;
      align-items: center;
      flex-wrap: wrap;
    }}

    .ticket-perf {{
      border-left: none;
      border-top: 2px dashed var(--border);
    }}

    .ticket-perf::before,
    .ticket-perf::after {{
      left: auto;
      top: -7px;
    }}

    .ticket-perf::before {{ left: -8px; }}
    .ticket-perf::after {{ right: -8px; left: auto; }}
  }}

  footer.page-footer {{
    text-align: center;
    color: var(--muted);
    font-family: ui-monospace, "SFMono-Regular", "IBM Plex Mono", Menlo, Consolas, monospace;
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    padding: 0.5rem 1.5rem 2.5rem;
  }}
</style>
</head>
<body>
  <header class="board">
    <div class="board-inner">
      <div class="board-title-row">
        <span class="board-tag">DEP</span>
        <h1>Flight Attendant &amp; Airline News</h1>
      </div>
      <div class="board-status">
        <div class="status-item">
          <span class="status-label">Fetched</span>
          <span class="status-value">{fetched}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Query</span>
          <span class="status-value">{query}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Results</span>
          <span class="status-value">{total}</span>
        </div>
      </div>
    </div>
  </header>

  <main>
    <div class="manifest">
{tickets_html}
    </div>
  </main>

  <footer class="page-footer">
    GENERATED FROM FLIGHT_NEWS.TXT &middot; {count} ENTRIES ON MANIFEST
  </footer>
</body>
</html>
""".format(
        fetched=html.escape(meta["fetched"]),
        query=html.escape(meta["query"]),
        total=html.escape(meta["total"]),
        tickets_html=tickets_html,
        count=len(articles),
    )


def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"ERROR: {INPUT_FILE} not found. Run flight_news.py first.", file=sys.stderr)
        sys.exit(1)

    meta, articles = parse_report(text)
    if not articles:
        print("ERROR: No articles parsed from flight_news.txt.", file=sys.stderr)
        sys.exit(1)

    html_out = build_html(meta, articles)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"Saved {len(articles)} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

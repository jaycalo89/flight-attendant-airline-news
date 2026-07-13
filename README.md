# ✈️ Flight Attendant News Aggregator

A lightweight, dependency-free news pipeline that pulls the latest flight attendant and airline industry news and renders it as a styled, airport-departures-board-themed HTML report.

**[View a sample report](flight_news.html)**

---

## What It Does

This project is a three-stage pipeline that turns a live news query into a polished, shareable report:

1. **Fetch** — `flight_news.py` queries [NewsAPI.org](https://newsapi.org) for articles mentioning `"flight attendant"`, `"flight attendants"`, or `airline` published in the last 7 days, and writes the results to a plain-text file (`flight_news.txt`).
2. **Render** — `generate_html_report.py` parses that text file and generates a self-contained HTML report (`flight_news.html`), styled to look like an airport departures board — complete with a glowing signage masthead and boarding-pass-style ticket cards for each article.
3. **Orchestrate** — `update_flight_news.py` chains both steps together into a single command, so the whole pipeline can be run (or scheduled) in one shot.

The result is a clean, themed, browser-ready digest of what's happening in the airline and flight attendant world — no dashboard, database, or framework required.

## Why I Built It

I wanted a fast, focused way to keep up with news relevant to flight attendants and the airline industry without manually searching multiple sites every day. Rather than reaching for a heavyweight framework, I set out to see how much value I could deliver with pure Python and the standard library — no external dependencies, no build step, just a script that fetches, formats, and presents. It also gave me a chance to push past a purely functional output and put real design effort into how automated, data-driven content can *look* — treating a news report like a piece of UI rather than a wall of text.

## How to Install and Run

### Prerequisites

- Python 3.8+
- A free [NewsAPI.org](https://newsapi.org/register) API key

### Setup

1. **Clone or download this repository.**

2. **Get a free API key** from [newsapi.org/register](https://newsapi.org/register).

3. **Set the API key as an environment variable:**

   **Windows (PowerShell):**
   ```powershell
   $env:NEWSAPI_KEY = "your_key_here"
   ```

   **macOS/Linux (bash):**
   ```bash
   export NEWSAPI_KEY="your_key_here"
   ```

### Running

Run the full pipeline (fetch + render) in one command:

```bash
python update_flight_news.py
```

Or run each stage independently:

```bash
python flight_news.py            # Fetch latest articles -> flight_news.txt
python generate_html_report.py   # Render the HTML report -> flight_news.html
```

Then open `flight_news.html` in any browser to view the report.

## Technologies Used

- **Python 3** — entire pipeline, zero third-party dependencies
- **`urllib`** — HTTP requests to the NewsAPI REST endpoint (no `requests` library needed)
- **`re` / `html`** — parsing the intermediate text report and safely escaping content for HTML output
- **`subprocess`** — orchestrating the fetch and render stages from a single entry point
- **NewsAPI.org** — external REST API providing real-time news article data
- **HTML5 / CSS3** — hand-written responsive, theme-aware report styling, including:
  - `prefers-color-scheme` and `data-theme` support for automatic and manual light/dark modes
  - CSS Grid for the ticket/card layout, with a responsive single-column fallback
  - `prefers-reduced-motion` handling for accessibility
  - Custom typography mixing monospace (departure-board digits) and serif (article headlines) for a print-meets-signage aesthetic

## What I Learned

- **You don't always need a framework.** The entire pipeline — HTTP calls, parsing, templating, and styling — runs on Python's standard library alone. It reinforced how much can be accomplished with deliberate, well-structured code before reaching for external dependencies.
- **Parsing your own output is a real skill.** Designing `flight_news.txt` as a clean intermediate format, and then writing a regex-based parser to reliably reconstruct structured article data from it, taught me a lot about designing data formats defensively — anticipating missing fields, inconsistent whitespace, and edge cases like articles with no summary.
- **Security-by-default matters even in small scripts.** Escaping every dynamic value with `html.escape()` before injecting it into the generated HTML was a deliberate choice to prevent injection issues from untrusted article titles/descriptions — a good habit regardless of project size.
- **Design is a force multiplier for "boring" data.** Applying a consistent visual metaphor (an airport departures board) to plain news data — via typography, color tokens, and layout — transformed a simple text dump into something that feels considered and portfolio-worthy.
- **Small pipelines benefit from clear separation of concerns.** Splitting fetch, render, and orchestration into three distinct scripts made each piece independently testable and reusable — for example, the HTML renderer can regenerate a report from any correctly formatted text file without re-hitting the API.

## Project Structure

```
.
├── flight_news.py            # Fetches news from NewsAPI -> flight_news.txt
├── generate_html_report.py   # Renders flight_news.txt -> flight_news.html
├── update_flight_news.py     # Runs the full fetch + render pipeline
├── flight_news.txt           # Latest fetched articles (generated)
└── flight_news.html          # Styled HTML report (generated)
```

## Possible Future Enhancements

- Scheduled execution (cron / Task Scheduler) for a daily auto-refreshed report
- Email or Slack delivery of the generated report
- Category/sentiment tagging of articles
- Historical archive of past reports for trend tracking

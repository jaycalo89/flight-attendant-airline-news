#!/usr/bin/env python3
"""
Chains the full pipeline: fetch latest news (flight_news.py) then render
the HTML report (generate_html_report.py).

Usage:
    python update_flight_news.py
"""

import subprocess
import sys


def run(script: str):
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    run("flight_news.py")
    run("generate_html_report.py")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
inspect_yahoo_page.py

Fetches a Yahoo Fantasy page and prints its HTML structure so we can
write correct parsers for fetch_yahoo_data.py.

Usage:
    python inspect_yahoo_page.py standings 2022
    python inspect_yahoo_page.py draftresults 2022
    python inspect_yahoo_page.py "https://full.url.here" 2022
"""

import asyncio
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

LEAGUE_SLUG = "sme327"
BASE_URL = "https://football.fantasysports.yahoo.com"
SESSION_FILE = Path(__file__).parent / ".yahoo_cookies.json"

LEAGUE_IDS: dict[int, tuple[str, int]] = {
    2018: ("f1", 1332374),
    2019: ("f1",  407071),
    2020: ("f1",  785513),
    2021: ("f1",   69643),
    2022: ("f1",  641538),
    2023: ("f1",    7167),
    2024: ("f1",   37702),
    2025: ("f1",   66119),
}


async def ensure_logged_in(context):
    if SESSION_FILE.exists():
        cookies = json.loads(SESSION_FILE.read_text())
        await context.add_cookies(cookies)
        page = await context.new_page()
        await page.goto("https://www.yahoo.com", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        content = await page.content()
        if 'id="ybar-useremail"' in content or "Sign Out" in content or "sme327" in content.lower():
            print("Already logged in via saved session.\n")
            await page.close()
            return
        await page.close()

    page = await context.new_page()
    await page.goto("https://login.yahoo.com", wait_until="domcontentloaded")
    print("\n" + "="*60)
    print("Please log in to Yahoo in the browser window.")
    print("After you're fully logged in, come back here and press Enter.")
    print("="*60)
    input("\nPress Enter after logging in > ")
    await asyncio.sleep(1)
    cookies = await context.cookies()
    SESSION_FILE.write_text(json.dumps(cookies))
    print("Session saved.\n")
    await page.close()


async def main():
    section = sys.argv[1] if len(sys.argv) > 1 else "standings"
    year    = sys.argv[2] if len(sys.argv) > 2 else "2022"
    extra   = sys.argv[3] if len(sys.argv) > 3 else ""

    if section.startswith("http"):
        url = section
        section = "url"
    else:
        year_int = int(year)
        game, lid = LEAGUE_IDS[year_int]
        base = f"{BASE_URL}/{year}/{game}/{lid}"
        if section == "standings":
            url = f"{base}?lhst=stand#leaguehomestandings"
        elif section == "matchups":
            url = f"{base}?matchup_week={extra}&module=matchups&lhst=matchups" if extra else f"{base}/matchup"
        elif section == "playoffs":
            url = f"{base}?module=standings&lhst=playoff#lhstplayoff"
        elif section == "schedule":
            url = f"{base}?module=standings&lhst=sched#lhstsched"
        elif section in ("", "home"):
            url = base
        else:
            url = f"{base}/{section}?{extra}" if extra else f"{base}/{section}"

    print(f"Target URL: {url}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        await ensure_logged_in(context)

        page = await context.new_page()
        print(f"Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(4)

        html = await page.content()
        if "Request denied" in html or len(html) < 500:
            print("\nYahoo returned 'Request denied' — IP is rate-limited.")
            print("Wait 15-20 minutes then try again.")
            input("Or navigate manually in the browser, then press Enter to capture what loaded.")
            html = await page.content()

        final_url = page.url
        out_file = Path(__file__).parent / f"debug_{year}_{section}.html"
        out_file.write_text(html, encoding="utf-8")
        print(f"Saved HTML to: {out_file}")

        soup = BeautifulSoup(html, "html.parser")
        print(f"\nPage title: {soup.title.get_text() if soup.title else '(none)'}")
        print(f"Final URL:  {final_url}")

        print("\n--- Tables found ---")
        for i, table in enumerate(soup.find_all("table")[:8]):
            classes = table.get("class", [])
            id_ = table.get("id", "")
            rows = len(table.find_all("tr"))
            cols = len(table.find_all("th"))
            print(f"  [{i}] id={id_!r} class={classes} rows={rows} cols={cols}")
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            if headers:
                print(f"       headers: {headers[:12]}")
            trs = table.find_all("tr")
            if len(trs) > 1:
                sample = [td.get_text(strip=True) for td in trs[1].find_all(["td", "th"])]
                print(f"       sample:  {sample[:8]}")

        print("\n--- Key divs/sections ---")
        for cls_pattern in ["standings", "draft", "scoreboard", "matchup", "bracket", "team", "player"]:
            els = soup.find_all(class_=re.compile(cls_pattern, re.I))
            if els:
                print(f"  .{cls_pattern}: {len(els)} elements")
                for el in els[:2]:
                    text = el.get_text(strip=True)[:100]
                    print(f"    → {el.name} class={el.get('class')} | {text!r}")

        print("\n--- IDs on page ---")
        for el in soup.find_all(id=True)[:20]:
            print(f"  #{el.get('id')} ({el.name})")

        cookies = await context.cookies()
        SESSION_FILE.write_text(json.dumps(cookies))

        input("\nPress Enter to close the browser.")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

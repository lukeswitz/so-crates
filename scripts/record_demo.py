#!/usr/bin/env python3
"""Record docs/videos/demo.mp4 against a locally running SO-CRATES server.

Requires: pip install -r requirements-screenshots.txt, plus a one-time
`playwright install ffmpeg` (Playwright's video muxing needs its own bundled
ffmpeg, separate from any system ffmpeg). Also needs a running server
(default http://127.0.0.1:8000/socrates.html - override with --base-url).
Uses the app's own built-in "Sample pcap file" (DEFAULT_SAMPLE_URL in
static/socrates.js), same as scripts/capture_screenshots.py, so it needs no
pre-existing local analysis or hardcoded MD5 - it works on a clean checkout
with an empty DATA_DIR.

Playwright's own video muxing can only record to WebM, but that raw
recording is treated as a discarded intermediate, not a published asset -
it's immediately re-encoded to H.264/AAC MP4 via a system `ffmpeg` binary,
since MP4 is universally browser-supported (unlike WebM, whose Safari/iOS
support is spotty) and is also the format required to upload the same clip
directly to X/Instagram/LinkedIn/Facebook, none of which accept WebM. A
still frame is also extracted to docs/videos/demo-poster.jpg, used as the
<video poster> on the Home page so it doesn't show a blank white square
before playback. If ffmpeg isn't found on PATH, the raw WebM is saved to
docs/videos/demo.webm as a last-resort fallback instead, with a warning -
better than no video at all, but docs/index.md's <video> tag would need a
matching <source> added back until ffmpeg is available and this script is
re-run.

Usage:
    python3 scripts/record_demo.py [--base-url http://127.0.0.1:8000/socrates.html]
"""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile

from playwright.async_api import async_playwright

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MP4_OUTPUT = os.path.join(REPO_ROOT, 'docs', 'videos', 'demo.mp4')
WEBM_FALLBACK_OUTPUT = os.path.join(REPO_ROOT, 'docs', 'videos', 'demo.webm')
POSTER_OUTPUT = os.path.join(REPO_ROOT, 'docs', 'videos', 'demo-poster.jpg')
POSTER_TIMESTAMP_SECONDS = 48  # lands during "Collapsing the Sankey Diagram..." - a visually rich frame
VIEWPORT = {'width': 1920, 'height': 1400}

CAPTION_JS = """
(text) => {
    let el = document.getElementById('demoCaption');
    if (!el) {
        el = document.createElement('div');
        el.id = 'demoCaption';
        el.style.cssText = [
            'position:fixed', 'left:50%', 'transform:translateX(-50%)',
            'background:rgba(0,0,0,0.85)', 'color:#fff', 'padding:14px 30px',
            'border-radius:10px', 'font-family:system-ui,-apple-system,sans-serif',
            'font-size:24px', 'font-weight:600', 'z-index:2147483647',
            'box-shadow:0 6px 20px rgba(0,0,0,0.6)', 'max-width:92vw',
            'text-align:center', 'line-height:1.3', 'pointer-events:none',
            'white-space:pre-line', 'border:1px solid rgba(255,255,255,0.15)'
        ].join(';');
        document.body.appendChild(el);
    }
    const header = document.querySelector('.app-header');
    const headerHeight = header ? header.getBoundingClientRect().height : 0;
    el.style.top = (headerHeight + 16) + 'px';
    el.textContent = text;
}
"""

CAPTION_REMOVE_JS = "() => { const el = document.getElementById('demoCaption'); if (el) el.remove(); }"

# Registered via page.add_init_script so it runs before the app's own scripts
# on the very first navigation - covers the page with an opaque overlay +
# caption from the first paint, so there's no gap/flicker where the caption
# disappears while the real page loads in behind it. document.documentElement
# is null the instant this runs (before the HTML parser creates <html>), so
# it retries via setTimeout rather than assuming it already exists.
OVERLAY_INIT_JS_TEMPLATE = """
(() => {
    function tryInit() {
        if (!document.documentElement) { setTimeout(tryInit, 0); return; }
        const overlay = document.createElement('div');
        overlay.id = 'demoOverlay';
        overlay.style.cssText = 'position:fixed;inset:0;background:#0d1117;z-index:2147483646;';
        document.documentElement.appendChild(overlay);

        const el = document.createElement('div');
        el.id = 'demoCaption';
        el.style.cssText = [
            'position:fixed', 'left:50%', 'top:72px', 'transform:translateX(-50%)',
            'background:rgba(0,0,0,0.85)', 'color:#fff', 'padding:14px 30px',
            'border-radius:10px', 'font-family:system-ui,-apple-system,sans-serif',
            'font-size:24px', 'font-weight:600', 'z-index:2147483647',
            'box-shadow:0 6px 20px rgba(0,0,0,0.6)', 'max-width:92vw',
            'text-align:center', 'line-height:1.3', 'pointer-events:none',
            'white-space:pre-line', 'border:1px solid rgba(255,255,255,0.15)'
        ].join(';');
        el.textContent = __CAPTION_TEXT__;
        document.documentElement.appendChild(el);
    }
    tryInit();
})();
"""


def find_chromium():
    for name in ('chromium', 'chromium-browser', 'google-chrome'):
        path = shutil.which(name)
        if path:
            return path
    return None


async def caption(page, text):
    await page.evaluate(CAPTION_JS, text)


async def main(base_url):
    os.makedirs(os.path.dirname(MP4_OUTPUT), exist_ok=True)
    tmp_video_dir = tempfile.mkdtemp(prefix='so-crates-demo-video-')

    async with async_playwright() as p:
        launch_kwargs = {'headless': True}
        chromium_path = find_chromium()
        if chromium_path:
            launch_kwargs['executable_path'] = chromium_path
        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=tmp_video_dir,
            record_video_size=VIEWPORT,
        )
        page = await context.new_page()

        # Show the intro caption alone first, covering the page with an
        # opaque overlay from the very first paint of the new document.
        welcome_caption = ("Welcome to the SO-CRATES recorded demo!\n\n"
                           "When you first connect to SO-CRATES, you'll be greeted by a welcome "
                           "window that gives you an overview of what you can do with SO-CRATES.")
        overlay_script = OVERLAY_INIT_JS_TEMPLATE.replace(
            '__CAPTION_TEXT__', json.dumps(welcome_caption))
        await page.add_init_script(overlay_script)

        # Welcome screen
        await page.goto(base_url, wait_until="networkidle")
        await page.wait_for_timeout(3000)  # overlay+caption alone, covering the load
        await page.evaluate("document.getElementById('demoOverlay')?.remove();")
        await page.wait_for_selector('#helpModal.active .modal-content', timeout=10000)
        await caption(page, welcome_caption)  # reposition under the now-real header
        await page.wait_for_timeout(4300)
        await page.evaluate("closeHelpModal()")
        await caption(page, "When you dismiss the welcome window, you will see the main screen "
                            "where you can upload a new file or re-open a previous analysis")
        await page.wait_for_timeout(3800)

        # Select the sample pcap file
        await caption(page, "Selecting the built-in sample pcap file")
        await page.wait_for_timeout(2200)
        await page.click(".sample-card:has-text('Sample pcap file')")
        await page.wait_for_selector('#statsGrid .stat-card', timeout=60000)
        await caption(page, "Analysis complete")
        await page.wait_for_timeout(2500)

        # Look at each of the individual data types
        card_count = await page.locator('.stat-card:not(.stat-disabled)').count()
        for i in range(card_count):
            card = page.locator('.stat-card:not(.stat-disabled)').nth(i)
            label = (await card.inner_text()).strip().split('\n')[-1]
            if label == 'ALL EVENTS':
                continue
            await card.click()
            await caption(page, f"Viewing {label}")
            await page.wait_for_timeout(3200)

        # All Events
        await page.locator(".stat-card:has-text('All Events')").first.click()
        await caption(page, "Switching to the merged All Events view")
        await page.wait_for_timeout(2800)

        # Collapse the Sankey Diagram so the Aggregation Tables and Data
        # Table have room to show, now that we're ready to expand them.
        sankey_toggle = page.locator('.section-toggle-bar', has_text='Sankey Diagram').first
        if await sankey_toggle.count() > 0:
            await caption(page, "Collapsing the Sankey Diagram to make room to see the Data Table")
            await page.wait_for_timeout(2600)
            await sankey_toggle.click()
            await page.wait_for_timeout(1400)

        # Expand Aggregation Tables
        await page.locator('.section-toggle-bar', has_text='Aggregation Tables').first.click()
        await caption(page, "Expanding Aggregation Tables")
        await page.wait_for_timeout(2800)

        # "Expand" (click, applying it as a filter) the STOR PW_tyler... aggregation value
        target = page.locator(
            ".agg-row:has-text('STOR PW_tyler-DESKTOP-W7F98GR_2026_02_03_16_13_59.html')"
        ).first
        await target.scroll_into_view_if_needed()
        await caption(page, "Clicking a Detail value to filter down to a single matching event")
        await page.wait_for_timeout(3200)
        await target.click()
        await page.wait_for_timeout(2600)

        # Drill into the single remaining row in the Data Table
        row_selector = '.section:not(.section-hidden):not(.agg-section) table tbody tr:not(.detail-row)'
        data_row = page.locator(row_selector).first
        await data_row.scroll_into_view_if_needed()
        await caption(page, "Drilling into the single filtered row")
        await page.wait_for_timeout(2400)
        await data_row.click()
        await page.wait_for_timeout(800)

        # Anchor the summary row just below the fixed header - the ASCII
        # Transcript/Hexdump content below it grows taller than the viewport
        # once expanded, so pin the top rather than scroll_into_view_if_needed
        # (which only guarantees the element's *edge* is visible, not that
        # there's room below it to actually see the payload).
        await data_row.evaluate(
            "(row) => { "
            "const header = document.querySelector('.app-header'); "
            "const headerHeight = header ? header.getBoundingClientRect().height : 0; "
            "const rect = row.getBoundingClientRect(); "
            "window.scrollBy(0, rect.top - headerHeight - 8); }"
        )
        await page.wait_for_timeout(600)

        # Show the ASCII Transcript (default view on expand)
        stream_payload = page.locator('.detail-row.visible .stream-payload').first
        await caption(page, "Viewing the ASCII Transcript of the stream")
        await page.wait_for_timeout(4000)  # let the transcript fetch finish + reading time

        # Click Hexdump
        await stream_payload.locator("button.view-tab:has-text('Hexdump')").click()
        await caption(page, "Switching to the Hexdump view")
        await page.wait_for_timeout(3200)

        # Click Expand All
        expand_all_btn = stream_payload.locator("button:has-text('Expand All')")
        await expand_all_btn.click()
        await caption(page, "Expanding all packets in the hexdump")
        await page.wait_for_timeout(2200)

        # Scroll down to reveal more of the expanded hexdump
        for _ in range(5):
            await page.mouse.wheel(0, 350)
            await page.wait_for_timeout(750)
        await page.wait_for_timeout(1500)

        await page.evaluate(CAPTION_REMOVE_JS)
        await page.wait_for_timeout(1000)

        await context.close()
        video_path = await page.video.path()
        await browser.close()

    # Playwright's raw recording is WebM-only; it's a discarded intermediate
    # (see module docstring), not what gets published, so it stays in the
    # temp dir rather than moving into docs/videos/.
    raw_webm_path = video_path

    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        subprocess.run(
            [ffmpeg_path, '-y', '-ss', str(POSTER_TIMESTAMP_SECONDS), '-i', raw_webm_path,
             '-frames:v', '1', '-q:v', '3', POSTER_OUTPUT],
            check=True, capture_output=True,
        )
        print('POSTER_SAVED_AT:', POSTER_OUTPUT)

        subprocess.run(
            [ffmpeg_path, '-y', '-i', raw_webm_path,
             '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '23',
             '-movflags', '+faststart', MP4_OUTPUT],
            check=True, capture_output=True,
        )
        print('MP4_SAVED_AT:', MP4_OUTPUT)
        if os.path.exists(WEBM_FALLBACK_OUTPUT):
            os.remove(WEBM_FALLBACK_OUTPUT)
    else:
        # Can't encode MP4 or extract a poster frame without ffmpeg - fall
        # back to publishing the raw WebM so there's still a video, with a
        # warning that docs/index.md's <video> tag needs a matching WebM
        # <source> added back until this is re-run with ffmpeg available.
        if os.path.exists(MP4_OUTPUT):
            os.remove(MP4_OUTPUT)
        shutil.move(raw_webm_path, WEBM_FALLBACK_OUTPUT)
        print('WEBM_FALLBACK_SAVED_AT:', WEBM_FALLBACK_OUTPUT)
        print('WARNING: ffmpeg not found on PATH - skipped generating '
              'docs/videos/demo.mp4 and docs/videos/demo-poster.jpg. Saved the raw '
              'WebM recording as a fallback instead; add a WebM <source> back to '
              "docs/index.md's <video> tag until ffmpeg is available and this "
              'script is re-run.',
              file=sys.stderr)

    shutil.rmtree(tmp_video_dir, ignore_errors=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000/socrates.html')
    args = parser.parse_args()
    asyncio.run(main(args.base_url))

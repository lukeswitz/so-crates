# AGENTS.md

This file contains agent-focused guidance for maintaining SO-CRATES.

## Updating Vendored Dependencies

SO-CRATES bundles D3 and d3-sankey in `static/` so the application works offline and builds remain deterministic.

### D3

To update to the latest version:

```bash
curl -sL "https://unpkg.com/d3@7/dist/d3.min.js" -o static/d3.min.js
curl -sL "https://unpkg.com/d3-sankey@0.12/dist/d3-sankey.min.js" -o static/d3-sankey.min.js
```

After updating, verify the files load correctly and run the test suite:

```bash
python3 -m unittest discover -v
```

If the copyright year changed, update `static/LICENSE` accordingly.

Check for D3 releases at https://github.com/d3/d3/releases.
Recommended cadence: every 6–12 months, or immediately if a security CVE is announced.

## Backend Architecture

SO-CRATES's backend is split into domain modules. Do not add new logic directly to `socrates.py` — place it in the appropriate module:

| Module | Add here if... |
|---|---|
| `validators.py` | Pure input validation (no HTTP, no I/O). IP/port checks, filename sanitization, URL safety, PCAP magic bytes, ZIP slip prevention. |
| `suricata_analyzer.py` | Anything related to Suricata lifecycle: config setup, rule downloads, spawning subprocesses, processing locks, file extraction. |
| `yara_analyzer.py` | YARA scanning: executable checks, rules download/setup, scanning extracted files, parsing output. |
| `sigma_analyzer.py` | Sigma rule conversion/execution via Zircolite, importing log events, querying Sigma alerts. |
| `file_analyzer.py` | Lightweight file metadata extraction (magic, hashes, strings). |
| `exif_analyzer.py` | EXIF metadata extraction for image/media files. |
| `db.py` | SQLite schema changes, new query functions, index optimization, bulk loading logic. |
| `models.py` | New Suricata event field extraction helpers (parsing JSON fields into typed values). |
| `config.py` | Application-wide constants: size limits, timeouts, thresholds. Adjust here for different deployments. |
| `socrates.py` | Only HTTP handler methods, request/response formatting, and thin orchestration that calls other modules. |

### Handler Conventions

- Use `_send_json(data)` for all JSON responses, `_send_error(code, message)` for errors.
- Extract shared endpoint logic into helper methods on `Handler` (e.g., `_validate_stream_params`).
- Keep `do_GET` and `do_POST` as thin dispatchers via `GET_ROUTES` / `POST_ROUTES` class attributes.

### Frontend Structure

The frontend is split into three files under `static/`:

| File | Content |
|---|---|
| `socrates.html` | HTML shell (one minimal inline theme-restore script in `<head>` to prevent FOUC; otherwise no inline CSS/JS) |
| `static/socrates.css` | All styles |
| `static/socrates.js` | All JavaScript |

`socrates.html` references them via `<link rel="stylesheet" href="static/socrates.css">` and `<script src="static/socrates.js"></script>`.

When updating styles or frontend logic, edit the appropriate split file. Keep `socrates.html` free of inline `<style>` blocks. The single inline `<script>` in `<head>` restores the user's theme before the first paint; keep it minimal and fault-tolerant.

### Theming Conventions

SO-CRATES supports twenty-five themes via CSS custom properties:

- **Catppuccin** — dark theme based on the soothing pastel Catppuccin Mocha palette
- **Ethereal** — dark blue theme with periwinkle accents and soft peach text
- **Everforest** — dark forest-green theme with teal accents and warm earth tones
- **Gruvbox** — dark theme with retro groove colors, aqua accents, and warm muted tones
- **Hackerman** — dark cyberpunk theme with neon mint-green accents and icy cyan text
- **Kanagawa** — dark theme inspired by the Great Wave, with crystal-blue accents and muted ink tones
- **Lumon** — dark monochrome blue theme inspired by the Lumon Industries aesthetic
- **Matte Black** — dark theme with orange/yellow accents
- **Miasma** — dark swampy theme with olive accents and murky rust/gold earth tones
- **Midnight** (default dark theme)
- **Nord** — dark arctic theme with frost-blue accents and aurora colors
- **Osaka Jade** — dark forest theme with jade-green accents and sage/cream text
- **Retro 82** — dark navy theme with warm orange accents and teal highlights
- **Ristretto** — dark coffee-toned theme with salmon accents and warm rose-white text
- **Tokyo Night** — dark theme with blue/purple accents inspired by the Tokyo Night palette
- **Vantablack** — pure monochrome theme with white text on true black
- **CGA** — black background with the classic 4-color CGA Palette 1 High-Intensity hues (cyan, magenta, white)
- **C64** — Commodore 64 blue-on-blue aesthetic, using the real Pepto/VICE C64 16-color palette (blue background, light-blue border/text/accent, cyan interactive highlight)
- **Hacker** — green-on-black terminal aesthetic with a subtle code-rain background
- **Sguil** — light theme inspired by the classic Sguil NSM interface, with gray chrome and navy headers
- **Vaporwave** — dark purple/navy theme with hot-pink accents and cyan/mint/pastel-yellow highlights, evoking the modern (2010s+) vaporwave internet aesthetic
- **Catppuccin Latte** — light theme based on the pastel Catppuccin Latte palette
- **Daylight** (light theme)
- **Rose Pine** — light theme based on the warm Rosé Pine Dawn palette
- **White** — pure monochrome light theme with black text on true white

- **Use CSS variables** (`var(--bg-primary)`, `var(--text-primary)`, `var(--accent)`, etc.) instead of hardcoded hex values for all structural/theme colors.
- **Add theme overrides** in the appropriate `[data-theme="..."]` block (e.g., `light`, `sguil`, `hacker`, `cga`, `c64`, `vaporwave`, `matte-black`, `tokyo-night`, `retro-82`, `ethereal`, `lumon`, `catppuccin`, `catppuccin-latte`, `everforest`, `gruvbox`, `hackerman`, `kanagawa`, `miasma`, `nord`, `osaka-jade`, `ristretto`, `rose-pine`, `vantablack`, or `white`) when a default dark color lacks contrast or does not match the theme's aesthetic.
- **Preserve hardcoded colors** only for functional/data-driven elements (event type colors, severity colors, ASCII transcript direction colors) that must stay consistent across themes.
- **Don't define a variable in every theme block "for completeness" without a real consumer.** `--accent-rgb` and `--filter-bar-bg` were defined identically in all 23 theme blocks but never referenced via `var(--name)` anywhere in CSS/JS/HTML — removed as dead CSS (`test_dead_theme_vars_removed` locks this in). If you add a new per-theme variable, grep for `var(--your-name` before considering it done.
- **`--bg-hover` and `--border-color` are deliberately separate variables.** `--bg-hover` is for hover-state background *fills* (table row hover, button hover); `--border-color` is for border/outline *decorations* (panel borders, header/footer dividers, input borders). Most themes set both to the same value since a muted color works fine for both roles, but don't assume they must match — CGA sets `--border-color` to a bright cyan (`#55ffff`, the real CGA light-cyan RGBI value) while keeping `--bg-hover` a much more muted teal (`#008080`), since a hover *fill* that bright would hurt text contrast but a 1px *border* reads fine at full brightness. `test_border_color_split_from_bg_hover` enforces that every theme defines both and that border declarations reference `var(--border-color)`, not `var(--bg-hover)`.
- **A theme can override structural colors per-selector, not just per-variable, when a single shared variable can't express the look.** CGA's header/footer use `background: #55ffff` (bright light cyan) directly on `[data-theme="cga"] .app-header, [data-theme="cga"] .footer`, rather than repointing `--bg-secondary` (which every other panel/card also uses and would go bright cyan too). When doing this, override `--text-bright`/`--text-muted` scoped to the same selector for legibility against the new background — but if any descendant element (like the gear dropdown menu, a child of `.app-header` but visually its own dark panel) uses those same variables against its *own* different background, reset them back to their normal value scoped to that descendant, or its text will inherit the parent override and become illegible. See `test_cga_header_footer_light_cyan`. Also note the CSS-file-ordering gotcha this ran into: place such overrides *after* the base rule for any selector another test extracts via naive string-splitting (e.g. `.split('.app-header-menu-dropdown {')[1].split('}')[0]`), or the override becomes a second matching substring earlier in the file and the test grabs the wrong block.
- **`--interactive-highlight` is an optional per-theme override for hover/focus/active border feedback.** Every hover/focus/active border rule (`.stat-card:hover`, `.stat-card.tab-active`, `.pagination-page-input:focus`, `.settings-number-input:focus`, `.drop-zone-active`, `.view-tab.active`, `.search-input:focus`, `.sample-card:hover`) reads `var(--interactive-highlight, var(--accent))` — a CSS fallback, so themes that don't define `--interactive-highlight` (all of them except C64) get exactly the old behavior (`--accent`) with zero risk. C64 needs this because its `--accent` is intentionally identical to `--border-color`/`--text-primary` (a deliberate flat, monochrome look the user asked for after trying a distinct accent color first) — without a separate highlight color, hovering/focusing would produce no visible change at all. C64 sets `--interactive-highlight: #67B6BD` (the real C64 palette Cyan — a different shade of blue, not a jarring color swap, per explicit user preference for "another shade of blue" over the initially-tried light green). If you add a new theme where `--accent` intentionally matches `--border-color`, check whether it needs `--interactive-highlight` too.
- **Use `currentColor`** for inline SVG icons so they inherit the surrounding text color and adapt automatically.
- **Avoid emojis** for UI icons when possible — use inline SVGs instead, since emojis render as full-color system glyphs that ignore CSS `color` and may be invisible in one theme.

Theme selection is in the gear icon menu in the upper right corner. The menu shows **Help** first, then a divider, then the **Dark Themes** section (alphabetical: Catppuccin … Vantablack), followed by the **Light Themes** section (alphabetical: Catppuccin Latte … White), followed by the **Fun Themes** section (C64, CGA, Hacker, Sguil, Vaporwave) — this order is `THEME_GROUP_ORDER = ['dark', 'light', 'fun']` in `static/socrates.js`. The `toggleTheme()` hotkey cycle follows this same menu order. The currently applied theme is marked with a ✓ (accent-colored `::before` glyph): each theme button carries `data-theme-option="<key>"`, and `updateThemeMenu()` toggles the `theme-active` class to match `getCurrentTheme()`. It runs from `setTheme()`, `previewTheme()` (so the mark follows hover previews), `init()`, and after every `renderGearMenu()` re-render. Hovering a theme name previews it temporarily; clicking commits it. The user's choice is persisted to `localStorage` as `socrates-theme` and restored on page load to prevent a flash of unstyled content.

To add a new theme:

1. Add it to the `THEMES` registry in `static/socrates.js` with the correct `group` (`'dark'`, `'fun'`, or `'light'`). `setTheme()`, `previewTheme()`, the `toggleTheme()` hotkey cycle, and the `renderGearMenu()` menu buttons are all generated automatically from the registry (menu sections are alphabetical by label within each group).
2. Add a `[data-theme="your-name"]` CSS override block in `static/socrates.css`.
3. Add the corresponding menu button under the correct section in the static `socrates.html` menu (the static menu is what renders before `renderGearMenu()` regenerates it from the registry — keep the two in sync). The button should use `onmouseenter="previewTheme('your-name')"`, `onmouseleave="revertTheme()"`, and `onclick="commitTheme('your-name')"`.
4. If the theme needs a custom favicon, add `static/favicon-your-name.svg` — `updateFavicon()` resolves per-theme favicons by naming convention (the `dark` and `light` themes use the plain `static/favicon.svg`).
5. Add any theme-specific runtime behavior (e.g. background effects) and gate it on `getCurrentTheme()`.
6. Add it to the `THEMES` list in `scripts/capture_screenshots.py` (a separate hardcoded list, not derived from the registry) and re-run the script to generate its Themes-page screenshot - see the Release Checklist below.
7. If it's a Fun-group theme, consider giving it a typed cheat code (see the `keyBuffer` easter eggs in the `keydown` listener in `static/socrates.js` - CGA/Hacker/Sguil all have one). Use `keyBuffer.endsWith('yourcode')` rather than `===` - the buffer holds the last 5 keys typed session-wide, so a code shorter than 5 characters checked with `===` would only ever match in the first few keystrokes after page load. Document the code in parentheses next to the theme on the Themes page (`docs/themes.md`).

## Docs Site Maintenance

User-facing documentation lives on the MkDocs Material site built from `docs/*.md` (config in `mkdocs.yml`, deployed by `.github/workflows/docs.yml`). When adding, removing, or renaming a docs page, update `mkdocs.yml`'s `nav:` list to match — pages not listed there still build but won't appear in the site navigation. `README.md` itself stays a short landing page (tagline, screenshots, links out to the docs site) and should not grow a Table of Contents again; new content belongs in `docs/`, not README.

Preview changes locally before pushing: `pip install -r requirements-docs.txt && mkdocs serve` (use `mkdocs serve -a 127.0.0.1:8001` if SO-CRATES' own server is already running on its default port 8000). Run `mkdocs build --strict` to catch broken internal links — this fails the build the same way the deploy workflow does.

## Release Checklist

Before cutting a release:

1. **Regenerate screenshots.** Start the server (`python3 socrates.py`), then run
   `pip install -r requirements-screenshots.txt && python3 scripts/capture_screenshots.py`.
   This refreshes all 6 `docs/images/so-crates-*.png` (Home page) and all 25
   `docs/images/themes/*.png` (Themes page) against the app's own built-in
   sample pcap (`DEFAULT_SAMPLE_URL` in `static/socrates.js`) — no local
   fixture or hardcoded MD5 needed, works on a clean checkout with an empty
   `DATA_DIR`. Run this on every release, not just when the UI visibly
   changes — stale screenshots (e.g. showing an old default value in the
   Welcome modal) are easy to miss otherwise. If a new theme was added since
   the last release, it's automatically included (the script reads the same
   `THEMES` list convention from `static/socrates.js`).
2. **Regenerate the demo video.** With the server still running, run
   `python3 -m playwright install ffmpeg` (one-time; Playwright's video
   muxing needs its own bundled ffmpeg, separate from any system ffmpeg)
   then `python3 scripts/record_demo.py`. This re-records the workflow
   end-to-end (sample pcap → each data type → All Events → Aggregation
   Tables filtering → drill-down → ASCII Transcript → Hexdump) and
   publishes `docs/videos/demo.mp4` (H.264/AAC, re-encoded via a system
   `ffmpeg` binary from Playwright's raw WebM capture — MP4 is used rather
   than WebM since it's universally browser-supported and is also the
   format required to upload the same clip directly to
   X/Instagram/LinkedIn/Facebook), embedded on the Home page just above
   Screenshots. If `ffmpeg` isn't on PATH, it falls back to publishing the
   raw `docs/videos/demo.webm` instead with a warning — see the script's
   module docstring. Re-run whenever the recorded workflow's on-screen
   text/labels change (e.g. a renamed button or tab) even if nothing else
   about the release does — the captions are hardcoded to match specific
   UI strings and will look wrong (or the script will fail to find an
   element) if those drift.
3. **Review the diff** of the regenerated PNGs (`git diff --stat docs/images/`)
   before committing — a near-identical diff for every file usually means
   nothing meaningful changed; a few files changing more than the rest is
   worth a manual look to confirm it's an intended UI change, not a bug.
4. Update `docs/release-notes.md` (the single source of truth — `README.md`
   links directly to it, there's no separate root-level stub) and bump the
   version shown in the app footer / `docs/api.md`'s `/api/version` example
   if it changed.
5. **Go through each page of the docs and make sure it is accurate.** Don't
   just proofread — verify claims (endpoint shapes, config defaults, file
   layouts, dependency lists, test counts) directly against the current
   source (`socrates.py`, `db.py`, `validators.py`, `config.py`,
   `Dockerfile`, `static/socrates.js`, `tests/*.py`), not against what the
   docs already say or what a prior release looked like. Docs drift
   silently as the app changes underneath them, and even a hardcoded
   *count* standing in for a full list (event types, columns, tests) goes
   stale the same way a full list would — see `docs/filtering.md`'s
   "Per-type columns are not enumerated here" note. Re-run
   `mkdocs build --strict` after each fix.
6. **Review all source and docs** for spelling errors, grammar issues, logic
   issues, security issues, orphaned code, and code that needs refactoring.
   Cover the whole tree, not just what changed since the last release —
   issues introduced several releases back are just as worth catching. Fix
   what's clearly correct to fix; for anything that implies a design
   decision (e.g. removing a function with no caller vs. wiring it up),
   flag it and confirm before acting rather than guessing.
7. Run the full test suite (`python3 -m unittest discover -v`) and
   `mkdocs build --strict` before pushing.

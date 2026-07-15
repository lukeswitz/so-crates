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

SO-CRATES supports four themes via CSS custom properties:

- **Midnight** (default dark theme)
- **Matte Black** — AMOLED-style dark theme with orange/yellow accents
- **Hacker** — green-on-black terminal aesthetic with a subtle code-rain background
- **Daylight** (light theme)

- **Use CSS variables** (`var(--bg-primary)`, `var(--text-primary)`, `var(--accent)`, etc.) instead of hardcoded hex values for all structural/theme colors.
- **Add theme overrides** in the appropriate `[data-theme="..."]` block (e.g., `light`, `hacker`, or `matte-black`) when a default dark color lacks contrast or does not match the theme's aesthetic.
- **Preserve hardcoded colors** only for functional/data-driven elements (event type colors, severity colors, ASCII transcript direction colors) that must stay consistent across themes.
- **Use `currentColor`** for inline SVG icons so they inherit the surrounding text color and adapt automatically.
- **Avoid emojis** for UI icons when possible — use inline SVGs instead, since emojis render as full-color system glyphs that ignore CSS `color` and may be invisible in one theme.

Theme selection is in the gear icon menu in the upper right corner. The menu shows **Help** first, then a divider, then the **Dark Themes** section (Midnight, Matte Black, Hacker), followed by the **Light Themes** section (Daylight). Hovering a theme name previews it temporarily; clicking commits it. The user's choice is persisted to `localStorage` as `socrates-theme` and restored on page load to prevent a flash of unstyled content.

To add a new theme:

1. Add it to the `THEMES` registry and `setTheme()`/`previewTheme()` logic in `static/socrates.js`.
2. Add a `[data-theme="your-name"]` CSS override block in `static/socrates.css`.
3. Add the corresponding menu button under the correct section in the static `socrates.html` menu and in the `renderGearMenu()` helper in `static/socrates.js`. The button should use `onmouseenter="previewTheme('your-name')"`, `onmouseleave="revertTheme()"`, and `onclick="commitTheme('your-name')"`.
4. If the theme needs a custom favicon, add the SVG file and update `updateFavicon()` in `static/socrates.js`.
5. Add any theme-specific runtime behavior (e.g. background effects) and gate it on `getCurrentTheme()`.

## README Maintenance

When adding, removing, or renaming sections in `README.md`, always update the **Table of Contents** at the top of the file. GitHub auto-generates anchor IDs from heading text (lowercased, spaces→hyphens, special chars stripped). Duplicate heading names get `-1`, `-2`, etc. suffixes.

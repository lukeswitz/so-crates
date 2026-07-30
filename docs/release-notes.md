# Release Notes

## 3.1.0

### OhMyDebn theme sync

A new opt-in "Sync theme with OS" setting (off by default, in the Themes
modal) lets SO-CRATES follow OhMyDebn desktop theme switches automatically.
A `GET /api/theme` endpoint reads the active theme's name and color
palette from a single `OHMYDEBN_THEME_DIR` environment variable (unset
outside an OhMyDebn/podman launch, so this is a no-op for every other
deployment), by convention at `<OHMYDEBN_THEME_DIR>/current/theme.name`
and `<OHMYDEBN_THEME_DIR>/current/theme/`, and the frontend polls it once
a second while the tab is visible.

- A theme name that matches one of SO-CRATES's built-in themes is applied
  directly, with a toast: "Changed SO-CRATES theme to `<name>` to match
  OhMyDebn".
- For a custom or Aether-generated theme with no built-in match, a full
  theme (~25 CSS custom properties) is instead synthesized at runtime from
  the theme's raw color palette, with a toast: "Generated color palette
  from OhMyDebn theme `<name>`". Three source formats are supported, tried
  in order against real installed themes until one works: the native
  `colors.toml`'s numbered `color0`-`color15` ANSI-slot scheme; the same
  file's alternate semantic-named scheme (`red`/`blue`/`bright_red`/
  `muted`/..., used by at least one of OhMyDebn's own bundled themes); and
  `alacritty.toml` (standard `[colors.primary]`/`[colors.normal]`/
  `[colors.bright]` tables), including its `0xrrggbb` hex variant and
  themes that omit `[colors.bright]` entirely (falls back to `[colors.normal]`
  per color). Every derived text/accent color (`--text-muted`,
  `--tag-*-text`, `--badge-*-text`, `--accent`) is nudged as needed to meet
  a real WCAG 3:1 contrast ratio against the derived background, so a
  low-contrast source palette can't make labels/headings unreadable.
  Verified against all themes bundled with a real OhMyDebn installation.
- If neither a known theme nor a usable palette is available, sync
  disables itself and SO-CRATES reverts to Midnight, with a sticky toast
  explaining why (click, or its "Open Themes" link, to dismiss).

### Rule updates moved to an on-demand Rules modal

Suricata/YARA/Sigma rule updates no longer block server startup. A new
"Rules" entry in the gear menu opens a modal showing each ruleset's current
rule count and last-updated time, with an independent "Update" button per
ruleset plus "Update All", streaming live progress. Startup now only does
the fast local bootstrap (no network) and prints a message pointing users
at the new Rules modal instead of the old startup rule-check.

### About modal and manual update checks

A new "About" entry in the gear menu opens a modal with the current
version, tagline, a "Made with ♥ by defenders for defenders - Sponsored by
Security Onion Solutions, LLC" line, and Documentation/GitHub links. The
"Check GitHub for newer releases" checkbox and its manual "Check Now"
button (added alongside the existing opt-in automatic check, not
replacing it) moved here from Settings. The footer's "SO-CRATES" link now
opens this modal instead of navigating to GitHub (the "Update available"
badge still links directly to the GitHub release).

### Theme renames and additions

- **C64 → Breadbin Blue**, **MS-DOS Blue → DOS Blue**, **Windows XP → Luna
  Blue** — both the display label and the underlying registry key/cheat
  code changed (`c64`→`breadbin-blue`/`bread`, `msdos`→`dos-blue`/`dos`,
  `winxp`→`luna-blue`/`luna`), to move away from specific product/console
  branding.
- Two new Fun themes: **Digital Frontier** (a Tron-inspired look, cheat
  code `digit`) and **Retro Handheld** (a Game Boy-inspired 4-shade green
  look, cheat code `retro`) — named generically for the same reason.

### Other UI fixes

- All modals now dismiss via Escape or a backdrop click, not just their
  close button.
- The Help modal links to https://so-crates.org.
- The Themes modal's "Sync theme with OS" toggle moves to the top and
  hides the manual picker while enabled, since OhMyDebn owns the theme
  while sync is on.

### YARA Forge / Sigma rule freshness

`setup_yara_rules()`/`setup_sigma_rules()` previously used a cached rules
file forever once downloaded or copied from the Docker image, with no
freshness check — a long-lived install's rules could silently drift
arbitrarily far behind YARA Forge's weekly and Zircolite-Rules-v2's daily
upstream releases. Both now refresh a cached copy in place if it's older
than 24 hours and the network is reachable, falling back to the
still-usable stale copy on any refresh failure rather than losing rules
entirely. The three potentially-stale sources (YARA, Sigma windows, Sigma
linux) share a single reachability probe instead of each blocking through
its own timeout, so a slow/unreachable network adds at most ~5s to
startup instead of ~15s.

Also fixed while touching the download path: `_download_yara_forge_rules`
and `_download_rule_file` used to write straight into the destination
file, which would have corrupted an already-good cached copy if a refresh
failed partway through. Both now write to a temp file and rename
atomically into place.

## 3.0.0

### Suricata upgraded to 8.0.6

SO-CRATES now installs Suricata from Debian's `trixie-backports` repo
(8.0.6) instead of the base `trixie` repo's 7.0.10, along with
`suricata-update` 1.3.8 (fixes a real security issue — arbitrary file write
via path traversal in rule archive extraction, OISF redmine #8633). This
applies to both the Dockerfile and bare-metal installs.

**Critical fix that came with the upgrade:** Suricata 8 silently changed DNS
logging to a new default format — `dns.rrname`/`dns.rrtype`, read directly
by every DNS column in the UI, no longer exist at the top level at all (the
same data moved to `dns.queries[0]`). This broke the `dns` tab completely
(Query/Type went blank) — one of the highest-volume, most-viewed tabs in the
app. Fixed with a fallback that keeps working for previously-stored
analyses from Suricata 7 too.

### New and fixed protocol support

- **enip** and **ntp** now produce real events — Suricata 7.0.10 detected
  both correctly but had no eve-log output module for either, so nothing
  ever reached the UI regardless of config. Both work now that Suricata 8
  ships the loggers.
- **websocket, pop3, mdns, ldap** — full column, filtering, and aggregation
  support for these protocols, new in Suricata 8.
- **arp** — decode-layer logging support added, but kept **off by default**
  (Suricata's own stance: "many events can be logged"). A live test across
  35 sample captures showed ARP at up to 12% of events in a realistic
  multi-host capture. Set the `ENABLE_ARP_LOGGING` environment variable to
  opt in.
- 18 previously-enabled-but-unsupported Suricata protocols gained full
  column/aggregation support for the first time (previously falling back to
  a generic 6-column view): quic, dhcp, ftp_data, smb, ssh, krb5, sip, snmp,
  mqtt, http2, dcerpc, rdp, tftp, ike, nfs, rfb, bittorrent_dht, smtp — plus
  `ftp` and `anomaly`, which predated this work but had the same gap.
- Fixed real data-shape bugs found while verifying against real traffic:
    - `quic.ja3`/`ja3s` are objects (`{hash, string}`), not plain strings —
      previously rendered as the literal text `[object Object]`.
    - `rfb.client_protocol_version`/`server_protocol_version` are `{major,
      minor}` objects, and `security_type` is nested under `authentication`,
      not top-level.
    - `anomaly.message` was read in three separate places (a field that has
      never existed in Suricata's eve.json) — the real field is
      `anomaly.event`.
    - HTTP/2 traffic (including cleartext h2c) is always logged by Suricata
      under `event_type: "http"`, never a separate `"http2"` type — removed
      dead code that assumed otherwise; real HTTP/2 traffic already renders
      correctly under the existing `http` tab.
- Fixed a Suricata config-generation bug: re-running setup on an
  already-provisioned install could silently stop adding any newly-added
  protocol to eve-log output, once earlier protocols had already been
  inserted.

### Performance & scalability

- Aggregation tables and the Sankey diagram are now computed server-side
  (`GET /api/aggregation-data`, `GET /api/sankey-data`) via SQL `GROUP BY`,
  scaling with the query instead of the full dataset size, with unfiltered
  results cached per-analysis.
- Uploads are now parsed as a stream instead of buffered in memory — peak
  memory no longer scales with upload size. Leftover temp files from an
  upload interrupted by a server crash are now swept on the next startup.
- Upload size limit raised from a fixed 1,000 MB to a user-configurable
  ceiling (up to 5,000 MB hard max) via Settings; a disk-space check now
  runs before accepting an upload.
- Query result limit raised from 5,000 to a user-configurable ceiling (up
  to 100,000 hard max) via Settings.

### UI

- 20 new themes (25 total, up from 5), grouped into Dark / Light / Fun
  sections in the gear menu, each with its own favicon — including three
  new Fun themes: **CGA** (classic 4-color CGA Palette 1 High-Intensity —
  black background, cyan/magenta/white), **C64** (Commodore 64 blue-on-blue
  aesthetic, using the real Pepto/VICE C64 16-color palette — blue
  background, light-blue border/text/accent, including the header's
  "SO-CRATES" logo, for a deliberately flat, monochrome resting look, with a
  distinct cyan `--interactive-highlight` for hover/focus/active borders so
  those states are still visible), and **Vaporwave** (a modern, non-retro
  counterpart to the other three — dark purple/navy background with hot-pink
  accents and cyan/mint/pastel-yellow highlights, evoking the 2010s+
  vaporwave internet aesthetic rather than nostalgia for old hardware).
- The active theme is now marked with a checkmark in the gear menu.
- Each Fun theme (C64, CGA, Hacker, Sguil, Vaporwave) now has its own typed
  cheat code — type it anywhere outside a text field to switch instantly. See
  [Themes](themes.md) for the codes.
- The gear menu's Fun Themes section now appears after Light Themes
  instead of between Dark and Light (`THEME_GROUP_ORDER` in
  `static/socrates.js` is now `['dark', 'light', 'fun']`); the `t` hotkey
  cycle follows the same updated order.
- CGA's header/footer text (the "SO-CRATES" logo, tagline, filename, and
  date/MD5 metadata) is now the CGA magenta accent instead of black/dark
  teal, matching the rest of the CGA palette more closely.
- **Sguil's expanded data-table rows had mismatched field backgrounds**:
  when a light-blue zebra-striped row (`nth-of-type(4n+3)`) was expanded,
  each field's *value* box stayed stark white instead of matching the
  light-blue row, looking like a patchwork of mismatched boxes. `.detail-value`
  now follows the row's light-blue background in that case; `.detail-label`
  intentionally keeps its own light-cyan background on every row.

### Documentation

- Docs now live on a real site (MkDocs Material, deployed to GitHub Pages)
  instead of a single growing README plus a handful of unlinked `docs/*.md`
  files. `README.md` is now a short landing page (tagline, a screenshot,
  and links out to the docs site); everything else — installation
  (Docker/Podman/OhMyDebn/Manual), usage, themes, configuration, security,
  architecture, the API reference, and the filtering design doc — is now
  properly cross-linked, searchable, and navigable instead of split across
  files with no shared nav.
- The Themes page shows a real screenshot of every one of the 25 themes,
  grouped under Dark/Light/Fun headings, click-to-zoom.
- Added `scripts/capture_screenshots.py` to regenerate every docs screenshot
  in one run against the app's own built-in sample pcap — no local fixture
  or hardcoded analysis needed.
- Added a recorded demo video (`scripts/record_demo.py`, Playwright) to the
  Home page, walking through a sample analysis end-to-end: upload, each
  data tab, All Events, Aggregation Tables filtering, drill-down, ASCII
  Transcript, and Hexdump. Published as an H.264/AAC MP4 (re-encoded from
  Playwright's raw WebM capture) rather than WebM directly, since MP4 is
  universally browser-supported and is also the format required to upload
  the same clip directly to X/Instagram/LinkedIn/Facebook.
- The Architecture page is now split into focused subpages (Overview, Data
  Storage, Database, Event Types, UI, Security Model, Test Coverage)
  instead of one long page, matching Installation's existing
  Overview/Docker/Podman/OhMyDebn/Manual split.
- Went through every docs page and verified its claims directly against
  current source rather than trusting what the docs already said — fixed
  real drift in the API reference (missing endpoint, wrong response
  shapes, a fictional error code), the security page, the architecture
  page, and several others (stale file-layout diagrams, wrong config
  defaults, stale test/column counts).

### Other fixes

- **CGA theme's borders read as dark green instead of cyan**: every
  border/panel-outline in the app was driven by `--bg-hover`, which also
  doubles as the hover-state background fill. CGA's `--bg-hover` (`#004040`)
  had equal green/blue channels at low brightness — green dominates human
  luminance perception far more than blue, so the color skewed
  green-looking despite being a "pure cyan" hue numerically. Fixed properly
  by splitting borders into their own `--border-color` variable, distinct
  from `--bg-hover`: CGA's `--border-color` is now the real CGA light-cyan
  RGBI value (`#55ffff`, verified by sampling pixel colors from an actual
  CGA Palette 1 High-Intensity game screenshot), while `--bg-hover` stays a
  muted `#008080` teal so hover-state fills don't get uncomfortably bright
  behind white text. Every other theme sets both variables to the same
  value they always rendered as, so this is a no-visible-change refactor
  for the other 22 themes.
- **CGA header/footer now use bright light cyan instead of near-black**: the
  dark `--bg-secondary` background shared with every panel/card was making
  the header and footer blend into the rest of the black-on-teal UI in a
  way that read poorly. CGA's `.app-header`/`.footer` now use the real CGA
  light-cyan background (`#55ffff`) directly, with `--text-bright`/
  `--text-muted` switched to dark colors scoped to that same rule for
  legibility. The gear dropdown menu (a child of the header in the DOM, but
  rendered on its own dark panel) resets those two variables back to their
  normal light values so its own text doesn't inherit the header's dark
  override.
- **Dead CSS custom properties removed**: `--accent-rgb` and
  `--filter-bar-bg` were defined identically in all 23 theme blocks but
  never referenced anywhere via `var(--name)` in CSS/JS/HTML. Removed, with
  a test (`test_dead_theme_vars_removed`) to keep them from quietly coming
  back. (`--border-color` was briefly removed alongside these for the same
  reason, then reintroduced with the real purpose described above.)
- **Upload disk-space check used the wrong number**: `/api/upload`'s
  upfront disk-space check was sized against the raw `Content-Length` of
  the request, not the resolved upload-size ceiling (`effective_max`) — a
  compressed upload (e.g. a ZIP) can have a `Content-Length` far smaller
  than what it's allowed to expand to, so the check could pass even when
  there wasn't really enough room. `/api/load-url` already checked against
  `effective_max`; `/api/upload` now does too.
- **Load-from-URL password gap**: `/api/load-url` only ever tried the
  MTA-style dated password (`infected_YYYYMMDD`) when a URL's path matched
  `/YYYY/MM/DD/` on `malware-traffic-analysis.net` — any other password
  attempt was skipped entirely, unlike `/api/upload`, which always tries
  the plain `infected` password regardless of source. `/api/load-url` now
  always tries `infected` too (cheap, harmless even when it doesn't apply),
  trying the MTA dated variant first when the URL matches.
- Fun-theme cheat codes shorter than 5 characters (e.g. `cga`) only ever
  matched in the first few keystrokes after page load, since the
  keystroke buffer they were checked against stays a fixed 5 characters
  once filled and the check used `===` instead of `.endsWith()`. Fixed
  for all three codes (`cga`, `31337`, `sguil`).
- The Welcome modal's help text had a hardcoded `Maximum file size is
  1000MB.` string that never reflected reality once upload size became
  user-configurable (see Performance & scalability, above) — a user who'd
  raised their own ceiling in Settings still saw the stale default with no
  indication it was adjustable. Now computed from the user's actual
  effective limit each time the modal opens.
- `extractAllValue()`'s `'Command'`/`'Message'` column overrides were stale
  and actively wrong — `Command` ignored pgsql/enip/pop3's own real command
  fields in the "All Events" view, and `Message` read the same
  never-existed `anomaly.message` field. Both removed in favor of the
  already-correct per-protocol handling.
- Fixed the equivalent `anomaly.message` bug in the event detail side panel.
- `docs/FILTERING.md`'s "Column Overlap" reference table, which had grown
  stale over many protocol additions, now points at the actual source of
  truth (`getColumnsForType()`) instead of duplicating an ever-drifting list.
- **Podman Compose deployment bug**: `docker-compose.podman.yml`'s
  `user: "${UID}:${GID}"` silently resolved to an empty `user: ":"` when
  following the README's exact instructions, since bash doesn't export
  `$UID`/`$GID` by default - this forced the container to run as root
  instead of the current user, defeating the whole point of the
  `userns_mode: keep-id` volume-permission mapping. Confirmed by actually
  building and running the image. README now has users write a `.env` file
  instead of relying on a shell export, since `podman compose` reads that
  automatically from any terminal, including for a later `down`/`restart`.

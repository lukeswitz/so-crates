# API Reference

Base URL: `http://localhost:8000`

All endpoints return `Content-Type: application/json` unless noted. Errors return `{"error": "<message>"}` with the appropriate HTTP status code.

## GET Endpoints

### `GET /`

Redirects to `/socrates.html`.

---

### `GET /api/version`

Returns the running SO-CRATES version.

**Response:** `{"version": "3.1.0"}`

---

### `GET /api/version-check`

Checks GitHub's releases API for a newer SO-CRATES version. Only ever called by the frontend if the user has opted in (the "Check GitHub for newer releases" checkbox in the About modal, or its manual "Check Now" button) - never fetched automatically otherwise.

**Response:** `{"currentVersion": "<version>", "latestVersion": <string or null>, "updateAvailable": <boolean>}` - `latestVersion`/`updateAvailable` stay `null`/`false` on any failure to reach GitHub (never surfaces an error to the caller).

---

### `GET /api/theme`

Reads the active OhMyDebn theme's name and color palette, for the opt-in "Sync theme with OS" feature. A no-op (`theme`/`customColors` both `null`) unless the `OHMYDEBN_THEME_DIR` environment variable is set.

**Response:** `{"theme": <string or null>, "customColors": <object or null>}` - `theme` is the raw theme name (from `<OHMYDEBN_THEME_DIR>/current/theme.name`) if it's set and passes a loose name-format check, else `null`. `customColors` is a set of ~25 CSS custom-property name/hex-value pairs synthesized from the theme's `colors.toml`/`alacritty.toml` palette (see [Themes](themes.md)), or `null` if no theme directory is configured or no palette could be derived.

---

### `GET /api/theme-sync-available`

Tells the frontend whether the "Sync theme with OS" toggle could ever do anything, so it isn't shown as a dead control on deployments not launched via OhMyDebn.

**Response:** `{"available": <boolean>}` - `true` iff `OHMYDEBN_THEME_DIR` is set and its `current/theme.name` file is currently readable (regardless of whether its *contents* are valid - that's `/api/theme`'s concern).

---

### `GET /api/events`

Returns event data from Suricata's eve.json (via SQLite index or direct JSON parse).

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | No | none | MD5 hash of a historical analysis (returns an empty array if omitted) |
| `type` | No | all | Filter by event type - any `event_type` Suricata's eve.json can produce (see [Event Types](architecture/event-types.md)), plus the app's own synthetic types (`filealerts`, `log`, `sigmaalert`) |
| `q` | No | none | Full-text search query (searches all event JSON). Multiple `q` params AND together. |
| `offset` | No | `0` | Pagination offset |
| `limit` | No | `1000` | Max events to return (capped at `MAX_QUERY_LIMIT`, 100,000 by default - see `GET /api/limits`) |
| `order_by` | No | none (sorts by `timestamp`) | Server-side sort column, e.g. `Source IP`. Only sortable for columns with a static JSON path for the given `type` (mirrors the same source-of-truth constraint as `GET /api/aggregation-data`); silently falls back to `timestamp` if the column isn't server-sortable for that type, rather than erroring |
| `sort_dir` | No | `asc` | `asc` or `desc`; any other value is treated as `asc` |

**Response:** Array of eve.json event objects.

**Example:**
```
GET /api/events?type=alert&limit=100
GET /api/events?q=192.168.1.1
GET /api/events?type=http&q=GET
GET /api/events?q=tcp&q=80          # AND: events containing both "tcp" and "80"
```

---

### `GET /api/stats`

Returns event-type counts for the current or specified analysis.

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | Yes | — | MD5 hash of a historical analysis |
| `q` | No | none | Full-text search query (counts only matching events). Multiple `q` params AND together. |

**Response:** `{"counts": <event type to count map>, "date_range": {"min": <timestamp or null>, "max": <timestamp or null>}}`

**Example:**
```json
{"counts": {"alert": 42, "dns": 1500, "http": 380, "tls": 95, "flow": 2200},
 "date_range": {"min": "2026-02-03T11:13:50.123456+0000", "max": "2026-02-03T11:16:02.654321+0000"}}
```

---

### `GET /api/count`

Returns total event count, optionally filtered by type or search query.

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | Yes | — | MD5 hash of a historical analysis |
| `type` | No | all | Filter by event type |
| `q` | No | none | Full-text search query (counts only matching events). Multiple `q` params AND together. |

**Response:** `{"count": <number>}`

---

### `GET /api/limits`

Returns server-enforced limits the client should respect (e.g. when validating the user-configurable query-limit setting).

**Response:** `{"maxQueryLimit": <number>, "maxUploadSize": <number>}` - `MAX_QUERY_LIMIT` (100,000 by default) and `MAX_UPLOAD_SIZE` in bytes (5,000 MB by default); both are hard ceilings that any client-requested override (`limit=`, or the `X-Max-Upload-Size` upload header) is clamped to server-side, regardless of what the client requests.

---

### `GET /api/rules-info`

Returns on-disk rule counts and last-updated times for all three rulesets, for the Rules modal (gear menu > Rules). Purely a snapshot of what's currently on disk - no job/update state involved (that's `/api/rule-update-status`'s job).

**Response:** `{"suricata": {"count": <number or null>, "updated": <epoch or null>}, "yara": {"count": <number or null>, "updated": <epoch or null>}, "sigma": {"windows": {"count": ..., "updated": ...}, "linux": {"count": ..., "updated": ...}}}` - fields are `null` if that ruleset has never been set up.

---

### `GET /api/rule-update-status`

Returns the live/last-run state of each ruleset's update job, polled by the Rules modal while open.

**Response:** `{"suricata": {"running": <boolean>, "lines": [<string>, ...], "done": <boolean>, "error": <string or null>}, "yara": {...}, "sigma": {...}}` - `lines` accumulates progress messages for the current (or most recent) run of that ruleset.

---

### `POST /api/update-rules`

Starts an update for one ruleset, or all three. Triggered by the Rules modal's per-ruleset "Update" buttons and its "Update All" button.

**Request body:** `{"ruleset": "suricata"|"yara"|"sigma"|"all"}`

**Response:** `{"status": "started"}`

**Errors:** `400` if `ruleset` isn't one of the four allowed values. `409` ("Rule update already in progress") if the targeted ruleset (or, for `"all"`, any one of the three) is already running.

---

### `GET /api/sankey-data`

Returns a pre-aggregated `{nodes, links}` Sankey diagram (Source IP → Dest IP → Dest Port) computed server-side via `GROUP BY`, so the payload stays small regardless of how many events match - the client never needs to fetch raw events to render the diagram.

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | Yes | — | MD5 hash of the analysis |
| `type` | No | all | Filter by event type |
| `q` | No | none | Full-text search query. Multiple `q` params AND together. |

**Response:**
```json
{"nodes": [{"id": "0:1.2.3.4", "name": "1.2.3.4", "column": 0}, ...],
 "links": [{"source": "0:1.2.3.4", "target": "1:5.6.7.8", "value": 42}, ...]}
```
Each column is capped to the top 50 nodes by event count; the remainder is bucketed into a synthetic `Other` node per column so the response size doesn't grow with the dataset. `column` is `0` (Source IP), `1` (Dest IP), or `2` (Dest Port).

Unfiltered (no `q`) responses are cached server-side per `(md5, type)` and invalidated on delete/reanalyze - repeat requests for the same view are effectively instant.

---

### `GET /api/aggregation-data`

Returns per-column frequency tables (top 10 values by count) for the given event type, computed server-side - the data behind the "Aggregations" panel.

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | Yes | — | MD5 hash of the analysis |
| `type` | No | all (merged view) | Event type (see [Event Types](architecture/event-types.md)), or omitted for the merged "All Events" view. Not supported for event types whose fields have no static JSON path to aggregate on server-side - currently `log`/`sigmaalert`/`binary` (dynamic/untrusted columns) and `mqtt`/`ldap` (dynamically keyed by message/operation subtype) - these fall back to client-side computation instead; see `AGGREGATION_JSON_PATHS` in `db.py` for the authoritative, current list. |
| `q` | No | none | Full-text search query. Multiple `q` params AND together. |

**Response:** Object mapping column label to an array of `{"value": ..., "count": ...}`, sorted descending by count and capped to the top 10.
```json
{"Protocol": [{"value": "TCP", "count": 1200}, {"value": "UDP", "count": 340}],
 "Source IP": [{"value": "10.0.0.5", "count": 88}, ...]}
```

Unfiltered (no `q`) responses are cached server-side per `(md5, type)`, same as `/api/sankey-data`.

---

### `GET /api/download-stream`

Carves a single TCP/UDP stream from the PCAP using `tcpdump` and returns it as a `.pcap` download.

**Query Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `src` | Yes | Source IP address |
| `sport` | Yes | Source port |
| `dst` | Yes | Destination IP address |
| `dport` | Yes | Destination port |
| `md5` | Yes | MD5 hash of a historical analysis |

**Response:** `application/vnd.tcpdump.pcap` file download.

**Validation:** IP addresses and ports are validated before passing to tcpdump. Invalid values return `400`.

---

### `GET /api/ascii-stream`

Extracts ASCII payload from a TCP/UDP stream using `tshark`. Tries TCP first, falls back to UDP. Truncated to `MAX_TRANSCRIPT_SIZE` characters (100,000 by default), capped to the first `MAX_TRANSCRIPT_LINES` lines (500 by default) once that threshold is hit.

**Query Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `src` | Yes | Source IP address |
| `sport` | Yes | Source port |
| `dst` | Yes | Destination IP address |
| `dport` | Yes | Destination port |
| `md5` | Yes | MD5 hash of a historical analysis |

**Response:** `application/json` — `{"lines": [{"text": "...", "direction": "src"|"dst"}, ...], "truncated": false}`. Non-printable characters replaced with `.`. Each line is tagged with which side of the connection sent it.

---

### `GET /api/hexdump-stream`

Extracts per-packet hex dumps from a TCP/UDP stream using `tcpdump -X`. Truncated to 100,000 characters or 500 packets.

**Query Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `src` | Yes | Source IP address |
| `sport` | Yes | Source port |
| `dst` | Yes | Destination IP address |
| `dport` | Yes | Destination port |
| `md5` | Yes | MD5 hash of a historical analysis |

**Response:** `application/json` — `{"packets": [{"header": "...", "lines": ["..."]}], "truncated": false}`.

**Validation:** IP addresses and ports are validated before passing to tcpdump. Invalid values return `400`.

---

### `GET /api/analyses`

Lists all previously-analyzed files.

**Response:** Array of `{"md5": "<hash>", "name": "<display name>"}` sorted alphabetically by name.

---

### `GET /api/load-analysis`

Loads a historical analysis by MD5.

**Query Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `md5` | Yes | MD5 hash of the analysis to load |

**Response:**
```json
{"success": true, "md5": "<hash>", "file_name": "<filename>"}
```

**Errors:** `400` if MD5 is invalid or path is unsafe. `404` if analysis not found. `400` if eve.json exceeds size limit.

---

### `GET /api/pcap-path`

Returns the filename (not the full filesystem path) of the PCAP file within an analysis's directory.

**Query Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `md5` | Yes | MD5 hash of the analysis |

**Response:** Plain text path. `404` if no PCAP found.

---

### `GET /api/status`

Same status information as `POST /api/check-status`, but accessible via query parameters for read-only polling.

**Query Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `md5` | Yes | MD5 hash of the analysis |

**Response:**
```json
{"status": "ready", "meta": {"version": 1, "original": "<filename>", "extracted": "<filename>", "detected_type": "pcap", "extracted_at": "<ISO timestamp>"}}
```
or
```json
{"status": "processing", "phase": "network", "meta": {...}}
```
or, if analysis (Suricata/YARA/Zircolite) failed:
```json
{"status": "error", "message": "<failure reason>"}
```

`meta` is present whenever `.meta` exists for the analysis (written after the file type is detected) and is omitted otherwise; it's absent entirely from the `error` response.

**Errors:** `400` for invalid or malformed MD5. There is no `404` for a well-formed MD5 that doesn't correspond to an existing analysis directory — the directory's absence just reads the same as "not ready yet" (`{"status": "processing", "phase": ""}`), since this endpoint never separately checks for the directory's existence.

---

### `GET /api/sigma-alerts`

Returns Sigma alerts stored in `events.db` for the specified analysis.

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | No | none | MD5 hash of a historical analysis (returns an empty array if omitted) |
| `offset` | No | `0` | Pagination offset |
| `limit` | No | `1000` | Max alerts to return (capped at `MAX_QUERY_LIMIT`, 100,000 by default - see `GET /api/limits`) |
| `severity` | No | none | Filter by severity level |
| `q` | No | none | Full-text search query. Multiple `q` params AND together. |

**Response:** Array of Sigma alert objects.

---

### `GET /api/sigma-count`

Returns the total Sigma alert count for the specified analysis, optionally filtered.

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | Yes | — | MD5 hash of a historical analysis |
| `severity` | No | none | Filter by severity level |
| `q` | No | none | Full-text search query. Multiple `q` params AND together. |

**Response:** `{"count": <number>}`

---

### `GET /api/sigma-stats`

Returns Sigma alert statistics (counts grouped by severity/rule/etc.) for the specified analysis.

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | No | none | MD5 hash of a historical analysis (returns an empty object if omitted) |

**Response:** Object mapping statistic names to counts.

---

## POST Endpoints

### `POST /api/upload`

Uploads a file for analysis. Accepts multipart form data.

**Request:** Multipart form with a file field. Accepts any file type. PCAPs (`.pcap`, `.pcapng`, `.cap`, `.trace`) get full Suricata network analysis; log files (`.evtx`, `.json`, `.jsonl`, `.csv`, `.xml`, `.log`) get Zircolite Sigma detection; everything else gets YARA scanning.

**Response (new file):**
```json
{"status": "processing", "md5": "<hash>", "phase": "network"}
```

or for non-PCAP files:

```json
{"status": "processing", "md5": "<hash>", "phase": "files"}
```

or for log files:

```json
{"status": "processing", "md5": "<hash>", "phase": "logs"}
```

**Response (already analyzed):**
```json
{"status": "ready", "md5": "<hash>"}
```

**Processing flow:**
1. Detects file type (PCAP magic bytes, log content, or `.zip` extension)
2. Computes MD5 hash
3. If already analyzed (`eve.json` for PCAPs, `events.db` for non-PCAPs), returns `ready`
4. For PCAPs: saves file, spawns Suricata in background thread, returns `processing` with `phase: "network"`
5. For log files: saves file and imports them into `events.db` in the background, returns `processing` with `phase: "logs"`
6. For other files: saves file, runs YARA/EXIF scans in the background, returns `processing` with `phase: "files"`
7. When analysis finishes, results are available in `events.db` (or `eve.json` for PCAPs)

**Special handling:** Password-protected zips are auto-decrypted using the common `infected` password; if the filename contains a `YYYY-MM-DD` date, the MTA-style dated password (`infected_YYYYMMDD`) is also tried.

**Client should poll** `POST /api/check-status` with the returned MD5 to know when analysis is complete.

---

### `POST /api/load-url`

Downloads a file from a URL and analyzes it.

**Request Body:**
```json
{"url": "https://example.com/capture.pcap"}
```

**Response:** Same as `/api/upload` — `{"status": "processing", "md5": "...", "phase": "..."}` or `{"status": "ready", "md5": "..."}`.

**Special handling:**
- Password-protected zips are auto-decrypted using the common `infected` password (same as `/api/upload`); for `malware-traffic-analysis.net` URLs specifically, the date-based password format (`infected_YYYYMMDD`, derived from the URL's `/YYYY/MM/DD/` path) is also tried, before the plain fallback
- URL safety validation blocks localhost, private IPs, link-local, and non-HTTP schemes
- Hostname is resolved to verify the resolved IP is not private

**Errors:** `400` for invalid URL or SSRF attempt. `413` if file exceeds upload size limit.

---

### `POST /api/check-status`

Polls whether analysis has finished for an uploaded file.

**Request Body:**
```json
{"md5": "<hash>"}
```

**Response:**
```json
{"status": "ready", "meta": {"version": 1, "original": "<filename>", "extracted": "<filename>", "detected_type": "pcap", "extracted_at": "<ISO timestamp>"}}
```
or
```json
{"status": "processing", "phase": "network", "meta": {...}}
```
or, if analysis (Suricata/YARA/Zircolite) failed:
```json
{"status": "error", "message": "<failure reason>"}
```

The `phase` field reflects the current analysis stage (`network`, `logs`, or `files`), or an empty string if no phase file exists yet. `meta` is present whenever `.meta` exists for the analysis and omitted otherwise (including on the `error` response). Same "no 404 for a well-formed-but-nonexistent MD5" caveat as `GET /api/status` applies here too.

**Ready detection:** For PCAPs, checks that `eve.json` exists and `events.db` is present. For other files, checks that `events.db` exists.

---

### `POST /api/reanalyze`

Re-runs the analysis pipeline for an existing MD5 directory. The original uploaded file is preserved; the previous analysis outputs (`eve.json`, `events.db`, etc.) are removed and regenerated.

**Request Body:**
```json
{"md5": "<hash>"}
```

Only `md5` is read from the request body — the response's `phase` is determined automatically from what's actually in the analysis's directory (`network` if a PCAP is found, `logs` if a log file is found, otherwise `files`), not accepted as client input.

**Response:**
```json
{"status": "processing", "md5": "<hash>", "phase": "network"}
```

**Errors:** `400` for invalid MD5 or unsafe path. `404` if analysis not found. `409` if analysis is already in progress.

---

### `POST /api/delete-analysis`

Deletes a single historical analysis (removes the entire MD5 directory).

**Request Body:**
```json
{"md5": "<hash>"}
```

**Response:**
```json
{"success": true}
```

**Errors:** `400` for invalid MD5 or unsafe path. `404` if analysis not found.

---

### `POST /api/delete-all-analyses`

Deletes all historical analyses (every MD5-shaped directory under the data root). Non-analysis directories and files are left untouched.

**Request Body:** `{}` (empty JSON object)

**Response:**
```json
{"success": true, "deleted": 5}
```

**Errors:** `500` if every analysis directory fails to delete.

---

## Error Codes

| Code | Meaning |
|---|---|
| `400` | Invalid input (bad IP, port, MD5, URL, path traversal) |
| `404` | Resource not found (no file, no analysis, no packets) |
| `409` | Conflict — analysis already in progress for this MD5 |
| `413` | File too large |
| `500` | Internal server error (generic message, no details leaked) |
| `507` | Not enough disk space available for this upload |

# API Reference

Base URL: `http://localhost:8000`

All endpoints return `Content-Type: application/json` unless noted. Errors return `{"error": "<message>"}` with the appropriate HTTP status code.

## GET Endpoints

### `GET /`

Redirects to `/socrates.html`.

---

### `GET /api/version`

Returns the running SO-CRATES version.

**Response:** `{"version": "2.1.0"}`

---

### `GET /api/events`

Returns event data from Suricata's eve.json (via SQLite index or direct JSON parse).

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | No | none | MD5 hash of a historical analysis (returns an empty array if omitted) |
| `type` | No | all | Filter by event type (`alert`, `dns`, `http`, `tls`, `flow`, `ftp`, `anomaly`, `fileinfo`, `filealerts`, `dnp3`, `modbus`, `pgsql`, `log`, `sigmaalert`) |
| `q` | No | none | Full-text search query (searches all event JSON). Multiple `q` params AND together. |
| `offset` | No | `0` | Pagination offset |
| `limit` | No | `1000` | Max events to return (capped at 5000) |

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

**Response:** Object mapping event type to count.

**Example:**
```json
{"alert": 42, "dns": 1500, "http": 380, "tls": 95, "flow": 2200}
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

Extracts ASCII payload from a TCP/UDP stream using `tshark`. Tries TCP first, falls back to UDP. Truncated to 100,000 characters.

**Query Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `src` | Yes | Source IP address |
| `sport` | Yes | Source port |
| `dst` | Yes | Destination IP address |
| `dport` | Yes | Destination port |
| `md5` | Yes | MD5 hash of a historical analysis |

**Response:** `text/plain` — decoded ASCII transcript. Non-printable characters replaced with `.`.

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

Returns the filesystem path to the PCAP file in an MD5 directory.

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
{"status": "ready"}
```
or
```json
{"status": "processing", "phase": "network"}
```

**Errors:** `400` for invalid MD5. `404` if analysis not found.

---

### `GET /api/sigma-alerts`

Returns Sigma alerts stored in `events.db` for the specified analysis.

**Query Parameters:**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `md5` | No | none | MD5 hash of a historical analysis (returns an empty array if omitted) |
| `offset` | No | `0` | Pagination offset |
| `limit` | No | `1000` | Max alerts to return (capped at 5000) |
| `severity` | No | none | Filter by severity level |
| `q` | No | none | Full-text search query. Multiple `q` params AND together. |

**Response:** Array of Sigma alert objects.

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

**Request:** Multipart form with a file field. Accepts any file type. PCAPs (`.pcap`, `.pcapng`, `.cap`, `.trace`) get full Suricata network analysis; non-PCAP files get YARA-only scanning.

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
- Password-protected zips from `malware-traffic-analysis.net` are auto-decrypted using the date-based password format (`infected_YYYYMMDD`)
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
{"status": "ready"}
```
or
```json
{"status": "processing", "phase": "network"}
```

The `phase` field reflects the current analysis stage (`network`, `logs`, or `files`).

**Ready detection:** For PCAPs, checks that `eve.json` exists and `events.db` is present. For other files, checks that `events.db` exists.

---

### `POST /api/reanalyze`

Re-runs the analysis pipeline for an existing MD5 directory. The original uploaded file is preserved; the previous analysis outputs (`eve.json`, `events.db`, etc.) are removed and regenerated.

**Request Body:**
```json
{"md5": "<hash>", "phase": "network"}
```

The `phase` field is optional and defaults based on file type (`network` for PCAPs, `logs` for log files, `files` for binaries).

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
| `413` | File too large |
| `429` | Rate limited (currently always returns true — no-op) |
| `500` | Internal server error (generic message, no details leaked) |

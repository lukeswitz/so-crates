# Security Model

- **Network:** Binds to `127.0.0.1` by default on manual/source installs; the Docker/Podman image binds `0.0.0.0` internally (required for port-publishing) — actual exposure is controlled by the `-p`/port choice made when running the container
- **Input validation:** All user inputs (IP, port, MD5, URL, filename) validated before use in subprocess calls or filesystem operations
- **Path safety:** `is_safe_path()` prevents directory traversal via `os.path.realpath()` comparison
- **Content validation:** File type detected by magic bytes and routed accordingly — PCAPs get Suricata, log files get Zircolite, everything else gets YARA
- **URL safety (SSRF):** `validate_url_safety()`/`resolve_safe_ips()` block localhost and private/internal IP ranges, and resolve the hostname once, connecting directly to the validated IP rather than letting the HTTP client re-resolve it — this closes a DNS-rebinding TOCTOU gap that a resolve-then-separately-connect design would have
- **Zip safety:** `validate_zip_extraction()` checks both zip-slip (every extracted path stays within the target directory) and zip-bomb (per-member and total decompressed-size limits)
- **Error handling:** Generic "Internal server error" — no stack traces or internal paths leaked
- **CSP:** `_add_security_headers()` sends `Content-Security-Policy: default-src 'self'; ...` on every response — `'unsafe-inline'` is allowed for `script-src`/`style-src` since the UI relies on inline `onclick`/`style` attributes by convention (see `AGENTS.md`'s frontend conventions)

See [Security](../security.md) for the user-facing summary of these same protections.

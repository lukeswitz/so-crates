# Security

- Binds to `127.0.0.1` by default on manual/source installs; the Docker/Podman image binds `0.0.0.0` internally so port-publishing works — actual exposure is controlled by the `-p`/port choice made when running the container, not by the app itself
- No CORS headers are sent (no cross-origin access, not even a wildcard)
- Input validation on all endpoints (IP, port, MD5, path traversal)
- File type detection routes each upload to the right analyzer only: PCAPs → Suricata, log files → Zircolite Sigma detection, everything else → YARA
- SSRF protection on "Load from URL": blocks localhost and private/internal IP ranges, and resolves the hostname once and connects directly to the validated IP (rather than letting the HTTP client re-resolve it) to prevent DNS-rebinding TOCTOU bypasses
- Zip-slip prevention and decompressed-size limits (zip-bomb protection) on archive extraction
- Upload size ceiling (5,000 MB hard max, user-adjustable up to that from a 1,000 MB default) and an upfront disk-space check before accepting an upload
- Generic error messages (no internal details leaked)
- Content-Security-Policy header (`default-src 'self'`, restricting scripts/styles/images/connections/forms to the app's own origin) on every response — `'unsafe-inline'` is allowed for scripts and styles, a deliberate tradeoff for the app's inline-`onclick`/inline-`style` UI architecture

# Manual Installation

If you prefer to run without Docker or Podman, then you will need these prerequisites:

- **Python 3** (stdlib only — no pip packages required)
- **Suricata** — for PCAP analysis and rule-based alerting
- **suricata-update** — for downloading/updating Suricata rules (internet access required; the app will warn and continue without rules if offline)
- **tcpdump** — for stream carving (`/api/download-stream`) and hexdump extraction (`/api/hexdump-stream`)
- **tshark** — for ASCII transcript extraction (`/api/ascii-stream`)
- **yara** (optional) — for scanning extracted files. If installed, SO-CRATES automatically downloads YARA rules on first run (or uses baked-in rules in Docker). If missing, file extraction and File Alerts are skipped.
- **Zircolite** (optional) — for Sigma rule detection on log files. SO-CRATES auto-detects if Zircolite is installed and skips log analysis if absent. The Dockerfile bakes in Zircolite v3.7.1.
- **exiftool** (optional) — for extracting EXIF/media metadata from binary files. If missing, EXIF extraction is silently skipped (the rest of the file analysis still runs).

Once you have the prerequisites, then you can clone this github repo and run the server:

```bash
python3 socrates.py
```

Then open http://localhost:8000/socrates.html in your browser.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATA_DIR` | `~/socrates-data` | Directory for analyzed files and Suricata config |
| `BIND_ADDRESS` | `127.0.0.1` | Address to bind the HTTP server to |
| `PORT` | `8000` | HTTP server port |
| `ENABLE_ARP_LOGGING` | unset (disabled) | Set to any non-empty value to enable Suricata's `arp` eve-log output. Off by default since ARP volume can be significant on a live network (Suricata's own default is disabled too, for the same reason) - only enable if you actually want ARP events. |

Environment variables override the hardcoded defaults at startup.

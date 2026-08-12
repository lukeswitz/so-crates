# SO-CRATES (macos-native-port)

Fork of [dougburks/so-crates](https://github.com/dougburks/so-crates) that runs natively on macOS and adds host-side telemetry collection.

Upstream analyzes pcaps, logs, and binaries you supply. This branch adds two things upstream doesn't: capturing a pcap from the Mac it's running on, and collecting macOS Endpoint Security events for Sigma analysis. Nothing about the upstream Docker deployment changes — the mac-native paths are additive.

## What this branch adds

**Native macOS runtime.** `python3 socrates.py` boots on macOS without Docker. Homebrew-installed Suricata / YARA / Wireshark are picked up automatically; base Suricata config is resolved from `/opt/homebrew/etc/suricata` (Apple Silicon) or `/usr/local/etc/suricata` (Intel). Zircolite is expected under `$DATA_DIR/zircolite/` and its venv under `$DATA_DIR/zircolite-venv/`. Everything DATA_DIR-aware, no hardcoded `/etc/suricata`. Linux/Docker paths remain the priority so existing deployments are byte-identical.

Setup:

```bash
sh scripts/setup-macos.sh          # brew + Zircolite venv
python3 socrates.py                # opens on http://127.0.0.1:8000/socrates.html
```

**Live traffic capture.** A **Capture live traffic from this Mac** card on the welcome screen prompts for interface + duration (30 s / 1 m / 5 m presets, up to 1 hour), shows elapsed time, bytes and packet count while it runs, and hands the finished pcap to the normal Suricata pipeline. **Stop & Analyze Now** ends a capture early and keeps what it already recorded. The button only renders when packet capture is actually possible — Wireshark's ChmodBPF helper provides the permission; the server never invokes sudo and runs `tcpdump -p` (non-promiscuous).

**macOS Endpoint Security telemetry.** `sudo sh scripts/mac-collect-logs.sh 60` collects process, file, mount, BTM, TCC, XProtect, gatekeeper, kext, SSH, screen-sharing, sudo, su, profile, and OD events for 60 seconds. Root prompt is interactive (one `sudo -v`, elevation applies only to `eslogger`); the mapper and output file stay unprivileged. The resulting `.ndjson` drops onto the welcome screen and gets recognized as macOS telemetry.

**215-rule macOS Sigma ruleset** (`rules/macos.json`) shipped in-repo. Sourced from SigmaHQ:
- 69 from `rules/macos` (process_creation + file_event)
- 2 from `rules-threat-hunting/macos`
- 4 from `rules-emerging-threats` tagged `product: macos`
- 120 from `rules/linux/process_creation` whose fields eslogger can supply
- 20 ES-only rules written for this repo covering event types SigmaHQ has no coverage for at all (XProtect malware detection, BTM persistence, TCC service modification, Gatekeeper override, remote thread creation, kext load, SSH login, screen-sharing attach, sudo/su, profile install, OD user creation, admin group additions, mount)

The ruleset auto-installs into `$DATA_DIR/sigma-rules/` on first run. Regenerate with `python3 scripts/gen-macos-ruleset.py --sigma <path/to/sigmahq> --backend <path/to/pySigma-backend-sqlite>` when SigmaHQ changes.

**Upstream fix.** `db.has_row_notes()` opened `events.db` with `sqlite3.connect()` and no existence check, so `GET /api/status` during an in-progress pcap analysis silently created a 0-byte database. Suricata's completion handler then saw the file as existing and skipped `create_sqlite_db()`, leaving the analysis permanently empty with no error surfaced. Fixed with an `os.path.isfile()` guard.

## Rest of the app

Everything upstream documents applies: pcap analysis, YARA scanning, Sigma log analysis, the same alert / metadata / transcript / hexdump UI. Full docs at [so-crates.org](https://so-crates.org/), and a macOS-specific installation page at [docs/installation/macos.md](docs/installation/macos.md).

## Tests

```bash
python3 -m pytest -q
```

2016 pass, 83 subtests, 0 fail on macOS 15 with brew Python 3.11.

## Scripts

- `scripts/setup-macos.sh` — brew tools + Zircolite venv
- `scripts/mac-collect-logs.sh` — capture Endpoint Security telemetry
- `scripts/mac-collect.sh` — capture a pcap and stage YARA candidates from the CLI
- `scripts/eslogger_to_sigma.py` — map raw eslogger JSON to Sigma field shape
- `scripts/gen-macos-ruleset.py` — regenerate `rules/macos.json`
- `scripts/trigger-macos-detections.sh` — self-cleaning script that generates real activity so ES-only rules have something to match
- `scripts/inspect-raw-eslogger.py` — count event types and print sample bodies from a raw eslogger dump

## Development

See [AGENTS.md](AGENTS.md) for the upstream contributor guidance.

## License

See [LICENSE](LICENSE).

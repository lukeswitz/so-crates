# macOS (native)

SO-CRATES runs natively on macOS, outside a container, using Homebrew for the tools it shells out to. Running natively is what makes the two host-facing features below possible: live packet capture from this Mac, and Endpoint Security log collection. If you only want to analyze files you already have, [Docker Desktop](docker.md#docker-desktop-windows-macos) works too.

## Setup

A helper script installs the tools and, optionally, Zircolite for Sigma log analysis:

```bash
# suricata, suricata-update, yara, tshark/tcpdump, and Zircolite
sh scripts/setup-macos.sh

# tools only, skip Zircolite / Sigma log analysis
sh scripts/setup-macos.sh --no-sigma

python3 socrates.py
```

To install the tools by hand instead:

```bash
brew install suricata yara wireshark
```

`suricata-update` ships with the `suricata` formula and `tcpdump` is already present on macOS. `tshark` comes from either the `wireshark` formula or the Wireshark.app bundle. SO-CRATES reads the base Suricata configuration from the Homebrew location automatically — `/opt/homebrew/etc/suricata` on Apple Silicon, `/usr/local/etc/suricata` on Intel. Zircolite is detected under `DATA_DIR` (`~/socrates-data/zircolite/zircolite.py` by default), which is where `setup-macos.sh` puts it.

## Capturing live traffic

When SO-CRATES can open a capture device, the Welcome screen shows a **Capture live traffic from this Mac** option. It asks which interface and how long to capture, shows elapsed time, bytes and packet count while it runs, and hands the finished pcap straight to the normal Suricata pipeline. **Stop & Analyze Now** ends a capture early and keeps what it already recorded.

Capture requires your user to hold packet-capture permission, which installing Wireshark provides via its ChmodBPF helper. Without it the option does not appear at all, rather than appearing and failing. SO-CRATES never invokes `sudo`: it captures as its own user or not at all, and it runs `tcpdump` non-promiscuously, so your interface's mode is never changed.

## Collecting Endpoint Security logs

macOS process and file telemetry comes from `eslogger(1)`, which requires root. SO-CRATES has no endpoint that escalates privilege, so you run the collector yourself and upload the result:

```bash
sudo sh scripts/mac-collect-logs.sh 60 macos-events.ndjson
```

It subscribes to Endpoint Security `exec` and `create` events for the given number of seconds, printing progress as it goes, then converts them into the field shape Sigma's macOS rules expect (`Image`, `CommandLine`, `ParentImage`, `TargetFilename`). Drop the resulting `.ndjson` onto the Welcome screen: SO-CRATES recognizes it as macOS telemetry and runs the bundled macOS ruleset against it with Zircolite.

Set `ESLOGGER_EVENTS` to subscribe to different events, for example `ESLOGGER_EVENTS="exec create unlink rename"`. If the collector reports no events, grant your terminal Full Disk Access in System Settings > Privacy & Security.

The macOS ruleset (`rules/macos.json`) is converted from [SigmaHQ](https://github.com/SigmaHQ/sigma)'s `rules/macos` — process creation and file event rules — and ships with SO-CRATES, because Zircolite-Rules-v2 publishes Windows and Linux rulesets only. It installs itself into `DATA_DIR` on first run and needs no network access.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATA_DIR` | `~/socrates-data` | Directory for analyzed files and Suricata config |
| `BIND_ADDRESS` | `127.0.0.1` | Address to bind the HTTP server to |
| `PORT` | `8000` | HTTP server port |

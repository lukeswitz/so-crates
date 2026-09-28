# macOS (native)

SO-CRATES runs natively on macOS, outside a container, using Homebrew for the tools it shells out to. Running natively is what makes the two host-facing features below possible: live packet capture from this Mac, and Endpoint Security log collection. If you only want to analyze files you already have, [Docker Desktop](docker.md#docker-desktop-windows-macos) works too.

## Setup

A helper script installs the tools and, optionally, Zircolite for Sigma log analysis:

```bash
# suricata, suricata-update, yara, tshark/tcpdump, Zircolite, and CyberChef
sh scripts/setup-macos.sh

# tools only, skip Zircolite / Sigma log analysis
sh scripts/setup-macos.sh --no-sigma

python3 socrates.py
```

To install the tools by hand instead:

```bash
brew install suricata yara wireshark
```

`suricata-update` ships with the `suricata` formula and `tcpdump` is already present on macOS. `tshark` comes from either the `wireshark` formula or the Wireshark.app bundle. SO-CRATES reads the base Suricata configuration from the Homebrew location automatically — `/opt/homebrew/etc/suricata` on Apple Silicon, `/usr/local/etc/suricata` on Intel. Zircolite is detected under `DATA_DIR` (`~/socrates-data/zircolite/zircolite.py` by default), which is where `setup-macos.sh` puts it. CyberChef (Send to CyberChef, `/cyberchef/`) is served from `$DATA_DIR/cyberchef`; `setup-macos.sh` installs the pinned, checksum-verified release there, or run `sh scripts/fetch-cyberchef.sh ~/socrates-data/cyberchef` directly. Set `CYBERCHEF_DIR` to serve a copy from elsewhere.

Run the test suite with:

```bash
sh scripts/run-tests.sh
```

It installs the test dependencies into `.venv` on first run and uses that interpreter directly, so there is no venv to activate or deactivate.

## Capturing live traffic

When SO-CRATES can open a capture device, the Welcome screen shows a **Capture live traffic from this Mac** option. It asks which interface and how long to capture, shows elapsed time, bytes and packet count while it runs, and hands the finished pcap straight to the normal Suricata pipeline. **Stop & Analyze Now** ends a capture early and keeps what it already recorded.

Capture requires your user to hold packet-capture permission, which installing Wireshark provides via its ChmodBPF helper. Without it the option does not appear at all, rather than appearing and failing. SO-CRATES never invokes `sudo`: it captures as its own user or not at all, and it runs `tcpdump` non-promiscuously, so your interface's mode is never changed.

## Collecting Endpoint Security logs

macOS process and file telemetry comes from `eslogger(1)`, which requires root. SO-CRATES has no endpoint that escalates privilege, so you run the collector yourself and upload the result:

```bash
sh scripts/mac-collect-logs.sh 60 macos-events.ndjson
```

The script prompts once for your password (`sudo -v`) and elevates only the `eslogger` invocation; the field mapper and the output file stay unprivileged, and nothing is installed or left running as root. Outputs are written `0600` (`umask 077`).

It subscribes to a curated set of 27 Endpoint Security events for the given number of seconds — process/file activity (`exec`, `create`, `unlink`, `rename`, `mount`) plus security events SigmaHQ covers directly: Background Task Management persistence, XProtect malware detections, Gatekeeper overrides, TCC changes, kext loads, remote thread creation, code-signing invalidation, SSH/screen-sharing/console logins, `su`/`sudo`, profile installs, and Open Directory user/group/password changes. It then converts them into the field shape Sigma's macOS rules expect (`Image`, `CommandLine`, `ParentImage`, `TargetFilename`). Drop the resulting `.ndjson` onto the Welcome screen: SO-CRATES recognizes it as macOS telemetry and runs the bundled macOS ruleset against it with Zircolite.

Set `ESLOGGER_EVENTS` to override the subscribed set, for example `ESLOGGER_EVENTS="exec create unlink rename"`. If the collector reports no events, grant your terminal Full Disk Access in System Settings > Privacy & Security.

The macOS ruleset (`rules/macos.json`) is converted from [SigmaHQ](https://github.com/SigmaHQ/sigma)'s `rules/macos` — process creation and file event rules — and ships with SO-CRATES, because Zircolite-Rules-v2 publishes Windows and Linux rulesets only. It installs itself into `DATA_DIR` on first run and needs no network access.

## Access control

Binding to `127.0.0.1` keeps the server off the network, but every other local user and every process running as you can still reach the port — and the native build can start a live packet capture of this host's traffic. So the server requires a per-session token: on startup it prints a URL carrying the token, e.g. `http://127.0.0.1:8000/socrates.html?token=…`. Open that once; it sets an `HttpOnly; SameSite=Strict` cookie and redirects to the plain URL, and the browser stays authenticated for the session. Requests without the token get `401`.

The token is generated on first run and persisted `0600` at `$DATA_DIR/.auth-token`, so a restart keeps the same link. `DATA_DIR` itself is `chmod 0700`. Set `AUTH_TOKEN=<value>` to pin a specific token, or `AUTH_TOKEN=off` to disable the gate (e.g. behind your own authenticating proxy).

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATA_DIR` | `~/socrates-data` | Directory for analyzed files and Suricata config (created `0700`) |
| `BIND_ADDRESS` | `127.0.0.1` | Address to bind the HTTP server to |
| `PORT` | `8000` | HTTP server port |
| `AUTH_TOKEN` | generated | Session token; a literal value pins it, `off` disables the gate |

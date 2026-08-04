# Usage

Once you've connected to SO-CRATES in your browser, here are some of the things you can do.

## Analyze a File

1. **Upload a file** — click "Choose File" and select a `.pcap`, `.pcapng`, `.cap`, `.trace`, `.evtx`, `.json`, `.jsonl`, `.csv`, `.xml`, `.log`, or any other file type (or a `.zip` containing one). File types are auto-detected:
   - **PCAP** files → Suricata network analysis
   - **Log files** (`.evtx`, `.json`, `.jsonl`, `.csv`, `.xml`, `.log`) → Zircolite Sigma rule detection
   - **Other files** → YARA binary scanning
2. **Load from URL** — paste a URL to a file and press **Enter** (or click **Go**). Password-protected zips from `malware-traffic-analysis.net` are auto-decrypted using the date-based password format
3. **Reopen a previous analysis** — previously analyzed files are listed on the welcome screen
4. **Re-analyze a previous file** — click the re-analyze button next to any previous file to delete its analysis and re-run the pipeline

## Navigate Results

After analysis completes, the UI displays different views depending on the file type:

**For PCAP files:**

- **Stats Grid** — clickable cards showing event counts by type (Alerts, DNS, HTTP, TLS, Flows, etc.)
- **Sankey Diagram** — expand the collapsible heading to visualize network flow relationships (Source IP → Dest IP → Dest Port)
- **Aggregation Tables** — frequency counts for each column; click a value to filter
- **Data Table** — sortable table with expandable detail rows showing full event JSON, ASCII transcripts, and hexdumps
- **Search** — full-text search across all event data using SQLite FTS5 (falls back to `LIKE` if FTS5 is unavailable)
- **Filtering** — apply filters by clicking aggregation values; filter chips show active filters; filters persist across all tabs and the Sankey diagram

**For log files (`.evtx`, `.json`, `.jsonl`, `.csv`, `.xml`, `.log`):**

- **Sigma Alerts** — detections matched by Sigma rules, with severity, MITRE techniques, and rule metadata
- **Log Events** — all parsed log events with dynamic column discovery based on the actual data
- **Aggregation Tables** — filterable counts for discovered fields (Channel, EventID, Image, Source IP, etc.)
- **Search & Filtering** — same full-text search and aggregation-click filtering as PCAP mode

**For binary files:**

- **File Info** — metadata extracted from the file
- **YARA Matches** — any rules that matched, with tags and author attribution

## Stream Analysis

Click any row in a data table to expand it, then:

- **ASCII Transcript** — view decoded TCP/UDP payload as readable text
- **Hexdump** — view per-packet hex dumps with collapsible packet headers
- **Download PCAP** — carve that specific stream into a standalone `.pcap` file

## Gear Menu

The gear icon in the upper-right corner opens a menu with five entries:

- **Help** — the welcome/help modal, including a link to this documentation site
- **Settings** — upload size, query result limit, and other user-configurable preferences
- **Themes** — browse and apply themes; see [Themes](themes.md)
- **Rules** — check the current rule count and last-updated time for Suricata, YARA, and Sigma, and trigger an update for one ruleset (or all three) with live progress. Rule updates are not run automatically at startup — this modal is the only way to refresh them after the initial install
- **About** — current version, links to this documentation site and the GitHub repo, and an opt-in "Check GitHub for newer releases" setting with a manual "Check Now" button

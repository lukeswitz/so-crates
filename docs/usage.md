# Usage

Once you've connected to SO-CRATES in your browser, here are some of the things you can do.

## Analyze a File

1. **Upload a file** - click "Choose File" and select a `.pcap`, `.pcapng`, `.cap`, `.trace`, `.evtx`, `.json`, `.jsonl`, `.csv`, `.xml`, `.log`, or any other file type (or a `.zip` containing one). File types are auto-detected:
   - **PCAP** files → Suricata network analysis
   - **Log files** (`.evtx`, `.json`, `.jsonl`, `.csv`, `.xml`, `.log`) → Zircolite Sigma rule detection
   - **Other files** → YARA binary scanning
2. **Load from URL** - paste a URL to a file and press **Enter** (or click **Go**). Password-protected zips from `malware-traffic-analysis.net` are auto-decrypted using the date-based password format
3. **Reopen a previous analysis** - previously analyzed files are listed on the welcome screen
4. **Reanalyze a previous file** - click the reanalyze button next to any previous file to delete its analysis and re-run the pipeline

## Navigate Results

After analysis completes, the UI displays different views depending on the file type:

**For PCAP files:**

- **Stats Grid** - clickable cards showing event counts by type (Alerts, DNS, HTTP, TLS, Flows, etc.). If you've enabled "Show protocol-anomaly noise alerts" (Gear Menu → Rules), those alerts get their own **Decoder Alerts** card instead of mixing into Network Alerts
- **Sankey Diagram** - expand the collapsible heading to visualize network flow relationships (Source IP → Dest IP → Dest Port)
- **Aggregation Tables** - frequency counts for each column; click a value to open the [pivot menu](#pivot-menu)
- **Data Table** - sortable table with expandable detail rows showing full event JSON, ASCII transcripts, and hexdumps
- **Search** - full-text search across all event data using SQLite FTS5 (falls back to `LIKE` if FTS5 is unavailable)
- **Filtering** - filter via the pivot menu's Include/Exclude/Only actions on any table cell or aggregation value; filter chips show active filters; filters persist across all tabs and the Sankey diagram

**For log files (`.evtx`, `.json`, `.jsonl`, `.csv`, `.xml`, `.log`):**

- **Sigma Alerts** - detections matched by Sigma rules, with severity, MITRE techniques, and rule metadata
- **Log Events** - all parsed log events with dynamic column discovery based on the actual data
- **Aggregation Tables** - filterable counts for discovered fields (Channel, EventID, Image, Source IP, etc.)
- **Search & Filtering** - same full-text search and pivot-menu filtering as PCAP mode

**For binary files:**

- **File Info** - metadata extracted from the file
- **YARA Matches** - any rules that matched, with tags and author attribution

## Pivot Menu

Clicking a value in a data table row, an expanded row's detail panel, or an aggregation table opens a pivot menu instead of immediately filtering or expanding the row:

- **Include** - broaden the current filter to also match this value
- **Exclude** - narrow the current filter to hide this value
- **Only** - start a new filter scoped to just this value, clearing every other filter
- **Hunt** - a full-text search for this value across every field, replacing the whole search and clearing any active filters
- **Copy to Clipboard** - copy the value as-is
- **Lookups** - one-click lookups against Google, VirusTotal, Shodan, AbuseIPDB, urlscan.io, and CyberChef, plus any custom lookup sites you've added in Settings
- **Expand Row / Collapse Row** - expand or collapse the row's detail panel (the row's timestamp cell also does this directly on click, without opening the menu)

## AI Summary

Expanding a Suricata alert, Sigma alert, or YARA file match shows an **AI Summary** field right at the top of Alert Details/Sigma Rule/Rule - a one-paragraph, plain-English explanation of what the rule actually detects. It only appears if a summary is actually available for that specific rule (there's no generic fallback, unlike Playbook below - a summary for the wrong rule would be misleading). A file with more than one YARA match shows one summary per match. AI Summary data ships baked into the official Docker/Podman image - a manually-installed (non-container) deployment won't see this field unless the maintainer has set it up with its own summary data (see [Development Setup](development-setup.md#environment-variables)).

## Playbook

Expanding a Suricata or Sigma alert shows a **Playbook** section (after Alert Details/Sigma Rule) with plain-English investigation guidance for that specific detection - a name, description, and a list of questions to help guide your investigation, which you can collapse if it's in the way while you're also looking at the Rule/Payload sections. The section only appears if a playbook is actually available for that detection; if none is available, no trace of the feature shows at all. Playbook data ships baked into the official Docker/Podman image - a manually-installed (non-container) deployment won't see this section unless the maintainer has set it up with its own playbook data (see [Development Setup](development-setup.md#environment-variables)).

## Notes

- **Analysis notes** - the notes icon in the app header (next to the reanalyze icon) lets you attach freeform investigation context to the whole analysis ("suspected GuLoader, C2 at x.top"). Always available once an analysis is loaded.
- **Row-level notes** - expand a row's detail panel and use the Notes section's **+ Add Note** link to attach a short annotation to that specific piece of evidence ("false positive, known scanner", "escalated to IR ticket #4521"), separate from the analysis-wide notes above. Once a row has a note, a small note icon appears directly on that row for quick access/editing without expanding it again. Row-level notes are lost if you reanalyze the file (which rebuilds the underlying database from scratch) - the reanalyze confirmation dialog warns you if the analysis has any before you confirm.

## Stream Analysis

Click a row's timestamp cell (or use the pivot menu's **Expand Row** entry) to expand it, then:

- **ASCII Transcript** - view decoded TCP/UDP payload as readable text
- **Hexdump** - view per-packet hex dumps with collapsible packet headers
- **Download PCAP** - carve that specific stream into a standalone `.pcap` file

## Gear Menu

The gear icon in the upper-right corner opens a menu with five entries:

- **Help** - the welcome/help modal, including a link to this documentation site
- **Settings** - upload size, query result limit, and other user-configurable preferences
- **Themes** - browse and apply themes; see [Themes](themes.md)
- **Rules** - check the current rule count and last-updated time for Suricata, YARA, and Sigma, and trigger an update for one ruleset (or all three) with live progress. Rule updates are not run automatically at startup - this modal is the only way to refresh them after the initial install. The Suricata section also has a "Show protocol-anomaly noise alerts" toggle (off by default) for Suricata's own built-in decoder alerts (e.g. excessive retransmissions) - see [Decoder Alerts](#navigate-results) above
- **About** - current version, links to this documentation site and the GitHub repo, and an opt-in "Check GitHub for newer releases" setting with a manual "Check Now" button

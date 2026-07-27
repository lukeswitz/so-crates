# Data Storage

```
~/socrates-data/
  suricata/
    suricata.yaml          # Copied from /etc/suricata/, rule path rewritten
    rules/
      suricata.rules       # Downloaded by suricata-update (online) or copied from baked-in image (offline/air-gapped)
    disable.conf
  zircolite/               # Zircolite source (auto-cloned on first run if not present)
  sigma-rules/
    windows.json           # Pre-compiled Sigma rules for Windows logs
    linux.json             # Pre-compiled Sigma rules for Linux logs
  yara-rules/              # Downloaded/baked-in YARA rules
  upload-tmp/              # Streaming-upload scratch space; swept on startup (see _cleanup_upload_tmp_dir)
  <md5>/
    <filename>             # Original uploaded file
    .meta                  # Analysis metadata (file type, extracted name, version)
    eve.json               # Suricata JSON output (newline-delimited, PCAP only)
    events.db              # SQLite index (auto-created after analysis)
    name.txt               # Human-readable display name
    filestore/             # Extracted files from Suricata file-store (PCAP only)
    yara_matches.json      # YARA scan results (auto-created after analysis)
    sigma_matches.json     # Sigma detection results (log files only)
    file_metadata.json     # Hashes/entropy/strings/EXIF, keyed by SHA256 (standalone binary uploads and extracted PCAP filestore files)
    fast.log               # Suricata's plaintext alert log (PCAP only)
    stats.log               # Suricata's periodic stats log (PCAP only)
    suricata.log            # Suricata's own process log (PCAP only)
```

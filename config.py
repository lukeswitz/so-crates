"""Application-wide configuration constants for SO-CRATES.

All tunable numeric values (size limits, timeouts, thresholds) are centralized
here so they can be adjusted for different deployments without scattering edits
across the codebase.
"""

# Size limits
# MAX_UPLOAD_SIZE is the hard ceiling enforced server-side (see
# socrates.py's _resolve_upload_size_limit) - any client-requested override,
# including the user-configurable frontend setting, is always clamped to
# this value. DEFAULT_UPLOAD_SIZE is what's used when no override is sent
# (preserves the old fixed ceiling for any caller that doesn't opt in).
MAX_UPLOAD_SIZE = 5000 * 1024 * 1024       # 5000 MB
DEFAULT_UPLOAD_SIZE = 1000 * 1024 * 1024   # 1000 MB
MAX_EVE_SIZE = 5000 * 1024 * 1024          # 5000 MB
MAX_REQUEST_BODY_SIZE = 1024 * 1024        # 1 MB
MAX_TRANSCRIPT_SIZE = 100000               # characters
DISK_SPACE_SAFETY_MARGIN = 100 * 1024 * 1024  # 100 MB buffer kept free on disk-space checks

# Query / display limits
# MAX_QUERY_LIMIT is the hard ceiling enforced server-side (see
# socrates.py's _parse_pagination) - any client-requested `limit=`,
# including the user-configurable frontend setting, is always clamped to
# this value regardless of what the client asked for.
MAX_QUERY_LIMIT = 100000
MAX_TRANSCRIPT_LINES = 500
MAX_HEXDUMP_PACKETS = 500

# Timeouts (seconds)
STREAM_TIMEOUT_SECONDS = 60
URL_DOWNLOAD_TIMEOUT = 30
SQLITE_TIMEOUT_SECONDS = 30
FILE_COMMAND_TIMEOUT = 10
RULES_DOWNLOAD_TIMEOUT = 60
YARA_SCAN_TIMEOUT = 300
SURICATA_UPDATE_TIMEOUT = 60
SURICATA_RUN_TIMEOUT = 300                 # 5 minutes max for a single PCAP
SIGMA_RUN_TIMEOUT = 300                    # 5 minutes max for Zircolite log analysis

# Sigma / Zircolite
ZIRCOLITE_VERSION = '3.7.1'
SIGMA_RULES_SUBDIR = 'sigma-rules'

# Rules freshness
# YARA Forge ships weekly and Zircolite-Rules-v2 ships daily, so this is a
# deliberately conservative shared ceiling rather than matching either
# cadence exactly - it just bounds how far a cached copy can drift before
# the next server startup tries to refresh it.
RULES_MAX_AGE_HOURS = 24

# Uploads
UPLOAD_TMP_SUBDIR = 'upload-tmp'

# Search / analysis limits
MAX_SEARCH_TERM_LENGTH = 200               # characters
MAX_DISPLAY_NAME_LENGTH = 255               # characters - user-renamed analysis display name
MAX_NOTES_LENGTH = 10000                    # characters - user-entered analysis notes
HASH_CHUNK_SIZE = 65536                    # bytes for incremental hashing
MAX_STRINGS_READ_SIZE = 2 * 1024 * 1024    # 2 MB cap for string extraction
MAX_ENTROPY_READ_SIZE = 10 * 1024 * 1024   # 10 MB cap for entropy calculation

# Thresholds
STALE_THRESHOLD_SECONDS = 600              # 10 minutes

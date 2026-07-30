# Test Coverage

Seven test files serve as executable specifications:

- **test_socrates_server.py** — Server-side: validation, security, API endpoints, SQLite, Suricata config
- **test_socrates_ui.py** — UI-side: HTML structure, CSS, JS functions, syntax, filtering, accessibility, performance
- **test_socrates_db.py** — Database: SQLite schema, bulk loading, query functions
- **test_sigma_db.py** — Sigma alerts table: insert/query, severity filtering, search, stats, log event import
- **test_sigma_analyzer.py** — Zircolite/Sigma pipeline: log type detection, result parsing, importing Zircolite output into SQLite
- **test_validators.py** — Input validation: office/log file detection by extension, safe-IP resolution (SSRF/DNS-rebinding)
- **test_ohmydebn_colors.py** — OhMyDebn theme-sync color derivation: `colors.toml`/`alacritty.toml` parsing, contrast-safety adjustments

Tests are static analysis (string matching in source files), live server integration tests, and JSDOM-based behavioral tests (`tests/jsdom_helper.py`) for JS functions that need real execution rather than source inspection. No Selenium/Playwright-style full-browser tests.

See [Testing](../testing.md) for how to run them.

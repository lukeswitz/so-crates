# SO-CRATES

*Security Onion Containerized Rapid Analysis of Threats, Evil, and Sus*

A standalone web application for analyzing pcap files, log files, and binary files. Features include Suricata network analysis, YARA binary scanning, Sigma rule detection for logs, and a single-page UI for browsing alerts, metadata, transcripts, and hexdumps.

📖 **Full documentation:** https://dougburks.github.io/so-crates/

![Main screen](docs/images/so-crates-main.png)

## Documentation

- [Interactive Demo](https://dougburks.github.io/so-crates/quick-demo/)
- [Installation](https://dougburks.github.io/so-crates/installation/) ([OhMyDebn](https://dougburks.github.io/so-crates/installation/ohmydebn/), [Docker](https://dougburks.github.io/so-crates/installation/docker/), [Podman](https://dougburks.github.io/so-crates/installation/podman/), [Manual](https://dougburks.github.io/so-crates/installation/manual/))
- [Usage](https://dougburks.github.io/so-crates/usage/)
- [Configuration](https://dougburks.github.io/so-crates/configuration/)
- [Security](https://dougburks.github.io/so-crates/security/)
- [Architecture](https://dougburks.github.io/so-crates/architecture/) / [API Reference](https://dougburks.github.io/so-crates/api/) / [Filtering](https://dougburks.github.io/so-crates/filtering/)
- [Credits](https://dougburks.github.io/so-crates/credits/)
- [Release Notes](https://dougburks.github.io/so-crates/release-notes/)

## Development

See [AGENTS.md](AGENTS.md) for agent-focused guidance on maintaining SO-CRATES, including updating vendored dependencies.

```bash
# All tests
python3 -m unittest discover -v
```

## License

See [LICENSE](LICENSE)

# SO-CRATES

*Security Onion Containerized Rapid Analysis of Threats, Evil, and Sus*

A standalone web application for analyzing pcap files, log files, and binary files. Features include Suricata network analysis, YARA binary scanning, Sigma rule detection for logs, and a single-page UI for browsing alerts, metadata, transcripts, and hexdumps.

📖 **Full documentation:** https://dougburks.github.io/so-crates/

![Main screen](docs/images/so-crates-main.png)

## Quick Start

Try the [online demo](https://securityonion.net/socrates-demo) (free accounts are limited to 60 minutes), or run your own instance with Docker:

```bash
sudo apt update && sudo apt -y install docker.io && sudo usermod -aG docker $USER
mkdir -p ~/socrates-data
newgrp docker -c "docker run -v ~/socrates-data:/data -p 8000:8000 ghcr.io/dougburks/so-crates:main"
```

Then open http://localhost:8000/socrates.html in your browser.

See the full [Installation guide](https://dougburks.github.io/so-crates/installation/) for Podman, air-gapped/offline deployment, manual (no container) installs, and building your own image.

## Documentation

- [Interactive Demo](https://dougburks.github.io/so-crates/quick-demo/)
- [Installation](https://dougburks.github.io/so-crates/installation/) ([OhMyDebn](https://dougburks.github.io/so-crates/installation/ohmydebn/), [Docker](https://dougburks.github.io/so-crates/installation/docker/), [Podman](https://dougburks.github.io/so-crates/installation/podman/), [Manual](https://dougburks.github.io/so-crates/installation/manual/))
- [Usage](https://dougburks.github.io/so-crates/usage/)
- [Configuration](https://dougburks.github.io/so-crates/configuration/)
- [Security](https://dougburks.github.io/so-crates/security/)
- [Architecture](https://dougburks.github.io/so-crates/architecture/) / [API Reference](https://dougburks.github.io/so-crates/api/) / [Filtering](https://dougburks.github.io/so-crates/filtering/)
- [Credits](https://dougburks.github.io/so-crates/credits/)

## Development

See [AGENTS.md](AGENTS.md) for agent-focused guidance on maintaining SO-CRATES, including updating vendored dependencies.

```bash
# All tests
python3 -m unittest discover -v
```

## Release Notes

See [docs/release-notes.md](docs/release-notes.md) or
https://dougburks.github.io/so-crates/release-notes/

## License

See [LICENSE](LICENSE)

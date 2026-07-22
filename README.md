# MediaVault releases

This repository is the public, machine-readable release channel for MediaVault.
It contains the signed Android and Android TV packages, the standalone TrueNAS
Custom App YAML, checksums and release notes. The server image is published as
`ghcr.io/scorpionzk89/mediavault-server`.

MediaVault installations use the GitHub Releases API of this repository to
check for updates. An update is never installed silently: TrueNAS application
updates remain controlled by TrueNAS, while Android users confirm the signed
APK installation on their device.

No passwords, API keys, media, databases or server configuration are published
here.

# MediaVault releases

This public repository is the machine-readable binary release channel for MediaVault. Release artifacts are attached to [GitHub Releases](https://github.com/ScorpionZK89/MediaVault-Releases/releases), rather than committed to the default branch.

The latest release contains:

- signed Android phone/tablet APK and v2/v3 signature metadata;
- signed Android TV / Google TV / NVIDIA Shield APK and v2/v3 signature metadata;
- one standalone TrueNAS Custom App Compose YAML;
- SHA-256 checksums and release notes.

The server image is published at `ghcr.io/scorpionzk89/mediavault-server`. It includes the .NET runtime, web interface, SQLite provider, FFmpeg and ffprobe; users do not install those dependencies separately.

## TrueNAS installation

MediaVault is currently supported and release-tested on **TrueNAS SCALE ElectricEel-24.10.2.4**. The `-electric-eel` image-tag suffix records that tested support target; it does not denote a separate rootful or host-modifying container.

1. Download `MediaVault-TrueNAS-v0.3.15.yml` from the [latest release](https://github.com/ScorpionZK89/MediaVault-Releases/releases/latest).
2. Verify it with `SHA256SUMS-v0.3.15.txt` from the same release.
3. In TrueNAS, open **Apps → Discover Apps → Custom App → Install via YAML**.
4. Replace only the example administrator credentials and the example host paths with values for your system. Keep the immutable image digest.
5. Install and wait for the healthcheck to become healthy, then open port 3000.

The main service is constrained directly by Compose with `user: "568:568"`; this is not an environment-variable-based UID/GID switch. It also uses a read-only root filesystem, read-only media, all Linux capabilities dropped and `no-new-privileges`. App-data mounts remain writable. The official TrueNAS catalog template additionally uses the standard temporary permissions helper only for TrueNAS-managed app-data volumes.

The prepared catalog template creates separate managed ixVolumes for configuration, database data, cache, transcodes, downloads, backups and the initial media location. Existing media is selected separately and mounted read-only. Until the catalog contribution is accepted, the standalone YAML remains the supported production installation path.

## Updates

MediaVault installations use the GitHub Releases API of this repository to check for updates. An update is never installed silently: TrueNAS application updates remain controlled by TrueNAS, while Android users confirm signed APK installation through Android.

No passwords, API keys, media, databases or live server configuration are published here.

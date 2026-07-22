# MediaVault releases

This public repository is the machine-readable binary release channel for MediaVault. Release artifacts are attached to [GitHub Releases](https://github.com/ScorpionZK89/MediaVault-Releases/releases), rather than committed to the default branch.

The latest release contains:

- signed Android phone/tablet APK and v2/v3 signature metadata;
- signed Android TV / Google TV / NVIDIA Shield APK and v2/v3 signature metadata;
- one standalone TrueNAS Custom App Compose YAML;
- SHA-256 checksums and release notes.

The server image is published at `ghcr.io/scorpionzk89/mediavault-server`. It includes the .NET runtime, web interface, SQLite provider, FFmpeg and ffprobe; users do not install those dependencies separately.

## Free personal use

Official MediaVault binary releases are free for personal, non-commercial use. No purchase, licence fee, subscription or paid feature unlock is required. The source code remains private; the public eligibility grant is documented in the [MediaVault Free Personal Use Terms](PERSONAL-USE-TERMS.md).

Publishing and installing MediaVault through GitHub and the TrueNAS community catalog does not require a payment to MediaVault. Hardware, electricity, Internet access and optional third-party services remain outside MediaVault.

## TrueNAS installation

MediaVault is currently supported and release-tested on **TrueNAS SCALE ElectricEel-24.10.2.4**. The `-electric-eel` image-tag suffix records that tested support target; it does not denote a separate rootful or host-modifying container.

1. Download `MediaVault-TrueNAS-v0.3.16.yml` from the [latest release](https://github.com/ScorpionZK89/MediaVault-Releases/releases/latest).
2. Verify it with `SHA256SUMS-v0.3.16.txt` from the same release.
3. In TrueNAS, open **Apps → Discover Apps → Custom App → Install via YAML**.
4. Replace only the example administrator credentials and the example host paths with values for your system. Keep the immutable image digest.
5. Install and wait for the healthcheck to become healthy, then open port 3000.

The standalone YAML constrains the main service directly with `user: "568:568"`; this is not an environment-variable-based UID/GID switch. The catalog form allows another numeric non-root UID/GID and applies that exact value through Compose `user:` plus the standard temporary permissions helper for managed writable app-data volumes. The published image was also started healthy as `1234:1234`; it is not tied to 568. The service uses a read-only root filesystem, read-only media, all Linux capabilities dropped and `no-new-privileges`.

The prepared catalog template creates separate managed ixVolumes for configuration, database data, cache, transcodes, downloads, backups and the initial media location. Existing media is selected separately and mounted read-only. Until the catalog contribution is accepted, the standalone YAML remains the supported production installation path.

## Updates

MediaVault installations use the GitHub Releases API of this repository to check for updates. An update is never installed silently: TrueNAS application updates remain controlled by TrueNAS, while Android users confirm signed APK installation through Android.

No passwords, API keys, media, databases or live server configuration are published here. Every catalog-set variable is described in the public [environment-variable reference](ENVIRONMENT.md).

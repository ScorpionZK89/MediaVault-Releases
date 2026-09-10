# MediaVault releases

This public repository is the machine-readable binary release channel for MediaVault. Release artifacts are attached to [GitHub Releases](https://github.com/ScorpionZK89/MediaVault-Releases/releases), rather than committed to the default branch.

The latest release contains:

- signed Android phone/tablet APK and v2/v3 signature metadata;
- signed Android TV / Google TV / NVIDIA Shield APK and v2/v3 signature metadata;
- one standalone TrueNAS Custom App Compose YAML;
- the Home Assistant integration bundle (`mediavault.zip`, from 0.3.236);
- SHA-256 checksums and release notes.

The server image is published at `ghcr.io/scorpionzk89/mediavault-server`. It includes the .NET runtime, web interface, SQLite provider, FFmpeg and ffprobe; users do not install those dependencies separately.

## Free personal use

Official MediaVault binary releases are free for personal, non-commercial use. No purchase, licence fee, subscription or paid feature unlock is required. The MediaVault server and native client source code remains private; this repository additionally distributes the Home Assistant component required for HACS installation. The public eligibility grant is documented in the [MediaVault Free Personal Use Terms](PERSONAL-USE-TERMS.md).

Publishing and installing MediaVault through GitHub as a standalone TrueNAS Custom App does not require a payment to MediaVault. Hardware, electricity, Internet access and optional third-party services remain outside MediaVault.

## TrueNAS installation

MediaVault targets **TrueNAS SCALE 25.10.6 Goldeye**. The historical `-electric-eel` image-tag suffix is retained for update compatibility; it does not denote a separate rootful or host-modifying container.

1. Download the versioned `MediaVault-TrueNAS-*.yml` from the [latest release](https://github.com/ScorpionZK89/MediaVault-Releases/releases/latest).
2. Verify it with the `SHA256SUMS-*.txt` from the same release.
3. In TrueNAS, open **Apps → Discover Apps → Custom App → Install via YAML**.
4. Replace the example host paths with your selected dataset paths. Keep the immutable image digest. There are no default administrator credentials.
5. Install and wait for the healthcheck to become healthy, then open port 3000 and create the first administrator using the local first-start wizard.

The standalone YAML constrains the main service directly with `user: "568:568"`; this is not an environment-variable-based UID/GID switch. The published image was also started healthy as `1234:1234`; it is not tied to 568. The service uses a read-only root filesystem, read-only media, all Linux capabilities dropped and `no-new-privileges`.

The standalone YAML is the only supported production installation path. It uses explicit persistent host mounts for configuration, database data, cache, transcodes, downloads and backups; existing media is selected separately and mounted read-only. MediaVault does not create or alter TrueNAS datasets or ACLs outside those selected mounts.

## Home Assistant via HACS

From MediaVault 0.3.236, add this repository as a custom **Integration** in HACS,
download MediaVault and restart Home Assistant. Then add the MediaVault integration
under Settings → Devices & services, using the local MediaVault URL and a dedicated
integration key created in MediaVault Settings → Integrations → Home Assistant.
See the [installation and permissions guide](HOME-ASSISTANT.md).

The integration requires Home Assistant Core 2026.9 or newer. It offers real
connected Web/Android/TV players, library browsing, server diagnostics and explicitly
authorized scan/task actions. Closed apps and powered-off devices cannot be started.
The MediaVault server-side API is already built into the server image; no extra
server container, GPT or cloud service is needed.

## Updates

MediaVault installations use the GitHub Releases API of this repository to check for updates. An update is never installed silently: the TrueNAS administrator deliberately replaces the immutable image pin in the Custom App, while Android users confirm signed APK installation through Android.

No passwords, API keys, media, databases or live server configuration are published here. Every supported variable is described in the public [environment-variable reference](ENVIRONMENT.md).

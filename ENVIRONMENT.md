# MediaVault environment variables

The standalone TrueNAS Custom App YAML supplies these values. Replace example credentials and paths in the TrueNAS form before installation; secrets must never be committed to Git.

| Variable | Purpose |
|---|---|
| `MEDIAVAULT_BIND_ADDRESS` | Address listened on inside the container. The standalone YAML sets `0.0.0.0` for LAN access. |
| `MEDIAVAULT_PORT` | Internal HTTP port. The standalone YAML uses `3000`; the published host port remains configurable. |
| `MEDIAVAULT_CONFIG_DIR` | Writable directory for control state and encrypted integration configuration. |
| `MEDIAVAULT_DATA_DIR` | Writable directory containing the SQLite database and persistent application data. |
| `MEDIAVAULT_CACHE_DIR` | Writable cache root, including downloaded metadata artwork. |
| `MEDIAVAULT_TRANSCODE_DIR` | Writable temporary FFmpeg/HLS transcode output directory. |
| `MEDIAVAULT_OFFLINE_RENDITION_DIR` | Directory reserved for offline renditions inside the downloads storage. |
| `MEDIAVAULT_DOWNLOADS_DIR` | Writable downloads root. Offline client work remains outside the current stable scope. |
| `MEDIAVAULT_BACKUPS_DIR` | Writable MediaVault backup destination. |
| `MEDIAVAULT_LOG_DIR` | Writable application log directory. |
| `MEDIAVAULT_LOG_MAX_BYTES` | Maximum size of one rotating log file; constrained by the server. |
| `MEDIAVAULT_LOG_RETAINED_FILES` | Number of rotated log files retained; constrained by the server. |
| `MEDIAVAULT_MEDIA_ROOTS` | Semicolon-separated allow-list of media roots. Media is mounted read-only at `/media`. |
| `MEDIAVAULT_FFMPEG_PATH` | Absolute path to the bundled FFmpeg binary. |
| `MEDIAVAULT_FFPROBE_PATH` | Absolute path to the bundled ffprobe binary. |
| `MEDIAVAULT_HARDWARE_DEVICE` | Optional exact `/dev/dri/renderD<number>` or `/dev/nvidia<number>` override. Empty means automatic assigned-device detection. |
| `MEDIAVAULT_ADMIN_EMAIL` | Initial owner account e-mail address. |
| `MEDIAVAULT_ADMIN_PASSWORD` | Initial owner password. LAN startup rejects missing, example or shorter-than-12-character values. |
| `MEDIAVAULT_CORS_ORIGINS` | Semicolon-separated browser origins allowed to call the API. |
| `MEDIAVAULT_TMDB_READ_ACCESS_TOKEN` | Optional TMDB read-access token. It stays server-side; empty keeps TMDB disabled. |
| `MEDIAVAULT_TMDB_LANGUAGE` | TMDB metadata locale in `ll-CC` form; default `nl-NL`. |
| `MEDIAVAULT_AUTO_SCAN_ENABLED` | Enables filesystem watchers, the lightweight snapshot check and scheduled scans. |
| `MEDIAVAULT_AUTO_SCAN_DEBOUNCE_SECONDS` | Quiet period before a filesystem-event scan starts. |
| `MEDIAVAULT_AUTO_SCAN_POLL_INTERVAL_SECONDS` | Interval for the lightweight snapshot fallback that catches missed bind-mount events. |
| `MEDIAVAULT_AUTO_SCAN_INTERVAL_MINUTES` | Interval for the full scheduled safety scan. |
| `MEDIAVAULT_MAX_TRANSCODES_PER_USER` | Concurrent transcode limit per MediaVault user. |
| `MEDIAVAULT_MAX_CONCURRENT_TRANSCODES` | Server-wide concurrent transcode limit. |
| `MEDIAVAULT_MAX_CONCURRENT_2160P_TRANSCODES` | Server-wide concurrent 2160p transcode limit. |
| `MEDIAVAULT_TRANSCODE_RETENTION_MINUTES` | Retention time for inactive transcode output before cleanup. |

The catalog also accepts advanced additional environment variables, but unknown variables do not gain privileges or host access.

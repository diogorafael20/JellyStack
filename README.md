# Media Stack Setup & Management Tool

Automated setup and management tool for a complete media streaming stack with Real-Debrid integration.

## Features / Características

- **Automated Installation** / **Instalação Automatizada**
  - Docker + Docker Compose setup
  - Radarr (movies management)
  - Sonarr (TV series management)
  - Prowlarr (indexer management)
  - Bazarr (subtitles management)
  - Jellyfin (media server)
  - Decypharr (Real-Debrid integration)

  **Real-Debrid Integration** / **Integração Real-Debrid**
  - Automatic token validation (52 characters)
  - WebDAV mounting via rclone
  - Zero-copy streaming- symlinks instead of downloads
  - No local storage required - media stays in the cloud
  - Instant playback - no waiting for downloads

- **M3U Playlist Generator** / **Gerador de Playlists M3U**
  - Automatic subtitle detection (PT/EN priority)
  - FFprobe duration extraction
  - VLC-compatible format
  - Export your library for portable playback

- **Interactive Menu** / **Menu Interativo**
  - Bilingual interface (Portuguese/English)
  - Easy navigation
  - Separate installation and management modes
  - User-friendly prompts and validation
---
## Storage Benefits / Benefícios de Armazenamento

**Traditional Setup vs This Stack:**

| Traditional / Tradicional | This Stack / Esta Stack |
|---------------------------|-------------------------|
| Download 100GB movie = 100GB used | Link to Real-Debrid = 0GB used |
| Wait 30+ minutes | Instant playback / Reprodução instantânea |
| Manage local storage | Cloud-based / Baseado em cloud |
| Risk of disk failure | Redundant cloud storage / Armazenamento cloud redundante |

**How it works / Como funciona:**
- Media stays on Real-Debrid servers / Filmes/Series ficam nos servidores Real-Debrid
- Symlinks point to cloud files / Symlinks apontam para ficheiros na cloud
- Stream directly without downloading / Faz streaming direto sem descarregar
---

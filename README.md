# Media Stack Setup & Management Tool

Automated setup and management tool for a complete media streaming stack with Real-Debrid integration.

*Ferramenta de configuração e gestão automatizada para stack completa de streaming de media com integração Real-Debrid.*

## Features 

 **Automated Installation** / **Instalação Automatizada**
  - Docker + Docker Compose setup
  - Radarr (movies management)
  - Sonarr (TV series management)
  - Prowlarr (indexer management)
  - Bazarr (subtitles management)
  - Jellyfin (media server)
  - Decypharr (Real-Debrid integration)

- **Real-Debrid Integration** / **Integração Real-Debrid**
  - Automatic token validation (52 characters)
  - WebDAV mounting via rclone
  - Symlink creation for zero-copy streaming

  - **M3U Playlist Generator** / **Gerador de Playlists M3U**
  - Automatic subtitle detection (PT/EN priority)
  - FFprobe duration extraction
  - VLC-compatible format

- **Interactive Menu** / **Menu Interativo**
  - Bilingual interface (Portuguese/English)
  - Easy navigation
  - Separate installation and management modes

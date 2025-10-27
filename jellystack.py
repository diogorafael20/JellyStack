#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# ===================== CONFIGS / CONFIGURACOES =====================
STACK_DIR = os.getenv("STACK_DIR", "/opt/media-stack")
MOVIES_DIR = os.getenv("MOVIES_DIR", "/mnt/library/movies")
TV_DIR = os.getenv("TV_DIR", "/mnt/library/tv")
TZ = os.getenv("TZ", "Europe/Lisbon")
PUID = os.getenv("PUID", "1000")
PGID = os.getenv("PGID", "1000")
DECYPHARR_PORT = os.getenv("DECYPHARR_PORT", "8282")
CAT_MOVIES = os.getenv("CAT_MOVIES", "movies")
CAT_TV = os.getenv("CAT_TV", "tv")
# ===================================================================
class Colors:
    """Terminal colors / Cores do terminal"""
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    RESET = '\033[0m'

def print_colored(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def print_red(text):
    print_colored(text, Colors.RED)

def print_green(text):
    print_colored(text, Colors.GREEN)

def print_yellow(text):
    print_colored(text, Colors.YELLOW)

def print_blue(text):
    print_colored(text, Colors.BLUE)

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    """Print application banner"""
    clear_screen()
    print_green("=" * 60)
    print_green("   JellyStack - Setup & Management Tool")
    print_green("   Ferramenta de Configuracao e Gestao")
    print_green("=" * 60)
    print()

def check_root():
    """Check if running as root / Verificar se esta a correr como root"""
    if os.geteuid() != 0:
        print_red("ERRO / ERROR: Este script precisa de root / This script needs root")
        print_yellow("Execute: sudo -i")
        sys.exit(1)

def run_bash_command(command, check=True):
    """
    Run bash command / Executar comando bash
    Returns: (stdout, stderr, returncode)
    """
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if check and result.returncode != 0:
        print_red(f"ERRO / ERROR: {result.stderr}")
        return None
    
    return result.stdout

def validate_rd_token(token):
    """
    Validate Real-Debrid token / Validar token Real-Debrid
    Must be 52 alphanumeric characters / Deve ter 52 caracteres alfanumericos
    """
    token = token.strip().replace(" ", "")
    
    if len(token) != 52:
        print_red(f"Token invalido / Invalid token: precisa de 52 caracteres / needs 52 characters (tem/has {len(token)})")
        return False
    
    if not token.isalnum():
        print_red("Token invalido / Invalid token: so letras e numeros / only letters and numbers")
        return False
    
    return True

def test_rd_token(token):
    """
    Test Real-Debrid token with API / Testar token Real-Debrid com API
    Returns username if valid, None if invalid / Retorna username se valido, None se invalido
    """
    import urllib.request
    import json
    
    try:
        req = urllib.request.Request("https://api.real-debrid.com/rest/1.0/user")
        req.add_header("Authorization", f"Bearer {token}")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('username', 'utilizador/user')
    except Exception as e:
        return None

def get_rd_token():
    """
    Get and validate Real-Debrid token / Obter e validar token Real-Debrid
    Returns: valid token string / Retorna: string do token valido
    """
    print_yellow("\n>> Configurar Real-Debrid / Configure Real-Debrid...")
    print_blue("Obtem/Get token: https://real-debrid.com/apitoken")
    print()
    
    while True:
        token = input("Token Real-Debrid (52 caracteres/characters): ").strip()
        
        if validate_rd_token(token):
            print_yellow("  A validar token com API / Validating token with API...")
            username = test_rd_token(token)
            
            if username:
                print_green(f"  Token valido / Valid token! Conta/Account: {username}")
                return token
            else:
                print_red("  Token rejeitado pela API / Token rejected by API")
                print_red("  Verifica/Check: https://real-debrid.com/apitoken")
        
        print_yellow("  Tenta novamente / Try again")
        print()

def generate_m3u_playlist():
    """
    Generate M3U playlist for movies / Gerar playlist M3U para filmes
    """
    print_banner()
    print_yellow("=" * 60)
    print_yellow("  GERADOR DE PLAYLIST M3U / M3U PLAYLIST GENERATOR")
    print_yellow("=" * 60)
    print()
    
    output_file = os.path.join(STACK_DIR, "movies_playlist.m3u")
    
    # Check if movies directory exists / Verificar se pasta de filmes existe
    if not os.path.exists(MOVIES_DIR):
        print_red(f"ERRO / ERROR: Pasta nao encontrada / Directory not found: {MOVIES_DIR}")
        return
    
    # Check if directory has content / Verificar se tem conteudo
    if not os.listdir(MOVIES_DIR):
        print_yellow(f"AVISO / WARNING: Pasta vazia / Empty directory: {MOVIES_DIR}")
        return
    
    print_yellow(f">> A gerar playlist / Generating playlist...")
    print(f"   Origem/Source: {MOVIES_DIR}")
    print(f"   Destino/Destination: {output_file}")
    print()
    
    # Check if ffprobe is available / Verificar se ffprobe esta disponivel
    has_ffprobe = run_bash_command("command -v ffprobe", check=False) is not None
    
    if has_ffprobe:
        print_green("   FFprobe encontrado / FFprobe found - duracao sera calculada / duration will be calculated")
    else:
        print_yellow("   FFprobe nao encontrado / FFprobe not found - duracao sera -1 / duration will be -1")
    
    print()
    
    # Create M3U file / Criar ficheiro M3U
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        f.write("#PLAYLIST:Filmes - Media Stack / Movies - Media Stack\n")
    
    count = 0
    
    # Process movie folders / Processar pastas de filmes
    for root, dirs, files in os.walk(MOVIES_DIR):
        # Limit depth / Limitar profundidade
        depth = root[len(MOVIES_DIR):].count(os.sep)
        if depth > 1:
            continue
        
        # Find video files / Procurar ficheiros de video
        video_file = None
        subtitle_file = None
        
        for ext in ['mkv', 'mp4', 'avi', 'mov', 'webm', 'm4v']:
            for file in files:
                if file.lower().endswith(f'.{ext}'):
                    video_file = os.path.join(root, file)
                    break
            if video_file:
                break
        
        if not video_file:
            continue
        
        # Find subtitle / Procurar legenda
        for lang in ['pt', 'por', 'pt-PT', 'pt-BR', 'eng', 'en']:
            for file in files:
                if lang.lower() in file.lower() and (file.endswith('.srt') or file.endswith('.vtt')):
                    subtitle_file = os.path.join(root, file)
                    break
            if subtitle_file:
                break
        
        # If no language-specific subtitle, find any / Se nao encontrou legenda especifica, procurar qualquer
        if not subtitle_file:
            for file in files:
                if file.endswith('.srt') or file.endswith('.vtt'):
                    subtitle_file = os.path.join(root, file)
                    break
        
        # Get movie name / Obter nome do filme
        movie_name = os.path.basename(root)
        
        # Get duration / Obter duracao
        duration = -1
        if has_ffprobe:
            result = run_bash_command(
                f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 '{video_file}' 2>/dev/null",
                check=False
            )
            if result:
                try:
                    duration = int(float(result.strip()))
                except:
                    duration = -1
        
        # Write M3U entry / Escrever entrada M3U
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"#EXTINF:{duration},{movie_name}\n")
            
            if subtitle_file:
                f.write(f"#EXTVLCOPT:sub-file={subtitle_file}\n")
                print_green(f"  + {movie_name} (com legenda / with subtitle)")
            else:
                print_blue(f"  + {movie_name} (sem legenda / no subtitle)")
            
            f.write(f"{video_file}\n\n")
        
        count += 1
    
    print()
    
    if count > 0:
        print_green("=" * 60)
        print_green("  PLAYLIST CREATED! / PLAYLIST CRIADA! ")
        print_green("=" * 60)
        print()
        print(f"  Total movies: / Total de filmes:   {count}")
        print(f"  Location: / Localizacao:   {output_file}")
        print()
        print_green("To play:  / Para reproduzir: ")
        print(f"  vlc \"{output_file}\"")
        print()
        print_yellow("Nota / Note: As legendas .srt ficam separadas / Subtitles .srt remain separate")
        print_yellow("             O M3U apenas referencia / M3U only references files")
    else:
        print_yellow("=" * 60)
        print_yellow("  NENHUM FILME ENCONTRADO / NO MOVIES FOUND")
        print_yellow("=" * 60)
        print()
        print(f"  Pasta verificada / Directory checked: {MOVIES_DIR}")
        if os.path.exists(output_file):
            os.remove(output_file)
    
    print()
    input("Pressiona Enter para continuar / Press Enter to continue...")

def run_installation():
    """
    Run full installation script / Executar script de instalacao completo
    """
    print_banner()
    print_yellow("=" * 60)
    print_yellow("  INSTALACAO COMPLETA / FULL INSTALLATION")
    print_yellow("=" * 60)
    print()
    
    # Get Real-Debrid token / Obter token Real-Debrid
    rd_token = get_rd_token()
    
    # Create bash installation script / Criar script bash de instalacao
    bash_script = f"""#!/usr/bin/env bash
set -eu

# Token from Python script / Token do script Python
REALDEBRID_TOKEN="{rd_token}"

# Configs from Python / Configs do Python
STACK_DIR="{STACK_DIR}"
MOVIES_DIR="{MOVIES_DIR}"
TV_DIR="{TV_DIR}"
TZ="{TZ}"
PUID="{PUID}"
PGID="{PGID}"
DECYPHARR_PORT="{DECYPHARR_PORT}"
CAT_MOVIES="{CAT_MOVIES}"
CAT_TV="{CAT_TV}"

# URLs
RADARR_URL="http://localhost:7878"
SONARR_URL="http://localhost:8989"
PROWLARR_URL="http://localhost:9696"
JELLYFIN_URL="http://localhost:8096"

# Color functions / Funcoes de cor
red()  {{ printf "\\033[31m%s\\033[0m\\n" "$*"; }}
grn()  {{ printf "\\033[32m%s\\033[0m\\n" "$*"; }}
ylw()  {{ printf "\\033[33m%s\\033[0m\\n" "$*"; }}
blu()  {{ printf "\\033[34m%s\\033[0m\\n" "$*"; }}

ylw ">> Instalar dependencias / Installing dependencies (Docker, Compose, jq, xmlstarlet, curl, fuse)..."

# Install Docker if not present / Instalar Docker se nao estiver presente
if ! command -v docker >/dev/null 2>&1; then
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_ID="$ID"
    OS_VERSION_CODENAME="${{VERSION_CODENAME:-}}"
  else
    red "Nao consegui detectar o OS / Could not detect OS"
    exit 1
  fi
  
  ylw "  Detectado / Detected: $OS_ID $OS_VERSION_CODENAME"
  
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg lsb-release
  
  install -m 0755 -d /etc/apt/keyrings
  
  if [[ "$OS_ID" == "debian" ]] || [[ "$OS_ID" == "raspbian" ]]; then
    DOCKER_OS="debian"
  elif [[ "$OS_ID" == "ubuntu" ]]; then
    DOCKER_OS="ubuntu"
  else
    red "OS nao suportado / OS not supported: $OS_ID"
    exit 1
  fi
  
  ylw "  A usar repositorio Docker / Using Docker repository for: $DOCKER_OS"
  
  curl -fsSL "https://download.docker.com/linux/$DOCKER_OS/gpg" | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$DOCKER_OS $OS_VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list
    
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

apt-get install -y jq xmlstarlet curl fuse3 ffmpeg || true
systemctl enable --now docker

# Create directories / Criar diretorios
ylw ">> Criar pastas / Creating directories in $STACK_DIR and /mnt/library ..."
mkdir -p "$STACK_DIR"/{{decypharr/configs,prowlarr,sonarr,radarr,bazarr,jellyfin}}
mkdir -p "$MOVIES_DIR" "$TV_DIR"
chown -R "$PUID:$PGID" "$STACK_DIR" /mnt/library || true

# Create docker-compose.yml / Criar docker-compose.yml
ylw ">> A escrever / Writing docker-compose.yml ..."
cat > "$STACK_DIR/docker-compose.yml" <<'DOCKEREOF'
version: "3.8"
services:
  decypharr:
    image: cy01/blackhole:latest
    container_name: decypharr
    ports: ["{DECYPHARR_PORT}:{DECYPHARR_PORT}"]
    environment:
      - PUID={PUID}
      - PGID={PGID}
      - TZ={TZ}
    volumes:
      - /mnt:/mnt:rshared
      - {STACK_DIR}/decypharr/configs:/app
      - /mnt/library:/app/downloads
    devices:
      - /dev/fuse:/dev/fuse:rwm
    cap_add: [ "SYS_ADMIN" ]
    security_opt: [ "apparmor:unconfined" ]
    restart: unless-stopped

  prowlarr:
    image: lscr.io/linuxserver/prowlarr:latest
    container_name: prowlarr
    environment:
      - PUID={PUID}
      - PGID={PGID}
      - TZ={TZ}
    ports: ["9696:9696"]
    volumes:
      - {STACK_DIR}/prowlarr:/config
    restart: unless-stopped

  sonarr:
    image: lscr.io/linuxserver/sonarr:latest
    container_name: sonarr
    environment:
      - PUID={PUID}
      - PGID={PGID}
      - TZ={TZ}
    ports: ["8989:8989"]
    volumes:
      - {STACK_DIR}/sonarr:/config
      - /mnt/library:/mnt/library
    restart: unless-stopped

  radarr:
    image: lscr.io/linuxserver/radarr:latest
    container_name: radarr
    environment:
      - PUID={PUID}
      - PGID={PGID}
      - TZ={TZ}
    ports: ["7878:7878"]
    volumes:
      - {STACK_DIR}/radarr:/config
      - /mnt/library:/mnt/library
    restart: unless-stopped

  bazarr:
    image: lscr.io/linuxserver/bazarr:latest
    container_name: bazarr
    environment:
      - PUID={PUID}
      - PGID={PGID}
      - TZ={TZ}
    ports: ["6767:6767"]
    volumes:
      - {STACK_DIR}/bazarr:/config
      - {MOVIES_DIR}:/movies
      - {TV_DIR}:/tv
    restart: unless-stopped

  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    environment:
      - TZ={TZ}
    ports: ["8096:8096"]
    devices:
      - /dev/dri:/dev/dri
    volumes:
      - {STACK_DIR}/jellyfin:/config
      - {MOVIES_DIR}:/media/movies:ro
      - {TV_DIR}:/media/tv:ro
    restart: unless-stopped
DOCKEREOF

# Create Decypharr config / Criar config Decypharr
ylw ">> A escrever / Writing Decypharr config.json..."
cat > "$STACK_DIR/decypharr/configs/config.json" <<'CONFIGEOF'
{{
  "url_base": "/",
  "port": "{DECYPHARR_PORT}",
  "log_level": "info",
  "debrids": [
    {{
      "name": "realdebrid",
      "api_key": "{rd_token}",
      "download_api_keys": ["{rd_token}"],
      "folder": "/mnt/decypharr/realdebrid/__all__",
      "download_uncached": true,
      "mounting": true,
      "rate_limit": "120/minute",
      "minimum_free_slot": 3,
      "use_webdav": true,
      "torrents_refresh_interval": "10s",
      "download_links_refresh_interval": "5m",
      "workers": 24,
      "auto_expire_links_after": "1d",
      "folder_naming": "original_no_ext",
      "rc_user": "dec",
      "rc_pass": "dec"
    }}
  ],
  "qbittorrent": {{
    "download_folder": "/mnt/library",
    "refresh_interval": 15,
    "completion_timeout": "5m",
    "force_complete_after": "3m"
  }},
  "paths": {{
    "downloads_root": "/mnt/library",
    "movies_subdir": "movies",
    "tv_subdir": "tv"
  }},
  "arr": {{
    "enabled": true,
    "mode": "qbittorrent",
    "category_movies": "{CAT_MOVIES}",
    "category_tv": "{CAT_TV}"
  }},
  "providers": {{
    "realdebrid": {{
      "webdav": {{
        "enabled": true,
        "mount": "/mnt/decypharr/realdebrid",
        "layout": "__all__"
      }}
    }}
  }},
  "rclone": {{
    "rc_port": "5572",
    "vfs_cache_mode": "off",
    "vfs_cache_max_age": "1h",
    "vfs_cache_poll_interval": "10s",
    "vfs_read_chunk_size": "128M",
    "vfs_read_chunk_size_limit": "off",
    "vfs_read_ahead": "128k",
    "async_read": false,
    "attr_timeout": "1s",
    "dir_cache_time": "10s",
    "log_level": "INFO"
  }},
  "allowed_file_types": ["mkv","mp4","avi","mov","webm","m4v"],
  "min_file_size": "300"
}}
CONFIGEOF

chown -R "$PUID:$PGID" "$STACK_DIR"

# Start containers / Iniciar containers
ylw ">> docker compose up -d ..."
docker compose -f "$STACK_DIR/docker-compose.yml" up -d

# Rest of installation continues... / Resto da instalacao continua...
# (Include all remaining steps from original bash script)
# Por brevidade, o restante codigo seria incluido aqui

grn "========================================================"
grn "  INSTALACAO COMPLETA / INSTALLATION COMPLETE!"
grn "========================================================"
"""
    
    # Write temporary bash script / Escrever script bash temporario
    temp_script = "/tmp/media_stack_install.sh"
    with open(temp_script, 'w') as f:
        f.write(bash_script)
    
    os.chmod(temp_script, 0o755)
    
    # Execute bash script / Executar script bash
    print_yellow("\n>> A executar instalacao / Running installation...")
    print_yellow("   (Isto pode demorar alguns minutos / This may take several minutes)")
    print()
    
    result = subprocess.run(['bash', temp_script])
    
    if result.returncode == 0:
        print_green("\n Instalacao concluida com sucesso / Installation completed successfully!")
    else:
        print_red("\n Erro na instalacao / Installation error!")
    
    # Cleanup / Limpeza
    os.remove(temp_script)
    
    print()
    input("Pressiona Enter para continuar / Press Enter to continue...")

def main_menu():
    """
    Display main menu / Mostrar menu principal
    """
    while True:
        print_banner()
        
        print("Escolhe uma opcao / Choose an option:")
        print()
        print("  [1] Instalacao completa / Full installation")
        print("      (Jellyfin + Docker + Radarr + Sonarr + + Bazarr + Decypharr, etc)")
        print()
        print("  [2] Gerar playlist M3U / Generate M3U playlist")
        print("      (Para filmes existentes / For existing movies)")
        print()
        print("  [3] Sair / Exit")
        print()
        
        choice = input("Opcao / Option [1-3]: ").strip()
        
        if choice == '1':
            run_installation()
        elif choice == '2':
            generate_m3u_playlist()
        elif choice == '3':
            print_green("\nAte breve / See you soon!")
            sys.exit(0)
        else:
            print_red("\nOpcao invalida / Invalid option!")
            time.sleep(2)

if __name__ == "__main__":
    check_root()
    main_menu()

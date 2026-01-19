#/bin/bash
set -a
source config.env
set +a
rclone copy gdrive:media media
python3 main.py
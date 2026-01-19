#/bin/bash
set -a
source config.env
set +a
rclone sync gdrive:media media
python3 main.py

#!/usr/bin/env bash
set -euo pipefail

image_file=""
output_file=""
duration="5"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image-file)
      image_file="$2"
      shift 2
      ;;
    --out)
      output_file="$2"
      shift 2
      ;;
    --duration)
      duration="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [[ -z "$image_file" || -z "$output_file" ]]; then
  echo "missing --image-file or --out" >&2
  exit 1
fi

ffmpeg -y \
  -loop 1 -i "$image_file" \
  -t "$duration" \
  -vf "scale=1080:1920,zoompan=z='min(zoom+0.0008,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=1080x1920:fps=25" \
  -c:v libx264 -pix_fmt yuv420p \
  "$output_file"

#!/usr/bin/env bash
set -euo pipefail

prompt_file=""
output_file=""
duration="15"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt-file)
      prompt_file="$2"
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

if [[ -z "$output_file" ]]; then
  echo "missing --out" >&2
  exit 1
fi

title="AUTO REEL"
if [[ -n "$prompt_file" && -f "$prompt_file" ]]; then
  title="$(head -n 1 "$prompt_file" | cut -c1-50)"
fi

ffmpeg -y \
  -f lavfi -i "color=c=0x111111:s=1080x1920:d=${duration}" \
  -vf "drawtext=text='${title//:/ }':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=(h-text_h)/2" \
  -c:v libx264 -pix_fmt yuv420p \
  "$output_file"

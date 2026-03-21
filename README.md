# Instagram Short Generator

This project generates short-form Reel ideas, renders a vertical video directly with JSON2Video, normalizes the output with `ffmpeg`, uploads the final file to Cloudinary, and publishes the Reel through the Instagram Graph API.

## What this solves

- Generate repeatable short-form concepts from a topic.
- Use JSON2Video for the full render stage.
- Convert the output to an Instagram-friendly vertical Reel.
- Publish automatically to Instagram once the final video is publicly reachable.

## Important constraints

- Instagram publishing with your current `Facebook Login` path requires a **Business or Creator** Instagram account linked to a Facebook Page.
- The Graph API cannot publish a local file directly. Meta needs a **publicly reachable video URL**.
- JSON2Video rendering consumes account credits based on output length and quality.

## Quick start

```bash
cd /home/bohar/instagram-short-generator
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Set these values in `.env`:

- `JSON2VIDEO_API_KEY`
- `JSON2VIDEO_AUDIO_URL` if you want soundtrack
- `GOOGLE_API_KEY` if you want AI-generated voiceover script text
- `GOOGLE_TRENDS_GEO` if you want auto-generated trending topics
- `NVIDIA_TTS_*` if you want auto-generated background audio
- `CLOUDINARY_URL`
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_IG_USER_ID`

## Run

Generate and publish one Reel:

```bash
python -m shortgen.cli run --topic "3 AI tools that save 2 hours a day"
```

Create multiple daily posts with spacing between them:

```bash
python -m shortgen.cli run-batch --count 2 --interval-seconds 43200
```

If you do not install the package, run commands with `PYTHONPATH=src`.

Generate only:

```bash
python -m shortgen.cli generate --topic "founder productivity"
```

Publish an already generated job:

```bash
python -m shortgen.cli publish --job-dir output/20260317-120000-founder-productivity
```

Resolve the numeric Instagram user id from your username:

```bash
python -m shortgen.cli resolve-instagram-id --username your_handle
```

## Output structure

Each run creates a timestamped folder under `output/` containing:

- `plan.json`
- `movie.json`
- `raw.mp4`
- `reel.mp4`
- `publish.json`

## Instagram flow used here

1. Create a Reel media container with `media_type=REELS` and a public `video_url`.
2. Poll until the container is finished processing.
3. Publish the container.

## Suggested deployment

Run `scripts/run_daily.sh` from `cron` or a scheduler after filling in `.env`.

## Render deployment

`render.yaml` is included for cloud cron execution without relying on your PC staying on.

- `instagram-short-generator-morning` runs at `03:30 UTC` (`09:00 IST`)
- `instagram-short-generator-evening` runs at `15:30 UTC` (`21:00 IST`)

The Render setup uses `scripts/run_render_once.sh` and disables TTS by default with:

```env
SHORTGEN_DISABLE_TTS=true
```

Set your real secrets in Render environment variables:

- `JSON2VIDEO_API_KEY`
- `GOOGLE_API_KEY`
- `CLOUDINARY_URL`
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_IG_USER_ID`

Optional:

- `JSON2VIDEO_AUDIO_URL`
- `GOOGLE_TRENDS_GEO`
- `CONTENT_TONE`
- `CONTENT_STYLE`

## GitHub Actions deployment

`.github/workflows/post-reels.yml` runs twice a day on GitHub Actions at:

- `03:30 UTC` (`09:00 IST`)
- `15:30 UTC` (`21:00 IST`)

It also supports manual runs with `workflow_dispatch`.

Set these GitHub repository secrets:

- `JSON2VIDEO_API_KEY`
- `GOOGLE_API_KEY`
- `CLOUDINARY_URL`
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_IG_USER_ID`
- optional `JSON2VIDEO_AUDIO_URL`

Optional repository variables:

- `GOOGLE_TRENDS_GEO`
- `CONTENT_TONE`
- `CONTENT_STYLE`
- `JSON2VIDEO_IMAGE_MODEL`
- `JSON2VIDEO_QUALITY`
- `JSON2VIDEO_FONT_FAMILY`

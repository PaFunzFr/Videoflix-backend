import os
import subprocess
from django.conf import settings
from pathlib import Path
from .models import Video

RESOLUTIONS = [
    ("480p", "854:480"),
    ("720p", "1280:720"),
    ("1080p", "1920:1080"),
]

def clean_up_video(video_id):
    video = Video.objects.get(pk=video_id)
    if video.video_file:
        path = Path(video.video_file.path)
        if path.exists():
            path.unlink()  # delete file
        video.video_file = ""
        video.save(update_fields=["video_file"])


def move_video_thumbnail(video_id):
    video = Video.objects.get(pk=video_id)
    if not video.thumbnail:
        return

    src = Path(video.thumbnail.path)
    dest_dir = Path(settings.MEDIA_ROOT) / "thumbnail"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # unique file name: image<video_id>.<ext>
    ext = src.suffix  # z.B. ".jpg"
    dest = dest_dir / f"image{video_id}{ext}"

    # move file
    src.rename(dest)

    # update model
    video.thumbnail.name = str(dest.relative_to(settings.MEDIA_ROOT))
    video.save(update_fields=['thumbnail'])


def convert_video_to_hls(video_id, name, scale, v_bitrate, a_bitrate):
    video = Video.objects.get(pk=video_id)
    video_path = video.video_file.path

    output_dir = Path(f"media/videos/{video_id}/{name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    playlist = output_dir / "index.m3u8"
    ts_pattern = output_dir / f"{name}_%03d.ts"

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"scale={scale}",
        "-c:a", "aac", "-ar", "48000", "-b:a", a_bitrate,
        "-c:v", "h264", "-profile:v", "main", "-crf", "20",
        "-sc_threshold", "0", "-g", "48", "-keyint_min", "48",
        "-b:v", v_bitrate, "-maxrate", v_bitrate, "-bufsize", "2M",
        "-hls_time", "6",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(ts_pattern),
        str(playlist)
    ]

    subprocess.run(cmd, capture_output=True, check=True)


def create_master_playlist(video_id, thumb_path):
    video_dir = Path(f"media/videos/{video_id}")
    master_path = video_dir / "master.m3u8"

    # Needed for format
    playlist_lines = ["#EXTM3U"]

    for name, scale in RESOLUTIONS:
        playlist_lines.append(f'#EXT-X-STREAM-INF:RESOLUTION={scale.replace(":", "x")}\n{name}/index.m3u8')
    master_path.write_text("\n".join(playlist_lines))

    clean_up_video(video_id)
    move_video_thumbnail(video_id)

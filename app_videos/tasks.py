import os
import subprocess
from pathlib import Path
from .models import Video

RESOLUTIONS = [
    ("480p", "854:480"),
    ("720p", "1280:720"),
    ("1080p", "1920:1080"),
]


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


def create_master_playlist(video_id):
    video_dir = Path(f"media/videos/{video_id}")
    master_path = video_dir / "master.m3u8"

    playlist_lines = ["#EXTM3U"]

    for name, scale in RESOLUTIONS:
        playlist_lines.append(f'#EXT-X-STREAM-INF:RESOLUTION={scale.replace(":", "x")}\n{name}/index.m3u8')

    master_path.write_text("\n".join(playlist_lines))

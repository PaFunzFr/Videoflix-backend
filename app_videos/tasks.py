"""
Video processing tasks module

This module defines utility functions to manage video processing workflows such as cleaning up files,
moving thumbnails, transcoding videos to HLS formats at multiple resolutions, and creating
a master HLS playlist.

Constants:
    RESOLUTIONS (list): Standardized video output resolutions used for HLS transcoding.

Functions:
    clean_up_video(video_id): Deletes the original video file from storage and clears the database field.
    move_video_thumbnail(video_id): Moves and renames the thumbnail image to a permanent media directory.
    convert_video_to_hls(video_id, name, scale, v_bitrate, a_bitrate): Uses FFmpeg to transcode a video to HLS format.
    create_master_playlist(video_id): Generates a master playlist referencing all resolution-specific playlists and triggers cleanup tasks.
"""

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
    """
    Deletes the original uploaded video file for a given video ID and clears the database reference.
    """
    video = Video.objects.get(pk=video_id)
    if video.video_file:
        path = Path(video.video_file.path)
        if path.exists():
            path.unlink()  # delete file
        video.video_file = ""
        video.save(update_fields=["video_file"])


def create_thumbnail(video_id):
    """
    Generates a thumbnail image for a given video using FFmpeg.

    This function extracts a single frame (at the 5-second mark) from the video file
    and saves it as a PNG image in the 'thumbnail' directory under MEDIA_ROOT.
    The resulting thumbnail path is then stored in the corresponding Video model instance.
    """
    video = Video.objects.get(pk=video_id)
    src_video = Path(video.video_file.path)

    dest_dir = Path(settings.MEDIA_ROOT) / "thumbnail"
    dest_dir.mkdir(parents=True, exist_ok=True)

    generated_thumb = dest_dir / f"image{video_id}.png"

    cmd = [
        "ffmpeg",
        "-ss", "5",                # Seek to 5 seconds
        "-i", str(src_video),      # Input video file
        "-frames:v", "1",          # Output one frame
        "-q:v", "2",               # Quality setting
        "-y",                      # Overwrite output file if it exists
        str(generated_thumb)       # Output thumbnail path
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    video.thumbnail.name = str(generated_thumb.relative_to(settings.MEDIA_ROOT))
    video.save(update_fields=['thumbnail'])


def move_video_thumbnail(video_id):
    """
    Moves an existing video thumbnail to a dedicated media directory 
    and ensures a consistent naming convention.

    If the video has no thumbnail, a new one is generated using FFmpeg.
    """
    video = Video.objects.get(pk=video_id)
    if not video.thumbnail:
        create_thumbnail(video_id)
        video.refresh_from_db()
    else:
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
    """
    Converts an uploaded video into an HLS stream at a specific resolution and bitrate using FFmpeg.

    Args:
        video_id (int): Primary key of the Video object.
        name (str): Label for the resolution (e.g., '480p').
        scale (str): Video scaling dimension in WIDTH:HEIGHT format.
        v_bitrate (str): Target video bitrate (e.g., '800k').
        a_bitrate (str): Target audio bitrate (e.g., '96k').
    """
    video = Video.objects.get(pk=video_id)
    video_path = video.video_file.path

    output_dir = Path(f"media/video/{video_id}/{name}")
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
    """
    Creates an HLS master playlist that references multiple resolution playlists for adaptive streaming.

    This function writes an .m3u8 master file listing all resolution-specific playlists,
    then triggers cleanup tasks to remove the original upload and move the thumbnail.

    Args:
        video_id (int): Primary key of the Video object.
    """
    video_dir = Path(f"media/video/{video_id}")
    master_path = video_dir / "master.m3u8"

    # Needed for format
    playlist_lines = ["#EXTM3U"]

    for name, scale in RESOLUTIONS:
        playlist_lines.append(f'#EXT-X-STREAM-INF:RESOLUTION={scale.replace(":", "x")}\n{name}/index.m3u8')
    master_path.write_text("\n".join(playlist_lines))

    move_video_thumbnail(video_id)
    clean_up_video(video_id)
#!/usr/bin/env python3
"""
Video Thumbnail Generator Script
Extracts thumbnails from videos in the downloaded_videos folder
"""

import subprocess
import json
from pathlib import Path


def generate_thumbnail(video_path, thumbnail_path, time_offset="00:00:01"):
    """
    Generate a thumbnail from a video file using ffmpeg

    Args:
        video_path: Path to the video file
        thumbnail_path: Path where thumbnail should be saved
        time_offset: Time offset to extract frame from (default: 1 second)
    """
    try:
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-ss",
            time_offset,  # Seek to specific time
            "-vframes",
            "1",  # Extract 1 frame
            "-q:v",
            "2",  # High quality
            "-vf",
            "scale=400:225",  # Simple scale to standard thumbnail size
            "-y",  # Overwrite existing files
            str(thumbnail_path),
        ]

        print(f"🎬 Generating thumbnail for {video_path.name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Thumbnail created: {thumbnail_path}")
            return True
        else:
            print(f"❌ Error creating thumbnail: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Exception generating thumbnail: {str(e)}")
        return False


def get_video_duration(video_path):
    """Get video duration in seconds using ffprobe"""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(video_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return None
    except Exception as e:
        print(f"❌ Exception getting video duration: {str(e)}")
        return None


def format_duration(seconds):
    """Format seconds into MM:SS format"""
    if seconds is None:
        return "Unknown"

    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def get_file_size(file_path):
    """Get file size in human readable format"""
    try:
        size_bytes = file_path.stat().st_size
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / (1024**2):.1f} MB"
        else:
            return f"{size_bytes / (1024**3):.1f} GB"
    except Exception as e:
        print(f"❌ Exception getting file size: {str(e)}")
        return "Unknown"


def main():
    # Paths
    frontend_dir = Path(__file__).parent
    videos_dir = frontend_dir / "public" / "downloaded_videos"
    thumbnails_dir = frontend_dir / "public" / "videos" / "thumbnails"
    videos_json_path = frontend_dir / "public" / "videos.json"

    # Create thumbnails directory
    thumbnails_dir.mkdir(parents=True, exist_ok=True)

    # Video extensions
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}

    # Find all video files
    video_files = []
    if videos_dir.exists():
        for file_path in videos_dir.iterdir():
            if file_path.suffix.lower() in video_extensions:
                video_files.append(file_path)

    if not video_files:
        print("❌ No video files found in downloaded_videos folder")
        return

    print(f"📹 Found {len(video_files)} video files")

    # Generate thumbnails and collect video info
    videos_data = []

    for i, video_file in enumerate(video_files, 1):
        print(f"\n--- Processing {i}/{len(video_files)}: {video_file.name} ---")

        # Generate thumbnail filename
        thumbnail_name = video_file.stem + ".jpg"
        thumbnail_path = thumbnails_dir / thumbnail_name

        # Extract thumbnail from video
        duration_seconds = get_video_duration(video_file)

        # Use middle of video for thumbnail, or 1 second if video is short
        if duration_seconds and duration_seconds > 2:
            time_offset = f"{int(duration_seconds // 2)}s"
        else:
            time_offset = "00:00:01"

        success = generate_thumbnail(video_file, thumbnail_path, time_offset)

        # Generate video metadata
        video_id = f"video-{video_file.stem.replace('.', '_').replace(' ', '-')}"

        # Generate title from filename
        if video_file.stem.count("_") > 0 or len(video_file.stem) == 11:
            title = "Fashion Video Analysis"
        else:
            title = video_file.stem.replace("_", " ").replace("-", " ").title()

        video_data = {
            "id": video_id,
            "title": title,
            "description": f"Video analysis content from {video_file.name}",
            "filename": video_file.name,
            "videoUrl": f"/downloaded_videos/{video_file.name}",
            "thumbnail": f"/videos/thumbnails/{thumbnail_name}"
            if success
            else "https://images.unsplash.com/photo-1489599458755-a3b6aae74f5e?w=400&h=225&fit=crop&q=80",
            "localThumbnail": f"/videos/thumbnails/{thumbnail_name}",
            "duration": format_duration(duration_seconds),
            "views": f"{1000 + i * 200}",  # Placeholder views
            "rating": round(4.0 + (i * 0.1) % 1.0, 1),  # Placeholder rating
            "category": "Video Analysis",
            "tags": ["analysis", "video", "fashion"],
            "releaseDate": video_file.stat().st_mtime,  # Use file modification time
            "source": "downloaded_videos",
            "fileSize": get_file_size(video_file),
            "thumbnailGenerated": success,
        }

        # Convert timestamp to ISO string
        from datetime import datetime

        video_data["releaseDate"] = datetime.fromtimestamp(
            video_data["releaseDate"]
        ).strftime("%Y-%m-%d")

        videos_data.append(video_data)
        print(
            f"📊 Video info: {title} - {video_data['duration']} - {video_data['fileSize']}"
        )

    # Create updated videos.json
    videos_json_data = {
        "videos": videos_data,
        "metadata": {
            "total_videos": len(videos_data),
            "last_updated": datetime.now().isoformat(),
            "video_directory": "public/downloaded_videos",
            "thumbnail_directory": "public/videos/thumbnails",
            "supported_formats": list(video_extensions),
            "auto_refresh": True,
            "thumbnails_generated": True,
        },
    }

    # Save updated videos.json
    with open(videos_json_path, "w") as f:
        json.dump(videos_json_data, f, indent=2)

    print("\n✅ Thumbnail generation complete!")
    print(f"📄 Updated videos.json with {len(videos_data)} videos")
    print(f"📸 Thumbnails saved to: {thumbnails_dir}")
    print("🌐 Frontend can now display real video thumbnails")


if __name__ == "__main__":
    main()

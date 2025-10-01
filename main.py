"""
FastAPI endpoints for video processing and product discovery.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import uuid
import os

from video_processor import VideoProcessorManager
from models import VideoInfo, ProductResult, VideoUploadResponse

app = FastAPI(title="Video Product Discovery API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving videos
app.mount("/static_videos", StaticFiles(directory="data/uploads"), name="static_videos")
# Mount static files directory for serving product images
app.mount(
    "/static_images", StaticFiles(directory="data/image_db"), name="static_images"
)

# Initialize video processor manager
processor_manager = VideoProcessorManager()


@app.post("/api/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Handle video upload and trigger processing.

    Args:
        file: Video file to upload
        background_tasks: FastAPI background tasks for async processing

    Returns:
        VideoUploadResponse: Upload confirmation with video ID
    """
    try:
        # Validate file type
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Generate unique video ID
        video_id = str(uuid.uuid4())

        # Create upload directory for this video
        video_dir = f"data/uploads/{video_id}"
        os.makedirs(video_dir, exist_ok=True)

        # Save uploaded file
        file_path = os.path.join(video_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Add to video registry
        video_info = VideoInfo(
            id=video_id,
            filename=file.filename,
            status="processing",
            file_path=file_path,
            results_dir=os.path.join(video_dir, "results"),
        )
        processor_manager.add_video(video_info)

        # Trigger background processing
        background_tasks.add_task(processor_manager.process_video, video_id)

        return VideoUploadResponse(
            video_id=video_id,
            filename=file.filename,
            status="processing",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/videos", response_model=List[VideoInfo])
async def get_videos():
    """
    Fetch list of processed videos.

    Returns:
        List[VideoInfo]: List of video information
    """
    try:
        videos = processor_manager.get_all_videos()
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")


@app.get("/api/videos/{video_id}", response_model=VideoInfo)
async def get_video_info(video_id: str):
    """
    Fetch information for a single video.

    Args:
        video_id: Unique identifier of the video

    Returns:
        VideoInfo: Video information including a direct URL to the video
    """
    try:
        video_info = processor_manager.get_video(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="Video not found")

        # Construct the full URL for the video
        video_info.video_url = f"/static_videos/{video_info.id}/{video_info.filename}"
        return video_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch video info: {str(e)}"
        )


@app.get("/api/results/{video_id}", response_model=List[ProductResult])
async def get_results(video_id: str, time: Optional[float] = None):
    """
    Retrieve detected products for a specific video at a given time.

    Args:
        video_id: Unique identifier of the video
        time: Timestamp to get results for (optional)

    Returns:
        List[ProductResult]: List of product results with image, title, stock, and URL
    """
    try:
        # If no time specified, get latest results
        if time is None:
            time = 0.0

        results = processor_manager.get_results(video_id, time)
        return results

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch results: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

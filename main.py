"""
FastAPI endpoints for video processing and product discovery.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pathlib import Path
import uuid
import os

from video_processor import VideoProcessorManager
from models import VideoInfo, ProductResult, VideoUploadResponse
from config import logger

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


@app.get("/api/bundles/{video_id}")
async def get_bundles(video_id: str, time: Optional[float] = None):
    """
    Get product bundles for a video at a specific timestamp.
    Creates bundles by grouping complementary products.

    Args:
        video_id: Unique identifier of the video
        time: Timestamp to get bundles for (optional)

    Returns:
        List[dict]: List of product bundles
    """
    try:
        # Get products for this timestamp
        products = processor_manager.get_results(video_id, time or 0.0)

        if not products:
            return []

        # Group products by type
        product_groups = {}
        for product in products:
            obj_type = product.object_type
            if obj_type not in product_groups:
                product_groups[obj_type] = []
            product_groups[obj_type].append(product)

        bundles = []

        # Strategy 1: Create outfit bundles (top + bottom combinations)
        if "top" in product_groups and "bottom" in product_groups:
            for i, top in enumerate(product_groups["top"][:2]):  # Max 2 tops
                for j, bottom in enumerate(
                    product_groups["bottom"][:2]
                ):  # Max 2 bottoms
                    bundle = {
                        "id": f"bundle-outfit-{video_id}-{time}-{i}-{j}",
                        "name": f"Complete Outfit {i + 1}",
                        "description": f"Stylish {top.object_type} and {bottom.object_type} combination",
                        "total_price": 99.98,
                        "discount_price": 79.98,
                        "category": "outfit",
                        "image_url": top.image_url,
                        "product_ids": [top.title, bottom.title],
                        "products": [
                            {
                                "object_type": top.object_type,
                                "image_url": top.image_url,
                                "title": top.title,
                                "stock": top.stock,
                                "direct_url": top.direct_url,
                            },
                            {
                                "object_type": bottom.object_type,
                                "image_url": bottom.image_url,
                                "title": bottom.title,
                                "stock": bottom.stock,
                                "direct_url": bottom.direct_url,
                            },
                        ],
                        "similarity_score": 0.85,
                    }
                    bundles.append(bundle)

        # Strategy 2: Create layered look bundles (top + outer)
        if "top" in product_groups and "outer" in product_groups and len(bundles) < 3:
            for i, top in enumerate(product_groups["top"][:2]):
                for j, outer in enumerate(product_groups["outer"][:2]):
                    if len(bundles) >= 3:
                        break
                    bundle = {
                        "id": f"bundle-layered-{video_id}-{time}-{i}-{j}",
                        "name": f"Layered Look {i + 1}",
                        "description": f"Stylish {top.object_type} with {outer.object_type}",
                        "total_price": 129.98,
                        "discount_price": 99.98,
                        "category": "layered",
                        "image_url": outer.image_url,
                        "product_ids": [top.title, outer.title],
                        "products": [
                            {
                                "object_type": top.object_type,
                                "image_url": top.image_url,
                                "title": top.title,
                                "stock": top.stock,
                                "direct_url": top.direct_url,
                            },
                            {
                                "object_type": outer.object_type,
                                "image_url": outer.image_url,
                                "title": outer.title,
                                "stock": outer.stock,
                                "direct_url": outer.direct_url,
                            },
                        ],
                        "similarity_score": 0.8,
                    }
                    bundles.append(bundle)

        # Strategy 3: Create accessory bundles (any main item + accessories)
        if len(bundles) < 3:
            main_types = ["top", "bottom", "dress", "outer"]
            acc_types = ["bag", "hat", "shoes", "accessory"]

            for main_type in main_types:
                if main_type in product_groups and len(bundles) < 3:
                    main_item = product_groups[main_type][0]
                    accessories = []
                    for acc_type in acc_types:
                        if acc_type in product_groups:
                            accessories.extend(product_groups[acc_type][:1])

                    if accessories:
                        bundle_products = [
                            {
                                "object_type": main_item.object_type,
                                "image_url": main_item.image_url,
                                "title": main_item.title,
                                "stock": main_item.stock,
                                "direct_url": main_item.direct_url,
                            }
                        ]
                        for acc in accessories[:2]:  # Max 2 accessories
                            bundle_products.append(
                                {
                                    "object_type": acc.object_type,
                                    "image_url": acc.image_url,
                                    "title": acc.title,
                                    "stock": acc.stock,
                                    "direct_url": acc.direct_url,
                                }
                            )

                        bundle = {
                            "id": f"bundle-accessories-{video_id}-{time}-{main_type}",
                            "name": "Complete Look",
                            "description": f"{main_item.object_type.title()} with accessories",
                            "total_price": 89.98 + (len(bundle_products) - 1) * 30,
                            "discount_price": 69.98 + (len(bundle_products) - 1) * 20,
                            "category": "accessories",
                            "image_url": main_item.image_url,
                            "product_ids": [p["title"] for p in bundle_products],
                            "products": bundle_products,
                            "similarity_score": 0.75,
                        }
                        bundles.append(bundle)
                        break

        logger.info(f"Created {len(bundles)} bundles for video {video_id} at {time}s")
        return bundles[:3]  # Return max 3 bundles

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating bundles: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create bundles: {str(e)}"
        )


@app.post("/api/regenerate-thumbnails")
async def regenerate_thumbnails():
    """
    Regenerate thumbnails for all videos that are missing them.

    Returns:
        dict: Summary of thumbnail generation
    """
    try:
        videos = processor_manager.get_all_videos()
        generated_count = 0
        failed_count = 0

        for video in videos:
            video_dir = Path(f"data/uploads/{video.id}")
            thumbnail_path = video_dir / "thumbnail.jpg"

            if not thumbnail_path.exists():
                try:
                    logger.info(f"Regenerating thumbnail for video: {video.id}")
                    processor_manager._generate_thumbnail(video.file_path, video.id)
                    generated_count += 1
                except Exception as e:
                    logger.error(f"Failed to generate thumbnail for {video.id}: {e}")
                    failed_count += 1

        return {
            "status": "completed",
            "generated": generated_count,
            "failed": failed_count,
            "total_videos": len(videos),
        }

    except Exception as e:
        logger.error(f"Error regenerating thumbnails: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to regenerate thumbnails: {str(e)}"
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

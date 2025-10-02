"""
Data models for the video product discovery API.
"""

from pydantic import BaseModel
from typing import Optional


class VideoInfo(BaseModel):
    """
    Model representing video information.
    """

    id: str
    filename: str
    status: str  # "processing", "completed", "failed"
    file_path: Optional[str] = None
    results_dir: Optional[str] = None
    error_message: Optional[str] = None
    video_url: Optional[str] = None


class ProductResult(BaseModel):
    """
    Model representing a product result from object detection.
    """

    object_type: str  # e.g., "shirt", "pants", "necklace", "ring"
    category: Optional[str] = None  # "clothing" or "jewelry"
    image_url: str  # URL to the similar product image (real image)
    title: str  # Product title (dummy data)
    stock: str  # Stock status (dummy data: "In Stock" or "Out of Stock")
    direct_url: str  # Direct URL to product page (dummy data)


class VideoUploadResponse(BaseModel):
    """
    Response model for video upload endpoint.
    """

    video_id: str
    filename: str
    status: str


class HealthCheckResponse(BaseModel):
    """
    Response model for health check endpoint.
    """

    status: str

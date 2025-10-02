"""
Configuration file for video processing application.
Contains constants and configuration settings.
"""

import logging
from dataclasses import dataclass


# Logger Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Create a named logger for the application
logger = logging.getLogger("video_processing")


# Model Configuration
@dataclass
class ModelConfig:
    """Configuration for the object detection model."""

    checkpoint: str = "yainage90/fashion-object-detection"
    confidence_threshold: float = 0.4


@dataclass
class JewelryDetectionConfig:
    """Configuration for the jewelry detection API."""

    api_url: str = "https://serverless.roboflow.com"
    api_key: str = "iNRp5F4XnK0BJSR0YMxv"
    model_id: str = "jewellery_detect-iwird/1"
    confidence_threshold: float = 0.4


@dataclass
class VideoProcessingConfig:
    """Configuration for video processing parameters."""

    interval_seconds: int = 5
    create_frame_folders: bool = True  # New configuration option


@dataclass
class SimilaritySearchConfig:
    """Configuration for image similarity search databases."""

    # Clothing database
    clothing_db_path: str = "data/similarity_db/clothing"
    clothing_images_path: str = "data/image_db/clothing"

    # Jewelry database
    jewelry_db_path: str = "data/similarity_db/jewelry"
    jewelry_images_path: str = "data/image_db/jewelry"


@dataclass
class Paths:
    """File paths configuration."""

    video_path: str
    output_directory: str


# Global Config Instances
MODEL_CONFIG = ModelConfig()
JEWELRY_CONFIG = JewelryDetectionConfig()
VIDEO_CONFIG = VideoProcessingConfig()
SIMILARITY_SEARCH_CONFIG = SimilaritySearchConfig()

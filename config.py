"""
Configuration file for video processing application.
Contains constants and configuration settings.
"""

import logging
from dataclasses import dataclass


# Logger Configuration
logging.basicConfig(
    level=logging.INFO,  # INFO level - use DEBUG only when needed for troubleshooting
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
class FrameQualityConfig:
    """Configuration for frame quality assessment."""

    # Blur detection - Laplacian variance threshold
    blur_threshold: float = 100.0  # Frames below this are considered blurry

    # Brightness thresholds (0-255 scale)
    min_brightness: float = 40.0  # Too dark
    max_brightness: float = 220.0  # Too bright

    # Frame quality check enabled
    enable_quality_check: bool = True

    # Nearby frame search range (in seconds) if primary frame fails quality check
    fallback_search_range: float = 1.0


@dataclass
class PersonDetectionConfig:
    """Configuration for person detection parameters."""

    # Enable person detection filter
    enable_person_detection: bool = True

    # Confidence threshold for person detection
    confidence_threshold: float = 0.5

    # Minimum person size (as fraction of frame area)
    min_person_area: float = 0.05  # 5% of frame

    # Model checkpoint for person detection
    checkpoint: str = "facebook/detr-resnet-50"  # DETR model with person detection


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
FRAME_QUALITY_CONFIG = FrameQualityConfig()
PERSON_DETECTION_CONFIG = PersonDetectionConfig()

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
class VideoProcessingConfig:
    """Configuration for video processing parameters."""

    interval_seconds: int = 6
    create_frame_folders: bool = True  # New configuration option


@dataclass
class Paths:
    """File paths configuration."""

    video_path: str
    output_directory: str


# Global Config Instances
MODEL_CONFIG = ModelConfig()
VIDEO_CONFIG = VideoProcessingConfig()

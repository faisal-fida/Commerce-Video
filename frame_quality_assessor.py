"""
Frame quality assessment module for intelligent frame selection.
Provides blur detection, brightness checking, and overall quality scoring.
"""

import cv2
import numpy as np
from typing import Tuple
from config import FRAME_QUALITY_CONFIG, logger


class FrameQualityAssessor:
    """
    Assesses frame quality using multiple metrics including blur detection,
    brightness analysis, and scene stability.
    """

    def __init__(self):
        """Initialize the frame quality assessor."""
        self.config = FRAME_QUALITY_CONFIG
        logger.info("FrameQualityAssessor initialized")

    def assess_frame_quality(self, frame: np.ndarray) -> Tuple[bool, float, dict]:
        """
        Assess the overall quality of a video frame.

        Args:
            frame: OpenCV frame (BGR format)

        Returns:
            Tuple of (is_good_quality, quality_score, metrics_dict)
            - is_good_quality: Boolean indicating if frame passes quality checks
            - quality_score: Normalized quality score (0-1, higher is better)
            - metrics_dict: Dictionary containing individual metric values
        """
        if not self.config.enable_quality_check:
            # If quality check is disabled, return True with perfect score
            return True, 1.0, {}

        metrics = {}

        # Check for blur
        sharpness_score = self._calculate_sharpness(frame)
        metrics["sharpness"] = sharpness_score
        is_sharp = sharpness_score >= self.config.blur_threshold

        # Check brightness
        brightness_score = self._calculate_brightness(frame)
        metrics["brightness"] = brightness_score
        is_good_brightness = (
            self.config.min_brightness <= brightness_score <= self.config.max_brightness
        )

        # Check contrast
        contrast_score = self._calculate_contrast(frame)
        metrics["contrast"] = contrast_score

        # Overall quality decision
        is_good_quality = is_sharp and is_good_brightness

        # Normalized quality score (0-1)
        quality_score = self._calculate_normalized_score(metrics)

        if not is_good_quality:
            logger.debug(
                f"Frame quality check failed - Sharpness: {sharpness_score:.2f} "
                f"(threshold: {self.config.blur_threshold}), "
                f"Brightness: {brightness_score:.2f} "
                f"(range: {self.config.min_brightness}-{self.config.max_brightness})"
            )
        else:
            logger.debug(
                f"Frame passed quality check - Quality score: {quality_score:.3f}"
            )

        return is_good_quality, quality_score, metrics

    def _calculate_sharpness(self, frame: np.ndarray) -> float:
        """
        Calculate frame sharpness using Laplacian variance method.
        Higher values indicate sharper images.

        Args:
            frame: OpenCV frame (BGR format)

        Returns:
            Sharpness score (Laplacian variance)
        """
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate Laplacian (measures second derivative, good for edge detection)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)

        # Variance of Laplacian - higher variance means more edges (sharper image)
        variance = laplacian.var()

        return float(variance)

    def _calculate_brightness(self, frame: np.ndarray) -> float:
        """
        Calculate average brightness of the frame.

        Args:
            frame: OpenCV frame (BGR format)

        Returns:
            Average brightness (0-255 scale)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate mean brightness
        brightness = np.mean(gray)

        return float(brightness)

    def _calculate_contrast(self, frame: np.ndarray) -> float:
        """
        Calculate contrast using standard deviation of pixel intensities.
        Higher values indicate better contrast.

        Args:
            frame: OpenCV frame (BGR format)

        Returns:
            Contrast score (standard deviation)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Standard deviation represents contrast
        contrast = np.std(gray)

        return float(contrast)

    def _calculate_normalized_score(self, metrics: dict) -> float:
        """
        Calculate normalized quality score (0-1) from individual metrics.

        Args:
            metrics: Dictionary of metric values

        Returns:
            Normalized quality score
        """
        # Normalize sharpness (assume max useful sharpness is 1000)
        sharpness_norm = min(metrics.get("sharpness", 0) / 1000.0, 1.0)

        # Normalize brightness (optimal is middle of range, penalize extremes)
        brightness = metrics.get("brightness", 128)
        optimal_brightness = (
            self.config.min_brightness + self.config.max_brightness
        ) / 2
        brightness_range = self.config.max_brightness - self.config.min_brightness
        brightness_deviation = abs(brightness - optimal_brightness)
        brightness_norm = max(0, 1.0 - (brightness_deviation / (brightness_range / 2)))

        # Normalize contrast (assume max useful contrast is 80)
        contrast_norm = min(metrics.get("contrast", 0) / 80.0, 1.0)

        # Weighted average (sharpness is most important)
        quality_score = (
            0.5 * sharpness_norm + 0.3 * brightness_norm + 0.2 * contrast_norm
        )

        return quality_score

    def detect_scene_change(
        self, frame1: np.ndarray, frame2: np.ndarray, threshold: float = 30.0
    ) -> bool:
        """
        Detect if there's a scene change between two frames.

        Args:
            frame1: First OpenCV frame (BGR format)
            frame2: Second OpenCV frame (BGR format)
            threshold: Mean absolute difference threshold for scene change

        Returns:
            True if scene change detected, False otherwise
        """
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Resize to same size if different
        if gray1.shape != gray2.shape:
            height = min(gray1.shape[0], gray2.shape[0])
            width = min(gray1.shape[1], gray2.shape[1])
            gray1 = cv2.resize(gray1, (width, height))
            gray2 = cv2.resize(gray2, (width, height))

        # Calculate mean absolute difference
        diff = np.abs(gray1.astype(float) - gray2.astype(float))
        mean_diff = np.mean(diff)

        is_scene_change = mean_diff > threshold

        if is_scene_change:
            logger.debug(f"Scene change detected - Mean diff: {mean_diff:.2f}")

        return is_scene_change

"""
Person detection module for filtering frames and extracting person regions.
Uses DETR (Detection Transformer) model for accurate person detection.
"""

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from typing import List, Tuple, Optional
import numpy as np
from config import PERSON_DETECTION_CONFIG, logger


class PersonDetector:
    """
    Person detection class for identifying and locating people in frames.
    Provides filtering and bounding box extraction for person-focused processing.
    """

    def __init__(self, checkpoint: str = None):
        """
        Initialize the person detector.

        Args:
            checkpoint: Model checkpoint to load (default from config)
        """
        self.checkpoint = checkpoint or PERSON_DETECTION_CONFIG.checkpoint
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.confidence_threshold = PERSON_DETECTION_CONFIG.confidence_threshold
        self.min_person_area = PERSON_DETECTION_CONFIG.min_person_area

        self.image_processor = None
        self.model = None
        self._load_model()

        logger.info(
            f"PersonDetector initialized - Threshold: {self.confidence_threshold}, "
            f"Min area: {self.min_person_area}"
        )

    def _load_model(self) -> None:
        """Load the pre-trained DETR model and processor."""
        try:
            logger.info(f"Loading person detection model from: {self.checkpoint}")
            self.image_processor = AutoImageProcessor.from_pretrained(self.checkpoint)
            self.model = AutoModelForObjectDetection.from_pretrained(
                self.checkpoint
            ).to(self.device)
            logger.info("Person detection model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading person detection model: {e}")
            raise

    def detect_persons(
        self, image: Image.Image
    ) -> Tuple[bool, List[Tuple[int, int, int, int]], List[float]]:
        """
        Detect persons in an image.

        Args:
            image: PIL Image object

        Returns:
            Tuple of (has_person, bounding_boxes, confidences)
            - has_person: Boolean indicating if valid person(s) detected
            - bounding_boxes: List of (x1, y1, x2, y2) tuples for detected persons
            - confidences: List of confidence scores for each detection
        """
        if not PERSON_DETECTION_CONFIG.enable_person_detection:
            # If person detection is disabled, return True (assume person present)
            logger.debug("Person detection disabled, assuming person present")
            return True, [], []

        try:
            # Prepare image for inference
            with torch.no_grad():
                inputs = self.image_processor(images=image, return_tensors="pt")
                outputs = self.model(**inputs.to(self.device))

                # Post-process to get bounding boxes
                target_sizes = torch.tensor([[image.size[1], image.size[0]]])
                results = self.image_processor.post_process_object_detection(
                    outputs,
                    threshold=self.confidence_threshold,
                    target_sizes=target_sizes,
                )[0]

            # Filter for person class (class_id = 1 in COCO dataset used by DETR)
            person_boxes = []
            person_confidences = []

            # Get image area for size filtering
            image_area = image.size[0] * image.size[1]

            for score, label, box in zip(
                results["scores"], results["labels"], results["boxes"]
            ):
                # Check if it's a person (label 1 in COCO)
                if label.item() == 1:  # Person class
                    confidence = score.item()

                    # Get box coordinates
                    x1, y1, x2, y2 = [int(coord) for coord in box.tolist()]

                    # Calculate person area
                    person_area = (x2 - x1) * (y2 - y1)
                    area_ratio = person_area / image_area

                    # Filter by minimum area to avoid tiny detections
                    if area_ratio >= self.min_person_area:
                        person_boxes.append((x1, y1, x2, y2))
                        person_confidences.append(confidence)

                        logger.debug(
                            f"Person detected - Confidence: {confidence:.3f}, "
                            f"Area ratio: {area_ratio:.3f}, Box: ({x1},{y1},{x2},{y2})"
                        )

            has_person = len(person_boxes) > 0

            if not has_person:
                logger.debug("No valid person detected in frame")
            else:
                logger.debug(f"Detected {len(person_boxes)} person(s) in frame")

            return has_person, person_boxes, person_confidences

        except Exception as e:
            logger.error(f"Error during person detection: {e}")
            # Return True to avoid skipping frames on errors
            return True, [], []

    def get_primary_person_box(
        self, image: Image.Image
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the bounding box of the primary (largest/most confident) person in the image.

        Args:
            image: PIL Image object

        Returns:
            Bounding box (x1, y1, x2, y2) or None if no person detected
        """
        has_person, boxes, confidences = self.detect_persons(image)

        if not has_person or not boxes:
            return None

        # Find the box with highest confidence
        primary_idx = confidences.index(max(confidences))
        primary_box = boxes[primary_idx]

        logger.debug(
            f"Primary person box: {primary_box} "
            f"(confidence: {confidences[primary_idx]:.3f})"
        )

        return primary_box

    def crop_to_person(
        self, image: Image.Image, padding: float = 0.1
    ) -> Optional[Image.Image]:
        """
        Crop image to the primary person with optional padding.

        Args:
            image: PIL Image object
            padding: Padding ratio to add around person box (default 10%)

        Returns:
            Cropped PIL Image or None if no person detected
        """
        person_box = self.get_primary_person_box(image)

        if person_box is None:
            logger.debug("Cannot crop: No person detected")
            return None

        x1, y1, x2, y2 = person_box

        # Add padding
        width = x2 - x1
        height = y2 - y1
        pad_x = int(width * padding)
        pad_y = int(height * padding)

        # Apply padding with bounds checking
        x1 = max(0, x1 - pad_x)
        y1 = max(0, y1 - pad_y)
        x2 = min(image.size[0], x2 + pad_x)
        y2 = min(image.size[1], y2 + pad_y)

        # Crop image
        cropped = image.crop((x1, y1, x2, y2))

        logger.debug(
            f"Cropped to person region: ({x1},{y1},{x2},{y2}) "
            f"with {padding * 100}% padding"
        )

        return cropped

    def is_person_present(self, image: Image.Image) -> bool:
        """
        Quick check if a person is present in the image.

        Args:
            image: PIL Image object

        Returns:
            True if person detected, False otherwise
        """
        has_person, _, _ = self.detect_persons(image)
        return has_person

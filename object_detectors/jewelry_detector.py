"""
Jewelry detection module using Roboflow API.
Handles jewelry object detection operations.
"""

from PIL import Image
from typing import Dict, Any
from inference_sdk import InferenceHTTPClient
from config import JEWELRY_CONFIG, logger
import numpy as np


class JewelryDetector:
    """
    Jewelry detection class that uses Roboflow API for inference.
    """

    def __init__(self, api_url: str = None, api_key: str = None, model_id: str = None):
        """
        Initialize the jewelry detector.

        Args:
            api_url: Roboflow API URL
            api_key: Roboflow API key
            model_id: Roboflow model ID
        """
        self.api_url = api_url or JEWELRY_CONFIG.api_url
        self.api_key = api_key or JEWELRY_CONFIG.api_key
        self.model_id = model_id or JEWELRY_CONFIG.model_id
        self.confidence_threshold = JEWELRY_CONFIG.confidence_threshold

        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Roboflow client."""
        try:
            logger.info("Initializing Roboflow client for jewelry detection")
            self.client = InferenceHTTPClient(
                api_url=self.api_url, api_key=self.api_key
            )
            logger.info("Jewelry detector client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing jewelry detector client: {e}")
            raise

    def detect_objects(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform jewelry detection on a single image.

        Args:
            image: Input PIL image

        Returns:
            Dict: Detection results with boxes, labels, and scores in format compatible
                  with ClothingDetector (for consistency)
        """
        try:
            # Convert PIL Image to numpy array (Roboflow SDK accepts numpy arrays, not BytesIO)
            image_np = np.array(image)

            # Perform inference
            logger.debug(
                f"Calling Roboflow API for jewelry detection (model: {self.model_id})"
            )
            result = self.client.infer(image_np, model_id=self.model_id)

            # Log raw API response for debugging
            logger.debug(f"Roboflow API response: {result}")

            # Convert Roboflow format to our standard format (matching ClothingDetector)
            predictions = result.get("predictions", [])
            logger.info(f"Jewelry detector found {len(predictions)} raw predictions")

            # Build lists of boxes, labels, and scores
            boxes = []
            labels = []
            scores = []

            for i, pred in enumerate(predictions):
                # Convert center-based box to corner-based box [x1, y1, x2, y2]
                x_center = pred["x"]
                y_center = pred["y"]
                width = pred["width"]
                height = pred["height"]

                x1 = x_center - width / 2
                y1 = y_center - height / 2
                x2 = x_center + width / 2
                y2 = y_center + height / 2

                boxes.append([x1, y1, x2, y2])
                labels.append(pred["class"])
                scores.append(pred["confidence"])

                logger.debug(
                    f"  Prediction {i + 1}: {pred['class']} (confidence: {pred['confidence']:.3f})"
                )

            # Log summary
            above_threshold = sum(1 for s in scores if s >= self.confidence_threshold)
            logger.info(
                f"Jewelry detection: {above_threshold}/{len(predictions)} predictions above threshold {self.confidence_threshold}"
            )

            return {"boxes": boxes, "labels": labels, "scores": scores}

        except Exception as e:
            logger.error(f"Error during jewelry detection: {e}", exc_info=True)
            logger.error(
                f"Jewelry detector config - API URL: {self.api_url}, Model: {self.model_id}"
            )
            logger.error(
                "This may be due to: (1) Invalid API key, (2) Network issues, (3) Roboflow service down"
            )
            return {"boxes": [], "labels": [], "scores": []}

    def get_label_name(self, label: Any) -> str:
        """
        Get the label name. For jewelry detector, labels are already strings.

        Args:
            label: Label (string or int)

        Returns:
            str: Label name
        """
        return str(label)

"""
Object detection module for video processing.
Handles model loading and object detection operations.
"""

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from typing import Dict, Any
from config import MODEL_CONFIG, logger


class ObjectDetector:
    """
    Object detection class that handles model loading and inference.
    """

    def __init__(self, checkpoint: str = None):
        """
        Initialize the object detector.

        Args:
            checkpoint (str): Model checkpoint to load.
        """
        self.checkpoint = checkpoint or MODEL_CONFIG.checkpoint
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.image_processor = None
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """
        Load the pre-trained model and processor.
        """
        try:
            logger.info(f"Loading model from checkpoint: {self.checkpoint}")
            self.image_processor = AutoImageProcessor.from_pretrained(self.checkpoint)
            logger.info("Image processor loaded successfully")
            self.model = AutoModelForObjectDetection.from_pretrained(
                self.checkpoint
            ).to(self.device)
            logger.info(f"Model loaded successfully from {self.checkpoint}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def detect_objects(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform object detection on a single image.

        Args:
            image (Image.Image): Input PIL image

        Returns:
            Dict: Detection results with boxes, labels, and scores
        """
        with torch.no_grad():
            inputs = self.image_processor(images=[image], return_tensors="pt")
            outputs = self.model(**inputs.to(self.device))
            target_sizes = torch.tensor([[image.size[1], image.size[0]]])
            results = self.image_processor.post_process_object_detection(
                outputs,
                threshold=MODEL_CONFIG.confidence_threshold,
                target_sizes=target_sizes,
            )[0]

        return results

    def get_label_name(self, label_id: int) -> str:
        """
        Get the label name for a given label ID.

        Args:
            label_id (int): Label ID

        Returns:
            str: Label name
        """
        return self.model.config.id2label[label_id]

    @property
    def confidence_threshold(self) -> float:
        """Get the confidence threshold."""
        return MODEL_CONFIG.confidence_threshold

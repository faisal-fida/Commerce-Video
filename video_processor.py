"""
Video processing manager for handling video uploads, processing, and result retrieval.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
import cv2
from PIL import Image

from config import VIDEO_CONFIG, logger
from detector import ObjectDetector
from image_similarity_search.similarity_search import ImageSimilaritySearch
from models import VideoInfo, ProductResult


class VideoProcessorManager:
    """
    Manages video processing workflow including frame extraction,
    object detection, and product similarity search.
    """

    def __init__(self):
        """Initialize the video processor manager."""
        self.videos: Dict[str, VideoInfo] = {}
        self.detector: Optional[ObjectDetector] = None
        self.similarity_search: Optional[ImageSimilaritySearch] = None
        logger.info("VideoProcessorManager initialized")

        # Load existing videos from data/uploads directory
        self._load_existing_videos()

    def _get_detector(self) -> ObjectDetector:
        """Lazy load the object detector."""
        if self.detector is None:
            logger.info("Loading object detector...")
            self.detector = ObjectDetector()
        return self.detector

    def _get_similarity_search(self) -> ImageSimilaritySearch:
        """Lazy load the similarity search engine."""
        if self.similarity_search is None:
            logger.info("Loading similarity search engine...")
            self.similarity_search = ImageSimilaritySearch(db_path="data/similarity_db")
        return self.similarity_search

    def _load_existing_videos(self) -> None:
        """
        Scan the data/uploads directory and load existing videos into the registry.
        """
        uploads_dir = Path("data/uploads")

        if not uploads_dir.exists():
            logger.info("Uploads directory does not exist, creating it")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            return

        logger.info(f"Scanning {uploads_dir} for existing videos...")
        video_count = 0

        # Scan all subdirectories (each should be a video ID)
        for video_dir in uploads_dir.iterdir():
            if not video_dir.is_dir():
                continue

            try:
                video_id = video_dir.name

                # Find video file in the directory
                video_files = (
                    list(video_dir.glob("*.mp4"))
                    + list(video_dir.glob("*.avi"))
                    + list(video_dir.glob("*.mov"))
                    + list(video_dir.glob("*.mkv"))
                    + list(video_dir.glob("*.webm"))
                    + list(video_dir.glob("*.m4v"))
                )

                if not video_files:
                    logger.warning(f"No video file found in {video_dir}")
                    continue

                video_file = video_files[0]
                filename = video_file.name
                file_path = str(video_file)
                results_dir = str(video_dir / "results")

                # Check if results exist to determine status
                results_file = video_dir / "results" / "detection_results.json"
                if results_file.exists():
                    status = "completed"
                    logger.debug(f"Found completed video: {video_id}")
                else:
                    # Check if results directory exists but is empty
                    if Path(results_dir).exists():
                        status = "failed"
                        logger.debug(f"Found failed video: {video_id}")
                    else:
                        status = "processing"
                        logger.debug(f"Found unprocessed video: {video_id}")

                # Create VideoInfo object
                video_info = VideoInfo(
                    id=video_id,
                    filename=filename,
                    status=status,
                    file_path=file_path,
                    results_dir=results_dir,
                )

                # Add to registry
                self.videos[video_id] = video_info
                video_count += 1

                # Generate thumbnail if it doesn't exist
                thumbnail_path = video_dir / "thumbnail.jpg"
                if not thumbnail_path.exists():
                    logger.info(f"Generating missing thumbnail for video: {video_id}")
                    self._generate_thumbnail(file_path, video_id)

            except Exception as e:
                logger.error(f"Error loading video from {video_dir}: {e}")
                continue

        logger.info(f"Loaded {video_count} existing videos from {uploads_dir}")

    def add_video(self, video_info: VideoInfo) -> None:
        """
        Add a video to the registry.

        Args:
            video_info: Video information object
        """
        self.videos[video_info.id] = video_info
        logger.info(f"Added video to registry: {video_info.id} - {video_info.filename}")

    def get_video(self, video_id: str) -> Optional[VideoInfo]:
        """
        Get video information by ID.

        Args:
            video_id: Unique identifier of the video

        Returns:
            VideoInfo object or None if not found
        """
        video = self.videos.get(video_id)
        if video is None:
            raise ValueError(f"Video not found: {video_id}")
        return video

    def get_all_videos(self) -> List[VideoInfo]:
        """
        Get all videos in the registry.

        Returns:
            List of VideoInfo objects
        """
        return list(self.videos.values())

    def process_video(self, video_id: str) -> None:
        """
        Process a video: extract frames, detect objects, find similar products.
        This is designed to run as a background task.

        Args:
            video_id: Unique identifier of the video
        """
        try:
            video_info = self.get_video(video_id)
            logger.info(f"Starting processing for video: {video_id}")

            # Update status to processing
            video_info.status = "processing"

            # Create results directory
            results_dir = Path(video_info.results_dir)
            results_dir.mkdir(exist_ok=True, parents=True)

            # Extract frames and process
            frames_data = self._extract_and_process_frames(
                video_info.file_path, results_dir
            )

            # Generate thumbnail
            self._generate_thumbnail(video_info.file_path, video_info.id)

            # Save results
            self._save_results(results_dir, frames_data)

            # Update status to completed
            video_info.status = "completed"
            logger.info(f"Successfully processed video: {video_id}")

        except Exception as e:
            logger.error(f"Error processing video {video_id}: {str(e)}", exc_info=True)
            video_info = self.videos.get(video_id)
            if video_info:
                video_info.status = "failed"
                video_info.error_message = str(e)

    def _extract_and_process_frames(
        self, video_path: str, results_dir: Path
    ) -> Dict[float, List[Dict]]:
        """
        Extract frames at intervals and process each frame.

        Args:
            video_path: Path to the video file
            results_dir: Directory to save frame images

        Returns:
            Dictionary mapping timestamps to detection results
        """
        logger.info(f"Extracting frames from video: {video_path}")

        # Create frames directory
        frames_dir = results_dir / "frames"
        frames_dir.mkdir(exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        logger.info(
            f"Video info - FPS: {fps}, Total frames: {total_frames}, Duration: {duration}s"
        )

        interval_seconds = VIDEO_CONFIG.interval_seconds
        frame_interval = int(fps * interval_seconds)

        frames_data = {}
        frame_count = 0
        detector = self._get_detector()

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Process frame at intervals
                if frame_count % frame_interval == 0:
                    timestamp = frame_count / fps
                    logger.info(f"Processing frame at {timestamp:.2f}s")

                    # Save frame image
                    frame_path = frames_dir / f"frame_{timestamp:.1f}s.jpg"
                    cv2.imwrite(str(frame_path), frame)

                    # Convert to PIL Image for detection
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)

                    # Detect objects
                    detections = self._detect_objects_in_frame(pil_image, detector)

                    # Find similar products for each detection
                    products = self._find_similar_products(
                        detections, pil_image, frames_dir, timestamp
                    )

                    if products:
                        frames_data[timestamp] = products

                frame_count += 1

        finally:
            cap.release()

        logger.info(f"Extracted and processed {len(frames_data)} frames")
        return frames_data

    def _detect_objects_in_frame(
        self, image: Image.Image, detector: ObjectDetector
    ) -> List[Dict]:
        """
        Detect objects in a single frame.

        Args:
            image: PIL Image object
            detector: ObjectDetector instance

        Returns:
            List of detection dictionaries
        """
        results = detector.detect_objects(image)

        detections = []
        for score, label, box in zip(
            results["scores"], results["labels"], results["boxes"]
        ):
            label_name = detector.get_label_name(label.item())
            confidence = score.item()

            if confidence >= detector.confidence_threshold:
                detection = {
                    "label": label_name,
                    "confidence": confidence,
                    "box": box.tolist(),
                }
                detections.append(detection)
                logger.debug(f"Detected {label_name} with confidence {confidence:.2f}")

        return detections

    def _find_similar_products(
        self,
        detections: List[Dict],
        image: Image.Image,
        frames_dir: Path,
        timestamp: float,
    ) -> List[Dict]:
        """
        Find similar products for detected objects.
        Returns only unique products (deduplicated by image_url),
        keeping the most confident match for each unique product.

        Args:
            detections: List of object detections
            image: Original frame image
            frames_dir: Directory to save cropped images
            timestamp: Frame timestamp

        Returns:
            List of unique product results
        """
        similarity_search = self._get_similarity_search()

        # Create crops directory
        crops_dir = frames_dir / "crops"
        crops_dir.mkdir(exist_ok=True)

        # Dictionary to track unique products by image_url
        # Key: image_url, Value: product dict with highest confidence
        unique_products = {}

        for idx, detection in enumerate(detections):
            try:
                # Crop detected object
                box = detection["box"]
                x1, y1, x2, y2 = [int(coord) for coord in box]
                cropped = image.crop((x1, y1, x2, y2))

                # Save cropped image
                crop_path = crops_dir / f"crop_{timestamp:.1f}s_{idx}.jpg"
                cropped.save(crop_path)

                # Search for most similar product (top 1 only)
                similar_images = similarity_search.search(str(crop_path), top_k=1)

                # Create product result for the most similar match
                if similar_images:
                    image_path = similar_images[0]

                    # Check if we already have this product
                    if image_path in unique_products:
                        # Keep the one with higher confidence
                        if (
                            detection["confidence"]
                            > unique_products[image_path]["confidence"]
                        ):
                            unique_products[image_path] = {
                                "object_type": detection["label"],
                                "image_url": image_path,
                                "title": f"{detection['label'].title()}",
                                "stock": "In Stock",
                                "direct_url": f"https://example.com/product/{uuid.uuid4()}",
                                "confidence": detection["confidence"],
                            }
                    else:
                        # Add new unique product
                        unique_products[image_path] = {
                            "object_type": detection["label"],
                            "image_url": image_path,
                            "title": f"{detection['label'].title()}",
                            "stock": "In Stock",
                            "direct_url": f"https://example.com/product/{uuid.uuid4()}",
                            "confidence": detection["confidence"],
                        }

            except Exception as e:
                logger.error(f"Error finding similar products for detection {idx}: {e}")
                continue

        # Convert dictionary values to list
        products = list(unique_products.values())

        # Sort by confidence (highest first)
        products.sort(key=lambda x: x["confidence"], reverse=True)

        logger.info(
            f"Found {len(products)} unique products from {len(detections)} detections"
        )
        return products

    def _save_results(
        self, results_dir: Path, frames_data: Dict[float, List[Dict]]
    ) -> None:
        """
        Save detection results to JSON file.

        Args:
            results_dir: Directory to save results
            frames_data: Dictionary of frame timestamps to product results
        """
        results_file = results_dir / "detection_results.json"

        # Convert float keys to strings for JSON serialization
        results_json = {
            str(timestamp): products for timestamp, products in frames_data.items()
        }

        with open(results_file, "w") as f:
            json.dump(results_json, f, indent=2)

        logger.info(f"Saved results to {results_file}")

    def _generate_thumbnail(self, video_path: str, video_id: str) -> None:
        """
        Generate a thumbnail from the video.

        Args:
            video_path: Path to the video file
            video_id: Unique identifier of the video
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.warning(f"Could not open video for thumbnail: {video_path}")
                return

            # Get frame at 10% of video duration
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_number = int(total_frames * 0.1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            ret, frame = cap.read()
            cap.release()

            if ret:
                thumbnail_path = f"data/uploads/{video_id}/thumbnail.jpg"
                cv2.imwrite(thumbnail_path, frame)
                logger.info(f"Generated thumbnail: {thumbnail_path}")
            else:
                logger.warning("Could not extract frame for thumbnail")

        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")

    def get_results(self, video_id: str, time: float) -> List[ProductResult]:
        """
        Get detection results for a video at a specific timestamp.

        Args:
            video_id: Unique identifier of the video
            time: Timestamp in seconds

        Returns:
            List of ProductResult objects
        """
        video_info = self.get_video(video_id)

        if video_info.status != "completed":
            logger.warning(
                f"Video {video_id} is not completed yet. Status: {video_info.status}"
            )
            return []

        results_file = Path(video_info.results_dir) / "detection_results.json"

        if not results_file.exists():
            logger.warning(f"Results file not found: {results_file}")
            return []

        try:
            with open(results_file, "r") as f:
                all_results = json.load(f)

            # Find the closest timestamp
            timestamps = [float(t) for t in all_results.keys()]
            if not timestamps:
                return []

            # Round the requested time to match our interval
            interval = VIDEO_CONFIG.interval_seconds
            rounded_time = round(time / interval) * interval

            # Find exact match or closest
            closest_time = min(timestamps, key=lambda t: abs(t - rounded_time))

            # Only return results if within reasonable range (2x interval)
            if abs(closest_time - rounded_time) > interval * 2:
                logger.debug(f"No results found near timestamp {time}s")
                return []

            products_data = all_results[str(closest_time)]

            # Convert to ProductResult objects
            products = [
                ProductResult(
                    object_type=p["object_type"],
                    image_url=p["image_url"],
                    title=p["title"],
                    stock=p["stock"],
                    direct_url=p["direct_url"],
                )
                for p in products_data
            ]

            logger.info(
                f"Found {len(products)} products for video {video_id} at {time}s"
            )
            return products

        except Exception as e:
            logger.error(f"Error loading results: {e}")
            return []

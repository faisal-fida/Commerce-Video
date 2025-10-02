"""
Video processing manager for handling video uploads, processing, and result retrieval.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
import cv2
from PIL import Image

from config import (
    VIDEO_CONFIG,
    SIMILARITY_SEARCH_CONFIG,
    FRAME_QUALITY_CONFIG,
    PERSON_DETECTION_CONFIG,
    logger,
)
from object_detectors import ClothingDetector, JewelryDetector, PersonDetector
from frame_quality_assessor import FrameQualityAssessor
from image_similarity_search import ImageSimilaritySearch
from models import VideoInfo, ProductResult


class VideoProcessorManager:
    """
    Manages video processing workflow including frame extraction,
    object detection, and product similarity search.
    """

    def __init__(self):
        """Initialize the video processor manager."""
        self.videos: Dict[str, VideoInfo] = {}
        self.detector: Optional[ClothingDetector] = None
        self.jewelry_detector: Optional[JewelryDetector] = None
        self.person_detector: Optional[PersonDetector] = None
        self.quality_assessor: Optional[FrameQualityAssessor] = None

        # Separate similarity search instances for clothing and jewelry
        self.clothing_similarity_search: Optional[ImageSimilaritySearch] = None
        self.jewelry_similarity_search: Optional[ImageSimilaritySearch] = None

        logger.info(
            "VideoProcessorManager initialized with intelligent frame selection "
            f"(Quality Check: {FRAME_QUALITY_CONFIG.enable_quality_check}, "
            f"Person Detection: {PERSON_DETECTION_CONFIG.enable_person_detection})"
        )

        # Load existing videos from data/uploads directory
        self._load_existing_videos()

    def _get_detector(self) -> ClothingDetector:
        """Lazy load the object detector."""
        if self.detector is None:
            logger.info("Loading object detector...")
            self.detector = ClothingDetector()
        return self.detector

    def _get_jewelry_detector(self) -> JewelryDetector:
        """Lazy load the jewelry detector."""
        if self.jewelry_detector is None:
            logger.info("Loading jewelry detector...")
            self.jewelry_detector = JewelryDetector()
        return self.jewelry_detector

    def _get_person_detector(self) -> PersonDetector:
        """Lazy load the person detector."""
        if self.person_detector is None:
            logger.info("Loading person detector...")
            self.person_detector = PersonDetector()
        return self.person_detector

    def _get_quality_assessor(self) -> FrameQualityAssessor:
        """Lazy load the frame quality assessor."""
        if self.quality_assessor is None:
            logger.info("Loading frame quality assessor...")
            self.quality_assessor = FrameQualityAssessor()
        return self.quality_assessor

    def _get_clothing_similarity_search(self) -> ImageSimilaritySearch:
        """Lazy load the clothing similarity search engine."""
        if self.clothing_similarity_search is None:
            logger.info("Loading clothing similarity search engine...")
            self.clothing_similarity_search = ImageSimilaritySearch(
                db_path=SIMILARITY_SEARCH_CONFIG.clothing_db_path
            )
        return self.clothing_similarity_search

    def _get_jewelry_similarity_search(self) -> ImageSimilaritySearch:
        """Lazy load the jewelry similarity search engine."""
        if self.jewelry_similarity_search is None:
            logger.info("Loading jewelry similarity search engine...")
            self.jewelry_similarity_search = ImageSimilaritySearch(
                db_path=SIMILARITY_SEARCH_CONFIG.jewelry_db_path
            )
        return self.jewelry_similarity_search

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

    def _select_best_frame_in_range(
        self,
        cap: cv2.VideoCapture,
        center_frame_num: int,
        fps: float,
        search_range_seconds: float = 1.0,
    ) -> Optional[tuple]:
        """
        Select the best quality frame within a time range around the center frame.

        Args:
            cap: OpenCV VideoCapture object
            center_frame_num: Center frame number to search around
            fps: Video frames per second
            search_range_seconds: Time range to search (in seconds)

        Returns:
            Tuple of (frame, frame_number, quality_score) or None if no good frame found
        """
        quality_assessor = self._get_quality_assessor()

        # Calculate search range in frames
        search_range_frames = int(fps * search_range_seconds)

        # Define search window
        start_frame = max(0, center_frame_num - search_range_frames)
        end_frame = center_frame_num + search_range_frames

        best_frame = None
        best_frame_num = center_frame_num
        best_quality = -1.0

        # Try frames in order: center, center+1, center-1, center+2, center-2, etc.
        offsets = [0]
        for i in range(1, search_range_frames + 1):
            offsets.extend([i, -i])

        for offset in offsets:
            frame_num = center_frame_num + offset

            if frame_num < start_frame or frame_num > end_frame:
                continue

            # Read frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()

            if not ret:
                continue

            # Assess quality
            is_good, quality_score, _ = quality_assessor.assess_frame_quality(frame)

            if quality_score > best_quality:
                best_quality = quality_score
                best_frame = frame.copy()
                best_frame_num = frame_num

                # If we found a good quality frame, we can stop early
                if is_good:
                    logger.debug(
                        f"Found good quality frame at offset {offset} "
                        f"(quality: {quality_score:.3f})"
                    )
                    break

        if best_frame is not None:
            return best_frame, best_frame_num, best_quality

        return None

    def _extract_and_process_frames(
        self, video_path: str, results_dir: Path
    ) -> Dict[float, List[Dict]]:
        """
        Extract frames at intervals and process each frame with intelligent selection.
        Uses quality assessment and person detection to select optimal frames.

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
        skipped_quality = 0
        skipped_person = 0
        processed_count = 0

        # Lazy load detectors
        detector = self._get_detector()
        jewelry_detector = self._get_jewelry_detector()
        person_detector = self._get_person_detector()
        quality_assessor = self._get_quality_assessor()

        try:
            # Process at intervals
            for interval_idx in range(0, total_frames, frame_interval):
                # Select best frame around this interval
                frame_result = self._select_best_frame_in_range(
                    cap,
                    interval_idx,
                    fps,
                    FRAME_QUALITY_CONFIG.fallback_search_range,
                )

                if frame_result is None:
                    logger.warning(f"Could not read frame at interval {interval_idx}")
                    skipped_quality += 1
                    continue

                frame, frame_num, quality_score = frame_result
                timestamp = frame_num / fps

                logger.info(
                    f"Processing frame at {timestamp:.2f}s "
                    f"(quality: {quality_score:.3f})"
                )

                # Convert to PIL Image for detection
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)

                # Check if person is present
                has_person = person_detector.is_person_present(pil_image)

                if not has_person:
                    logger.info(
                        f"Skipping frame at {timestamp:.2f}s - No person detected"
                    )
                    skipped_person += 1
                    continue

                # Get person bounding box for focused detection
                person_box = person_detector.get_primary_person_box(pil_image)

                # Save frame image
                frame_path = frames_dir / f"frame_{timestamp:.1f}s.jpg"
                cv2.imwrite(str(frame_path), frame)

                # Detect objects (both clothing and jewelry)
                # If person box available, focus detection on person region
                detections = self._detect_objects_in_frame(
                    pil_image, detector, jewelry_detector, person_box
                )

                # Find similar products for each detection
                products = self._find_similar_products(
                    detections, pil_image, frames_dir, timestamp
                )

                if products:
                    frames_data[timestamp] = products
                    processed_count += 1

        finally:
            cap.release()

        logger.info(
            f"Frame processing complete - Processed: {processed_count}, "
            f"Skipped (quality): {skipped_quality}, "
            f"Skipped (no person): {skipped_person}"
        )
        return frames_data

    def _detect_objects_in_frame(
        self,
        image: Image.Image,
        detector: ClothingDetector,
        jewelry_detector: JewelryDetector,
        person_box: Optional[tuple] = None,
    ) -> List[Dict]:
        """
        Detect objects in a single frame using both clothing and jewelry detectors.
        Optionally focuses detection on person region for improved accuracy.

        Args:
            image: PIL Image object
            detector: ClothingDetector instance for clothing
            jewelry_detector: JewelryDetector instance for jewelry
            person_box: Optional (x1, y1, x2, y2) tuple for person bounding box

        Returns:
            List of detection dictionaries from both detectors
        """
        detections = []

        # If person box provided, crop to person region for detection
        if person_box is not None:
            x1, y1, x2, y2 = person_box
            # Add small padding around person box
            padding = 0.05
            width = x2 - x1
            height = y2 - y1
            pad_x = int(width * padding)
            pad_y = int(height * padding)

            # Apply padding with bounds checking
            crop_x1 = max(0, x1 - pad_x)
            crop_y1 = max(0, y1 - pad_y)
            crop_x2 = min(image.size[0], x2 + pad_x)
            crop_y2 = min(image.size[1], y2 + pad_y)

            # Crop to person region
            detection_image = image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            offset_x, offset_y = crop_x1, crop_y1

            logger.debug(
                f"Detecting in person region: ({crop_x1},{crop_y1},{crop_x2},{crop_y2})"
            )
        else:
            # Use full image
            detection_image = image
            offset_x, offset_y = 0, 0

        # Detect clothing items
        clothing_results = detector.detect_objects(detection_image)
        for score, label, box in zip(
            clothing_results["scores"],
            clothing_results["labels"],
            clothing_results["boxes"],
        ):
            label_name = detector.get_label_name(label.item())
            confidence = score.item()

            if confidence >= detector.confidence_threshold:
                # Map coordinates back to original image if cropped
                box_coords = box.tolist()
                if person_box is not None:
                    box_coords = [
                        box_coords[0] + offset_x,
                        box_coords[1] + offset_y,
                        box_coords[2] + offset_x,
                        box_coords[3] + offset_y,
                    ]

                detection = {
                    "label": label_name,
                    "confidence": confidence,
                    "box": box_coords,
                    "category": "clothing",
                }
                detections.append(detection)
                logger.debug(
                    f"Detected clothing: {label_name} with confidence {confidence:.2f}"
                )

        # Detect jewelry items
        jewelry_results = jewelry_detector.detect_objects(detection_image)
        for score, label, box in zip(
            jewelry_results["scores"],
            jewelry_results["labels"],
            jewelry_results["boxes"],
        ):
            label_name = jewelry_detector.get_label_name(label)
            confidence = score

            if confidence >= jewelry_detector.confidence_threshold:
                # Map coordinates back to original image if cropped
                box_coords = box if isinstance(box, list) else box
                if person_box is not None and isinstance(box_coords, list):
                    box_coords = [
                        box_coords[0] + offset_x,
                        box_coords[1] + offset_y,
                        box_coords[2] + offset_x,
                        box_coords[3] + offset_y,
                    ]

                detection = {
                    "label": label_name,
                    "confidence": confidence,
                    "box": box_coords,
                    "category": "jewelry",
                }
                detections.append(detection)
                logger.debug(
                    f"Detected jewelry: {label_name} with confidence {confidence:.2f}"
                )

        logger.info(
            f"Total detections: {len(detections)} (clothing + jewelry) "
            f"{'in person region' if person_box else 'in full frame'}"
        )
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
        Routes searches to appropriate database based on detection category.
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
        # Get both similarity search instances
        clothing_search = self._get_clothing_similarity_search()
        jewelry_search = self._get_jewelry_similarity_search()

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

                # Save cropped image with category prefix
                category = detection.get("category", "unknown")
                crop_path = crops_dir / f"crop_{category}_{timestamp:.1f}s_{idx}.jpg"
                cropped.save(crop_path)

                # Route to appropriate similarity search based on category
                if category == "clothing":
                    similar_images = clothing_search.search(str(crop_path), top_k=1)
                    logger.debug(f"Searching clothing database for detection {idx}")
                elif category == "jewelry":
                    similar_images = jewelry_search.search(str(crop_path), top_k=1)
                    logger.debug(f"Searching jewelry database for detection {idx}")
                else:
                    logger.warning(
                        f"Unknown category '{category}' for detection {idx}, skipping"
                    )
                    continue

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
                                "category": detection.get("category", "unknown"),
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
                            "category": detection.get("category", "unknown"),
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
                    category=p.get("category"),
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

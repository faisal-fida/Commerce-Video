"""
Jewelry Detection and Similarity Search Test Pipeline

This script allows you to test the jewelry detection and similarity search
on a single video file. It will:
1. Extract frames from the video
2. Detect jewelry items in each frame
3. Save cropped jewelry images
4. Perform similarity search for each detected jewelry
5. Save results with source and similar images side by side
"""

import os
import sys
import cv2
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import shutil
from PIL import Image

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from object_detectors.jewelry_detector import JewelryDetector
from image_similarity_search.similarity_search import ImageSimilaritySearch
from config import VIDEO_CONFIG, SIMILARITY_SEARCH_CONFIG

# Set up logging for this module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class JewelryTestPipeline:
    """Test pipeline for jewelry detection and similarity search."""

    def __init__(self, output_base_dir: str = "jewelry_test/data"):
        """
        Initialize the test pipeline.

        Args:
            output_base_dir: Base directory for saving results
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

        # Initialize detectors
        logger.info("Initializing jewelry detector...")
        self.jewelry_detector = JewelryDetector()

        logger.info("Initializing jewelry similarity search...")
        self.similarity_search = ImageSimilaritySearch(
            db_path=SIMILARITY_SEARCH_CONFIG.jewelry_db_path
        )
        self.similarity_search._load_database()

        logger.info("Pipeline initialized successfully!")

    def extract_frames(
        self, video_path: str, interval_seconds: int = None
    ) -> List[Tuple[float, any]]:
        """
        Extract frames from video at specified intervals.

        Args:
            video_path: Path to the video file
            interval_seconds: Interval between frames (uses config if None)

        Returns:
            List of (timestamp, frame) tuples
        """
        if interval_seconds is None:
            interval_seconds = VIDEO_CONFIG.interval_seconds

        logger.info(f"Extracting frames from video: {video_path}")
        logger.info(f"Frame extraction interval: {interval_seconds} seconds")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        logger.info(
            f"Video FPS: {fps}, Total Frames: {total_frames}, Duration: {duration:.2f}s"
        )

        frame_interval = int(fps * interval_seconds)
        frames = []
        frame_number = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_number % frame_interval == 0:
                timestamp = frame_number / fps
                frames.append((timestamp, frame))
                logger.info(f"Extracted frame at {timestamp:.2f}s")

            frame_number += 1

        cap.release()
        logger.info(f"Extracted {len(frames)} frames from video")
        return frames

    def detect_and_crop_jewelry(
        self, frame: any, timestamp: float, run_dir: Path
    ) -> List[Tuple[dict, any]]:
        """
        Detect jewelry in a frame and crop detected items.

        Args:
            frame: Video frame (numpy array)
            timestamp: Frame timestamp
            run_dir: Directory for saving cropped images

        Returns:
            List of (detection_info, cropped_image) tuples
        """
        # Convert frame to PIL Image for the detector
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Detect jewelry in the frame
        detection_result = self.jewelry_detector.detect_objects(frame_pil)

        # Extract boxes, labels, and scores
        boxes = detection_result.get("boxes", [])
        labels = detection_result.get("labels", [])
        scores = detection_result.get("scores", [])

        # Filter by confidence threshold
        filtered_detections = [
            (box, label, score)
            for box, label, score in zip(boxes, labels, scores)
            if score >= self.jewelry_detector.confidence_threshold
        ]

        if not filtered_detections:
            logger.info(f"No jewelry detected at {timestamp:.2f}s")
            return []

        logger.info(
            f"Detected {len(filtered_detections)} jewelry items at {timestamp:.2f}s"
        )

        cropped_dir = run_dir / "cropped_jewelry"
        cropped_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for idx, (box, label, confidence) in enumerate(filtered_detections):
            # Extract bounding box
            x1, y1, x2, y2 = box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Ensure coordinates are within frame bounds
            h, w = frame.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            # Skip if box is invalid
            if x2 <= x1 or y2 <= y1:
                logger.warning(f"Invalid box coordinates: {box}, skipping")
                continue

            # Crop the jewelry from the frame
            cropped = frame[y1:y2, x1:x2]

            # Save cropped image
            filename = f"jewelry_t{timestamp:.2f}s_det{idx}_{label}.jpg"
            crop_path = cropped_dir / filename
            cv2.imwrite(str(crop_path), cropped)

            detection_info = {
                "timestamp": timestamp,
                "index": idx,
                "label": label,
                "confidence": confidence,
                "box": [x1, y1, x2, y2],
                "crop_path": str(crop_path),
            }

            results.append((detection_info, cropped))
            logger.info(f"  └─ {label} (conf: {confidence:.2f}) -> {filename}")

        return results

    def search_similar_jewelry(
        self, detection_info: dict, cropped_image: any, run_dir: Path, top_k: int = 5
    ):
        """
        Search for similar jewelry in the database.

        Args:
            detection_info: Detection information dictionary
            cropped_image: Cropped jewelry image
            run_dir: Directory for saving results
            top_k: Number of similar images to retrieve
        """
        crop_path = detection_info["crop_path"]
        timestamp = detection_info["timestamp"]
        idx = detection_info["index"]

        logger.info(
            f"Searching for similar jewelry to detection {idx} at {timestamp:.2f}s"
        )

        # Perform similarity search (returns just paths)
        similar_paths = self.similarity_search.search(query=crop_path, top_k=top_k)

        if not similar_paths:
            logger.warning(f"No similar jewelry found for detection {idx}")
            return

        # Create results directory for this detection
        results_dir = run_dir / "search_results" / f"t{timestamp:.2f}s_det{idx}"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Copy the source (cropped) image
        source_filename = f"source_{detection_info['label']}.jpg"
        source_path = results_dir / source_filename
        shutil.copy2(crop_path, source_path)

        logger.info(f"Found {len(similar_paths)} similar items:")

        # Save similar images
        for rank, similar_path in enumerate(similar_paths, 1):
            # Copy similar image
            similar_filename = f"similar_{rank}_{Path(similar_path).name}"
            dest_path = results_dir / similar_filename
            shutil.copy2(similar_path, dest_path)

            logger.info(f"  {rank}. {Path(similar_path).name}")

        # Create a comparison image showing source and top results
        self._create_comparison_image(
            source_path, similar_paths, results_dir, detection_info
        )

    def _create_comparison_image(
        self,
        source_path: Path,
        similar_paths: List[str],
        results_dir: Path,
        detection_info: dict,
    ):
        """
        Create a side-by-side comparison image of source and similar items.

        Args:
            source_path: Path to source (cropped) image
            similar_paths: List of paths to similar images
            results_dir: Directory to save comparison image
            detection_info: Detection information
        """
        # Load source image
        source_img = cv2.imread(str(source_path))
        if source_img is None:
            logger.warning("Could not load source image for comparison")
            return

        # Resize source to a standard height
        target_height = 200
        h, w = source_img.shape[:2]
        source_img = cv2.resize(source_img, (int(w * target_height / h), target_height))

        # Add label to source
        source_img = cv2.copyMakeBorder(
            source_img, 30, 0, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255)
        )
        cv2.putText(
            source_img,
            f"SOURCE: {detection_info['label']}",
            (5, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
        )

        # Load and resize similar images (top 3)
        similar_images = []
        for i, similar_path in enumerate(similar_paths[:3], 1):
            img = cv2.imread(similar_path)
            if img is None:
                continue

            h, w = img.shape[:2]
            img = cv2.resize(img, (int(w * target_height / h), target_height))

            # Add label
            img = cv2.copyMakeBorder(
                img, 30, 0, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255)
            )
            cv2.putText(
                img,
                f"MATCH #{i}",
                (5, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
            )
            similar_images.append(img)

        if not similar_images:
            logger.warning("No similar images loaded for comparison")
            return

        # Concatenate images horizontally
        comparison = cv2.hconcat([source_img] + similar_images)

        # Save comparison image
        comparison_path = results_dir / "comparison.jpg"
        cv2.imwrite(str(comparison_path), comparison)
        logger.info(f"Created comparison image: {comparison_path}")

    def process_video(
        self,
        video_path: str,
        interval_seconds: int = None,
        top_k_similar: int = 5,
    ) -> str:
        """
        Process a video through the complete jewelry detection pipeline.

        Args:
            video_path: Path to the video file
            interval_seconds: Interval between frames (uses config if None)
            top_k_similar: Number of similar images to retrieve

        Returns:
            Path to the output directory containing results
        """
        # Create a timestamped run directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = Path(video_path).stem
        run_dir = self.output_base_dir / f"{video_name}_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info(f"Starting jewelry detection pipeline for: {video_path}")
        logger.info(f"Results will be saved to: {run_dir}")
        logger.info("=" * 80)

        # Step 1: Extract frames
        logger.info("\n[STEP 1] Extracting frames from video...")
        frames = self.extract_frames(video_path, interval_seconds)

        if not frames:
            logger.error("No frames extracted from video!")
            return str(run_dir)

        # Step 2: Detect and crop jewelry
        logger.info("\n[STEP 2] Detecting jewelry in frames...")
        all_detections = []
        for timestamp, frame in frames:
            detections = self.detect_and_crop_jewelry(frame, timestamp, run_dir)
            all_detections.extend(detections)

        if not all_detections:
            logger.warning("No jewelry detected in any frame!")
            return str(run_dir)

        logger.info(f"\nTotal jewelry items detected: {len(all_detections)}")

        # Step 3: Search for similar jewelry
        logger.info("\n[STEP 3] Searching for similar jewelry in database...")
        for detection_info, cropped_image in all_detections:
            self.search_similar_jewelry(
                detection_info, cropped_image, run_dir, top_k_similar
            )

        # Create summary
        self._create_summary(run_dir, video_path, all_detections)

        logger.info("=" * 80)
        logger.info("Pipeline completed successfully!")
        logger.info(f"Results saved to: {run_dir}")
        logger.info("=" * 80)

        return str(run_dir)

    def _create_summary(
        self, run_dir: Path, video_path: str, all_detections: List[Tuple[dict, any]]
    ):
        """Create a summary file with pipeline results."""
        summary_path = run_dir / "summary.txt"

        with open(summary_path, "w") as f:
            f.write("JEWELRY DETECTION PIPELINE SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Video: {video_path}\n")
            f.write(
                f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Total Detections: {len(all_detections)}\n\n")

            f.write("DETECTIONS:\n")
            f.write("-" * 80 + "\n")

            for detection_info, _ in all_detections:
                f.write(
                    f"Timestamp: {detection_info['timestamp']:.2f}s | "
                    f"Label: {detection_info['label']} | "
                    f"Confidence: {detection_info['confidence']:.2f} | "
                    f"Box: {detection_info['box']}\n"
                )

            f.write("\nDIRECTORY STRUCTURE:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{run_dir}/\n")
            f.write("├── cropped_jewelry/          (All cropped jewelry images)\n")
            f.write("├── search_results/           (Similarity search results)\n")
            f.write("│   └── t<time>s_det<n>/     (Results for each detection)\n")
            f.write("│       ├── source_*.jpg      (Original cropped jewelry)\n")
            f.write("│       ├── similar_*.jpg     (Similar items from database)\n")
            f.write("│       └── comparison.jpg    (Side-by-side comparison)\n")
            f.write("└── summary.txt               (This file)\n")

        logger.info(f"Summary saved to: {summary_path}")


def main():
    """Main entry point for the jewelry test pipeline."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test jewelry detection and similarity search on a video"
    )
    parser.add_argument("video_path", help="Path to the video file to process")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Frame extraction interval in seconds (default: 5)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of similar images to retrieve (default: 5)",
    )
    parser.add_argument(
        "--output-dir",
        default="jewelry_test/data",
        help="Output directory for results (default: jewelry_test/data)",
    )

    args = parser.parse_args()

    # Validate video path
    if not os.path.exists(args.video_path):
        logger.error(f"Video file not found: {args.video_path}")
        sys.exit(1)

    # Create pipeline and process video
    pipeline = JewelryTestPipeline(output_base_dir=args.output_dir)
    result_dir = pipeline.process_video(
        video_path=args.video_path,
        interval_seconds=args.interval,
        top_k_similar=args.top_k,
    )

    print(f"\n✅ Processing complete! Results saved to: {result_dir}")


if __name__ == "__main__":
    main()

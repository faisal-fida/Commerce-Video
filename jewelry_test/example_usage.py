"""
Example script showing how to use the jewelry test pipeline.

This demonstrates various ways to use the JewelryTestPipeline class.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jewelry_test.test_jewelry_pipeline import JewelryTestPipeline


def example_basic():
    """Basic usage example."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 80 + "\n")

    # Create pipeline
    pipeline = JewelryTestPipeline()

    # Process a video (replace with your video path)
    video_path = "jewelry_test/data/videos/sample.mp4"

    if not os.path.exists(video_path):
        print(f"⚠️  Video not found: {video_path}")
        print("Please place a video file at the above path to run this example.")
        return

    result_dir = pipeline.process_video(video_path)
    print(f"\n✅ Results saved to: {result_dir}")


def example_custom_settings():
    """Example with custom settings."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Custom Settings")
    print("=" * 80 + "\n")

    # Create pipeline with custom output directory
    pipeline = JewelryTestPipeline(output_base_dir="jewelry_test/my_custom_results")

    # Process with custom settings
    video_path = "jewelry_test/data/videos/sample.mp4"

    if not os.path.exists(video_path):
        print(f"⚠️  Video not found: {video_path}")
        return

    result_dir = pipeline.process_video(
        video_path=video_path,
        interval_seconds=3,  # Extract frames every 3 seconds
        top_k_similar=10,  # Get top 10 similar items
    )
    print(f"\n✅ Results saved to: {result_dir}")


def example_batch_processing():
    """Example processing multiple videos."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Batch Processing")
    print("=" * 80 + "\n")

    # Create pipeline once
    pipeline = JewelryTestPipeline()

    # List of videos to process
    video_dir = "jewelry_test/data/videos"

    if not os.path.exists(video_dir):
        print(f"⚠️  Directory not found: {video_dir}")
        return

    videos = [
        f for f in os.listdir(video_dir) if f.endswith((".mp4", ".avi", ".mov", ".mkv"))
    ]

    if not videos:
        print(f"⚠️  No videos found in: {video_dir}")
        print("Please add video files to process.")
        return

    print(f"Found {len(videos)} videos to process:\n")

    results = []
    for i, video_file in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] Processing: {video_file}")
        video_path = os.path.join(video_dir, video_file)

        try:
            result_dir = pipeline.process_video(video_path)
            results.append((video_file, result_dir, "SUCCESS"))
            print(f"✅ Completed: {video_file}")
        except Exception as e:
            print(f"❌ Failed: {video_file} - {str(e)}")
            results.append((video_file, None, f"FAILED: {str(e)}"))

    # Print summary
    print("\n" + "=" * 80)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 80 + "\n")

    for video_file, result_dir, status in results:
        if result_dir:
            print(f"✅ {video_file}")
            print(f"   └─ {result_dir}")
        else:
            print(f"❌ {video_file}")
            print(f"   └─ {status}")


def example_detailed_analysis():
    """Example showing how to access individual steps."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Detailed Step-by-Step Analysis")
    print("=" * 80 + "\n")

    from pathlib import Path

    pipeline = JewelryTestPipeline()
    video_path = "jewelry_test/data/videos/sample.mp4"

    if not os.path.exists(video_path):
        print(f"⚠️  Video not found: {video_path}")
        return

    # Step 1: Extract frames manually
    print("\n[STEP 1] Extracting frames...")
    frames = pipeline.extract_frames(video_path, interval_seconds=5)
    print(f"Extracted {len(frames)} frames")

    # Step 2: Process first frame only
    if frames:
        print("\n[STEP 2] Processing first frame...")
        timestamp, frame = frames[0]

        # Create temporary run directory
        run_dir = Path("jewelry_test/data/temp_analysis")
        run_dir.mkdir(parents=True, exist_ok=True)

        # Detect and crop jewelry
        detections = pipeline.detect_and_crop_jewelry(frame, timestamp, run_dir)
        print(f"Detected {len(detections)} jewelry items")

        # Step 3: Search for first detection
        if detections:
            print("\n[STEP 3] Searching for similar jewelry...")
            detection_info, cropped_image = detections[0]
            pipeline.search_similar_jewelry(
                detection_info, cropped_image, run_dir, top_k=5
            )
            print(f"✅ Results saved to: {run_dir}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("JEWELRY TEST PIPELINE - USAGE EXAMPLES")
    print("=" * 80)

    # Check if jewelry database exists
    from config import SIMILARITY_SEARCH_CONFIG

    jewelry_db_path = SIMILARITY_SEARCH_CONFIG.jewelry_db_path

    if not os.path.exists(f"{jewelry_db_path}/faiss_index.bin"):
        print("\n⚠️  WARNING: Jewelry database not found!")
        print("Please build the database first:")
        print("  python image_similarity_search/build_similarity_databases.py")
        print("\nExiting...\n")
        return

    # Run examples
    try:
        example_basic()
    except Exception as e:
        print(f"\n❌ Example 1 failed: {e}")

    # Uncomment to run other examples:
    # example_custom_settings()
    # example_batch_processing()
    # example_detailed_analysis()

    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

# Jewelry Detection Test Module

This module provides a standalone testing environment for the jewelry detection and similarity search pipeline.

## Features

- **Video Frame Extraction**: Extracts frames from videos at specified intervals
- **Jewelry Detection**: Detects jewelry items in each frame using the Roboflow API
- **Image Cropping**: Automatically crops detected jewelry items
- **Similarity Search**: Finds similar jewelry from the product database
- **Visual Comparison**: Creates side-by-side comparison images
- **Organized Output**: Saves all results in a structured directory

## Directory Structure

```
jewelry_test/
├── __init__.py
├── test_jewelry_pipeline.py    # Main pipeline script
├── README.md                    # This file
└── data/                        # Output directory
    └── <video_name>_<timestamp>/
        ├── cropped_jewelry/         # All cropped jewelry images
        ├── search_results/          # Similarity search results
        │   └── t<time>s_det<n>/    # Results for each detection
        │       ├── source_*.jpg     # Original cropped jewelry
        │       ├── similar_*.jpg    # Similar items from database
        │       └── comparison.jpg   # Side-by-side comparison
        └── summary.txt              # Processing summary
```

## Usage

### Command Line

```bash
# Basic usage - process a video with default settings
python jewelry_test/test_jewelry_pipeline.py path/to/video.mp4

# Custom frame interval (extract frames every 3 seconds)
python jewelry_test/test_jewelry_pipeline.py path/to/video.mp4 --interval 3

# Get more similar results (default is 5)
python jewelry_test/test_jewelry_pipeline.py path/to/video.mp4 --top-k 10

# Custom output directory
python jewelry_test/test_jewelry_pipeline.py path/to/video.mp4 --output-dir my_results

# All options combined
python jewelry_test/test_jewelry_pipeline.py \
    path/to/video.mp4 \
    --interval 3 \
    --top-k 10 \
    --output-dir my_results
```

### Python Script

```python
from jewelry_test.test_jewelry_pipeline import JewelryTestPipeline

# Create pipeline instance
pipeline = JewelryTestPipeline(output_base_dir="jewelry_test/data")

# Process a video
result_dir = pipeline.process_video(
    video_path="path/to/video.mp4",
    interval_seconds=5,
    top_k_similar=5
)

print(f"Results saved to: {result_dir}")
```

## Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `video_path` | str | *required* | Path to the video file to process |
| `--interval` | int | 5 | Frame extraction interval in seconds |
| `--top-k` | int | 5 | Number of similar images to retrieve |
| `--output-dir` | str | jewelry_test/data | Output directory for results |

## Output Files

### Cropped Jewelry Images
- **Location**: `<run_dir>/cropped_jewelry/`
- **Format**: `jewelry_t<timestamp>s_det<index>_<label>.jpg`
- **Description**: Cropped images of each detected jewelry item

### Search Results
- **Location**: `<run_dir>/search_results/t<timestamp>s_det<index>/`
- **Files**:
  - `source_<label>.jpg` - The cropped jewelry that was searched
  - `similar_<rank>_score<score>_<name>.jpg` - Similar items found in database
  - `comparison.jpg` - Side-by-side visual comparison

### Summary File
- **Location**: `<run_dir>/summary.txt`
- **Contents**: Processing information, all detections, directory structure

## Requirements

Before running the test pipeline, ensure:

1. **Backend Models Initialized**: The jewelry detector and similarity search models must be loaded
2. **Jewelry Database Built**: Run `python image_similarity_search/build_similarity_databases.py` if needed
3. **Jewelry Images Available**: Product images should be in `data/image_db/jewelry/`

## Example Workflow

```bash
# 1. Ensure jewelry database is built
python image_similarity_search/build_similarity_databases.py

# 2. Place your test video in the jewelry_test/data/videos/ directory
cp ~/my_video.mp4 jewelry_test/data/videos/

# 3. Run the test pipeline
python jewelry_test/test_jewelry_pipeline.py jewelry_test/data/videos/my_video.mp4

# 4. Check results
ls -la jewelry_test/data/my_video_*/
```

## Troubleshooting

### No jewelry detected
- Check that the video contains visible jewelry items
- Try adjusting the confidence threshold in `config.py`
- Verify the Roboflow API is working (check logs)

### No similar images found
- Ensure the jewelry database is built and loaded
- Check that there are images in `data/image_db/jewelry/`
- Rebuild the database if needed

### Import errors
- Make sure you're running from the project root directory
- Check that all dependencies are installed

## Tips

- **Start with short videos**: Test with 10-20 second clips first
- **Adjust frame interval**: Increase interval for faster processing of long videos
- **Review comparisons**: The `comparison.jpg` files show visual similarity quality
- **Check logs**: The script provides detailed logging of each step

## API Reference

### JewelryTestPipeline

#### `__init__(output_base_dir: str = "jewelry_test/data")`
Initialize the pipeline with detectors and similarity search.

#### `extract_frames(video_path: str, interval_seconds: int = None) -> List[Tuple[float, np.ndarray]]`
Extract frames from video at specified intervals.

#### `detect_and_crop_jewelry(frame: np.ndarray, timestamp: float, run_dir: Path) -> List[Tuple[dict, np.ndarray]]`
Detect jewelry in a frame and return cropped images.

#### `search_similar_jewelry(detection_info: dict, cropped_image: np.ndarray, run_dir: Path, top_k: int = 5)`
Search for similar jewelry and save results.

#### `process_video(video_path: str, interval_seconds: int = None, top_k_similar: int = 5) -> str`
Process a complete video through the pipeline. Returns output directory path.


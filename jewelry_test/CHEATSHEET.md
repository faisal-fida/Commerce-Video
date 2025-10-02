# Jewelry Test Pipeline - Cheat Sheet

Quick reference for common commands and workflows.

## 🚀 Basic Commands

### Run with default settings
```bash
python jewelry_test/test_jewelry_pipeline.py path/to/video.mp4
```

### Using the helper script
```bash
./jewelry_test/run_test.sh path/to/video.mp4
```

### Show help
```bash
python jewelry_test/test_jewelry_pipeline.py --help
```

## ⚙️ Common Options

### Frame extraction interval
```bash
# Every 1 second (detailed)
python jewelry_test/test_jewelry_pipeline.py video.mp4 --interval 1

# Every 5 seconds (default)
python jewelry_test/test_jewelry_pipeline.py video.mp4 --interval 5

# Every 10 seconds (faster)
python jewelry_test/test_jewelry_pipeline.py video.mp4 --interval 10
```

### Number of similar results
```bash
# Top 3 matches
python jewelry_test/test_jewelry_pipeline.py video.mp4 --top-k 3

# Top 10 matches (more options)
python jewelry_test/test_jewelry_pipeline.py video.mp4 --top-k 10
```

### Custom output directory
```bash
python jewelry_test/test_jewelry_pipeline.py video.mp4 --output-dir my_results
```

### All options together
```bash
python jewelry_test/test_jewelry_pipeline.py \
    path/to/video.mp4 \
    --interval 3 \
    --top-k 10 \
    --output-dir results
```

## 📂 Working with Results

### View summary
```bash
cat jewelry_test/data/myvideo_*/summary.txt
```

### List all cropped jewelry
```bash
ls -lh jewelry_test/data/myvideo_*/cropped_jewelry/
```

### View search results
```bash
ls -lh jewelry_test/data/myvideo_*/search_results/
```

### Open comparison images (Linux)
```bash
xdg-open jewelry_test/data/myvideo_*/search_results/*/comparison.jpg
```

### Open comparison images (macOS)
```bash
open jewelry_test/data/myvideo_*/search_results/*/comparison.jpg
```

### Copy results elsewhere
```bash
cp -r jewelry_test/data/myvideo_20251002_143055 ~/Desktop/results
```

## 🔧 Setup & Maintenance

### Check if database exists
```bash
ls -lh data/similarity_db/jewelry/
```

### Build/rebuild jewelry database
```bash
python image_similarity_search/build_similarity_databases.py
```

### Add new jewelry images
```bash
cp new_jewelry_*.jpg data/image_db/jewelry/
python image_similarity_search/build_similarity_databases.py
```

### Clean up old results
```bash
rm -rf jewelry_test/data/myvideo_*
```

## 🐍 Python Usage

### Basic
```python
from jewelry_test.test_jewelry_pipeline import JewelryTestPipeline

pipeline = JewelryTestPipeline()
result_dir = pipeline.process_video("video.mp4")
```

### Custom settings
```python
pipeline = JewelryTestPipeline(output_base_dir="my_results")
result_dir = pipeline.process_video(
    video_path="video.mp4",
    interval_seconds=3,
    top_k_similar=10
)
```

### Batch processing
```python
pipeline = JewelryTestPipeline()
videos = ["video1.mp4", "video2.mp4", "video3.mp4"]

for video in videos:
    result_dir = pipeline.process_video(video)
    print(f"✅ {video} -> {result_dir}")
```

### Manual step-by-step
```python
from pathlib import Path

pipeline = JewelryTestPipeline()
frames = pipeline.extract_frames("video.mp4", interval_seconds=5)

run_dir = Path("jewelry_test/data/test_run")
run_dir.mkdir(parents=True, exist_ok=True)

for timestamp, frame in frames:
    detections = pipeline.detect_and_crop_jewelry(frame, timestamp, run_dir)
    for det_info, cropped in detections:
        pipeline.search_similar_jewelry(det_info, cropped, run_dir, top_k=5)
```

## 🐛 Quick Fixes

### Module import error
```bash
cd /home/azureuser/CommerceVideo
python jewelry_test/test_jewelry_pipeline.py video.mp4
```

### Database not found
```bash
python image_similarity_search/build_similarity_databases.py
```

### Video not found
```bash
# Use absolute path
python jewelry_test/test_jewelry_pipeline.py /full/path/to/video.mp4

# Or copy video to known location
cp ~/video.mp4 jewelry_test/data/videos/
python jewelry_test/test_jewelry_pipeline.py jewelry_test/data/videos/video.mp4
```

### No jewelry detected
- Try lower confidence threshold in `config.py`
- Check video quality and lighting
- Verify jewelry is visible

### Permission denied
```bash
chmod +x jewelry_test/run_test.sh
chmod +x jewelry_test/test_jewelry_pipeline.py
```

## 📊 Common Workflows

### Quick Test (Fast)
```bash
# Extract frames every 10 seconds, get top 3 matches
python jewelry_test/test_jewelry_pipeline.py video.mp4 --interval 10 --top-k 3
```

### Detailed Analysis (Thorough)
```bash
# Extract frames every 1 second, get top 10 matches
python jewelry_test/test_jewelry_pipeline.py video.mp4 --interval 1 --top-k 10
```

### Production Quality (Balanced)
```bash
# Extract frames every 5 seconds, get top 5 matches
python jewelry_test/test_jewelry_pipeline.py video.mp4 --interval 5 --top-k 5
```

## 💡 Pro Tips

### Find latest results
```bash
ls -lt jewelry_test/data/ | head
```

### Count detections
```bash
ls jewelry_test/data/myvideo_*/cropped_jewelry/ | wc -l
```

### Find best matches (score > 0.9)
```bash
find jewelry_test/data/myvideo_*/search_results/ -name "similar_1_score0.9*.jpg"
```

### Create results archive
```bash
tar -czf results.tar.gz jewelry_test/data/myvideo_*
```

### View all comparison images
```bash
find jewelry_test/data/myvideo_*/ -name "comparison.jpg" -exec xdg-open {} \;
```

## 📋 File Naming Patterns

### Cropped jewelry
```
jewelry_t{timestamp}s_det{index}_{label}.jpg

Examples:
- jewelry_t5.00s_det0_ring.jpg
- jewelry_t10.50s_det1_necklace.jpg
```

### Similar products
```
similar_{rank}_score{score}_{original_name}.jpg

Examples:
- similar_1_score0.892_ring1.jpg
- similar_2_score0.845_ring2.jpg
```

### Directories
```
{video_name}_{timestamp}/

Examples:
- myvideo_20251002_143055/
- test_clip_20251002_153022/
```

## 🎯 Performance Guide

| Scenario | Interval | Top-K | Time |
|----------|----------|-------|------|
| Quick test | 10s | 3 | ~30s |
| Standard | 5s | 5 | ~1min |
| Detailed | 3s | 10 | ~2min |
| Exhaustive | 1s | 10 | ~5min |

*Times are approximate for a 60-second video

---

**Need more details?** Check README.md for full documentation.


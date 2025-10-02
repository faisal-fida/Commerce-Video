# Jewelry Test Module Overview

A comprehensive testing environment for jewelry detection and similarity search.

## 📁 Module Structure

```
jewelry_test/
├── __init__.py                    # Module initialization
├── test_jewelry_pipeline.py       # Main pipeline implementation
├── example_usage.py               # Usage examples
├── run_test.sh                    # Bash helper script
├── QUICKSTART.md                  # Quick start guide
├── README.md                      # Full documentation
├── OVERVIEW.md                    # This file
├── .gitignore                     # Git ignore rules
└── data/                          # Data directory
    ├── videos/                    # Input videos
    ├── cropped_jewelry/           # Cropped detections (created automatically)
    └── search_results/            # Search results (created automatically)
```

## 🎯 What This Module Does

### 1. Video Frame Extraction
- Extracts frames at configurable intervals (default: 5 seconds)
- Displays FPS, duration, and total frames
- Logs each extracted frame with timestamp

### 2. Jewelry Detection
- Uses Roboflow API for jewelry detection
- Detects: rings, necklaces, bracelets, earrings, watches, etc.
- Configurable confidence threshold
- Logs detection count and confidence scores

### 3. Image Cropping
- Automatically crops detected jewelry from frames
- Saves with descriptive filenames: `jewelry_t{time}s_det{n}_{label}.jpg`
- Organizes all crops in `cropped_jewelry/` directory

### 4. Similarity Search
- Uses CLIP embeddings and FAISS for fast similarity search
- Searches against jewelry product database
- Returns top-k most similar items with scores

### 5. Visual Comparison
- Creates side-by-side comparison images
- Shows source jewelry next to top 3 matches
- Displays similarity scores on images
- Saves as `comparison.jpg` for easy review

### 6. Results Organization
- Timestamped output directories
- Structured subdirectories for different result types
- Detailed summary file with all metadata
- Easy to navigate and review

## 🚀 Quick Start

### Option 1: Command Line
```bash
python jewelry_test/test_jewelry_pipeline.py path/to/video.mp4
```

### Option 2: Bash Script
```bash
./jewelry_test/run_test.sh path/to/video.mp4
```

### Option 3: Python Code
```python
from jewelry_test.test_jewelry_pipeline import JewelryTestPipeline

pipeline = JewelryTestPipeline()
result_dir = pipeline.process_video("path/to/video.mp4")
```

## 📊 Output Structure

```
jewelry_test/data/
└── myvideo_20251002_143055/           # Timestamped run directory
    ├── summary.txt                     # Processing summary
    ├── cropped_jewelry/                # All cropped jewelry
    │   ├── jewelry_t5.00s_det0_ring.jpg
    │   ├── jewelry_t5.00s_det1_necklace.jpg
    │   └── jewelry_t10.00s_det0_bracelet.jpg
    └── search_results/                 # Similarity search results
        ├── t5.00s_det0/                # Results for ring at 5s
        │   ├── source_ring.jpg         # Original cropped ring
        │   ├── similar_1_score0.892_ring1.jpg
        │   ├── similar_2_score0.845_ring2.jpg
        │   ├── similar_3_score0.801_ring3.jpg
        │   └── comparison.jpg          # Visual comparison
        └── t5.00s_det1/                # Results for necklace at 5s
            ├── source_necklace.jpg
            ├── similar_1_score0.876_necklace1.jpg
            └── comparison.jpg
```

## 🎨 Features

### ✅ Automated Pipeline
- Single command processes entire video
- No manual intervention needed
- Progress logging at each step

### ✅ Flexible Configuration
- Adjustable frame extraction interval
- Configurable number of similar results (top-k)
- Custom output directories
- Works with any video format

### ✅ Detailed Logging
- Real-time progress updates
- Detection counts and confidence scores
- Similarity scores for each match
- Processing time information

### ✅ Visual Results
- Side-by-side comparison images
- Labeled with scores and metadata
- Easy to evaluate quality
- Shareable for review

### ✅ Organized Output
- Timestamped directories (no overwrites)
- Logical subdirectory structure
- Summary file with all information
- Easy to find specific results

## 🔧 Configuration

### Frame Extraction Interval
```bash
# Extract frames every 3 seconds
python jewelry_test/test_jewelry_pipeline.py video.mp4 --interval 3
```

### Number of Similar Results
```bash
# Get top 10 similar items for each detection
python jewelry_test/test_jewelry_pipeline.py video.mp4 --top-k 10
```

### Custom Output Directory
```bash
# Save results to custom location
python jewelry_test/test_jewelry_pipeline.py video.mp4 --output-dir my_results
```

### Confidence Threshold
Edit `config.py`:
```python
class JewelryDetectionConfig:
    confidence_threshold: float = 0.4  # Adjust this value
```

## 📋 Requirements

### 1. Jewelry Database
The jewelry similarity database must be built:
```bash
python image_similarity_search/build_similarity_databases.py
```

### 2. Jewelry Product Images
Add jewelry images to:
```
data/image_db/jewelry/
```

### 3. Dependencies
All Python packages from `requirements.txt` must be installed.

### 4. Roboflow API
Jewelry detection requires Roboflow API access (configured in `config.py`).

## 🎓 Use Cases

### Development & Testing
- Test jewelry detection accuracy
- Evaluate similarity search quality
- Debug detection issues
- Optimize confidence thresholds

### Quality Assurance
- Verify end-to-end pipeline
- Check product database coverage
- Validate search results
- Compare detection algorithms

### Research & Analysis
- Analyze jewelry appearance in videos
- Study similarity patterns
- Benchmark performance
- Generate training data

### Client Demonstrations
- Show detection capabilities
- Demonstrate search quality
- Provide visual proof of concept
- Generate sample results

## 📈 Performance Tips

### For Faster Processing
- Increase frame extraction interval
- Use shorter test videos
- Reduce top-k value
- Process videos in batches

### For Better Quality
- Use high-quality input videos
- Ensure good lighting
- Decrease frame interval for more coverage
- Increase top-k for more options

### For Debugging
- Start with 10-20 second clips
- Process single frames first
- Check logs for errors
- Review comparison images

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the project root
cd /home/azureuser/CommerceVideo
python jewelry_test/test_jewelry_pipeline.py video.mp4
```

### "Database not found"
```bash
# Build the jewelry database
python image_similarity_search/build_similarity_databases.py
```

### "No jewelry detected"
- Check video quality and lighting
- Verify jewelry is visible and clear
- Lower confidence threshold in config.py
- Try different video segments

### "No similar images found"
- Ensure jewelry database has images
- Check that database is loaded
- Verify image paths are correct
- Rebuild database if needed

## 📚 Documentation Files

- **QUICKSTART.md**: Get started in 3 steps
- **README.md**: Complete documentation and API reference
- **OVERVIEW.md**: This file - module overview
- **example_usage.py**: Python code examples

## 🔗 Related Files

- `config.py`: Global configuration
- `object_detectors/jewelry_detector.py`: Jewelry detection implementation
- `image_similarity_search/similarity_search.py`: Similarity search engine
- `image_similarity_search/build_similarity_databases.py`: Database builder

## 💡 Tips

1. **Start Small**: Use short videos for initial testing
2. **Review Logs**: Check console output for detailed progress
3. **Check Comparisons**: Visual comparisons show search quality
4. **Iterate**: Adjust settings based on results
5. **Organize**: Use descriptive video names for easy identification

## ⚡ Advanced Usage

### Batch Processing
Process multiple videos:
```python
from jewelry_test.test_jewelry_pipeline import JewelryTestPipeline

pipeline = JewelryTestPipeline()
videos = ["video1.mp4", "video2.mp4", "video3.mp4"]

for video in videos:
    result_dir = pipeline.process_video(video)
    print(f"Processed {video} -> {result_dir}")
```

### Custom Analysis
Access individual pipeline steps:
```python
pipeline = JewelryTestPipeline()

# Extract frames
frames = pipeline.extract_frames("video.mp4")

# Process specific frame
from pathlib import Path
run_dir = Path("jewelry_test/data/custom_run")
detections = pipeline.detect_and_crop_jewelry(frames[0][1], 0.0, run_dir)

# Search for specific detection
if detections:
    pipeline.search_similar_jewelry(detections[0][0], detections[0][1], run_dir)
```

## 🎯 Next Steps

1. **Test with sample video**: Place a video and run the pipeline
2. **Review results**: Check the comparison images
3. **Adjust settings**: Fine-tune based on your needs
4. **Scale up**: Process longer videos or batches
5. **Integrate**: Use insights to improve main pipeline

---

**Need help?** Check the other documentation files or review the example scripts!


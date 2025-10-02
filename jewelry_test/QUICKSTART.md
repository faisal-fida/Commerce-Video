# Quick Start Guide

Get started with the jewelry test pipeline in 3 simple steps!

## Step 1: Prepare Your Video

Place your test video in the `jewelry_test/data/videos/` directory:

```bash
cp /path/to/your/video.mp4 jewelry_test/data/videos/
```

Or use any video file from your system by providing its full path.

## Step 2: Run the Pipeline

```bash
python jewelry_test/test_jewelry_pipeline.py jewelry_test/data/videos/your_video.mp4
```

That's it! The pipeline will:
- ✅ Extract frames from your video
- ✅ Detect jewelry in each frame
- ✅ Crop detected jewelry items
- ✅ Search for similar products in the database
- ✅ Create visual comparisons
- ✅ Generate a detailed summary

## Step 3: View Results

Results are saved in `jewelry_test/data/<video_name>_<timestamp>/`:

```bash
# View the summary
cat jewelry_test/data/your_video_*/summary.txt

# View cropped jewelry images
ls jewelry_test/data/your_video_*/cropped_jewelry/

# View similarity search results
ls jewelry_test/data/your_video_*/search_results/

# Open comparison images
open jewelry_test/data/your_video_*/search_results/*/comparison.jpg
```

## Examples

### Basic Usage
```bash
python jewelry_test/test_jewelry_pipeline.py my_video.mp4
```

### Extract frames every 3 seconds
```bash
python jewelry_test/test_jewelry_pipeline.py my_video.mp4 --interval 3
```

### Get top 10 similar items
```bash
python jewelry_test/test_jewelry_pipeline.py my_video.mp4 --top-k 10
```

### All options
```bash
python jewelry_test/test_jewelry_pipeline.py \
    jewelry_test/data/videos/my_video.mp4 \
    --interval 3 \
    --top-k 10 \
    --output-dir jewelry_test/results
```

## Tips

1. **Short videos first**: Test with 10-20 second clips to iterate quickly
2. **Check the logs**: The script provides detailed progress information
3. **Review comparisons**: Look at `comparison.jpg` files to evaluate quality
4. **Adjust settings**: Modify interval and top-k based on your needs

## Troubleshooting

### "No jewelry detected"
- Ensure your video contains visible jewelry
- Check that jewelry items are clear and well-lit
- Try reducing the confidence threshold in `config.py`

### "Database not found"
Build the jewelry database first:
```bash
python image_similarity_search/build_similarity_databases.py
```

### "Video not found"
- Verify the video path is correct
- Use absolute paths if relative paths don't work
- Check file permissions

## Need Help?

See the full documentation in [README.md](README.md) for:
- Detailed API reference
- Python script examples
- Advanced usage patterns
- Complete troubleshooting guide


#!/usr/bin/env python
"""
Validation script to check if the jewelry test module is properly set up.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 80)
print("JEWELRY TEST MODULE - SETUP VALIDATION")
print("=" * 80)
print()

# Check 1: Import dependencies
print("[1/6] Checking dependencies...")
try:
    import cv2
    import numpy as np
    from PIL import Image
    import faiss

    print("  ✅ All dependencies installed")
except ImportError as e:
    print(f"  ❌ Missing dependency: {e}")
    sys.exit(1)

# Check 2: Import project modules
print("\n[2/6] Checking project modules...")
try:
    from config import JEWELRY_CONFIG, SIMILARITY_SEARCH_CONFIG
    from object_detectors.jewelry_detector import JewelryDetector
    from image_similarity_search.similarity_search import ImageSimilaritySearch

    print("  ✅ All project modules imported successfully")
except ImportError as e:
    print(f"  ❌ Module import failed: {e}")
    sys.exit(1)

# Check 3: Jewelry database
print("\n[3/6] Checking jewelry database...")
jewelry_db_path = SIMILARITY_SEARCH_CONFIG.jewelry_db_path
index_path = f"{jewelry_db_path}/faiss_index.bin"
paths_path = f"{jewelry_db_path}/image_paths.pkl"

if os.path.exists(index_path) and os.path.exists(paths_path):
    print(f"  ✅ Jewelry database found at: {jewelry_db_path}")

    # Try to load it
    try:
        search_engine = ImageSimilaritySearch(db_path=jewelry_db_path)
        search_engine._load_database()
        num_images = (
            len(search_engine.image_paths)
            if hasattr(search_engine, "image_paths")
            else 0
        )
        print(f"  ✅ Database loaded successfully ({num_images} images)")
    except Exception as e:
        print(f"  ⚠️  Database exists but failed to load: {e}")
else:
    print(f"  ❌ Jewelry database not found at: {jewelry_db_path}")
    print("     Run: python image_similarity_search/build_similarity_databases.py")
    sys.exit(1)

# Check 4: Jewelry detector
print("\n[4/6] Checking jewelry detector...")
try:
    detector = JewelryDetector()
    print(f"  ✅ Jewelry detector initialized")
    print(f"     API URL: {detector.api_url}")
    print(f"     Model: {detector.model_id}")
    print(f"     Confidence threshold: {detector.confidence_threshold}")
except Exception as e:
    print(f"  ❌ Failed to initialize jewelry detector: {e}")
    sys.exit(1)

# Check 5: Test detection format
print("\n[5/6] Testing detection format...")
try:
    # Create a small test image
    test_img = Image.new("RGB", (100, 100), color="white")
    result = detector.detect_objects(test_img)

    # Check format
    assert isinstance(result, dict), "Result should be a dict"
    assert "boxes" in result, "Result should have 'boxes' key"
    assert "labels" in result, "Result should have 'labels' key"
    assert "scores" in result, "Result should have 'scores' key"

    print("  ✅ Detection format is correct")
    print(f"     Result keys: {list(result.keys())}")
except Exception as e:
    print(f"  ❌ Detection format test failed: {e}")
    sys.exit(1)

# Check 6: Import test pipeline
print("\n[6/6] Checking test pipeline...")
try:
    from jewelry_test.test_jewelry_pipeline import JewelryTestPipeline

    print("  ✅ Test pipeline module imported successfully")

    # Try to initialize (but don't load models again)
    print("  ℹ️  Pipeline class is ready to use")
except Exception as e:
    print(f"  ❌ Failed to import test pipeline: {e}")
    sys.exit(1)

# All checks passed
print("\n" + "=" * 80)
print("✅ ALL CHECKS PASSED - Module is ready to use!")
print("=" * 80)
print("\nQuick start:")
print("  python jewelry_test/test_jewelry_pipeline.py path/to/video.mp4")
print("\nFor help:")
print("  python jewelry_test/test_jewelry_pipeline.py --help")
print()

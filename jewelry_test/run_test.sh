#!/bin/bash
#
# Helper script to run the jewelry test pipeline
# Usage: ./jewelry_test/run_test.sh <video_path> [options]
#

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Jewelry Test Pipeline${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if video path is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: No video path provided${NC}"
    echo ""
    echo "Usage: $0 <video_path> [options]"
    echo ""
    echo "Examples:"
    echo "  $0 jewelry_test/data/videos/sample.mp4"
    echo "  $0 /path/to/video.mp4 --interval 3 --top-k 10"
    echo ""
    exit 1
fi

# Find Python interpreter
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif [ -f "/home/azureuser/.pyenv/versions/3.12.1/bin/python" ]; then
    PYTHON_CMD="/home/azureuser/.pyenv/versions/3.12.1/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo -e "${RED}❌ Error: Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}Using Python: $PYTHON_CMD${NC}"
echo ""

# Run the test pipeline
$PYTHON_CMD jewelry_test/test_jewelry_pipeline.py "$@"

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Pipeline completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Pipeline failed${NC}"
    exit 1
fi


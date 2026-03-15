#!/bin/bash
# AI Dashboard - Run Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🤖 AI Dashboard - Enterprise Edition${NC}"
echo "=================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
if [ ! -f "venv/lib/python*/site-packages/textual/__init__.py" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
fi

# Run the dashboard
echo -e "${GREEN}Starting AI Dashboard...${NC}"
python dashboard.py "$@"

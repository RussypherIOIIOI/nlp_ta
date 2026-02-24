#!/bin/bash
#  Telecom Transcript Analyzer - Setup Script

set -e

GREEN='\033[0;32m'
BRIGHT_GREEN='\033[1;32m'
DIM='\033[2m'
NC='\033[0m'

echo -e "${BRIGHT_GREEN}"
echo "============================================================"
echo "  Telecom Transcript Analyzer - Setup"
echo "============================================================"
echo -e "${NC}"

# Check Python version
echo -e "${GREEN}[1/5] Checking Python version...${NC}"
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "  Found Python ${PYTHON_VERSION}"

# Create virtual environment
echo -e "\n${GREEN}[2/5] Creating virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    $PYTHON_CMD -m venv .venv
    echo "  Virtual environment created."
else
    echo "  Virtual environment already exists."
fi

# Activate virtual environment
source .venv/bin/activate 2>/dev/null || . .venv/bin/activate
echo "  Activated .venv"

# Install dependencies
echo -e "\n${GREEN}[3/5] Installing dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  All packages installed."

# Download NLP models
echo -e "\n${GREEN}[4/5] Downloading NLP models...${NC}"
python -m spacy download en_core_web_sm -q 2>/dev/null || python -m spacy download en_core_web_sm
python -c "
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)
nltk.download('vader_lexicon', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
print('  NLTK data downloaded.')
"
echo "  NLP models ready."

# Run tests
echo -e "\n${GREEN}[5/5] Running component tests...${NC}"
python test_app.py

echo -e "\n${BRIGHT_GREEN}"
echo "============================================================"
echo "  Setup Complete!"
echo ""
echo "  To run the application:"
echo "    source .venv/bin/activate"
echo "    python telecom_transcript_analyzer.py"
echo ""
echo "  Sample transcripts available in ./samples/"
echo "============================================================"
echo -e "${NC}"
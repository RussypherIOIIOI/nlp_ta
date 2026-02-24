# ta_v2.3
NLP-powered transcript analysis tool for telecom professionals, built with PySide6 (Qt for Python) featuring a Matrix-themed GUI

# Transcript Analyzer 

> A comprehensive NLP-powered transcript analysis tool for telecom professionals, built with PySide6 (Qt for Python) featuring a Matrix-themed GUI.

![Python](https://img.shields.io/badge/Python-3.11+-00FF41?style=flat&logo=python&logoColor=00FF41&labelColor=0D0D0D)
![PySide6](https://img.shields.io/badge/PySide6-Qt-00FF41?style=flat&logo=qt&logoColor=00FF41&labelColor=0D0D0D)
![NLP](https://img.shields.io/badge/NLP-spaCy%20%7C%20NLTK%20%7C%20TextBlob-00FF41?style=flat&labelColor=0D0D0D)
![License](https://img.shields.io/badge/License-MIT-00FF41?style=flat&labelColor=0D0D0D)

---

## Overview
The Telecom Transcript Analyzer is a single-file Python desktop application designed for analyzing text transcripts with a focus on telecommunications-specific insights. It combines robust NLP backend processing with a professional, Matrix-themed graphical user interface to transform unstructured conversational data into actionable intelligence.

The application supports multiple transcript formats (.txt, .vtt, .srt, .csv) and provides comprehensive analysis including sentiment analysis, keyword extraction, named entity recognition, speaker diarization, text summarization, topic modeling, and telecom-specific keyword detection — all visualized through interactive charts and word clouds.

---

## Features
### Frontend (PySide6 GUI)
- **Matrix-themed Interface**: Retro black and green color scheme inspired by The Matrix
- **Multi-tab Analysis Dashboard**: Overview, Sentiment, Keywords, Entities, Speakers, Summary, Topics, Telecom, Visualizations
- **Transcript Editor**: Full-featured text editor with undo/redo, search, zoom, and syntax awareness
- **Segment Viewer**: Table view of parsed transcript segments with speaker and timestamp columns
- **Interactive Visualizations**: Embedded matplotlib charts with Matrix-styled rendering
- **File Operations**: Open, Save, Save As, Print, Export (JSON/CSV/Text)
- **Keyboard Shortcuts**: Full set of professional shortcuts (Ctrl+O, Ctrl+S, Ctrl+R, etc.)

### Backend (NLP Analysis Engine)
- **Transcript Ingestion**: Reads .txt, .vtt (WebVTT), .srt (SubRip), and .csv files with automatic encoding detection
- **Text Preprocessing**: Timestamp removal, speaker ID cleaning, filler word removal, normalization, tokenization
- **Sentiment Analysis**: Dual-engine analysis using VADER (NLTK) and TextBlob with per-sentence breakdown
- **Keyword Extraction**: Word frequency, TF-IDF scoring, bigrams, trigrams, and vocabulary richness metrics
- **Named Entity Recognition (NER)**: spaCy-powered extraction of persons, organizations, locations, and more
- **Speaker Diarization**: Identifies speakers, calculates talk share, word counts, and per-speaker sentiment
- **Text Summarization**: LSA and LexRank algorithms via sumy with configurable sentence count
- **Topic Modeling**: Latent Dirichlet Allocation (LDA) via scikit-learn with adjustable topic count
- **Telecom Analysis**: Domain-specific keyword detection across 5 categories (Network, Service, Customer, Technical, Compliance)
- **Word Cloud Generation**: Matrix-styled word clouds with green color palette
- **Sentiment Trend Visualization**: Scatter plots with moving average overlay

### Security
- File path validation and sanitization
- File size limits (100MB max)
- Encoding detection with chardet
- Null byte removal from input text
- Input validation on all file operations

---

## Quick Start
### Prerequisites
- Python 3.11 or newer
- pip (Python package manager)

### Installation

1. **Clone or download the project:**
   ```bash
   cd telecom-transcript-analyzer
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate   # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLP models:**
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('averaged_perceptron_tagger_eng'); nltk.download('vader_lexicon'); nltk.download('wordnet'); nltk.download('omw-1.4')"
   ```

5. **Run the application:**
   ```bash
   python telecom_transcript_analyzer.py
   ```

Or use the automated setup script:
```bash
chmod +x setup.sh
./setup.sh
```

---

## Usage Guide

### Loading a Transcript
1. Click **"Load Transcript"** in the header bar or use **Ctrl+O**
2. Select a supported file (.txt, .vtt, .srt, .csv)
3. The transcript appears in the left panel with raw text and parsed segments

### Running Analysis
1. Click **"Analyze"** or press **Ctrl+R**
2. Watch the progress bar as the NLP engine processes the transcript
3. Results populate across all analysis tabs automatically

### Analysis Tabs

| Tab | Description |
|-----|-------------|
| **Overview** | Dashboard with key metrics, sentiment summary, and quick stats |
| **Sentiment** | VADER/TextBlob scores, sentiment distribution chart, per-sentence trend |
| **Keywords** | Word frequency, TF-IDF, bigrams, trigrams, and word cloud |
| **Entities** | Named entities (people, orgs, locations) with type breakdown chart |
| **Speakers** | Speaker diarization with talk share pie chart and sentiment comparison |
| **Summary** | LSA and LexRank extractive summaries with adjustable length |
| **Topics** | LDA topic modeling with configurable topic count |
| **Telecom** | Telecom-specific keyword analysis across 5 industry categories |
| **Visualizations** | Additional keyword frequency bar chart |

### Exporting Results
- **JSON**: Full structured analysis data
- **CSV**: Tabular format for spreadsheet analysis
- **Text Report**: Human-readable formatted report
- **Print**: Print preview with full transcript and analysis

### Editing & Search
- Edit transcript text directly in the Raw Transcript tab
- Use **Ctrl+F** or the search bar to find text
- **Ctrl+Z/Y** for undo/redo
- **Ctrl++/-/0** for zoom in/out/reset

---

## Supported File Formats
| Format | Extension | Description |
|--------|-----------|-------------|
| Plain Text | `.txt` | Speaker labels detected via `Speaker: text` pattern |
| WebVTT | `.vtt` | Web Video Text Tracks with timestamps |
| SubRip | `.srt` | SubRip subtitle format with timestamps |
| CSV | `.csv` | Comma-separated with auto-detected columns (speaker, text, timestamp) |

---

## Project Structure
```
telecom-transcript-analyzer/
├── telecom_transcript_analyzer.py   # Main application (single file)
├── requirements.txt                 # Python dependencies
├── setup.sh                         # Automated setup script
├── test_app.py                      # Component test suite
├── README.md                        # This file
└── samples/                         # Sample transcript files
    ├── telecom_support_call.txt     # Customer support call transcript
    ├── network_incident.vtt         # Network incident review (WebVTT)
    └── customer_feedback.csv        # Multi-customer feedback (CSV)
```

---

## Telecom Keyword Categories
The analyzer detects keywords across five telecom-specific categories:

1. **Network**: bandwidth, latency, throughput, 5G, LTE, WiFi, router, firewall, VPN, DNS, etc.
2. **Service**: plan, subscription, billing, upgrade, cancellation, roaming, data cap, etc.
3. **Customer**: complaint, resolution, escalation, ticket, satisfaction, FCR, hold time, etc.
4. **Technical**: troubleshoot, firmware, configuration, provisioning, signal, coverage, antenna, etc.
5. **Compliance**: regulation, FCC, GDPR, privacy, encryption, SLA, KPI, audit, etc.

---

## Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open transcript file |
| `Ctrl+S` | Save transcript |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+R` | Run full analysis |
| `Ctrl+P` | Print |
| `Ctrl+F` | Find in transcript |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom |
| `Ctrl+Q` | Exit |

---

## Dependencies
| Library | Purpose |
|---------|---------|
| PySide6 | Qt GUI framework (LGPL license) |
| spaCy + en_core_web_sm | Named Entity Recognition, tokenization |
| NLTK | Sentiment analysis (VADER), stopwords, tokenization |
| TextBlob | Sentiment polarity and subjectivity |
| textacy | Advanced text analysis utilities |
| scikit-learn | Topic modeling (LDA), TF-IDF vectorization |
| pandas | Data handling and CSV export |
| matplotlib | Chart and visualization rendering |
| wordcloud | Word cloud generation |
| sumy | Text summarization (LSA, LexRank) |
| gensim | Topic modeling support |
| chardet | Automatic file encoding detection |

---

## Packaging as Executable
To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "TelecomAnalyzer" telecom_transcript_analyzer.py
```

The executable will be in the `dist/` directory.

---

## Author
Russ

## License
MIT License — See LICENSE file for details.

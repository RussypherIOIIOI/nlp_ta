#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telecom Transcript Analyzer 
A comprehensive NLP-powered transcript analysis tool for telecom professionals.
Built with PySide6 (Qt) for a professional desktop GUI.
License: MIT | Python: 3.11+
"""

import sys
import os
import re
import json
import csv
import ssl
import html as html_module
import logging
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Optional, Dict, List, Tuple, Any
from io import StringIO

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPlainTextEdit, QPushButton, QLabel, QFileDialog,
    QTabWidget, QSplitter, QStatusBar, QMenuBar, QMenu, QToolBar,
    QMessageBox, QProgressBar, QComboBox, QGroupBox, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QDialogButtonBox, QSpinBox, QCheckBox, QLineEdit, QFrame,
    QScrollArea, QSizePolicy, QTreeWidget, QTreeWidgetItem,
    QInputDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QSettings, QUrl
from PySide6.QtGui import (
    QFont, QColor, QPalette, QAction, QIcon, QTextCursor,
    QTextCharFormat, QPainter, QPixmap, QKeySequence,
    QDesktopServices, QTextDocument
)

import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as SumyTokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from wordcloud import WordCloud
import chardet

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('TelecomAnalyzer')

APP_NAME = "Telecom Transcript Analyzer"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "The Matrix Edition"
MAX_FILE_SIZE_MB = 100
SUPPORTED_EXTENSIONS = {'.txt', '.vtt', '.srt', '.csv'}

TELECOM_KEYWORDS = {
    'network': ['network', 'bandwidth', 'latency', 'throughput', 'uptime', 'downtime',
                'outage', 'connectivity', 'fiber', 'broadband', 'wireless', '5g', '4g',
                'lte', 'wifi', 'wi-fi', 'ethernet', 'router', 'modem', 'switch',
                'firewall', 'vpn', 'dns', 'ip', 'tcp', 'udp', 'packet', 'jitter'],
    'service': ['service', 'plan', 'subscription', 'billing', 'invoice', 'payment',
                'account', 'contract', 'upgrade', 'downgrade', 'cancellation', 'renewal',
                'activation', 'deactivation', 'porting', 'roaming', 'data cap',
                'unlimited', 'prepaid', 'postpaid', 'bundle'],
    'customer': ['customer', 'complaint', 'issue', 'problem', 'resolution', 'escalation',
                 'ticket', 'case', 'feedback', 'satisfaction', 'experience', 'support',
                 'helpdesk', 'call center', 'agent', 'representative', 'supervisor',
                 'hold time', 'wait time', 'first call resolution', 'fcr'],
    'technical': ['technical', 'troubleshoot', 'diagnose', 'repair', 'maintenance',
                  'firmware', 'software', 'hardware', 'configuration', 'provisioning',
                  'installation', 'signal', 'coverage', 'interference', 'spectrum',
                  'tower', 'cell site', 'base station', 'antenna', 'handover'],
    'compliance': ['compliance', 'regulation', 'fcc', 'gdpr', 'privacy', 'security',
                   'encryption', 'authentication', 'authorization', 'audit', 'sla',
                   'kpi', 'nda', 'terms of service', 'acceptable use']
}

MC = {
    'bg_primary': '#0D0D0D', 'bg_secondary': '#1A1A2E', 'bg_tertiary': '#16213E',
    'bg_panel': '#0F3460', 'text_primary': '#00FF41', 'text_secondary': '#00CC33',
    'text_dim': '#008F11', 'text_bright': '#39FF14', 'accent': '#00FF41',
    'accent_hover': '#39FF14', 'border': '#00FF41', 'border_dim': '#004D00',
    'error': '#FF0040', 'warning': '#FFD700', 'success': '#00FF41',
    'highlight': '#003300', 'selection_bg': '#004D00', 'selection_text': '#00FF41',
    'tab_active': '#1A3A1A', 'tab_inactive': '#0D0D0D', 'button_bg': '#003300',
    'button_hover': '#004D00', 'button_pressed': '#006600',
    'scrollbar': '#003300', 'scrollbar_handle': '#00FF41',
}


def get_matrix_stylesheet():
    c = MC
    ss = (
        "QMainWindow { background-color: " + c['bg_primary'] + "; color: " + c['text_primary'] + "; }"
        " QWidget { background-color: " + c['bg_primary'] + "; color: " + c['text_primary'] + ";"
        " font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; }"
        " QMenuBar { background-color: " + c['bg_secondary'] + "; color: " + c['text_primary'] + ";"
        " border-bottom: 1px solid " + c['border_dim'] + "; padding: 2px; }"
        " QMenuBar::item { background-color: transparent; padding: 6px 12px; border-radius: 3px; }"
        " QMenuBar::item:selected { background-color: " + c['button_hover'] + "; }"
        " QMenu { background-color: " + c['bg_secondary'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; padding: 4px; }"
        " QMenu::item { padding: 6px 30px 6px 20px; border-radius: 3px; }"
        " QMenu::item:selected { background-color: " + c['button_hover'] + "; color: " + c['text_bright'] + "; }"
        " QMenu::separator { height: 1px; background: " + c['border_dim'] + "; margin: 4px 10px; }"
        " QToolBar { background-color: " + c['bg_secondary'] + "; border-bottom: 1px solid " + c['border_dim'] + ";"
        " padding: 4px; spacing: 4px; }"
        " QTabWidget::pane { border: 1px solid " + c['border_dim'] + "; background-color: " + c['bg_primary'] + ";"
        " border-radius: 4px; }"
        " QTabBar::tab { background-color: " + c['tab_inactive'] + "; color: " + c['text_dim'] + ";"
        " border: 1px solid " + c['border_dim'] + "; padding: 8px 18px; margin-right: 2px;"
        " border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 12px; }"
        " QTabBar::tab:selected { background-color: " + c['tab_active'] + "; color: " + c['text_bright'] + ";"
        " border-bottom-color: " + c['tab_active'] + "; }"
        " QTabBar::tab:hover { background-color: " + c['button_hover'] + "; color: " + c['text_primary'] + "; }"
        " QPushButton { background-color: " + c['button_bg'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; padding: 8px 16px; border-radius: 4px;"
        " font-weight: bold; font-size: 12px; min-height: 20px; }"
        " QPushButton:hover { background-color: " + c['button_hover'] + "; color: " + c['text_bright'] + ";"
        " border-color: " + c['border'] + "; }"
        " QPushButton:pressed { background-color: " + c['button_pressed'] + "; }"
        " QPushButton:disabled { background-color: " + c['bg_secondary'] + "; color: " + c['text_dim'] + ";"
        " border-color: " + c['bg_secondary'] + "; }"
        " QTextEdit, QPlainTextEdit { background-color: " + c['bg_primary'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; border-radius: 4px; padding: 8px;"
        " font-family: 'Consolas', 'Courier New', monospace; font-size: 13px;"
        " selection-background-color: " + c['selection_bg'] + "; selection-color: " + c['selection_text'] + "; }"
        " QTextEdit:focus, QPlainTextEdit:focus { border-color: " + c['border'] + "; }"
        " QLabel { color: " + c['text_primary'] + "; font-size: 13px; background-color: transparent; }"
        " QGroupBox { border: 1px solid " + c['border_dim'] + "; border-radius: 6px; margin-top: 12px;"
        " padding-top: 16px; font-weight: bold; color: " + c['text_secondary'] + "; }"
        " QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left;"
        " padding: 2px 10px; color: " + c['text_bright'] + "; }"
        " QTableWidget { background-color: " + c['bg_primary'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; gridline-color: " + c['border_dim'] + "; font-size: 12px; }"
        " QTableWidget::item { padding: 4px; }"
        " QTableWidget::item:selected { background-color: " + c['selection_bg'] + "; color: " + c['selection_text'] + "; }"
        " QHeaderView::section { background-color: " + c['bg_secondary'] + "; color: " + c['text_bright'] + ";"
        " padding: 6px; border: 1px solid " + c['border_dim'] + "; font-weight: bold; font-size: 12px; }"
        " QTreeWidget { background-color: " + c['bg_primary'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; border-radius: 4px; }"
        " QTreeWidget::item { padding: 4px; }"
        " QTreeWidget::item:selected { background-color: " + c['selection_bg'] + "; color: " + c['selection_text'] + "; }"
        " QComboBox { background-color: " + c['button_bg'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; padding: 6px 12px; border-radius: 4px; }"
        " QComboBox:hover { border-color: " + c['border'] + "; }"
        " QComboBox::drop-down { border: none; width: 24px; }"
        " QComboBox QAbstractItemView { background-color: " + c['bg_secondary'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; selection-background-color: " + c['selection_bg'] + "; }"
        " QSpinBox { background-color: " + c['button_bg'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; padding: 4px; border-radius: 4px; }"
        " QLineEdit { background-color: " + c['bg_primary'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; padding: 6px; border-radius: 4px; font-size: 13px; }"
        " QLineEdit:focus { border-color: " + c['border'] + "; }"
        " QCheckBox { color: " + c['text_primary'] + "; spacing: 8px; font-size: 12px; }"
        " QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid " + c['border_dim'] + ";"
        " border-radius: 3px; background-color: " + c['bg_primary'] + "; }"
        " QCheckBox::indicator:checked { background-color: " + c['accent'] + "; border-color: " + c['accent'] + "; }"
        " QProgressBar { border: 1px solid " + c['border_dim'] + "; border-radius: 4px; text-align: center;"
        " color: " + c['text_primary'] + "; background-color: " + c['bg_primary'] + "; font-size: 11px; height: 20px; }"
        " QProgressBar::chunk { background-color: " + c['accent'] + "; border-radius: 3px; }"
        " QStatusBar { background-color: " + c['bg_secondary'] + "; color: " + c['text_dim'] + ";"
        " border-top: 1px solid " + c['border_dim'] + "; font-size: 12px; }"
        " QScrollBar:vertical { background-color: " + c['bg_primary'] + "; width: 12px; margin: 0; }"
        " QScrollBar::handle:vertical { background-color: " + c['scrollbar'] + "; min-height: 30px;"
        " border-radius: 6px; margin: 2px; }"
        " QScrollBar::handle:vertical:hover { background-color: " + c['scrollbar_handle'] + "; }"
        " QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        " QScrollBar:horizontal { background-color: " + c['bg_primary'] + "; height: 12px; margin: 0; }"
        " QScrollBar::handle:horizontal { background-color: " + c['scrollbar'] + "; min-width: 30px;"
        " border-radius: 6px; margin: 2px; }"
        " QScrollBar::handle:horizontal:hover { background-color: " + c['scrollbar_handle'] + "; }"
        " QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }"
        " QSplitter::handle { background-color: " + c['border_dim'] + "; }"
        " QSplitter::handle:horizontal { width: 3px; }"
        " QSplitter::handle:vertical { height: 3px; }"
        " QDialog { background-color: " + c['bg_primary'] + "; color: " + c['text_primary'] + "; }"
        " QFrame { background-color: transparent; }"
        " QListWidget { background-color: " + c['bg_primary'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border_dim'] + "; border-radius: 4px; }"
        " QListWidget::item { padding: 4px; }"
        " QListWidget::item:selected { background-color: " + c['selection_bg'] + "; color: " + c['selection_text'] + "; }"
        " QScrollArea { border: none; background-color: transparent; }"
        " QToolTip { background-color: " + c['bg_secondary'] + "; color: " + c['text_primary'] + ";"
        " border: 1px solid " + c['border'] + "; padding: 6px; font-size: 12px; }"
    )
    return ss


class SecurityUtils:
    @staticmethod
    def validate_file_path(file_path):
        try:
            path = Path(file_path).resolve()
            if not path.exists():
                return False, "File does not exist."
            if not path.is_file():
                return False, "Path is not a file."
            ext = path.suffix.lower()
            if ext not in SUPPORTED_EXTENSIONS:
                return False, "Unsupported file type: " + ext
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                return False, "File too large: " + str(round(size_mb, 1)) + "MB"
            return True, "Valid"
        except Exception as e:
            return False, "Path validation error: " + str(e)

    @staticmethod
    def sanitize_text(text):
        if not isinstance(text, str):
            return ""
        return text.replace('\x00', '')

    @staticmethod
    def safe_read_file(file_path):
        try:
            valid, msg = SecurityUtils.validate_file_path(file_path)
            if not valid:
                return False, msg
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8') or 'utf-8'
            try:
                text = raw_data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                text = raw_data.decode('utf-8', errors='replace')
            text = SecurityUtils.sanitize_text(text)
            return True, text
        except Exception as e:
            return False, "Error reading file: " + str(e)


class TranscriptParser:
    @staticmethod
    def parse_file(file_path):
        ext = Path(file_path).suffix.lower()
        success, content = SecurityUtils.safe_read_file(file_path)
        if not success:
            return {'success': False, 'error': content, 'raw_text': '', 'segments': []}
        parsers = {'.txt': TranscriptParser._parse_txt, '.vtt': TranscriptParser._parse_vtt,
                   '.srt': TranscriptParser._parse_srt, '.csv': TranscriptParser._parse_csv}
        parser = parsers.get(ext, TranscriptParser._parse_txt)
        try:
            result = parser(content)
            result['file_path'] = file_path
            result['file_name'] = Path(file_path).name
            result['file_size'] = Path(file_path).stat().st_size
            result['success'] = True
            return result
        except Exception as e:
            logger.error("Parse error: " + str(e))
            return {'success': False, 'error': str(e), 'raw_text': content, 'segments': [],
                    'file_path': file_path, 'file_name': Path(file_path).name}

    @staticmethod
    def _parse_txt(content):
        segments = []
        lines = content.strip().split('\n')
        simple_speaker = re.compile(r'^([A-Za-z][A-Za-z0-9_ ]{0,30})\s*:\s*(.+)$')
        current_speaker = "Unknown"
        for line in lines:
            line = line.strip()
            if not line:
                continue
            m = simple_speaker.match(line)
            if m:
                speaker = m.group(1).strip()
                text = m.group(2).strip()
                current_speaker = speaker
                segments.append({'speaker': speaker, 'text': text, 'timestamp': ''})
            else:
                segments.append({'speaker': current_speaker, 'text': line, 'timestamp': ''})
        raw_text = '\n'.join(seg['text'] for seg in segments)
        return {'raw_text': raw_text, 'segments': segments, 'format': 'txt'}

    @staticmethod
    def _parse_vtt(content):
        segments = []
        content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
        blocks = re.split(r'\n\n+', content.strip())
        ts_re = re.compile(r'(\d{2}:\d{2}[:.]\d{3})\s*-->\s*(\d{2}:\d{2}[:.]\d{3})')
        for block in blocks:
            blines = block.strip().split('\n')
            if not blines:
                continue
            timestamp = ""
            text_lines = []
            for bl in blines:
                tm = ts_re.search(bl)
                if tm:
                    timestamp = tm.group(1) + " --> " + tm.group(2)
                    continue
                if re.match(r'^\d+$', bl.strip()):
                    continue
                text_lines.append(bl)
            text = ' '.join(text_lines).strip()
            if not text:
                continue
            text = re.sub(r'<[^>]+>', '', text)
            speaker = "Unknown"
            segments.append({'speaker': speaker, 'text': text, 'timestamp': timestamp})
        raw_text = '\n'.join(seg['text'] for seg in segments)
        return {'raw_text': raw_text, 'segments': segments, 'format': 'vtt'}

    @staticmethod
    def _parse_srt(content):
        segments = []
        blocks = re.split(r'\n\n+', content.strip())
        ts_re = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})')
        for block in blocks:
            blines = block.strip().split('\n')
            if len(blines) < 2:
                continue
            timestamp = ""
            text_lines = []
            for bl in blines:
                if re.match(r'^\d+$', bl.strip()):
                    continue
                tm = ts_re.search(bl)
                if tm:
                    timestamp = tm.group(1) + " --> " + tm.group(2)
                    continue
                text_lines.append(bl.strip())
            text = ' '.join(text_lines)
            text = re.sub(r'<[^>]+>', '', text)
            if text:
                segments.append({'speaker': 'Unknown', 'text': text, 'timestamp': timestamp})
        raw_text = '\n'.join(seg['text'] for seg in segments)
        return {'raw_text': raw_text, 'segments': segments, 'format': 'srt'}

    @staticmethod
    def _parse_csv(content):
        segments = []
        reader = csv.DictReader(StringIO(content))
        fieldnames = reader.fieldnames or []
        fn_lower = [f.lower().strip() for f in fieldnames]
        speaker_col = text_col = time_col = None
        for i, fn in enumerate(fn_lower):
            if fn in ('speaker', 'name', 'agent', 'participant', 'from'):
                speaker_col = fieldnames[i]
            elif fn in ('text', 'message', 'content', 'transcript', 'utterance', 'body'):
                text_col = fieldnames[i]
            elif fn in ('time', 'timestamp', 'start', 'start_time', 'date'):
                time_col = fieldnames[i]
        if text_col is None and fieldnames:
            text_col = fieldnames[-1]
        for row in reader:
            speaker = row.get(speaker_col, 'Unknown') if speaker_col else 'Unknown'
            text = row.get(text_col, '') if text_col else ''
            timestamp = row.get(time_col, '') if time_col else ''
            if text.strip():
                segments.append({'speaker': speaker.strip() or 'Unknown', 'text': text.strip(),
                                 'timestamp': str(timestamp).strip()})
        raw_text = '\n'.join(seg['text'] for seg in segments)
        return {'raw_text': raw_text, 'segments': segments, 'format': 'csv'}


class TextPreprocessor:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text, options=None):
        if options is None:
            options = {'remove_timestamps': True, 'remove_speaker_ids': True,
                       'remove_filler_words': True, 'normalize_whitespace': True,
                       'lowercase': False, 'remove_special_chars': False}
        cleaned = text
        if options.get('remove_timestamps', True):
            cleaned = re.sub(r'\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d+)?', '', cleaned)
            cleaned = re.sub(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', '', cleaned)
        if options.get('remove_speaker_ids', True):
            cleaned = re.sub(r'^[A-Za-z][A-Za-z0-9_ ]{0,30}:\s*', '', cleaned, flags=re.MULTILINE)
        if options.get('remove_filler_words', True):
            fillers = r'\b(um|uh|er|ah|like|you know|i mean|basically|actually|literally|right)\b'
            cleaned = re.sub(fillers, '', cleaned, flags=re.IGNORECASE)
        if options.get('normalize_whitespace', True):
            cleaned = re.sub(r'\s+', ' ', cleaned)
            cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        if options.get('lowercase', False):
            cleaned = cleaned.lower()
        if options.get('remove_special_chars', False):
            cleaned = re.sub(r'[^\w\s.,!?;:\'-]', '', cleaned)
        return cleaned.strip()

    def tokenize(self, text):
        try:
            return word_tokenize(text)
        except LookupError:
            nltk.download('punkt_tab', quiet=True)
            return word_tokenize(text)

    def remove_stopwords(self, tokens):
        return [t for t in tokens if t.lower() not in self.stop_words and len(t) > 1]

    def get_sentences(self, text):
        try:
            return sent_tokenize(text)
        except LookupError:
            nltk.download('punkt_tab', quiet=True)
            return sent_tokenize(text)


class FallbackNER:
    """Regex + NLTK based NER fallback when spaCy is unavailable due to SSL or other issues."""

    PERSON_PATTERNS = [
        r'\b(?:Mr|Mrs|Ms|Dr|Prof|Sir|Madam)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?',
    ]
    ORG_PATTERNS = [
        r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,3}\s+(?:Inc|Corp|LLC|Ltd|Co|Group|Technologies|Telecom|Communications|Networks|Services|Solutions)\b\.?',
        r'\b(?:FCC|GDPR|NOC|ISP|AT&T|Verizon|T-Mobile|Comcast|Sprint)\b',
    ]
    LOC_PATTERNS = [
        r'\b(?:New York|Los Angeles|San Francisco|Palo Alto|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose|Austin|Jacksonville|Fort Worth|Columbus|Charlotte|Indianapolis|Seattle|Denver|Washington|Nashville|Oklahoma City|El Paso|Boston|Portland|Las Vegas|Memphis|Louisville|Baltimore|Milwaukee|Albuquerque|Tucson|Fresno|Sacramento|Mesa|Kansas City|Atlanta|Omaha|Colorado Springs|Raleigh|Long Beach|Virginia Beach|Miami|Oakland|Minneapolis|Tulsa|Tampa|Arlington|New Orleans)\b',
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s*,\s*[A-Z]{2}\b',
    ]
    DATE_PATTERNS = [
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b',
        r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
    ]

    def __init__(self):
        self.patterns = {
            'PERSON': [re.compile(p) for p in self.PERSON_PATTERNS],
            'ORG': [re.compile(p) for p in self.ORG_PATTERNS],
            'GPE': [re.compile(p) for p in self.LOC_PATTERNS],
            'DATE': [re.compile(p) for p in self.DATE_PATTERNS],
        }
        self.label_descriptions = {
            'PERSON': 'People, including fictional',
            'ORG': 'Companies, agencies, institutions',
            'GPE': 'Countries, cities, states',
            'DATE': 'Absolute or relative dates or periods',
            'MONEY': 'Monetary values',
            'PERCENT': 'Percentage',
            'TIME': 'Times smaller than a day',
            'CARDINAL': 'Numerals that do not fall under another type',
        }

    def extract(self, text):
        entities = []
        seen_texts = {}
        # Priority order: ORG > GPE > DATE > PERSON (more specific wins)
        priority = {'ORG': 1, 'GPE': 2, 'DATE': 3, 'PERSON': 4}
        ordered_labels = sorted(self.patterns.keys(), key=lambda l: priority.get(l, 99))
        for label in ordered_labels:
            for pattern in self.patterns[label]:
                for match in pattern.finditer(text):
                    ent_text = match.group().strip()
                    if len(ent_text) <= 1:
                        continue
                    text_lower = ent_text.lower()
                    existing_priority = priority.get(seen_texts.get(text_lower, ''), 99)
                    current_priority = priority.get(label, 99)
                    if text_lower not in seen_texts or current_priority < existing_priority:
                        if text_lower in seen_texts:
                            entities = [e for e in entities if e['text'].lower() != text_lower]
                        seen_texts[text_lower] = label
                        entities.append({
                            'text': ent_text, 'label': label,
                            'description': self.label_descriptions.get(label, label),
                            'start': match.start(), 'end': match.end()
                        })
        money_pattern = re.compile(r'\$[\d,]+(?:\.\d{2})?')
        for match in money_pattern.finditer(text):
            entities.append({'text': match.group(), 'label': 'MONEY',
                             'description': 'Monetary values', 'start': match.start(), 'end': match.end()})
        pct_pattern = re.compile(r'\b\d+(?:\.\d+)?%')
        for match in pct_pattern.finditer(text):
            entities.append({'text': match.group(), 'label': 'PERCENT',
                             'description': 'Percentage', 'start': match.start(), 'end': match.end()})
        return entities


def _try_load_spacy():
    """Attempt to load spaCy with multiple SSL workaround strategies."""
    # Strategy 1: Direct load (model already installed)
    try:
        nlp = spacy.load('en_core_web_sm')
        logger.info("spaCy model loaded successfully.")
        return nlp
    except OSError:
        logger.info("spaCy model not found locally. Attempting download...")

    # Strategy 2: Download with SSL verification disabled
    try:
        import urllib.request
        original_context = ssl._create_default_https_context
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'],
                timeout=120, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            nlp = spacy.load('en_core_web_sm')
            logger.info("spaCy model downloaded (SSL bypass) and loaded.")
            return nlp
        except Exception as e:
            logger.warning("SSL bypass download failed: " + str(e))
        finally:
            ssl._create_default_https_context = original_context
    except Exception as e:
        logger.warning("SSL context override failed: " + str(e))

    # Strategy 3: pip install with trusted hosts
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', 'en_core_web_sm',
             '--trusted-host', 'pypi.org',
             '--trusted-host', 'files.pythonhosted.org',
             '--trusted-host', 'github.com',
             '--trusted-host', 'objects.githubusercontent.com',
             '--no-cache-dir',
             '-f', 'https://github.com/explosion/spacy-models/releases/expanded_assets/en_core_web_sm-3.8.0'],
            timeout=120, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        nlp = spacy.load('en_core_web_sm')
        logger.info("spaCy model installed via pip (trusted hosts) and loaded.")
        return nlp
    except Exception as e:
        logger.warning("Pip trusted-host install failed: " + str(e))

    # Strategy 4: Direct URL download with SSL bypass
    try:
        import urllib.request
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        model_url = "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
        tmp_path = Path("/tmp/en_core_web_sm.whl")
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(model_url, str(tmp_path))
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', str(tmp_path)],
            timeout=60, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        tmp_path.unlink(missing_ok=True)
        nlp = spacy.load('en_core_web_sm')
        logger.info("spaCy model installed from direct download and loaded.")
        return nlp
    except Exception as e:
        logger.warning("Direct URL download failed: " + str(e))

    logger.warning("All spaCy download strategies failed. Using fallback NER.")
    return None


class NLPAnalysisEngine:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.vader = SentimentIntensityAnalyzer()
        self.nlp = _try_load_spacy()
        self.fallback_ner = FallbackNER() if self.nlp is None else None
        if self.nlp is None:
            logger.warning("Running with fallback NER (regex+NLTK). "
                           "For best results, install spaCy model: "
                           "python -m spacy download en_core_web_sm")

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        vader_scores = self.vader.polarity_scores(text)
        sentences = self.preprocessor.get_sentences(text)
        sentence_sentiments = []
        for sent in sentences[:500]:
            tb = TextBlob(sent)
            vs = self.vader.polarity_scores(sent)
            sentence_sentiments.append({
                'text': sent[:200], 'textblob_polarity': round(tb.sentiment.polarity, 4),
                'textblob_subjectivity': round(tb.sentiment.subjectivity, 4),
                'vader_compound': round(vs['compound'], 4), 'vader_pos': round(vs['pos'], 4),
                'vader_neg': round(vs['neg'], 4), 'vader_neu': round(vs['neu'], 4)})
        compound = vader_scores['compound']
        overall = 'Positive' if compound >= 0.05 else ('Negative' if compound <= -0.05 else 'Neutral')
        return {
            'overall_sentiment': overall,
            'textblob': {'polarity': round(blob.sentiment.polarity, 4),
                         'subjectivity': round(blob.sentiment.subjectivity, 4)},
            'vader': {'compound': round(vader_scores['compound'], 4),
                      'positive': round(vader_scores['pos'], 4),
                      'negative': round(vader_scores['neg'], 4),
                      'neutral': round(vader_scores['neu'], 4)},
            'sentence_sentiments': sentence_sentiments, 'sentence_count': len(sentences)}

    def extract_keywords(self, text, top_n=30):
        tokens = self.preprocessor.tokenize(text)
        filtered = self.preprocessor.remove_stopwords(tokens)
        filtered_lower = [t.lower() for t in filtered if t.isalpha()]
        word_freq = Counter(filtered_lower)
        sentences = self.preprocessor.get_sentences(text)
        tfidf_top = []
        if len(sentences) > 1:
            try:
                tfidf = TfidfVectorizer(max_features=200, stop_words='english', ngram_range=(1, 1), min_df=1)
                tfidf_matrix = tfidf.fit_transform(sentences)
                feature_names = tfidf.get_feature_names_out()
                scores = tfidf_matrix.sum(axis=0).A1
                tfidf_scores = dict(zip(feature_names, scores))
                tfidf_top = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            except Exception:
                pass
        bigrams = list(nltk.ngrams(filtered_lower, 2))
        trigrams = list(nltk.ngrams(filtered_lower, 3))
        bigram_freq = Counter([' '.join(bg) for bg in bigrams])
        trigram_freq = Counter([' '.join(tg) for tg in trigrams])
        return {'word_frequency': word_freq.most_common(top_n), 'tfidf_keywords': tfidf_top,
                'bigrams': bigram_freq.most_common(top_n), 'trigrams': trigram_freq.most_common(top_n),
                'total_words': len(tokens), 'unique_words': len(set(filtered_lower)),
                'vocabulary_richness': round(len(set(filtered_lower)) / max(len(filtered_lower), 1), 4)}

    def extract_entities(self, text):
        max_chars = 100000
        truncated = text[:max_chars] if len(text) > max_chars else text

        if self.nlp is not None:
            # Primary: spaCy NER
            try:
                doc = self.nlp(truncated)
                entities = []
                entity_types = defaultdict(list)
                for ent in doc.ents:
                    entities.append({'text': ent.text, 'label': ent.label_,
                                     'description': spacy.explain(ent.label_) or ent.label_,
                                     'start': ent.start_char, 'end': ent.end_char})
                    entity_types[ent.label_].append(ent.text)
                entity_summary = {}
                for label, texts in entity_types.items():
                    counter = Counter(texts)
                    entity_summary[label] = {'count': len(texts), 'unique': len(counter),
                                             'top_entities': counter.most_common(10),
                                             'description': spacy.explain(label) or label}
                return {'entities': entities[:500], 'entity_summary': entity_summary,
                        'total_entities': len(entities), 'engine': 'spaCy'}
            except Exception as e:
                logger.error("spaCy NER failed, falling back: " + str(e))

        # Fallback: Regex + NLTK NER
        if self.fallback_ner is None:
            self.fallback_ner = FallbackNER()
        entities = self.fallback_ner.extract(truncated)
        entity_types = defaultdict(list)
        for ent in entities:
            entity_types[ent['label']].append(ent['text'])
        entity_summary = {}
        for label, texts in entity_types.items():
            counter = Counter(texts)
            desc = self.fallback_ner.label_descriptions.get(label, label)
            entity_summary[label] = {'count': len(texts), 'unique': len(counter),
                                     'top_entities': counter.most_common(10),
                                     'description': desc}
        return {'entities': entities[:500], 'entity_summary': entity_summary,
                'total_entities': len(entities), 'engine': 'fallback (regex+NLTK)'}

    def analyze_speakers(self, segments):
        if not segments:
            return {'speakers': {}, 'total_speakers': 0, 'total_utterances': 0, 'total_words': 0}
        speaker_data = defaultdict(lambda: {'utterances': [], 'word_count': 0, 'char_count': 0,
                                            'sentiment_scores': [], 'utterance_count': 0})
        for seg in segments:
            speaker = seg.get('speaker', 'Unknown')
            text = seg.get('text', '')
            speaker_data[speaker]['utterances'].append(text)
            speaker_data[speaker]['word_count'] += len(text.split())
            speaker_data[speaker]['char_count'] += len(text)
            speaker_data[speaker]['utterance_count'] += 1
            vs = self.vader.polarity_scores(text)
            speaker_data[speaker]['sentiment_scores'].append(vs['compound'])
        speaker_stats = {}
        total_words = sum(d['word_count'] for d in speaker_data.values())
        for speaker, data in speaker_data.items():
            avg_s = float(np.mean(data['sentiment_scores'])) if data['sentiment_scores'] else 0.0
            speaker_stats[speaker] = {
                'utterance_count': data['utterance_count'], 'word_count': data['word_count'],
                'char_count': data['char_count'],
                'avg_words_per_utterance': round(data['word_count'] / max(data['utterance_count'], 1), 1),
                'talk_share_pct': round(data['word_count'] / max(total_words, 1) * 100, 1),
                'avg_sentiment': round(avg_s, 4),
                'sentiment_label': 'Positive' if avg_s > 0.05 else ('Negative' if avg_s < -0.05 else 'Neutral')}
        return {'speakers': speaker_stats, 'total_speakers': len(speaker_stats),
                'total_utterances': sum(s['utterance_count'] for s in speaker_stats.values()),
                'total_words': total_words}

    def generate_summary(self, text, sentence_count=5):
        if not text.strip():
            return {'lsa_summary': '', 'lexrank_summary': '', 'sentence_count': 0}
        try:
            parser = PlaintextParser.from_string(text, SumyTokenizer("english"))
            stemmer = Stemmer("english")
            lsa = LsaSummarizer(stemmer)
            lsa.stop_words = get_stop_words("english")
            lsa_sentences = lsa(parser.document, sentence_count)
            lsa_summary = ' '.join(str(s) for s in lsa_sentences)
            lexrank = LexRankSummarizer(stemmer)
            lexrank.stop_words = get_stop_words("english")
            lexrank_sentences = lexrank(parser.document, sentence_count)
            lexrank_summary = ' '.join(str(s) for s in lexrank_sentences)
        except Exception as e:
            logger.error("Summarization error: " + str(e))
            sentences = self.preprocessor.get_sentences(text)
            lsa_summary = ' '.join(sentences[:sentence_count])
            lexrank_summary = lsa_summary
        return {'lsa_summary': lsa_summary, 'lexrank_summary': lexrank_summary, 'sentence_count': sentence_count}

    def topic_modeling(self, text, n_topics=5, n_words=10):
        sentences = self.preprocessor.get_sentences(text)
        if len(sentences) < 3:
            return {'topics': [], 'method': 'insufficient_data'}
        try:
            n_topics = min(n_topics, len(sentences))
            vectorizer = CountVectorizer(max_features=1000, stop_words='english', min_df=1, max_df=0.95)
            doc_term = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=20, learning_method='online')
            lda.fit(doc_term)
            topics = []
            for idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-n_words:][::-1]
                top_words = [(feature_names[i], round(float(topic[i]), 4)) for i in top_indices]
                topics.append({'topic_id': idx + 1, 'words': top_words, 'label': "Topic " + str(idx + 1)})
            return {'topics': topics, 'method': 'LDA', 'n_topics': n_topics}
        except Exception as e:
            logger.error("Topic modeling error: " + str(e))
            return {'topics': [], 'method': 'error', 'error': str(e)}

    def telecom_analysis(self, text):
        text_lower = text.lower()
        category_hits = {}
        all_hits = []
        for category, keywords in TELECOM_KEYWORDS.items():
            hits = []
            for kw in keywords:
                kw_lower = kw.lower()
                count = len(re.findall(r'\b' + re.escape(kw_lower) + r'\b', text_lower))
                if count > 0:
                    hits.append({'keyword': kw, 'count': count})
                    all_hits.append({'keyword': kw, 'category': category, 'count': count})
            category_hits[category] = {'hits': sorted(hits, key=lambda x: x['count'], reverse=True),
                                       'total_mentions': sum(h['count'] for h in hits),
                                       'unique_keywords': len(hits)}
        all_hits.sort(key=lambda x: x['count'], reverse=True)
        return {'categories': category_hits, 'top_telecom_keywords': all_hits[:30],
                'total_telecom_mentions': sum(c['total_mentions'] for c in category_hits.values())}


class AnalysisWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, engine, text, segments, options=None):
        super().__init__()
        self.engine = engine
        self.text = text
        self.segments = segments

    def run(self):
        try:
            results = {}
            self.progress.emit(5, "Preprocessing text...")
            cleaned = self.engine.preprocessor.clean_text(self.text)
            results['cleaned_text'] = cleaned
            results['stats'] = {'original_length': len(self.text), 'cleaned_length': len(cleaned),
                                'word_count': len(cleaned.split()),
                                'sentence_count': len(self.engine.preprocessor.get_sentences(cleaned)),
                                'segment_count': len(self.segments)}
            self.progress.emit(15, "Analyzing sentiment...")
            results['sentiment'] = self.engine.analyze_sentiment(cleaned)
            self.progress.emit(35, "Extracting keywords...")
            results['keywords'] = self.engine.extract_keywords(cleaned)
            self.progress.emit(50, "Named Entity Recognition...")
            results['entities'] = self.engine.extract_entities(cleaned)
            self.progress.emit(65, "Analyzing speakers...")
            results['speakers'] = self.engine.analyze_speakers(self.segments)
            self.progress.emit(75, "Generating summary...")
            results['summary'] = self.engine.generate_summary(cleaned)
            self.progress.emit(85, "Topic modeling...")
            results['topics'] = self.engine.topic_modeling(cleaned)
            self.progress.emit(92, "Telecom analysis...")
            results['telecom'] = self.engine.telecom_analysis(cleaned)
            self.progress.emit(100, "Analysis complete!")
            results['timestamp'] = datetime.now().isoformat()
            self.finished.emit(results)
        except Exception as e:
            logger.error("Analysis error: " + traceback.format_exc())
            self.error.emit(str(e))


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#0D0D0D')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def clear(self):
        self.fig.clear()
        self.draw()


class VizGen:
    @staticmethod
    def style_ax(ax):
        ax.set_facecolor('#0D0D0D')
        ax.tick_params(colors='#00FF41', labelsize=9)
        ax.xaxis.label.set_color('#00FF41')
        ax.yaxis.label.set_color('#00FF41')
        ax.title.set_color('#39FF14')
        ax.title.set_fontsize(13)
        ax.title.set_fontweight('bold')
        for spine in ax.spines.values():
            spine.set_color('#004D00')

    @staticmethod
    def gen_wordcloud(canvas, word_freq):
        canvas.clear()
        if not word_freq:
            return
        freq_dict = dict(word_freq)
        def green_func(*a, **kw):
            return "#{:02x}{:02x}{:02x}".format(np.random.randint(0, 80), np.random.randint(180, 255), np.random.randint(0, 80))
        wc = WordCloud(width=800, height=400, background_color='#0D0D0D', color_func=green_func,
                       max_words=100, prefer_horizontal=0.7, min_font_size=8).generate_from_frequencies(freq_dict)
        ax = canvas.fig.add_subplot(111)
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Word Cloud', color='#39FF14', fontsize=14, fontweight='bold', pad=10)
        canvas.fig.tight_layout()
        canvas.draw()

    @staticmethod
    def gen_sentiment(canvas, sd):
        canvas.clear()
        if not sd:
            return
        fig = canvas.fig
        ax1 = fig.add_subplot(121)
        vader = sd.get('vader', {})
        labels = ['Positive', 'Negative', 'Neutral']
        values = [vader.get('positive', 0), vader.get('negative', 0), vader.get('neutral', 0)]
        colors = ['#00FF41', '#FF0040', '#FFD700']
        bars = ax1.bar(labels, values, color=colors, edgecolor='#004D00', linewidth=1)
        VizGen.style_ax(ax1)
        ax1.set_title('VADER Sentiment Distribution', pad=10)
        ax1.set_ylabel('Score')
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.01,
                     str(round(val, 3)), ha='center', va='bottom', color='#00FF41', fontsize=10)
        ax2 = fig.add_subplot(122)
        ss = sd.get('sentence_sentiments', [])
        if ss:
            compounds = [s['vader_compound'] for s in ss[:100]]
            x = range(len(compounds))
            cl = ['#00FF41' if c >= 0.05 else '#FF0040' if c <= -0.05 else '#FFD700' for c in compounds]
            ax2.scatter(x, compounds, c=cl, s=15, alpha=0.7, zorder=5)
            ax2.axhline(y=0, color='#004D00', linestyle='--', alpha=0.5)
            if len(compounds) > 3:
                w = min(5, len(compounds))
                ma = np.convolve(compounds, np.ones(w) / w, mode='valid')
                ax2.plot(range(w - 1, len(compounds)), ma, color='#39FF14', linewidth=2, alpha=0.8, label='Moving Avg')
                ax2.legend(facecolor='#0D0D0D', edgecolor='#004D00', labelcolor='#00FF41')
        VizGen.style_ax(ax2)
        ax2.set_title('Sentiment Trend', pad=10)
        ax2.set_xlabel('Sentence Index')
        ax2.set_ylabel('Compound Score')
        fig.tight_layout(pad=2.0)
        canvas.draw()

    @staticmethod
    def gen_keywords(canvas, kd):
        canvas.clear()
        if not kd:
            return
        wf = kd.get('word_frequency', [])[:15]
        if not wf:
            return
        words, counts = zip(*wf)
        ax = canvas.fig.add_subplot(111)
        y_pos = range(len(words))
        bars = ax.barh(y_pos, counts, color='#00FF41', edgecolor='#004D00', alpha=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(words)
        ax.invert_yaxis()
        VizGen.style_ax(ax)
        ax.set_title('Top Keywords by Frequency', pad=10)
        ax.set_xlabel('Frequency')
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2.,
                    str(count), ha='left', va='center', color='#00FF41', fontsize=9)
        canvas.fig.tight_layout()
        canvas.draw()

    @staticmethod
    def gen_speakers(canvas, sd):
        canvas.clear()
        if not sd or not sd.get('speakers'):
            return
        speakers = sd['speakers']
        names = list(speakers.keys())
        if not names:
            return
        fig = canvas.fig
        ax1 = fig.add_subplot(121)
        shares = [speakers[n]['talk_share_pct'] for n in names]
        gs = []
        for i in range(len(names)):
            gs.append("#{:02x}{:02x}{:02x}".format(max(0, 50 - i * 10), min(255, 180 + i * 15), max(0, 50 - i * 10)))
        wedges, texts, autotexts = ax1.pie(shares, labels=names, autopct='%1.1f%%', colors=gs[:len(names)],
                                           textprops={'color': '#00FF41', 'fontsize': 9},
                                           wedgeprops={'edgecolor': '#004D00', 'linewidth': 1})
        for t in autotexts:
            t.set_color('#0D0D0D')
            t.set_fontweight('bold')
        ax1.set_title('Talk Share', color='#39FF14', fontsize=13, fontweight='bold')
        ax2 = fig.add_subplot(122)
        sents = [speakers[n]['avg_sentiment'] for n in names]
        bc = ['#00FF41' if s >= 0.05 else '#FF0040' if s <= -0.05 else '#FFD700' for s in sents]
        ax2.bar(names, sents, color=bc, edgecolor='#004D00')
        ax2.axhline(y=0, color='#004D00', linestyle='--', alpha=0.5)
        VizGen.style_ax(ax2)
        ax2.set_title('Speaker Sentiment', pad=10)
        ax2.set_ylabel('Avg. Compound')
        ax2.tick_params(axis='x', rotation=30)
        fig.tight_layout(pad=2.0)
        canvas.draw()

    @staticmethod
    def gen_telecom(canvas, td):
        canvas.clear()
        if not td or not td.get('categories'):
            return
        fig = canvas.fig
        cats = td['categories']
        cn = list(cats.keys())
        cm = [cats[c]['total_mentions'] for c in cn]
        if sum(cm) == 0:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No telecom keywords detected', ha='center', va='center',
                    color='#00FF41', fontsize=14, transform=ax.transAxes)
            ax.set_facecolor('#0D0D0D')
            ax.axis('off')
            canvas.draw()
            return
        ax1 = fig.add_subplot(121)
        gs = ['#00FF41', '#00CC33', '#009926', '#006619', '#00330D']
        bars = ax1.bar(cn, cm, color=gs[:len(cn)], edgecolor='#004D00')
        VizGen.style_ax(ax1)
        ax1.set_title('Telecom Categories', pad=10)
        ax1.set_ylabel('Mentions')
        ax1.tick_params(axis='x', rotation=30)
        for bar, val in zip(bars, cm):
            if val > 0:
                ax1.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.3,
                         str(val), ha='center', va='bottom', color='#00FF41', fontsize=10)
        ax2 = fig.add_subplot(122)
        tkw = td.get('top_telecom_keywords', [])[:10]
        if tkw:
            kn = [k['keyword'] for k in tkw]
            kc = [k['count'] for k in tkw]
            yp = range(len(kn))
            ax2.barh(yp, kc, color='#00FF41', edgecolor='#004D00', alpha=0.8)
            ax2.set_yticks(yp)
            ax2.set_yticklabels(kn)
            ax2.invert_yaxis()
        VizGen.style_ax(ax2)
        ax2.set_title('Top Telecom Keywords', pad=10)
        ax2.set_xlabel('Count')
        fig.tight_layout(pad=2.0)
        canvas.draw()

    @staticmethod
    def gen_entities(canvas, ed):
        canvas.clear()
        if not ed or not ed.get('entity_summary'):
            return
        summary = ed['entity_summary']
        if not summary:
            return
        ax = canvas.fig.add_subplot(111)
        labels = list(summary.keys())
        counts = [summary[l]['count'] for l in labels]
        descs = [summary[l]['description'] for l in labels]
        dl = [l + "\n(" + d + ")" for l, d in zip(labels, descs)]
        gs = []
        for i in range(len(labels)):
            gs.append("#{:02x}{:02x}{:02x}".format(max(0, 30 + i * 8), min(255, 150 + i * 12), max(0, 30 + i * 8)))
        bars = ax.bar(range(len(labels)), counts, color=gs[:len(labels)], edgecolor='#004D00')
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(dl, fontsize=8)
        VizGen.style_ax(ax)
        ax.set_title('Named Entity Types', pad=10)
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=45)
        for bar, val in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.3,
                    str(val), ha='center', va='bottom', color='#00FF41', fontsize=9)
        canvas.fig.tight_layout()
        canvas.draw()


class TelecomAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME + " v" + APP_VERSION + " - " + APP_SUBTITLE)
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.current_file = None
        self.transcript_data = None
        self.analysis_results = None
        self.worker = None
        self.engine = None
        self.is_modified = False
        self.settings = QSettings('NinjaTech', 'TelecomAnalyzer')
        self._init_engine()
        self._init_ui()
        self._init_menus()
        self._init_toolbar()
        self._init_statusbar()
        self.setStyleSheet(get_matrix_stylesheet())
        geo = self.settings.value('geometry')
        if geo:
            self.restoreGeometry(geo)
        self.statusBar().showMessage("System initialized. Ready to analyze transcripts.")

    def _init_engine(self):
        try:
            self.engine = NLPAnalysisEngine()
            logger.info("NLP engine initialized.")
            if self.engine.nlp is None:
                QMessageBox.warning(
                    self, "spaCy Model Unavailable",
                    "The spaCy NER model could not be loaded (likely due to SSL/network issues).\n\n"
                    "The application will use a fallback NER engine (regex + NLTK patterns).\n"
                    "All other features (sentiment, keywords, topics, etc.) work normally.\n\n"
                    "To fix, run one of these commands:\n\n"
                    "  Option 1 (standard):\n"
                    "    python -m spacy download en_core_web_sm\n\n"
                    "  Option 2 (SSL bypass):\n"
                    "    pip install en_core_web_sm --trusted-host pypi.org "
                    "--trusted-host files.pythonhosted.org\n\n"
                    "  Option 3 (direct URL):\n"
                    "    pip install https://github.com/explosion/spacy-models/"
                    "releases/download/en_core_web_sm-3.8.0/"
                    "en_core_web_sm-3.8.0-py3-none-any.whl\n\n"
                    "  Option 4 (disable SSL verify):\n"
                    "    pip install --trusted-host pypi.org --trusted-host "
                    "files.pythonhosted.org en-core-web-sm -f "
                    "https://github.com/explosion/spacy-models/releases"
                )
        except Exception as e:
            logger.error("Engine init error: " + str(e))
            QMessageBox.critical(self, "Init Error", "Failed to init NLP engine:\n" + str(e))

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        ml = QVBoxLayout(central)
        ml.setContentsMargins(6, 6, 6, 6)
        ml.setSpacing(4)
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("QFrame { background-color: " + MC['bg_secondary'] + "; border: 1px solid " + MC['border_dim'] + "; border-radius: 6px; }")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 4, 16, 4)
        tl = QLabel(":: " + APP_NAME + " ::")
        tl.setStyleSheet("font-size: 20px; font-weight: bold; color: " + MC['text_bright'] + "; background-color: transparent;")
        hl.addWidget(tl)
        sl = QLabel("[ " + APP_SUBTITLE + " ]")
        sl.setStyleSheet("font-size: 14px; font-style: italic; color: " + MC['text_dim'] + "; background-color: transparent;")
        hl.addWidget(sl)
        hl.addStretch()
        self.btn_load = QPushButton("Load Transcript")
        self.btn_load.clicked.connect(self.load_transcript)
        hl.addWidget(self.btn_load)
        self.btn_format = QPushButton("Format/Pipe")
        self.btn_format.setToolTip("Parse transcript into pipe-delimited speaker format")
        self.btn_format.clicked.connect(self._format_transcript)
        hl.addWidget(self.btn_format)
        self.btn_analyze = QPushButton("Analyze")
        self.btn_analyze.clicked.connect(self.run_analysis)
        self.btn_analyze.setEnabled(False)
        hl.addWidget(self.btn_analyze)
        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.export_results)
        self.btn_export.setEnabled(False)
        hl.addWidget(self.btn_export)
        ml.addWidget(header)
        self.main_splitter = QSplitter(Qt.Horizontal)
        left = self._create_left_panel()
        self.main_splitter.addWidget(left)
        right = self._create_right_panel()
        self.main_splitter.addWidget(right)
        self.main_splitter.setSizes([500, 900])
        ml.addWidget(self.main_splitter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        ml.addWidget(self.progress_bar)

    def _create_left_panel(self):
        panel = QWidget()
        lo = QVBoxLayout(panel)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(4)
        self.file_info_label = QLabel("No file loaded")
        self.file_info_label.setStyleSheet("padding: 6px; font-size: 11px; color: " + MC['text_dim'] + "; border: 1px solid " + MC['border_dim'] + "; border-radius: 4px;")
        lo.addWidget(self.file_info_label)
        self.transcript_tabs = QTabWidget()
        self.raw_text_edit = QPlainTextEdit()
        self.raw_text_edit.setPlaceholderText("Load a transcript file to begin analysis...\n\nSupported: .txt, .vtt, .srt, .csv\n\nYou can also paste text directly here.")
        self.raw_text_edit.textChanged.connect(self._on_text_changed)
        self.transcript_tabs.addTab(self.raw_text_edit, "Raw Transcript")
        self.formatted_view = QTextEdit()
        self.formatted_view.setReadOnly(True)
        self.formatted_view.setPlaceholderText("Formatted pipe-delimited view appears after loading a transcript...\n\nExample:\n|Agent| Thank you for calling...\n|Caller| Hi, I have an issue with...")
        self.transcript_tabs.addTab(self.formatted_view, "Formatted View")
        self.cleaned_text_edit = QPlainTextEdit()
        self.cleaned_text_edit.setReadOnly(True)
        self.cleaned_text_edit.setPlaceholderText("Cleaned text appears after analysis...")
        self.transcript_tabs.addTab(self.cleaned_text_edit, "Cleaned Text")
        self.segments_table = QTableWidget()
        self.segments_table.setColumnCount(3)
        self.segments_table.setHorizontalHeaderLabels(['Speaker', 'Timestamp', 'Text'])
        self.segments_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.segments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.segments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.segments_table.setAlternatingRowColors(True)
        self.segments_table.setStyleSheet("QTableWidget::item:alternate { background-color: " + MC['bg_secondary'] + "; }")
        self.transcript_tabs.addTab(self.segments_table, "Segments")
        lo.addWidget(self.transcript_tabs)
        slo = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search transcript...")
        self.search_input.returnPressed.connect(self._search_text)
        slo.addWidget(self.search_input)
        bf = QPushButton("Find")
        bf.clicked.connect(self._search_text)
        bf.setFixedWidth(60)
        slo.addWidget(bf)
        bc = QPushButton("Clear")
        bc.clicked.connect(self._clear_search)
        bc.setFixedWidth(60)
        slo.addWidget(bc)
        lo.addLayout(slo)
        return panel

    def _create_right_panel(self):
        panel = QWidget()
        lo = QVBoxLayout(panel)
        lo.setContentsMargins(0, 0, 0, 0)
        self.analysis_tabs = QTabWidget()
        # Overview
        ow = QWidget()
        owl = QVBoxLayout(ow)
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setPlaceholderText("Analysis overview appears here...")
        owl.addWidget(self.overview_text)
        self.analysis_tabs.addTab(ow, "Overview")
        # Sentiment
        sw = QWidget()
        swl = QVBoxLayout(sw)
        ss = QSplitter(Qt.Vertical)
        self.sentiment_canvas = MatplotlibCanvas(sw, width=10, height=4)
        ss.addWidget(self.sentiment_canvas)
        self.sentiment_table = QTableWidget()
        self.sentiment_table.setColumnCount(5)
        self.sentiment_table.setHorizontalHeaderLabels(['Sentence', 'TB Polarity', 'TB Subjectivity', 'VADER Compound', 'Label'])
        self.sentiment_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        ss.addWidget(self.sentiment_table)
        ss.setSizes([400, 300])
        swl.addWidget(ss)
        self.analysis_tabs.addTab(sw, "Sentiment")
        # Keywords
        kw = QWidget()
        kwl = QVBoxLayout(kw)
        ks = QSplitter(Qt.Vertical)
        self.wordcloud_canvas = MatplotlibCanvas(kw, width=10, height=4)
        ks.addWidget(self.wordcloud_canvas)
        kt = QTabWidget()
        self.word_freq_table = QTableWidget()
        self.word_freq_table.setColumnCount(2)
        self.word_freq_table.setHorizontalHeaderLabels(['Word', 'Frequency'])
        self.word_freq_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        kt.addTab(self.word_freq_table, "Words")
        self.tfidf_table = QTableWidget()
        self.tfidf_table.setColumnCount(2)
        self.tfidf_table.setHorizontalHeaderLabels(['Keyword', 'TF-IDF Score'])
        self.tfidf_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        kt.addTab(self.tfidf_table, "TF-IDF")
        self.bigram_table = QTableWidget()
        self.bigram_table.setColumnCount(2)
        self.bigram_table.setHorizontalHeaderLabels(['Bigram', 'Frequency'])
        self.bigram_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        kt.addTab(self.bigram_table, "Bigrams")
        self.trigram_table = QTableWidget()
        self.trigram_table.setColumnCount(2)
        self.trigram_table.setHorizontalHeaderLabels(['Trigram', 'Frequency'])
        self.trigram_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        kt.addTab(self.trigram_table, "Trigrams")
        ks.addWidget(kt)
        ks.setSizes([350, 350])
        kwl.addWidget(ks)
        self.analysis_tabs.addTab(kw, "Keywords")
        # Entities
        ew = QWidget()
        ewl = QVBoxLayout(ew)
        es = QSplitter(Qt.Vertical)
        self.entity_canvas = MatplotlibCanvas(ew, width=10, height=4)
        es.addWidget(self.entity_canvas)
        et = QTabWidget()
        self.entity_tree = QTreeWidget()
        self.entity_tree.setHeaderLabels(['Entity Type', 'Count', 'Description'])
        self.entity_tree.setColumnWidth(0, 200)
        self.entity_tree.setColumnWidth(1, 80)
        et.addTab(self.entity_tree, "Summary")
        self.entity_table = QTableWidget()
        self.entity_table.setColumnCount(3)
        self.entity_table.setHorizontalHeaderLabels(['Entity', 'Type', 'Description'])
        self.entity_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        et.addTab(self.entity_table, "All Entities")
        es.addWidget(et)
        es.setSizes([350, 350])
        ewl.addWidget(es)
        self.analysis_tabs.addTab(ew, "Entities")
        # Speakers
        spw = QWidget()
        spwl = QVBoxLayout(spw)
        sps = QSplitter(Qt.Vertical)
        self.speaker_canvas = MatplotlibCanvas(spw, width=10, height=4)
        sps.addWidget(self.speaker_canvas)
        self.speaker_table = QTableWidget()
        self.speaker_table.setColumnCount(7)
        self.speaker_table.setHorizontalHeaderLabels(['Speaker', 'Utterances', 'Words', 'Avg W/U', 'Talk%', 'Avg Sent', 'Label'])
        self.speaker_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        sps.addWidget(self.speaker_table)
        sps.setSizes([400, 300])
        spwl.addWidget(sps)
        self.analysis_tabs.addTab(spw, "Speakers")
        # Summary
        smw = QWidget()
        smwl = QVBoxLayout(smw)
        scl = QHBoxLayout()
        scl.addWidget(QLabel("Summary sentences:"))
        self.summary_spin = QSpinBox()
        self.summary_spin.setRange(1, 20)
        self.summary_spin.setValue(5)
        scl.addWidget(self.summary_spin)
        brs = QPushButton("Re-summarize")
        brs.clicked.connect(self._resummarize)
        scl.addWidget(brs)
        scl.addStretch()
        smwl.addLayout(scl)
        lg = QGroupBox("LSA Summary")
        lgl = QVBoxLayout(lg)
        self.lsa_text = QTextEdit()
        self.lsa_text.setReadOnly(True)
        self.lsa_text.setMaximumHeight(200)
        lgl.addWidget(self.lsa_text)
        smwl.addWidget(lg)
        lxg = QGroupBox("LexRank Summary")
        lxgl = QVBoxLayout(lxg)
        self.lexrank_text = QTextEdit()
        self.lexrank_text.setReadOnly(True)
        self.lexrank_text.setMaximumHeight(200)
        lxgl.addWidget(self.lexrank_text)
        smwl.addWidget(lxg)
        smwl.addStretch()
        self.analysis_tabs.addTab(smw, "Summary")
        # Topics
        tw = QWidget()
        twl = QVBoxLayout(tw)
        tcl = QHBoxLayout()
        tcl.addWidget(QLabel("Topics:"))
        self.topics_spin = QSpinBox()
        self.topics_spin.setRange(2, 15)
        self.topics_spin.setValue(5)
        tcl.addWidget(self.topics_spin)
        brt = QPushButton("Re-model")
        brt.clicked.connect(self._remodel_topics)
        tcl.addWidget(brt)
        tcl.addStretch()
        twl.addLayout(tcl)
        self.topics_tree = QTreeWidget()
        self.topics_tree.setHeaderLabels(['Topic / Word', 'Weight'])
        self.topics_tree.setColumnWidth(0, 300)
        twl.addWidget(self.topics_tree)
        self.analysis_tabs.addTab(tw, "Topics")
        # Telecom
        tcw = QWidget()
        tcwl = QVBoxLayout(tcw)
        tcs = QSplitter(Qt.Vertical)
        self.telecom_canvas = MatplotlibCanvas(tcw, width=10, height=4)
        tcs.addWidget(self.telecom_canvas)
        tct = QTabWidget()
        self.telecom_tree = QTreeWidget()
        self.telecom_tree.setHeaderLabels(['Category / Keyword', 'Count'])
        self.telecom_tree.setColumnWidth(0, 300)
        tct.addTab(self.telecom_tree, "Categories")
        self.telecom_kw_table = QTableWidget()
        self.telecom_kw_table.setColumnCount(3)
        self.telecom_kw_table.setHorizontalHeaderLabels(['Keyword', 'Category', 'Count'])
        self.telecom_kw_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tct.addTab(self.telecom_kw_table, "Top Keywords")
        tcs.addWidget(tct)
        tcs.setSizes([350, 350])
        tcwl.addWidget(tcs)
        self.analysis_tabs.addTab(tcw, "Telecom")
        # Viz
        vw = QWidget()
        vwl = QVBoxLayout(vw)
        self.keyword_canvas = MatplotlibCanvas(vw, width=10, height=6)
        vwl.addWidget(self.keyword_canvas)
        self.analysis_tabs.addTab(vw, "Visualizations")
        lo.addWidget(self.analysis_tabs)
        return panel

    def _init_menus(self):
        mb = self.menuBar()
        fm = mb.addMenu("File")
        ao = QAction("Open Transcript...", self)
        ao.setShortcut(QKeySequence.Open)
        ao.triggered.connect(self.load_transcript)
        fm.addAction(ao)
        asv = QAction("Save Transcript", self)
        asv.setShortcut(QKeySequence.Save)
        asv.triggered.connect(self.save_transcript)
        fm.addAction(asv)
        asa = QAction("Save As...", self)
        asa.setShortcut(QKeySequence("Ctrl+Shift+S"))
        asa.triggered.connect(self.save_transcript_as)
        fm.addAction(asa)
        fm.addSeparator()
        aej = QAction("Export as JSON...", self)
        aej.triggered.connect(lambda: self.export_results('json'))
        fm.addAction(aej)
        aec = QAction("Export as CSV...", self)
        aec.triggered.connect(lambda: self.export_results('csv'))
        fm.addAction(aec)
        aet = QAction("Export as Text...", self)
        aet.triggered.connect(lambda: self.export_results('txt'))
        fm.addAction(aet)
        aep = QAction("Export Pipe-Formatted Transcript...", self)
        aep.triggered.connect(self._export_pipe_formatted)
        fm.addAction(aep)
        fm.addSeparator()
        ap = QAction("Print...", self)
        ap.setShortcut(QKeySequence.Print)
        ap.triggered.connect(self.print_transcript)
        fm.addAction(ap)
        fm.addSeparator()
        ax = QAction("Exit", self)
        ax.setShortcut(QKeySequence("Ctrl+Q"))
        ax.triggered.connect(self.close)
        fm.addAction(ax)
        em = mb.addMenu("Edit")
        au = QAction("Undo", self)
        au.setShortcut(QKeySequence.Undo)
        au.triggered.connect(lambda: self.raw_text_edit.undo())
        em.addAction(au)
        ar = QAction("Redo", self)
        ar.setShortcut(QKeySequence.Redo)
        ar.triggered.connect(lambda: self.raw_text_edit.redo())
        em.addAction(ar)
        em.addSeparator()
        act = QAction("Cut", self)
        act.setShortcut(QKeySequence.Cut)
        act.triggered.connect(lambda: self.raw_text_edit.cut())
        em.addAction(act)
        acp = QAction("Copy", self)
        acp.setShortcut(QKeySequence.Copy)
        acp.triggered.connect(lambda: self.raw_text_edit.copy())
        em.addAction(acp)
        aps = QAction("Paste", self)
        aps.setShortcut(QKeySequence.Paste)
        aps.triggered.connect(lambda: self.raw_text_edit.paste())
        em.addAction(aps)
        em.addSeparator()
        aal = QAction("Select All", self)
        aal.setShortcut(QKeySequence.SelectAll)
        aal.triggered.connect(lambda: self.raw_text_edit.selectAll())
        em.addAction(aal)
        af = QAction("Find...", self)
        af.setShortcut(QKeySequence.Find)
        af.triggered.connect(lambda: self.search_input.setFocus())
        em.addAction(af)
        am = mb.addMenu("Analysis")
        ara = QAction("Run Full Analysis", self)
        ara.setShortcut(QKeySequence("Ctrl+R"))
        ara.triggered.connect(self.run_analysis)
        am.addAction(ara)
        am.addSeparator()
        ase = QAction("Sentiment Only", self)
        ase.triggered.connect(lambda: self._run_single('sentiment'))
        am.addAction(ase)
        ake = QAction("Keywords Only", self)
        ake.triggered.connect(lambda: self._run_single('keywords'))
        am.addAction(ake)
        ane = QAction("NER Only", self)
        ane.triggered.connect(lambda: self._run_single('entities'))
        am.addAction(ane)
        ate = QAction("Telecom Only", self)
        ate.triggered.connect(lambda: self._run_single('telecom'))
        am.addAction(ate)
        vm = mb.addMenu("View")
        azi = QAction("Zoom In", self)
        azi.setShortcut(QKeySequence.ZoomIn)
        azi.triggered.connect(self._zoom_in)
        vm.addAction(azi)
        azo = QAction("Zoom Out", self)
        azo.setShortcut(QKeySequence.ZoomOut)
        azo.triggered.connect(self._zoom_out)
        vm.addAction(azo)
        azr = QAction("Reset Zoom", self)
        azr.setShortcut(QKeySequence("Ctrl+0"))
        azr.triggered.connect(self._reset_zoom)
        vm.addAction(azr)
        hm = mb.addMenu("Help")
        aab = QAction("About", self)
        aab.triggered.connect(self._show_about)
        hm.addAction(aab)
        ask = QAction("Shortcuts", self)
        ask.triggered.connect(self._show_shortcuts)
        hm.addAction(ask)

    def _init_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(20, 20))
        self.addToolBar(tb)
        tb.addAction("Open", self.load_transcript)
        tb.addAction("Save", self.save_transcript)
        tb.addSeparator()
        tb.addAction("Format", self._format_transcript)
        tb.addAction("Analyze", self.run_analysis)
        tb.addAction("Export", self.export_results)
        tb.addAction("Print", self.print_transcript)

    def _init_statusbar(self):
        self.statusBar()
        self.word_count_label = QLabel("Words: 0")
        self.word_count_label.setStyleSheet("color: " + MC['text_dim'] + "; padding: 0 10px;")
        self.statusBar().addPermanentWidget(self.word_count_label)
        self.char_count_label = QLabel("Chars: 0")
        self.char_count_label.setStyleSheet("color: " + MC['text_dim'] + "; padding: 0 10px;")
        self.statusBar().addPermanentWidget(self.char_count_label)

    def closeEvent(self, event):
        if self.is_modified:
            reply = QMessageBox.question(self, 'Unsaved Changes', 'Save before exiting?',
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            if reply == QMessageBox.Save:
                self.save_transcript()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        self.settings.setValue('geometry', self.saveGeometry())
        event.accept()

    def _on_text_changed(self):
        self.is_modified = True
        text = self.raw_text_edit.toPlainText()
        wc = len(text.split()) if text.strip() else 0
        self.word_count_label.setText("Words: " + str(wc))
        self.char_count_label.setText("Chars: " + str(len(text)))
        if text.strip():
            self.btn_analyze.setEnabled(True)

    def _search_text(self):
        query = self.search_input.text()
        if not query:
            return
        cursor = self.raw_text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(MC['selection_bg']))
        fmt.setForeground(QColor(MC['text_bright']))
        doc = self.raw_text_edit.document()
        cursor = doc.find(query, cursor)
        if not cursor.isNull():
            self.raw_text_edit.setTextCursor(cursor)
            self.raw_text_edit.ensureCursorVisible()
            self.statusBar().showMessage("Found: " + query)
        else:
            cursor = QTextCursor(doc)
            cursor = doc.find(query, cursor)
            if not cursor.isNull():
                self.raw_text_edit.setTextCursor(cursor)
                self.raw_text_edit.ensureCursorVisible()
                self.statusBar().showMessage("Wrapped search: " + query)
            else:
                self.statusBar().showMessage("Not found: " + query)

    def _clear_search(self):
        self.search_input.clear()
        cursor = self.raw_text_edit.textCursor()
        cursor.clearSelection()
        self.raw_text_edit.setTextCursor(cursor)

    def _zoom_in(self):
        self.raw_text_edit.zoomIn(2)
        self.cleaned_text_edit.zoomIn(2)
        self.overview_text.zoomIn(2)

    def _zoom_out(self):
        self.raw_text_edit.zoomOut(2)
        self.cleaned_text_edit.zoomOut(2)
        self.overview_text.zoomOut(2)

    def _reset_zoom(self):
        font = QFont('Consolas', 13)
        self.raw_text_edit.setFont(font)
        self.cleaned_text_edit.setFont(font)

    def _show_about(self):
        QMessageBox.about(self, "About", APP_NAME + " v" + APP_VERSION + "\n" + APP_SUBTITLE +
                          "\n\nA comprehensive NLP transcript analysis tool\nfor telecom professionals.\n\nBuilt by NinjaTech AI")

    def _show_shortcuts(self):
        shortcuts = ("Ctrl+O: Open\nCtrl+S: Save\nCtrl+Shift+S: Save As\nCtrl+R: Run Analysis\n"
                     "Ctrl+P: Print\nCtrl+F: Find\nCtrl++: Zoom In\nCtrl+-: Zoom Out\nCtrl+0: Reset Zoom\nCtrl+Q: Exit")
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts)

    def _resummarize(self):
        if not self.analysis_results or 'cleaned_text' not in self.analysis_results:
            QMessageBox.information(self, "No Data", "Run analysis first.")
            return
        self.statusBar().showMessage("Re-summarizing...")
        QApplication.processEvents()
        result = self.engine.generate_summary(self.analysis_results['cleaned_text'], self.summary_spin.value())
        self.analysis_results['summary'] = result
        self._update_summary_tab(result)
        self.statusBar().showMessage("Re-summarization complete.")

    def _remodel_topics(self):
        if not self.analysis_results or 'cleaned_text' not in self.analysis_results:
            QMessageBox.information(self, "No Data", "Run analysis first.")
            return
        self.statusBar().showMessage("Re-modeling topics...")
        QApplication.processEvents()
        result = self.engine.topic_modeling(self.analysis_results['cleaned_text'], self.topics_spin.value())
        self.analysis_results['topics'] = result
        self._update_topics_tab(result)
        self.statusBar().showMessage("Topic re-modeling complete.")

    def load_transcript(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Open Transcript", "",
                                            "All Supported (*.txt *.vtt *.srt *.csv);;Text (*.txt);;WebVTT (*.vtt);;SRT (*.srt);;CSV (*.csv)")
        if not fp:
            return
        self.statusBar().showMessage("Loading: " + fp + "...")
        QApplication.processEvents()
        result = TranscriptParser.parse_file(fp)
        if not result.get('success'):
            QMessageBox.warning(self, "Load Error", "Failed:\n" + result.get('error', 'Unknown'))
            return
        self.transcript_data = result
        self.current_file = fp
        ok, raw = SecurityUtils.safe_read_file(fp)
        self.raw_text_edit.setPlainText(raw if ok else result.get('raw_text', ''))
        self._populate_segments(result.get('segments', []))
        skb = result.get('file_size', 0) / 1024
        self.file_info_label.setText("File: " + result['file_name'] + " | Format: " + result.get('format', '?').upper() +
                                     " | Size: " + str(round(skb, 1)) + " KB | Segments: " + str(len(result.get('segments', []))))
        self.file_info_label.setStyleSheet("padding: 6px; font-size: 11px; color: " + MC['text_primary'] +
                                           "; border: 1px solid " + MC['border'] + "; border-radius: 4px; background-color: " + MC['highlight'] + ";")
        self.btn_analyze.setEnabled(True)
        self.is_modified = False
        self.statusBar().showMessage("Loaded: " + result['file_name'] + " (" + str(len(result.get('segments', []))) + " segments)")

    def save_transcript(self):
        if self.current_file:
            self._save_file(self.current_file)
        else:
            self.save_transcript_as()

    def save_transcript_as(self):
        fp, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Text (*.txt);;All (*)")
        if fp:
            self._save_file(fp)

    def _save_file(self, fp):
        try:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(self.raw_text_edit.toPlainText())
            self.current_file = fp
            self.is_modified = False
            self.statusBar().showMessage("Saved: " + Path(fp).name)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def print_transcript(self):
        try:
            from PySide6.QtPrintSupport import QPrintPreviewDialog, QPrinter
            printer = QPrinter(QPrinter.HighResolution)
            preview = QPrintPreviewDialog(printer, self)
            preview.paintRequested.connect(self._do_print)
            preview.exec()
        except Exception as e:
            QMessageBox.warning(self, "Print Error", str(e))

    def _do_print(self, printer):
        doc = QTextDocument()
        pipe_text = self.get_pipe_formatted_text()
        if pipe_text:
            text = pipe_text
        else:
            text = self.raw_text_edit.toPlainText()
        if self.analysis_results:
            text += "\n\n" + "=" * 60 + "\nANALYSIS RESULTS\n" + "=" * 60 + "\n" + self._gen_report()
        doc.setPlainText(text)
        doc.print_(printer)

    def export_results(self, fmt=None):
        if not self.analysis_results:
            QMessageBox.information(self, "No Results", "Run analysis first.")
            return
        if fmt is None:
            fmt, ok = QInputDialog.getItem(self, "Export Format", "Format:", ["JSON", "CSV", "Text Report"], 0, False)
            if not ok:
                return
            fmt = fmt.lower().split()[0]
        ext_map = {'json': '.json', 'csv': '.csv', 'text': '.txt'}
        ext = ext_map.get(fmt, '.json')
        dn = "analysis_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ext
        fp, _ = QFileDialog.getSaveFileName(self, "Export", dn, "Files (*" + ext + ");;All (*)")
        if not fp:
            return
        try:
            if fmt == 'json':
                self._exp_json(fp)
            elif fmt == 'csv':
                self._exp_csv(fp)
            else:
                self._exp_txt(fp)
            self.statusBar().showMessage("Exported: " + Path(fp).name)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _exp_json(self, fp):
        ed = {}
        for k, v in self.analysis_results.items():
            if k == 'cleaned_text':
                ed[k] = v[:5000]
            elif k == 'sentiment':
                ed[k] = {kk: vv for kk, vv in v.items() if kk != 'sentence_sentiments'}
                ed[k]['sentence_sentiments_sample'] = v.get('sentence_sentiments', [])[:20]
            else:
                ed[k] = v
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(ed, f, indent=2, default=str, ensure_ascii=False)

    def _exp_csv(self, fp):
        rows = []
        r = self.analysis_results
        for k, v in r.get('stats', {}).items():
            rows.append({'Section': 'Statistics', 'Key': k, 'Value': str(v)})
        s = r.get('sentiment', {})
        rows.append({'Section': 'Sentiment', 'Key': 'Overall', 'Value': s.get('overall_sentiment', '')})
        for k, v in s.get('vader', {}).items():
            rows.append({'Section': 'VADER', 'Key': k, 'Value': str(v)})
        for w, c in r.get('keywords', {}).get('word_frequency', []):
            rows.append({'Section': 'Keywords', 'Key': w, 'Value': str(c)})
        for e in r.get('entities', {}).get('entities', [])[:100]:
            rows.append({'Section': 'Entities', 'Key': e['text'], 'Value': e['label']})
        for sp, d in r.get('speakers', {}).get('speakers', {}).items():
            for k, v in d.items():
                rows.append({'Section': 'Speaker-' + sp, 'Key': k, 'Value': str(v)})
        for kw in r.get('telecom', {}).get('top_telecom_keywords', []):
            rows.append({'Section': 'Telecom', 'Key': kw['keyword'], 'Value': str(kw['count']) + " (" + kw['category'] + ")"})
        pd.DataFrame(rows).to_csv(fp, index=False, encoding='utf-8')

    def _exp_txt(self, fp):
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(self._gen_report())

    def _export_pipe_formatted(self):
        pipe_text = self.get_pipe_formatted_text()
        if not pipe_text:
            QMessageBox.information(self, "No Data", "Load a transcript first to export the pipe-formatted view.")
            return
        dn = "pipe_transcript_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".txt"
        fp, _ = QFileDialog.getSaveFileName(self, "Export Pipe-Formatted Transcript", dn, "Text (*.txt);;All (*)")
        if not fp:
            return
        try:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(pipe_text)
            self.statusBar().showMessage("Exported pipe-formatted transcript: " + Path(fp).name)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _gen_report(self):
        r = self.analysis_results
        if not r:
            return "No results."
        lines = ["=" * 70, "  " + APP_NAME + " - Analysis Report",
                 "  Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "=" * 70]
        st = r.get('stats', {})
        lines.append("\nDOCUMENT STATISTICS\n" + "-" * 40)
        for k, v in st.items():
            lines.append("  " + k.replace('_', ' ').title() + ": " + str(v))
        se = r.get('sentiment', {})
        lines.append("\nSENTIMENT\n" + "-" * 40)
        lines.append("  Overall: " + se.get('overall_sentiment', 'N/A'))
        vd = se.get('vader', {})
        lines.append("  VADER Compound: " + str(vd.get('compound', 'N/A')))
        lines.append("  Positive: " + str(vd.get('positive', 'N/A')))
        lines.append("  Negative: " + str(vd.get('negative', 'N/A')))
        lines.append("  Neutral: " + str(vd.get('neutral', 'N/A')))
        tb = se.get('textblob', {})
        lines.append("  TextBlob Polarity: " + str(tb.get('polarity', 'N/A')))
        lines.append("  TextBlob Subjectivity: " + str(tb.get('subjectivity', 'N/A')))
        kw = r.get('keywords', {})
        lines.append("\nTOP KEYWORDS\n" + "-" * 40)
        for w, c in kw.get('word_frequency', [])[:20]:
            lines.append("  " + w + ": " + str(c))
        en = r.get('entities', {})
        lines.append("\nENTITIES (" + str(en.get('total_entities', 0)) + ")\n" + "-" * 40)
        for lb, d in en.get('entity_summary', {}).items():
            lines.append("  " + lb + " (" + d['description'] + "): " + str(d['count']))
            for t, c in d['top_entities'][:5]:
                lines.append("    - " + t + ": " + str(c))
        sp = r.get('speakers', {})
        lines.append("\nSPEAKERS (" + str(sp.get('total_speakers', 0)) + ")\n" + "-" * 40)
        for n, d in sp.get('speakers', {}).items():
            lines.append("  " + n + ": " + str(d['utterance_count']) + " utterances, " + str(d['word_count']) + " words, " +
                         str(d['talk_share_pct']) + "% share, " + d['sentiment_label'])
        sm = r.get('summary', {})
        lines.append("\nSUMMARY (LSA)\n" + "-" * 40)
        lines.append("  " + sm.get('lsa_summary', 'N/A'))
        tp = r.get('topics', {})
        lines.append("\nTOPICS\n" + "-" * 40)
        for t in tp.get('topics', []):
            ws = ', '.join(w for w, _ in t['words'][:7])
            lines.append("  " + t['label'] + ": " + ws)
        tc = r.get('telecom', {})
        lines.append("\nTELECOM (" + str(tc.get('total_telecom_mentions', 0)) + " mentions)\n" + "-" * 40)
        for cat, d in tc.get('categories', {}).items():
            lines.append("  " + cat.title() + ": " + str(d['total_mentions']) + " mentions")
        lines.extend(["", "=" * 70, "  End of Report", "=" * 70])
        return '\n'.join(lines)

    def run_analysis(self):
        text = self.raw_text_edit.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "No Text", "Load or paste a transcript first.")
            return
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "Busy", "Analysis already running.")
            return
        segments = []
        if self.transcript_data and self.transcript_data.get('segments'):
            segments = self.transcript_data['segments']
        else:
            parsed = TranscriptParser._parse_txt(text)
            segments = parsed.get('segments', [])
            self._populate_segments(segments)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_analyze.setEnabled(False)
        self.statusBar().showMessage("Running analysis...")
        self.worker = AnalysisWorker(self.engine, text, segments)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_complete)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _run_single(self, atype):
        text = self.raw_text_edit.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "No Text", "Load or paste a transcript first.")
            return
        self.statusBar().showMessage("Running " + atype + "...")
        QApplication.processEvents()
        try:
            cleaned = self.engine.preprocessor.clean_text(text)
            if not self.analysis_results:
                self.analysis_results = {}
            if atype == 'sentiment':
                res = self.engine.analyze_sentiment(cleaned)
                self.analysis_results['sentiment'] = res
                self._update_sentiment(res)
            elif atype == 'keywords':
                res = self.engine.extract_keywords(cleaned)
                self.analysis_results['keywords'] = res
                self._update_keywords(res)
            elif atype == 'entities':
                res = self.engine.extract_entities(cleaned)
                self.analysis_results['entities'] = res
                self._update_entities(res)
            elif atype == 'telecom':
                res = self.engine.telecom_analysis(cleaned)
                self.analysis_results['telecom'] = res
                self._update_telecom(res)
            self.statusBar().showMessage(atype.title() + " complete.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_progress(self, val, msg):
        self.progress_bar.setValue(val)
        self.statusBar().showMessage(msg)

    def _on_complete(self, results):
        self.analysis_results = results
        self.progress_bar.setVisible(False)
        self.btn_analyze.setEnabled(True)
        self.btn_export.setEnabled(True)
        self._update_overview(results)
        self.cleaned_text_edit.setPlainText(results.get('cleaned_text', ''))
        self._update_sentiment(results.get('sentiment', {}))
        self._update_keywords(results.get('keywords', {}))
        self._update_entities(results.get('entities', {}))
        self._update_speakers(results.get('speakers', {}))
        self._update_summary_tab(results.get('summary', {}))
        self._update_topics_tab(results.get('topics', {}))
        self._update_telecom(results.get('telecom', {}))
        VizGen.gen_keywords(self.keyword_canvas, results.get('keywords', {}))
        self.statusBar().showMessage("Analysis complete! All results ready.")
        self.analysis_tabs.setCurrentIndex(0)

    def _on_error(self, msg):
        self.progress_bar.setVisible(False)
        self.btn_analyze.setEnabled(True)
        QMessageBox.critical(self, "Error", msg)

    def _format_transcript(self):
        text = self.raw_text_edit.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "No Text", "Load or paste a transcript first.")
            return
        if self.transcript_data and self.transcript_data.get('segments'):
            segments = self.transcript_data['segments']
        else:
            parsed = TranscriptParser._parse_txt(text)
            segments = parsed.get('segments', [])
        if not segments:
            QMessageBox.information(self, "No Segments", "Could not identify speaker segments.\n\n"
                                    "Tip: Use 'Speaker: text' format for speaker detection.")
            return
        self._populate_segments(segments)
        self.transcript_tabs.setCurrentWidget(self.formatted_view)
        self.statusBar().showMessage("Formatted " + str(len(segments)) + " segments into pipe-delimited view.")

    def get_pipe_formatted_text(self, segments=None):
        if segments is None:
            if self.transcript_data and self.transcript_data.get('segments'):
                segments = self.transcript_data['segments']
            else:
                return ""
        if not segments:
            return ""
        lines = []
        lines.append("=" * 70)
        lines.append("  FORMATTED TRANSCRIPT - Pipe Delimited View")
        lines.append("  Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        lines.append("=" * 70)
        lines.append("")
        unique_speakers = []
        for seg in segments:
            sp = seg.get('speaker', 'Unknown')
            if sp not in unique_speakers:
                unique_speakers.append(sp)
        lines.append("Speakers: " + ", ".join(unique_speakers))
        lines.append("-" * 70)
        lines.append("")
        prev_speaker = None
        for seg in segments:
            speaker = seg.get('speaker', 'Unknown')
            text = seg.get('text', '')
            timestamp = seg.get('timestamp', '')
            if speaker != prev_speaker:
                if prev_speaker is not None:
                    lines.append("")
                ts_str = " [" + timestamp + "]" if timestamp else ""
                lines.append("|" + speaker + "|" + ts_str)
                lines.append("    " + text)
            else:
                ts_str = " [" + timestamp + "] " if timestamp else "    "
                lines.append(ts_str + text)
            prev_speaker = speaker
        lines.append("")
        lines.append("-" * 70)
        lines.append("Total segments: " + str(len(segments)) + " | Speakers: " + str(len(unique_speakers)))
        lines.append("=" * 70)
        return "\n".join(lines)

    def _populate_segments(self, segments):
        self.segments_table.setRowCount(len(segments))
        for i, seg in enumerate(segments):
            self.segments_table.setItem(i, 0, QTableWidgetItem(seg.get('speaker', '')))
            self.segments_table.setItem(i, 1, QTableWidgetItem(seg.get('timestamp', '')))
            self.segments_table.setItem(i, 2, QTableWidgetItem(seg.get('text', '')))
        self._populate_formatted_view(segments)

    def _populate_formatted_view(self, segments):
        if not segments:
            self.formatted_view.clear()
            return
        speaker_colors = [
            '#00FF41', '#00BFFF', '#FFD700', '#FF6B6B', '#DA70D6',
            '#00CED1', '#FF8C00', '#7FFF00', '#FF69B4', '#87CEEB',
            '#FFA07A', '#98FB98', '#DDA0DD', '#F0E68C', '#ADD8E6',
        ]
        unique_speakers = []
        for seg in segments:
            sp = seg.get('speaker', 'Unknown')
            if sp not in unique_speakers:
                unique_speakers.append(sp)
        color_map = {}
        for i, sp in enumerate(unique_speakers):
            color_map[sp] = speaker_colors[i % len(speaker_colors)]
        html_parts = []
        html_parts.append(
            '<html><body style="background-color:#0D0D0D; color:#00FF41; '
            'font-family: Consolas, Courier New, monospace; font-size:13px; padding:12px;">'
        )
        html_parts.append(
            '<div style="border-bottom:1px solid #004D00; padding-bottom:10px; margin-bottom:14px;">'
            '<span style="color:#39FF14; font-size:15px; font-weight:bold;">'
            ':: Formatted Transcript View ::</span><br/>'
            '<span style="color:#008F11; font-size:11px;">Speakers identified: '
        )
        legend_items = []
        for sp in unique_speakers:
            c = color_map[sp]
            legend_items.append(
                '<span style="color:' + c + '; font-weight:bold;">|' + html_module.escape(sp) + '|</span>'
            )
        html_parts.append(' &amp;nbsp; '.join(legend_items))
        html_parts.append('</span></div>')
        prev_speaker = None
        for idx, seg in enumerate(segments):
            speaker = seg.get('speaker', 'Unknown')
            text = seg.get('text', '')
            timestamp = seg.get('timestamp', '')
            sc = color_map.get(speaker, '#00FF41')
            if speaker != prev_speaker:
                if prev_speaker is not None:
                    html_parts.append('<div style="height:8px;"></div>')
                html_parts.append(
                    '<div style="margin-bottom:2px;">'
                )
                if timestamp:
                    html_parts.append(
                        '<span style="color:#004D00; font-size:10px;">[' +
                        html_module.escape(timestamp) + ']</span> '
                    )
                html_parts.append(
                    '<span style="color:' + sc + '; font-weight:bold; '
                    'background-color:#001A00; padding:2px 6px; border-radius:3px; '
                    'border:1px solid ' + sc + ';">'
                    '|' + html_module.escape(speaker) + '|</span>'
                    '</div>'
                )
                html_parts.append(
                    '<div style="margin-left:20px; margin-bottom:6px; padding:4px 8px; '
                    'border-left:2px solid ' + sc + '; color:#00CC33;">'
                    + html_module.escape(text) + '</div>'
                )
            else:
                html_parts.append(
                    '<div style="margin-left:20px; margin-bottom:6px; padding:4px 8px; '
                    'border-left:2px solid ' + sc + '; color:#00CC33;">'
                )
                if timestamp:
                    html_parts.append(
                        '<span style="color:#004D00; font-size:10px;">[' +
                        html_module.escape(timestamp) + ']</span> '
                    )
                html_parts.append(html_module.escape(text) + '</div>')
            prev_speaker = speaker
        html_parts.append(
            '<div style="border-top:1px solid #004D00; margin-top:14px; padding-top:8px; '
            'color:#008F11; font-size:11px;">'
            'Total segments: ' + str(len(segments)) +
            ' | Speakers: ' + str(len(unique_speakers)) + '</div>'
        )
        html_parts.append('</body></html>')
        self.formatted_view.setHtml(''.join(html_parts))
        self.transcript_tabs.setCurrentWidget(self.formatted_view)

    def _update_overview(self, results):
        stats = results.get('stats', {})
        sentiment = results.get('sentiment', {})
        keywords = results.get('keywords', {})
        entities = results.get('entities', {})
        speakers = results.get('speakers', {})
        telecom = results.get('telecom', {})
        overall = sentiment.get('overall_sentiment', 'N/A')
        sc = '#00FF41' if overall == 'Positive' else '#FF0040' if overall == 'Negative' else '#FFD700'
        tkw = ', '.join(w for w, _ in keywords.get('word_frequency', [])[:5])
        vr = keywords.get('vocabulary_richness', 0)
        p = []
        p.append('<html><body style="background-color:#0D0D0D;color:#00FF41;font-family:Consolas,monospace;padding:16px;">')
        p.append('<h2 style="color:#39FF14;border-bottom:2px solid #004D00;padding-bottom:8px;">Analysis Dashboard</h2>')
        p.append('<table style="width:100%;border-collapse:collapse;margin:12px 0;"><tr>')
        p.append('<td style="padding:12px;border:1px solid #004D00;width:25%;vertical-align:top;">')
        p.append('<h3 style="color:#39FF14;margin:0 0 8px 0;">Document Stats</h3>')
        p.append('<p>Words: <b>' + str(stats.get('word_count', 0)) + '</b></p>')
        p.append('<p>Sentences: <b>' + str(stats.get('sentence_count', 0)) + '</b></p>')
        p.append('<p>Segments: <b>' + str(stats.get('segment_count', 0)) + '</b></p>')
        p.append('</td>')
        p.append('<td style="padding:12px;border:1px solid #004D00;width:25%;vertical-align:top;">')
        p.append('<h3 style="color:#39FF14;margin:0 0 8px 0;">Sentiment</h3>')
        p.append('<p>Overall: <b style="color:' + sc + ';font-size:16px;">' + overall + '</b></p>')
        p.append('<p>VADER: <b>' + str(sentiment.get('vader', {}).get('compound', 'N/A')) + '</b></p>')
        p.append('<p>Polarity: <b>' + str(sentiment.get('textblob', {}).get('polarity', 'N/A')) + '</b></p>')
        p.append('</td>')
        p.append('<td style="padding:12px;border:1px solid #004D00;width:25%;vertical-align:top;">')
        p.append('<h3 style="color:#39FF14;margin:0 0 8px 0;">Keywords</h3>')
        p.append('<p>Total: <b>' + str(keywords.get('total_words', 0)) + '</b></p>')
        p.append('<p>Unique: <b>' + str(keywords.get('unique_words', 0)) + '</b></p>')
        p.append('<p>Top: ' + html_module.escape(tkw) + '</p>')
        p.append('</td>')
        p.append('<td style="padding:12px;border:1px solid #004D00;width:25%;vertical-align:top;">')
        p.append('<h3 style="color:#39FF14;margin:0 0 8px 0;">Entities/Speakers</h3>')
        ner_engine = entities.get('engine', 'spaCy')
        ner_color = '#00FF41' if 'spaCy' in str(ner_engine) else '#FFD700'
        p.append('<p>Entities: <b>' + str(entities.get('total_entities', 0)) + '</b></p>')
        p.append('<p>NER: <span style="color:' + ner_color + ';">' + str(ner_engine) + '</span></p>')
        p.append('<p>Speakers: <b>' + str(speakers.get('total_speakers', 0)) + '</b></p>')
        p.append('<p>Telecom: <b>' + str(telecom.get('total_telecom_mentions', 0)) + '</b> mentions</p>')
        p.append('</td></tr></table>')
        sm = results.get('summary', {})
        p.append('<h3 style="color:#39FF14;">Summary (LSA)</h3>')
        p.append('<p style="color:#00CC33;">' + html_module.escape(sm.get('lsa_summary', 'N/A')) + '</p>')
        p.append('<p style="color:#008F11;font-size:11px;">Completed: ' + results.get('timestamp', '') + '</p>')
        p.append('</body></html>')
        self.overview_text.setHtml('\n'.join(p))

    def _update_sentiment(self, sentiment):
        VizGen.gen_sentiment(self.sentiment_canvas, sentiment)
        ss = sentiment.get('sentence_sentiments', [])
        self.sentiment_table.setRowCount(len(ss))
        for i, s in enumerate(ss):
            self.sentiment_table.setItem(i, 0, QTableWidgetItem(s['text'][:100]))
            self.sentiment_table.setItem(i, 1, QTableWidgetItem(str(round(s['textblob_polarity'], 4))))
            self.sentiment_table.setItem(i, 2, QTableWidgetItem(str(round(s['textblob_subjectivity'], 4))))
            self.sentiment_table.setItem(i, 3, QTableWidgetItem(str(round(s['vader_compound'], 4))))
            c = s['vader_compound']
            lb = 'Positive' if c >= 0.05 else 'Negative' if c <= -0.05 else 'Neutral'
            it = QTableWidgetItem(lb)
            it.setForeground(QColor('#00FF41' if lb == 'Positive' else '#FF0040' if lb == 'Negative' else '#FFD700'))
            self.sentiment_table.setItem(i, 4, it)

    def _update_keywords(self, keywords):
        VizGen.gen_wordcloud(self.wordcloud_canvas, keywords.get('word_frequency', []))
        wf = keywords.get('word_frequency', [])
        self.word_freq_table.setRowCount(len(wf))
        for i, (w, c) in enumerate(wf):
            self.word_freq_table.setItem(i, 0, QTableWidgetItem(w))
            self.word_freq_table.setItem(i, 1, QTableWidgetItem(str(c)))
        tf = keywords.get('tfidf_keywords', [])
        self.tfidf_table.setRowCount(len(tf))
        for i, (w, s) in enumerate(tf):
            self.tfidf_table.setItem(i, 0, QTableWidgetItem(w))
            self.tfidf_table.setItem(i, 1, QTableWidgetItem(str(round(s, 4))))
        bg = keywords.get('bigrams', [])
        self.bigram_table.setRowCount(len(bg))
        for i, (g, c) in enumerate(bg):
            self.bigram_table.setItem(i, 0, QTableWidgetItem(g))
            self.bigram_table.setItem(i, 1, QTableWidgetItem(str(c)))
        tg = keywords.get('trigrams', [])
        self.trigram_table.setRowCount(len(tg))
        for i, (g, c) in enumerate(tg):
            self.trigram_table.setItem(i, 0, QTableWidgetItem(g))
            self.trigram_table.setItem(i, 1, QTableWidgetItem(str(c)))

    def _update_entities(self, entities):
        VizGen.gen_entities(self.entity_canvas, entities)
        self.entity_tree.clear()
        for lb, d in entities.get('entity_summary', {}).items():
            parent = QTreeWidgetItem(self.entity_tree)
            parent.setText(0, lb)
            parent.setText(1, str(d['count']))
            parent.setText(2, d['description'])
            for t, c in d['top_entities']:
                child = QTreeWidgetItem(parent)
                child.setText(0, t)
                child.setText(1, str(c))
        el = entities.get('entities', [])
        self.entity_table.setRowCount(len(el))
        for i, e in enumerate(el):
            self.entity_table.setItem(i, 0, QTableWidgetItem(e['text']))
            self.entity_table.setItem(i, 1, QTableWidgetItem(e['label']))
            self.entity_table.setItem(i, 2, QTableWidgetItem(e['description']))

    def _update_speakers(self, speakers):
        VizGen.gen_speakers(self.speaker_canvas, speakers)
        ss = speakers.get('speakers', {})
        self.speaker_table.setRowCount(len(ss))
        for i, (n, d) in enumerate(ss.items()):
            self.speaker_table.setItem(i, 0, QTableWidgetItem(n))
            self.speaker_table.setItem(i, 1, QTableWidgetItem(str(d['utterance_count'])))
            self.speaker_table.setItem(i, 2, QTableWidgetItem(str(d['word_count'])))
            self.speaker_table.setItem(i, 3, QTableWidgetItem(str(d['avg_words_per_utterance'])))
            self.speaker_table.setItem(i, 4, QTableWidgetItem(str(d['talk_share_pct']) + "%"))
            self.speaker_table.setItem(i, 5, QTableWidgetItem(str(d['avg_sentiment'])))
            it = QTableWidgetItem(d['sentiment_label'])
            it.setForeground(QColor('#00FF41' if d['sentiment_label'] == 'Positive' else '#FF0040' if d['sentiment_label'] == 'Negative' else '#FFD700'))
            self.speaker_table.setItem(i, 6, it)

    def _update_summary_tab(self, summary):
        self.lsa_text.setPlainText(summary.get('lsa_summary', ''))
        self.lexrank_text.setPlainText(summary.get('lexrank_summary', ''))

    def _update_topics_tab(self, topics):
        self.topics_tree.clear()
        for t in topics.get('topics', []):
            parent = QTreeWidgetItem(self.topics_tree)
            parent.setText(0, t['label'])
            for w, wt in t['words']:
                child = QTreeWidgetItem(parent)
                child.setText(0, w)
                child.setText(1, str(round(wt, 4)))

    def _update_telecom(self, telecom):
        VizGen.gen_telecom(self.telecom_canvas, telecom)
        self.telecom_tree.clear()
        for cat, d in telecom.get('categories', {}).items():
            parent = QTreeWidgetItem(self.telecom_tree)
            parent.setText(0, cat.title())
            parent.setText(1, str(d['total_mentions']))
            for h in d['hits']:
                child = QTreeWidgetItem(parent)
                child.setText(0, h['keyword'])
                child.setText(1, str(h['count']))
        tkw = telecom.get('top_telecom_keywords', [])
        self.telecom_kw_table.setRowCount(len(tkw))
        for i, k in enumerate(tkw):
            self.telecom_kw_table.setItem(i, 0, QTableWidgetItem(k['keyword']))
            self.telecom_kw_table.setItem(i, 1, QTableWidgetItem(k['category']))
            self.telecom_kw_table.setItem(i, 2, QTableWidgetItem(str(k['count'])))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("NinjaTech")
    window = TelecomAnalyzerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
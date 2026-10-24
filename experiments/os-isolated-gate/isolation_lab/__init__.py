"""Unadopted Linux isolation experiment; imports prior experiments without changing them."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT.parent / 'pre-record-gate'))
import record_gate  # Also loads the sibling verifier's import path.

VERSION = '0.1.0'
ROLES = {'agent': 10001, 'gate': 10002, 'audit': 10003, 'backend': 10004, 'open-backend': 10005}

"""Unadopted, local-only execution gate experiment; not part of VAP v1.2."""
from pathlib import Path
import sys

# Reuse the merged research verifier without modifying its implementation.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'declared-scope-verifier'))
VERSION = '0.1.1'
DOMAIN = b'pre-record-gate-experiment/1\0'

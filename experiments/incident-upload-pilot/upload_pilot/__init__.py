"""Synthetic controlled upload experiment, separate from VAP requirements."""

import sys
from pathlib import Path

ASSESSOR_ROOT = Path(__file__).resolve().parents[2] / "incident-evidence-assessor"
if not (ASSESSOR_ROOT / "incident_assessor" / "assess.py").is_file():
    raise ImportError("The pinned sibling incident-evidence-assessor checkout is required")
sys.path.insert(0, str(ASSESSOR_ROOT))

VERSION = "0.1.0"

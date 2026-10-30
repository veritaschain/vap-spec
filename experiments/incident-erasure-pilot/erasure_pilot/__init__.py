"""Synthetic, unadopted, same-controller local erasure evidence experiment."""

from pathlib import Path
import sys

ASSESSOR_ROOT = Path(__file__).resolve().parents[2] / "incident-evidence-assessor"
if str(ASSESSOR_ROOT) not in sys.path:
    sys.path.insert(0, str(ASSESSOR_ROOT))

VERSION = "0.1.0"

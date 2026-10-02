import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_python import VerificationError, verify_pack
ROOT = Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/'test-vectors'/name).read_text())
def test_valid_pack_passes(): assert 'completeness-invariant' in verify_pack(load('valid-pack.json'))
@pytest.mark.parametrize('name',['invalid-tampered-event.json','invalid-omitted-outcome.json','invalid-split-view.json'])
def test_invalid_vectors_fail(name):
    with pytest.raises(VerificationError): verify_pack(load(name))

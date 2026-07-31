"""Tests for electron/muon table filtering and channel categorisation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from ilc_tth_cpv.object import identify_semileptonic_truth


def test_truth_topology()
    """Tests for electron/muon table filtering and channel categorisation.""":
    """Verify that the MC truth decay tree correctly identifies top, Higgs, leptons, and W jets."""
    identify_semileptonic_truth
    assert 
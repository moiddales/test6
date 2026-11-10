"""Regression tests for audit findings; run with unittest discovery."""
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "stage2"))
sys.path.insert(0, str(ROOT / "stage2b"))
from model import utci
from station import station, systems, run


class ApplicabilityTests(unittest.TestCase):
    def test_utci_rejects_extrapolation(self):
        u = utci(np.array([40.0, 50.1]), np.array([44.0, 54.1]), 1.0, 20.0)
        self.assertTrue(np.isfinite(u[0]))
        self.assertTrue(np.isnan(u[1]))

    def test_enclosed_phoenix_does_not_report_unsupported_day(self):
        r, _, _ = run(station("Enclosed waiting room"), systems()[2], "Hot-dry (Phoenix-like)")
        self.assertGreater(r["utci_invalid_hours"], 4)
        self.assertFalse(r["full_day_supported"])
        self.assertTrue(np.isnan(r["eta"]))
        self.assertTrue(np.isnan(r["person_h_UTCI38_before"]))


if __name__ == "__main__":
    unittest.main()

"""Regression tests for audit findings; run with unittest discovery."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "stage2"))
sys.path.insert(0, str(ROOT / "stage2b"))
from model import utci, Params, devices_for, evaluate
from station import station, systems, run, simulate, comfort


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


class RatingTests(unittest.TestCase):
    def test_occupied_ratings_in_2a(self):
        p = Params()
        for d in devices_for(p):
            r = evaluate(d, np.array([35., 45., 49.]), 15., 0.1, 10., p)
            drop = r["dU"] if d.kind == "fan" else np.array([35., 45., 49.]) - r["T_person"]
            self.assertTrue(np.all(drop <= d.rated_drop + 1e-6))

    def test_occupied_ratings_in_station(self):
        st = station("Platform screen doors")
        clim = "Hot-dry (Phoenix-like)"
        base = simulate(st, systems()[0], clim)
        for sysm in systems()[1:4]:
            sim = simulate(st, sysm, clim, base=base)
            cf = comfort(st, sysm, sim, base)
            drop = cf["U0"] - cf["U_cov"] if sysm.kind == "fan" else base["T"] - cf["T_person"]
            self.assertLessEqual(np.nanmax(drop), sysm.rated_drop + 1e-5)


class ControlTests(unittest.TestCase):
    def test_evap_off_has_no_resources_and_matches_uncooled_state(self):
        st = station("Platform screen doors")
        clim = "Hot-humid (Houston-like)"
        base = simulate(st, systems()[0], clim)
        s = simulate(st, systems()[2], clim, on=np.zeros_like(base["t"], dtype=bool), base=base)
        self.assertEqual(s["P"].sum(), 0)
        self.assertEqual(s["water"].sum(), 0)
        np.testing.assert_allclose(s["T"], base["T"])
        np.testing.assert_allclose(s["W"], base["W"])

    def test_humidistat_finds_usable_window_without_powered_exceedance(self):
        r, s, _ = run(station("Platform screen doors"), replace(systems()[2], control="demand"),
                      "Hot-humid (Houston-like)")
        self.assertGreater(r["hours_on"], 0)
        self.assertLess(r["hours_on"], 16)
        self.assertEqual(r["powered_hours_RH_over_65"], 0)
        self.assertTrue(np.all(s["P"][~s["on"]] == 0))
        self.assertTrue(np.all(s["water"][~s["on"]] == 0))


if __name__ == "__main__":
    unittest.main()

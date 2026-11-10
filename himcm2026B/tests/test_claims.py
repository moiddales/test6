"""Ensure the provenance checker rejects plausible but incorrectly sourced claims."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_numbers import check_claim


class ClaimChecks(unittest.TestCase):
    def test_exact_values_rows_units_and_baselines(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "paper").mkdir()
            (root / "values.csv").write_text("scenario,value\na,17.5\nb,35.0\n")
            (root / "paper/metric_schema.json").write_text(json.dumps({"values.csv:value": {"unit":"kWh", "baseline":"a day"}}))
            (root / "doc.md").write_text("<!-- claim:x -->17.5<!-- /claim -->")
            c = dict(id="x", csv="values.csv", where={"scenario":"a"}, column="value", unit="kWh", baseline="a day", decimals=1, document="doc.md")
            self.assertEqual(check_claim(c, root), "17.5")
            for edit in ({"where":{"scenario":"b"}}, {"unit":"L"}, {"baseline":"another day"}):
                with self.assertRaises(ValueError):
                    check_claim(dict(c, **edit), root)
            (root / "doc.md").write_text("<!-- claim:x -->17.6<!-- /claim -->")
            with self.assertRaises(ValueError):
                check_claim(c, root)

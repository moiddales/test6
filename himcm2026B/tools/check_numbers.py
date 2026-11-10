"""Check explicitly registered report claims against named CSV cells.

Unlike the retired numeric-token search, each claim has an exact row key,
column, unit, baseline, rounding rule and document marker. Coverage is limited
by design to registered claims, not every numeral in historical documents.
"""
import json
import math
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def check_claim(claim, root=ROOT):
    required = {"id", "csv", "where", "column", "unit", "baseline", "decimals", "document"}
    if not required <= claim.keys() or not claim["unit"] or not claim["baseline"]:
        raise ValueError("Incomplete claim provenance")
    schema = json.loads((root / "paper" / "metric_schema.json").read_text())
    key = claim["csv"] + ":" + claim["column"]
    if key not in schema or schema[key] != {"unit": claim["unit"], "baseline": claim["baseline"]}:
        raise ValueError(f"Unit/baseline mismatch: {claim['id']}")
    table = pd.read_csv(root / claim["csv"])
    for col, value in claim["where"].items():
        table = table[table[col] == value]
    if len(table) != 1:
        raise ValueError(f"Expected one exact source row: {claim['id']}")
    value = float(table.iloc[0][claim["column"]])
    expected = f"{value:.{claim['decimals']}f}" if math.isfinite(value) else "unsupported"
    doc = (root / claim["document"]).read_text()
    pattern = r"<!-- claim:" + re.escape(claim["id"]) + r" -->(.*?)<!-- /claim -->"
    found = re.findall(pattern, doc)
    if not found or any(x != expected for x in found):
        raise ValueError(f"Claim {claim['id']}: expected {expected}, found {found}")
    return expected


def main():
    claims = json.loads((ROOT / "paper" / "claims.json").read_text())
    if not claims or len({x["id"] for x in claims}) != len(claims):
        raise ValueError("Claim register must be nonempty with unique IDs")
    for claim in claims:
        check_claim(claim)
    print(f"PASS: {len(claims)} registered claims: exact CSV rows, columns, units, baselines and rounding")
    print("Historical audits, source quotations, and unregistered prose are outside this automated check.")


if __name__ == "__main__":
    main()

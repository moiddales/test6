"""Flag numbers in the Chinese READMEs and English drafts that appear in no
output file (CSV tables, run logs) and in no model source file.

Run from himcm2026B/ after all stages have been run:
    python3 tools/check_numbers.py
A flagged number is not necessarily wrong (it may be a hand calculation or a
literature value); each one needs a look. Exit code 1 if anything is flagged.
"""
import glob
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# data/README.md lists literature values and AUDIT.md reports exploratory runs;
# neither is a model-output document, so both are skipped.
SKIP = {"AUDIT.md", os.path.join("data", "README.md")}
DOCS = sorted(f for f in glob.glob(os.path.join(ROOT, "*.md")) + glob.glob(os.path.join(ROOT, "*", "*.md"))
              if os.path.relpath(f, ROOT) not in SKIP)
# Literature values, citation pages, standard and section numbers quoted in the
# docs; they are not model outputs.
ALLOW = {"62.1", "5.13", "431.96", "431.66", "0.622", "75.6", "724", "507", "481", "494", "1576", "1809",
         "403", "503", "2.27", "0.57", "192523679", "10.1001", "100578", "2267", "2269"}
NUM = re.compile(r"(?<![\w.§/])[-−]?\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\w.])|(?<![\w.§/])[-−]?\d+(?:\.\d+)?(?![\w])")


def forms(v):
    """String forms a value may take in prose: rounded, absolute, as a percentage."""
    out = set()
    for x in (v, abs(v), v * 100, abs(v) * 100):
        for nd in (0, 1, 2, 3):
            s = f"{round(x, nd):.{nd}f}"
            out.add(s)
            out.add(s.rstrip("0").rstrip(".") if "." in s else s)
    return out


def known_values():
    vals = set()
    for f in glob.glob(os.path.join(ROOT, "**", "*.csv"), recursive=True):
        if f.endswith("_raw.csv"):
            continue
        df = pd.read_csv(f)
        for col in df.columns:
            for v in pd.to_numeric(df[col], errors="coerce").dropna().unique():
                vals |= forms(float(v))
        for col in df.select_dtypes(include=["object", "string"]).columns:          # numbers inside text cells
            for s in df[col].dropna().astype(str):
                vals |= {m.replace(",", "") for m in NUM.findall(s)}
    for f in glob.glob(os.path.join(ROOT, "**", "*_log.txt"), recursive=True) + \
            glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True):
        for m in NUM.findall(open(f, encoding="utf-8").read()):
            v = float(m.replace(",", "").replace("−", "-"))
            vals |= forms(v)
    return vals


def main():
    vals = known_values()
    flagged = 0
    for doc in DOCS:
        rel = os.path.relpath(doc, ROOT)
        in_code = False
        for ln, line in enumerate(open(doc, encoding="utf-8"), 1):
            if line.startswith("```"):
                in_code = not in_code
            if in_code or "http" in line:
                continue
            for m in NUM.findall(line):
                s = m.replace(",", "").replace("−", "-").lstrip("-")
                x = float(s)
                if x <= 10 and "." not in s:       # small integers: counts, list items, section numbers
                    continue
                if 1900 <= x <= 2100 and "." not in s:   # years
                    continue
                if s in ALLOW or s in vals or s.rstrip("0").rstrip(".") in vals:
                    continue
                flagged += 1
                print(f"{rel}:{ln}: {m}    | {line.strip()[:110]}")
    print(f"\n{flagged} number(s) not found in outputs or source")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())

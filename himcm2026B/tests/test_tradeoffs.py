import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"venues"))
from tradeoffs import nondominated

class ParetoTests(unittest.TestCase):
    def test_tradeoffs_dominance_and_missing_results(self):
        # Two alternatives trade cost against exposure; the third loses on both.
        result=nondominated([[1,5],[3,2],[4,6],[np.nan,0],[1,5]])
        np.testing.assert_array_equal(result,[True,True,False,False,True])

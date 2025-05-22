import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lab_utils import parse_lab_results, build_lab_chart

sample = """HDL 45 mg/dL
LDL 130 mg/dL
Triglycerides 160 mg/dL"""


def test_parse_lab_results():
    res = parse_lab_results(sample)
    assert res == {"HDL": 45.0, "LDL": 130.0, "Triglycerides": 160.0}


def test_build_lab_chart():
    res = parse_lab_results(sample)
    fig = build_lab_chart(res)
    try:
        import matplotlib
        from matplotlib.figure import Figure
        assert isinstance(fig, Figure)
    except ImportError:
        assert fig is None

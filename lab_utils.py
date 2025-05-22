import re
from typing import Dict

# some typical reference ranges (lower, upper)
NORMAL_RANGES = {
    'HDL': (40, 60),
    'LDL': (0, 100),
    'Triglycerides': (0, 150),
    'Total Cholesterol': (125, 200),
    'Hemoglobin A1c': (4, 5.6),
}

def parse_lab_results(text: str) -> Dict[str, float]:
    """Extract simple lab results like ``"HDL 45 mg/dL"`` from ``text``."""
    pattern = re.compile(r"([A-Za-z][A-Za-z0-9 ]+)\s+(\d+(?:\.\d+)?)\s*(mg/dL|g/dL|mmol/L|%)", re.I) # noqa: E501
    results: Dict[str, float] = {}
    for name, value, _ in re.findall(pattern, text):
        try:
            results[name.strip()] = float(value)
        except ValueError:
            continue
    return results

def build_lab_chart(results: Dict[str, float]):
    """Return a matplotlib bar chart comparing results to reference ranges.

    If matplotlib is not available, returns ``None``.
    """
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None

    names = list(results.keys())
    values = [results[n] for n in names]

    fig, ax = plt.subplots()
    ax.bar(names, values, color='skyblue')

    for i, name in enumerate(names):
        if name in NORMAL_RANGES:
            low, high = NORMAL_RANGES[name]
            ax.axhspan(low, high, color='green', alpha=0.2)

    ax.set_ylabel('Value')
    ax.set_title('Lab Results')
    plt.xticks(rotation=45, ha='right')
    fig.tight_layout()
    return fig

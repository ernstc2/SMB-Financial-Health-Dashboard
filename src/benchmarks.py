"""
Benchmarking layer — industry benchmarks for SaaS SMBs and RAG status logic.

RAG Status:
  Green  — at or above benchmark (healthy)
  Amber  — approaching threshold (watch closely)
  Red    — below acceptable range (action required)
"""

from dataclasses import dataclass
from typing import Literal

RAGStatus = Literal["Green", "Amber", "Red"]


@dataclass
class KPIBenchmark:
    name: str
    unit: str
    benchmark_value: float
    green_threshold: float
    amber_threshold: float
    higher_is_better: bool
    description: str
    benchmark_label: str


# SaaS SMB industry benchmarks (sourced from SaaS Capital, OpenView, Bessemer benchmarks)
BENCHMARKS: dict[str, KPIBenchmark] = {
    "gross_margin_pct": KPIBenchmark(
        name="Gross Margin",
        unit="%",
        benchmark_value=70.0,
        green_threshold=70.0,
        amber_threshold=60.0,
        higher_is_better=True,
        description="Revenue minus COGS as % of revenue. SaaS benchmark: ≥70%.",
        benchmark_label="≥70% (SaaS SMB median)",
    ),
    "revenue_growth_mom": KPIBenchmark(
        name="Revenue Growth (MoM)",
        unit="%",
        benchmark_value=5.0,
        green_threshold=5.0,
        amber_threshold=2.0,
        higher_is_better=True,
        description="Month-over-month revenue growth rate. Healthy SaaS SMB: ≥5% MoM.",
        benchmark_label="≥5% MoM",
    ),
    "opex_ratio": KPIBenchmark(
        name="OpEx Ratio",
        unit="%",
        benchmark_value=40.0,
        green_threshold=40.0,
        amber_threshold=55.0,
        higher_is_better=False,
        description="Operating expenses as % of revenue. Efficient SaaS SMB: ≤40%.",
        benchmark_label="≤40% of revenue",
    ),
    "revenue_per_employee": KPIBenchmark(
        name="Revenue / Employee",
        unit="$",
        benchmark_value=15_000,
        green_threshold=15_000,
        amber_threshold=10_000,
        higher_is_better=True,
        description="Monthly revenue per FTE. SaaS SMB benchmark: ≥$15k/employee/month.",
        benchmark_label="≥$15,000 / employee / month",
    ),
    "burn_rate": KPIBenchmark(
        name="Burn Rate",
        unit="$",
        benchmark_value=0,
        green_threshold=0,
        amber_threshold=-30_000,
        higher_is_better=True,
        description="Net monthly cash flow. Positive = profitable. Negative = burning cash.",
        benchmark_label="Breakeven or profitable",
    ),
    "runway_months": KPIBenchmark(
        name="Runway",
        unit="mo",
        benchmark_value=18,
        green_threshold=18,
        amber_threshold=12,
        higher_is_better=True,
        description="Months of cash remaining at current burn rate.",
        benchmark_label="≥18 months",
    ),
}


def get_rag_status(kpi_key: str, value: float) -> RAGStatus:
    """Assign Red / Amber / Green status to a KPI value against its benchmark."""
    bm = BENCHMARKS[kpi_key]

    if bm.higher_is_better:
        if value >= bm.green_threshold:
            return "Green"
        elif value >= bm.amber_threshold:
            return "Amber"
        else:
            return "Red"
    else:
        # Lower is better (e.g. OpEx Ratio)
        if value <= bm.green_threshold:
            return "Green"
        elif value <= bm.amber_threshold:
            return "Amber"
        else:
            return "Red"


def build_scorecard(kpis: dict) -> list[dict]:
    """
    Build a RAG scorecard list from a KPI dict.
    Returns a list of dicts suitable for a table display.
    """
    scorecard = []
    for key, bm in BENCHMARKS.items():
        value = kpis.get(key)
        if value is None:
            continue

        status = get_rag_status(key, value)

        # Format display value
        if bm.unit == "%":
            display_value = f"{value:.1f}%"
        elif bm.unit == "$" and key == "burn_rate":
            prefix = "+" if value >= 0 else "-"
            display_value = f"{prefix}${abs(value):,.0f}"
        elif bm.unit == "$":
            display_value = f"${value:,.0f}"
        elif bm.unit == "mo":
            display_value = "Profitable" if value >= 999 else f"{value:.0f} months"
        else:
            display_value = str(value)

        scorecard.append({
            "KPI": bm.name,
            "Value": display_value,
            "Benchmark": bm.benchmark_label,
            "Status": status,
            "_raw_value": value,
            "_key": key,
            "_description": bm.description,
        })

    return scorecard


RAG_COLORS = {
    "Green": "#00c896",
    "Amber": "#f5a623",
    "Red": "#e84545",
}

RAG_BG_COLORS = {
    "Green": "#0d2e1f",
    "Amber": "#2e1f00",
    "Red": "#2e0d0d",
}

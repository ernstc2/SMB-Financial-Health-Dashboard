"""
KPI Engine — calculates all key performance indicators from raw financial data.
"""

import pandas as pd
import numpy as np


def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Accepts a raw financial DataFrame and returns it enriched with all KPI columns.

    KPIs calculated:
    - Gross Margin %
    - Revenue Growth MoM %
    - Operating Expense Ratio %
    - Revenue per Employee
    - Burn Rate (monthly net cash flow; negative = burning cash)
    - Runway (months of cash remaining at current burn rate)
    """
    df = df.copy().sort_values("date").reset_index(drop=True)

    # Gross Margin %
    df["gross_margin_pct"] = ((df["revenue"] - df["cogs"]) / df["revenue"] * 100).round(1)

    # Revenue Growth MoM %
    df["revenue_growth_mom"] = (df["revenue"].pct_change() * 100).round(1)

    # Operating Expense Ratio %  (opex as % of revenue)
    df["opex_ratio"] = (df["opex"] / df["revenue"] * 100).round(1)

    # Revenue per Employee  (monthly, in dollars)
    df["revenue_per_employee"] = (df["revenue"] / df["headcount"]).round(0)

    # Burn Rate = net income (positive = profitable, negative = burning cash)
    df["burn_rate"] = df["net_income"].round(0)

    # Runway = cash balance / |burn rate| when burning, else infinity
    def compute_runway(row):
        if row["burn_rate"] >= 0:
            return 999  # profitable — infinite runway (capped for display)
        return round(row["cash_balance"] / abs(row["burn_rate"]), 1)

    df["runway_months"] = df.apply(compute_runway, axis=1)

    return df


def get_latest_kpis(df: pd.DataFrame) -> dict:
    """Return the most recent month's KPI values as a dictionary."""
    latest = df.iloc[-1]
    return {
        "gross_margin_pct": latest["gross_margin_pct"],
        "revenue_growth_mom": latest["revenue_growth_mom"],
        "opex_ratio": latest["opex_ratio"],
        "revenue_per_employee": latest["revenue_per_employee"],
        "burn_rate": latest["burn_rate"],
        "runway_months": latest["runway_months"],
        "revenue": latest["revenue"],
        "cash_balance": latest["cash_balance"],
        "headcount": latest["headcount"],
        "month_label": latest["month_label"],
    }


def get_trailing_avg_kpis(df: pd.DataFrame, n: int = 3) -> dict:
    """Return trailing n-month average for each KPI (useful for trend context)."""
    tail = df.tail(n)
    return {
        "gross_margin_pct": tail["gross_margin_pct"].mean().round(1),
        "revenue_growth_mom": tail["revenue_growth_mom"].mean().round(1),
        "opex_ratio": tail["opex_ratio"].mean().round(1),
        "revenue_per_employee": tail["revenue_per_employee"].mean().round(0),
        "burn_rate": tail["burn_rate"].mean().round(0),
    }

"""
Synthetic financial data generator for SMB Financial Health Dashboard.
Generates 24 months of realistic financial data for fictional companies
with baked-in problem signals for analytical interest.
"""

import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta


COMPANY_PROFILES = {
    "NovaSaaS": {
        "description": "B2B project management SaaS — healthy growth with rising cost pressure",
        "industry": "SaaS / Project Management",
        "founded": "2020",
        "seed": 42,
        # Revenue
        "revenue_start": 180_000,
        "revenue_growth_base": 0.055,      # ~5.5% MoM early on
        "revenue_growth_decel": 0.0018,    # growth slows over time (problem signal)
        "revenue_noise": 0.04,
        # COGS
        "cogs_ratio_start": 0.26,          # starts healthy (~74% gross margin)
        "cogs_ratio_drift": 0.0025,        # COGS creep (problem signal)
        "cogs_noise": 0.015,
        # Headcount
        "headcount_start": 18,
        "headcount_growth_interval": 2,    # new hire roughly every 2 months
        "headcount_spike_months": [6, 12, 18],
        "headcount_spike_size": [2, 3, 2],
        # Operating Expenses (excl. COGS)
        "opex_per_head": 9_500,
        "opex_base": 35_000,
        "opex_noise": 0.06,
        "opex_surge_month": 14,            # marketing push (problem signal)
        "opex_surge_amount": 28_000,
        # Cash
        "cash_start": 2_400_000,
    },

    "CloudForge": {
        "description": "DevOps tooling SaaS — aggressive growth strategy burning cash fast",
        "industry": "SaaS / DevOps",
        "founded": "2021",
        "seed": 99,
        # Revenue
        "revenue_start": 95_000,
        "revenue_growth_base": 0.07,       # faster growth
        "revenue_growth_decel": 0.003,     # but decelerates sharply
        "revenue_noise": 0.06,
        # COGS
        "cogs_ratio_start": 0.38,          # thinner margins from day 1
        "cogs_ratio_drift": 0.004,         # rapid COGS deterioration (problem signal)
        "cogs_noise": 0.02,
        # Headcount
        "headcount_start": 11,
        "headcount_growth_interval": 2,
        "headcount_spike_months": [4, 8, 16],
        "headcount_spike_size": [3, 4, 3],
        # Operating Expenses
        "opex_per_head": 11_000,           # higher cost per head
        "opex_base": 25_000,
        "opex_noise": 0.08,
        "opex_surge_month": 10,
        "opex_surge_amount": 45_000,       # large sales/marketing surge
        # Cash
        "cash_start": 1_500_000,
    },
}


def generate_company_data(company_name: str) -> pd.DataFrame:
    """Generate 24 months of synthetic financial data for a given company profile."""
    profile = COMPANY_PROFILES[company_name]
    rng = np.random.default_rng(profile["seed"])

    start_date = date(2023, 1, 1)
    months = 24
    records = []

    revenue = profile["revenue_start"]
    cogs_ratio = profile["cogs_ratio_start"]
    headcount = profile["headcount_start"]
    cash = profile["cash_start"]

    for i in range(months):
        period = start_date + relativedelta(months=i)

        # --- Revenue ---
        growth_rate = max(
            0.005,
            profile["revenue_growth_base"] - profile["revenue_growth_decel"] * i
        )
        noise = rng.normal(0, profile["revenue_noise"])
        if i > 0:
            revenue = revenue * (1 + growth_rate + noise)
        revenue = max(revenue, 50_000)

        # --- COGS ---
        cogs_ratio = min(
            0.72,
            cogs_ratio + profile["cogs_ratio_drift"] + rng.normal(0, profile["cogs_noise"])
        )
        cogs = revenue * cogs_ratio

        # --- Headcount ---
        if i > 0 and i % profile["headcount_growth_interval"] == 0:
            headcount += 1
        if i in profile["headcount_spike_months"]:
            idx = profile["headcount_spike_months"].index(i)
            headcount += profile["headcount_spike_size"][idx]

        # --- Operating Expenses ---
        base_opex = (
            profile["opex_base"]
            + headcount * profile["opex_per_head"]
            + rng.normal(0, profile["opex_noise"]) * headcount * profile["opex_per_head"]
        )
        surge = profile["opex_surge_amount"] if i == profile["opex_surge_month"] else 0
        opex = base_opex + surge

        # --- Cash ---
        net_cash_flow = revenue - cogs - opex
        cash = cash + net_cash_flow

        records.append({
            "date": pd.Timestamp(period),
            "month_label": period.strftime("%b %Y"),
            "month_index": i + 1,
            "revenue": round(revenue, 2),
            "cogs": round(cogs, 2),
            "gross_profit": round(revenue - cogs, 2),
            "opex": round(opex, 2),
            "net_income": round(revenue - cogs - opex, 2),
            "headcount": int(headcount),
            "cash_balance": round(max(cash, 0), 2),
        })

    return pd.DataFrame(records)


def get_all_companies() -> list[str]:
    return list(COMPANY_PROFILES.keys())


def get_company_profile(company_name: str) -> dict:
    return COMPANY_PROFILES[company_name]

"""
Insights engine — auto-generates plain-English consultant findings
based on RAG scorecard results and KPI trends.
"""

import pandas as pd
from src.benchmarks import BENCHMARKS, get_rag_status


def generate_insights(scorecard: list[dict], df: pd.DataFrame, kpis: dict) -> list[dict]:
    """
    Generate 3–5 consultant-style findings based on RAG status and trend data.

    Each insight is a dict with:
      - 'status': RAGStatus ("Green" / "Amber" / "Red")
      - 'title': short headline
      - 'body': plain-English explanation with context
    """
    insights = []
    status_map = {row["_key"]: row["Status"] for row in scorecard}
    tail3 = df.tail(3)
    tail6 = df.tail(6)

    # --- Insight 1: Gross Margin Trend ---
    gm_status = status_map.get("gross_margin_pct", "Green")
    gm_now = kpis["gross_margin_pct"]
    gm_6mo_ago = df.iloc[-6]["gross_margin_pct"] if len(df) >= 6 else df.iloc[0]["gross_margin_pct"]
    gm_delta = gm_now - gm_6mo_ago

    if gm_status == "Red":
        insights.append({
            "status": "Red",
            "title": "Gross Margin Below SaaS Benchmark",
            "body": (
                f"Current gross margin of {gm_now:.1f}% falls below the SaaS SMB benchmark of 70%. "
                f"Over the past 6 months, margin has {'declined' if gm_delta < 0 else 'shifted'} by "
                f"{abs(gm_delta):.1f} percentage points. This signals rising COGS — likely from "
                f"infrastructure scaling costs or support team growth outpacing revenue. "
                f"Recommend auditing cloud hosting contracts and exploring tier-based support models."
            ),
        })
    elif gm_status == "Amber":
        insights.append({
            "status": "Amber",
            "title": "Gross Margin Approaching Risk Zone",
            "body": (
                f"Gross margin stands at {gm_now:.1f}%, just above the critical 60% floor. "
                f"The 6-month trend shows a {abs(gm_delta):.1f}pp {'deterioration' if gm_delta < 0 else 'improvement'}. "
                f"If cost creep continues at this rate, margin will breach the red threshold within 2–3 months. "
                f"Proactive vendor renegotiation or pricing adjustments are advised."
            ),
        })
    else:
        insights.append({
            "status": "Green",
            "title": "Gross Margin Is Healthy",
            "body": (
                f"At {gm_now:.1f}%, gross margin comfortably exceeds the 70% SaaS benchmark, "
                f"indicating strong unit economics and effective cost discipline. "
                f"The 6-month change of {gm_delta:+.1f}pp suggests "
                f"{'stable or improving' if gm_delta >= -1 else 'mild pressure on'} COGS management."
            ),
        })

    # --- Insight 2: Revenue Growth Deceleration ---
    growth_status = status_map.get("revenue_growth_mom", "Green")
    growth_now = kpis["revenue_growth_mom"]
    growth_early = df.iloc[1:4]["revenue_growth_mom"].mean() if len(df) >= 4 else growth_now

    if growth_status in ("Red", "Amber"):
        decel = growth_early - growth_now
        insights.append({
            "status": growth_status,
            "title": "Revenue Growth Is Decelerating",
            "body": (
                f"Month-over-month revenue growth has slowed to {growth_now:.1f}%, down from an early-period "
                f"average of {growth_early:.1f}%. This {decel:.1f}pp deceleration over 24 months is a "
                f"classic sign of market saturation or weakening top-of-funnel activity. "
                f"{'Growth is now below the 5% benchmark, requiring immediate pipeline review.' if growth_status == 'Red' else 'While still above the red threshold, the trend warrants close monitoring.'} "
                f"Recommend evaluating CAC trends, churn rates, and expansion revenue as leading indicators."
            ),
        })
    else:
        insights.append({
            "status": "Green",
            "title": "Revenue Growth Remains Strong",
            "body": (
                f"MoM revenue growth of {growth_now:.1f}% meets or exceeds the 5% SaaS benchmark. "
                f"Early-period average was {growth_early:.1f}%, reflecting "
                f"{'natural maturation with growth remaining healthy.' if growth_now < growth_early else 'an acceleration in momentum.'} "
                f"Continue monitoring pipeline velocity to sustain this trajectory."
            ),
        })

    # --- Insight 3: Operating Expense Efficiency ---
    opex_status = status_map.get("opex_ratio", "Green")
    opex_now = kpis["opex_ratio"]
    opex_6mo = tail6["opex_ratio"].mean()
    headcount_growth = df.iloc[-1]["headcount"] - df.iloc[-6]["headcount"] if len(df) >= 6 else 0

    if opex_status == "Red":
        insights.append({
            "status": "Red",
            "title": "Operating Expenses Consuming Excess Revenue",
            "body": (
                f"OpEx ratio has reached {opex_now:.1f}% of revenue — significantly above the 40% efficiency "
                f"benchmark and above the 55% amber ceiling. The 6-month average is {opex_6mo:.1f}%. "
                f"Headcount grew by {headcount_growth} FTEs over the last 6 months, contributing to fixed cost inflation. "
                f"Immediate action recommended: freeze discretionary spend, review contractor usage, "
                f"and model a hiring pause scenario against revenue projections."
            ),
        })
    elif opex_status == "Amber":
        insights.append({
            "status": "Amber",
            "title": "OpEx Ratio Trending Above Benchmark",
            "body": (
                f"Operating expenses represent {opex_now:.1f}% of revenue, exceeding the 40% benchmark. "
                f"The 6-month trailing average of {opex_6mo:.1f}% confirms this is a persistent trend, not a one-time spike. "
                f"Headcount expanded by {headcount_growth} FTEs recently, adding to the cost base. "
                f"A structured cost efficiency review — particularly G&A and sales overhead — is recommended."
            ),
        })
    else:
        insights.append({
            "status": "Green",
            "title": "Operating Cost Efficiency Is Strong",
            "body": (
                f"OpEx ratio of {opex_now:.1f}% is within the healthy SaaS range (≤40%), "
                f"demonstrating effective cost control relative to revenue scale. "
                f"Sustaining this discipline during growth phases (headcount +{headcount_growth} in 6 months) "
                f"is a positive operational signal."
            ),
        })

    # --- Insight 4: Cash Runway ---
    runway_status = status_map.get("runway_months", "Green")
    runway_now = kpis["runway_months"]
    burn_now = kpis["burn_rate"]
    cash_now = kpis["cash_balance"]

    if runway_status == "Red":
        insights.append({
            "status": "Red",
            "title": "Cash Runway Is Critically Short",
            "body": (
                f"At the current burn rate of ${abs(burn_now):,.0f}/month, the company has approximately "
                f"{runway_now:.0f} months of runway remaining on a cash balance of ${cash_now:,.0f}. "
                f"This is below the 12-month minimum threshold and requires immediate attention. "
                f"Priority actions: initiate fundraising conversations, assess receivables acceleration, "
                f"and model break-even scenarios with a 20–30% cost reduction."
            ),
        })
    elif runway_status == "Amber":
        insights.append({
            "status": "Amber",
            "title": "Runway Window Is Narrowing",
            "body": (
                f"With {runway_now:.0f} months of runway at ${abs(burn_now):,.0f}/month burn, "
                f"the company is within the 12–18 month amber zone. Cash balance stands at ${cash_now:,.0f}. "
                f"Now is the appropriate time to begin fundraising outreach or explore debt financing, "
                f"as lead times for Series A/B rounds average 6–9 months."
            ),
        })
    elif burn_now >= 0:
        insights.append({
            "status": "Green",
            "title": "Company Is Operating Cash Flow Positive",
            "body": (
                f"The business generated ${burn_now:,.0f} in net positive cash flow this month — "
                f"a significant milestone that reduces dilutive fundraising pressure. "
                f"Cash balance of ${cash_now:,.0f} provides a strong operational buffer. "
                f"Focus on maintaining contribution margin discipline as the company scales."
            ),
        })
    else:
        insights.append({
            "status": "Green",
            "title": "Cash Runway Is Adequate",
            "body": (
                f"With {runway_now:.0f} months of runway remaining, the company is above the 18-month "
                f"green threshold. Cash balance of ${cash_now:,.0f} provides reasonable operating headroom. "
                f"Begin fundraising planning at ~15 months of runway to maintain negotiating leverage."
            ),
        })

    # --- Insight 5: Revenue per Employee Productivity ---
    rpe_status = status_map.get("revenue_per_employee", "Green")
    rpe_now = kpis["revenue_per_employee"]
    rpe_trend = tail6["revenue_per_employee"].mean() if "revenue_per_employee" in tail6.columns else rpe_now

    if rpe_status in ("Red", "Amber"):
        insights.append({
            "status": rpe_status,
            "title": "Revenue per Employee Signals Productivity Gap",
            "body": (
                f"At ${rpe_now:,.0f}/month per employee, the team is generating below the ${15_000:,} SaaS benchmark. "
                f"The 6-month average of ${rpe_trend:,.0f} confirms this is structural rather than seasonal. "
                f"This typically indicates over-hiring ahead of revenue, or an inefficient go-to-market motion. "
                f"Recommend mapping headcount to revenue-generating activities and setting productivity targets "
                f"by department before approving future headcount additions."
            ),
        })
    else:
        insights.append({
            "status": "Green",
            "title": "Workforce Productivity Is Above Benchmark",
            "body": (
                f"Revenue per employee of ${rpe_now:,.0f}/month exceeds the ${15_000:,} SaaS benchmark, "
                f"indicating the team is generating strong output relative to its size. "
                f"6-month average of ${rpe_trend:,.0f} confirms this is a sustained strength. "
                f"Maintain hiring discipline to preserve this efficiency advantage as the company scales."
            ),
        })

    # Return top 5 insights, prioritizing Red > Amber > Green
    priority = {"Red": 0, "Amber": 1, "Green": 2}
    insights_sorted = sorted(insights, key=lambda x: priority[x["status"]])
    return insights_sorted[:5]

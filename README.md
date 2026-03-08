# SMB Financial Health Dashboard

A portfolio-grade **consulting analytics tool** that simulates how a tech consultant would analyze the financial health of small-to-medium SaaS businesses. Built with Python, Pandas, Streamlit, and Plotly.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.20+-purple?style=flat-square&logo=plotly)
![Pandas](https://img.shields.io/badge/Pandas-2.2+-green?style=flat-square&logo=pandas)

---

## Overview

This dashboard demonstrates end-to-end analytical capability — from raw data generation through KPI computation, benchmarking, and actionable consultant-style narrative. It mirrors the type of financial health monitoring a technology consultant would build for a CFO or board-level audience.

**Two fictional SaaS companies** are included, each with distinct financial profiles and embedded problem signals designed to surface meaningful analytical findings.

---

## Features

| Module | Description |
|---|---|
| **Synthetic Data Generator** | 24 months of realistic monthly financials with noise, growth deceleration, and cost signals |
| **KPI Engine** | Computes 6 key metrics: Gross Margin, MoM Growth, OpEx Ratio, Rev/Employee, Burn Rate, Runway |
| **Benchmarking Layer** | Compares each KPI to SaaS SMB industry benchmarks; assigns Red / Amber / Green status |
| **Streamlit Dashboard** | Multi-section interactive dashboard with time-series charts, scorecard table, and radar chart |
| **Consultant Findings** | Auto-generated plain-English insights prioritized by severity |
| **P&L Waterfall** | Visual breakdown of revenue → COGS → OpEx → net income for the latest month |

---

## Company Profiles

### NovaSaaS
> B2B project management SaaS — healthy growth with rising cost pressure

- Revenue starting at ~$180K/month, growing at ~5.5% MoM
- Gross margin begins at 74% but faces COGS creep over time
- Marketing spend surge baked in at month 14
- Hiring sprints at months 6, 12, and 18

### CloudForge
> DevOps tooling SaaS — aggressive growth strategy burning cash fast

- Faster initial growth (~7% MoM) but sharper deceleration
- Thinner margins from the start (COGS ratio ~38%, drifting higher)
- Higher cost-per-head and a large sales/marketing surge at month 10
- Cash burn accelerates as revenue growth slows — runway hits zero

---

## KPIs & Benchmarks

| KPI | Green | Amber | Red | Source |
|---|---|---|---|---|
| Gross Margin % | ≥ 70% | 60–70% | < 60% | SaaS Capital / Bessemer |
| Revenue Growth MoM | ≥ 5% | 2–5% | < 2% | OpenView SaaS benchmarks |
| OpEx Ratio | ≤ 40% | 40–55% | > 55% | SaaS Capital |
| Revenue / Employee | ≥ $15K/mo | $10–15K | < $10K | OpenView productivity benchmarks |
| Burn Rate | Profitable | < $30K/mo burn | ≥ $30K/mo burn | General startup guidance |
| Runway | ≥ 18 months | 12–18 months | < 12 months | Standard VC guidance |

---

## Project Structure

```
smb-financial-dashboard/
├── app.py                  # Main Streamlit application (5 dashboard sections)
├── requirements.txt        # Python dependencies
├── README.md
├── data/                   # Reserved for exported data (optional)
└── src/
    ├── __init__.py
    ├── data_generator.py   # Synthetic financial data generation (2 company profiles)
    ├── kpi_engine.py       # KPI calculation engine
    ├── benchmarks.py       # Industry benchmarks & RAG status logic
    └── insights.py         # Auto-generated consultant findings
```

---

## Getting Started

### Prerequisites
- Python 3.11 or higher

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd smb-financial-dashboard

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run app.py
```

The dashboard opens at `http://localhost:8501` in your browser.

---

## Dashboard Sections

1. **Company Overview** — Key metrics header: revenue, cash balance, gross margin, burn rate, headcount
2. **Financial Trends** — Interactive Plotly charts across three tabs:
   - Revenue & Profitability (revenue, gross profit, MoM growth bars color-coded by RAG status)
   - Cost Structure (revenue vs. COGS vs. OpEx, OpEx ratio trend)
   - Headcount & Productivity (headcount growth, revenue per employee)
3. **KPI Scorecard** — RAG-status table with benchmark comparisons + health radar chart
4. **Consultant Findings** — Auto-generated narrative insights, prioritized Red → Amber → Green
5. **Cash Flow & Burn Analysis** — P&L waterfall for latest month + cash balance/burn dual-axis chart

### Sidebar Controls
- **Company selector** — Switch between NovaSaaS and CloudForge
- **Date range slider** — Display 6 to 24 months of data

---

## Design

- **Color scheme**: Dark navy (`#0b1437`) background, white text, blue accent (`#4f8ef7`)
- **RAG colors**: Green `#00c896` · Amber `#f5a623` · Red `#e84545`
- All charts use a consistent dark-theme Plotly layout with transparent backgrounds
- Custom CSS for metric cards, RAG badges, and insight panels

---

## Skills Demonstrated

- **Data Engineering**: Synthetic data generation with controlled noise using NumPy
- **Financial Analytics**: KPI computation from raw financials using Pandas
- **Business Intelligence**: Benchmark comparison logic and RAG status framework
- **Insight Generation**: Rule-based narrative generation from analytical outputs
- **Data Visualization**: Multi-chart Plotly dashboard with waterfall, radar, time-series, and bar charts
- **UI/UX**: Custom CSS-styled Streamlit app with a professional dark-theme interface
- **Software Architecture**: Clean modular project structure (data → engine → benchmarks → app)

---

## Portfolio Context

This project demonstrates the type of analytical tooling a **technology consultant** might deliver to a CFO, finance team, or investor audience. It showcases:

- Ability to translate business questions into measurable KPIs
- Understanding of SaaS financial metrics and industry benchmarks
- Skill in building clear, audience-appropriate data visualizations
- Capacity to generate narrative insights from quantitative analysis

---

*All data is entirely synthetic. No real company is represented.*

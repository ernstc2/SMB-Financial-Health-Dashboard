"""
SMB Financial Health Dashboard
A portfolio-grade consulting analytics tool built with Python, Pandas, Streamlit, and Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_generator import generate_company_data, get_all_companies, get_company_profile
from src.kpi_engine import calculate_kpis, get_latest_kpis
from src.benchmarks import build_scorecard, BENCHMARKS, RAG_COLORS
from src.insights import generate_insights

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SMB Financial Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design Tokens ─────────────────────────────────────────────────────────────
NAVY       = "#0b1437"
NAVY_LIGHT = "#131d4f"
CARD_BG    = "#111936"
BORDER     = "#1e2d6b"
TEXT_WHITE = "#f0f4ff"
TEXT_MUTED = "#8b95c9"
ACCENT     = "#4f8ef7"
TEAL       = "#00c896"
AMBER      = "#f5a623"
RED        = "#e84545"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  html, body, [data-testid="stAppViewContainer"] {{
    background-color: {NAVY};
    color: {TEXT_WHITE};
    font-family: 'Inter', 'Segoe UI', sans-serif;
  }}
  [data-testid="stSidebar"] {{
    background-color: {NAVY_LIGHT};
    border-right: 1px solid {BORDER};
  }}
  [data-testid="stSidebar"] * {{ color: {TEXT_WHITE} !important; }}
  #MainMenu, footer, header {{ visibility: hidden; }}

  .metric-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px 24px;
    height: 100%;
  }}
  .metric-label {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    margin-bottom: 8px;
  }}
  .metric-value {{
    font-size: 28px;
    font-weight: 700;
    color: {TEXT_WHITE};
    line-height: 1.1;
  }}
  .metric-sub {{ font-size: 12px; color: {TEXT_MUTED}; margin-top: 6px; }}
  .metric-delta-pos {{ color: {TEAL}; font-weight: 600; }}
  .metric-delta-neg {{ color: {RED}; font-weight: 600; }}

  .section-header {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {ACCENT};
    padding-bottom: 8px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 20px;
    margin-top: 8px;
  }}

  .dash-title {{ font-size: 26px; font-weight: 800; color: {TEXT_WHITE}; letter-spacing: -0.3px; }}
  .dash-subtitle {{ font-size: 13px; color: {TEXT_MUTED}; margin-top: 4px; }}

  .rag-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .rag-table th {{
    background: {NAVY_LIGHT};
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-size: 11px;
    padding: 10px 14px;
    border-bottom: 1px solid {BORDER};
    text-align: left;
  }}
  .rag-table td {{
    padding: 11px 14px;
    border-bottom: 1px solid {BORDER};
    color: {TEXT_WHITE};
    vertical-align: middle;
  }}
  .rag-table tr:last-child td {{ border-bottom: none; }}
  .rag-table tr:hover td {{ background: rgba(79,142,247,0.05); }}
  .rag-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
  }}
  .badge-Green {{ background: rgba(0,200,150,0.15);  color: #00c896; border: 1px solid #00c896; }}
  .badge-Amber {{ background: rgba(245,166,35,0.15); color: #f5a623; border: 1px solid #f5a623; }}
  .badge-Red   {{ background: rgba(232,69,69,0.15);  color: #e84545; border: 1px solid #e84545; }}

  .insight-card {{
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 4px solid;
  }}
  .insight-Green {{ border-color: {TEAL};  background: rgba(0,200,150,0.06); }}
  .insight-Amber {{ border-color: {AMBER}; background: rgba(245,166,35,0.06); }}
  .insight-Red   {{ border-color: {RED};   background: rgba(232,69,69,0.06); }}
  .insight-title {{ font-weight: 700; font-size: 14px; margin-bottom: 6px; }}
  .insight-title-Green {{ color: {TEAL}; }}
  .insight-title-Amber {{ color: {AMBER}; }}
  .insight-title-Red   {{ color: {RED}; }}
  .insight-body {{ font-size: 13px; color: {TEXT_MUTED}; line-height: 1.6; }}

  .styled-divider {{ border: none; border-top: 1px solid {BORDER}; margin: 32px 0; }}
</style>
""", unsafe_allow_html=True)

# ── Chart Theme ───────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT_WHITE, size=12),
    margin=dict(l=12, r=12, t=40, b=12),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(size=11),
    ),
    xaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(size=10, color=TEXT_MUTED), showgrid=False),
    yaxis=dict(gridcolor="#1a2460", linecolor=BORDER, tickfont=dict(size=10, color=TEXT_MUTED)),
    hovermode="x unified",
)


def fmt_currency(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    elif abs(v) >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"


def metric_card(label: str, value: str, sub: str = "", delta: str = "", delta_pos: bool | None = None) -> str:
    if delta:
        cls = "metric-delta-pos" if delta_pos is True else "metric-delta-neg" if delta_pos is False else "metric-sub"
        extra = f'<div class="metric-sub"><span class="{cls}">{delta}</span></div>'
    else:
        extra = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      {extra}
    </div>
    """


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 8px 0 20px 0;">
      <div style="font-size:18px; font-weight:800; color:{TEXT_WHITE};">SMB Financial</div>
      <div style="font-size:11px; color:{TEXT_MUTED}; letter-spacing:1.2px; text-transform:uppercase;">Health Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    companies = get_all_companies()
    selected_company = st.selectbox("Select Company", companies,
                                    help="Switch between fictional company profiles")

    profile = get_company_profile(selected_company)
    st.markdown(f"""
    <div style="background:{CARD_BG}; border:1px solid {BORDER}; border-radius:10px; padding:14px 16px; margin-top:8px;">
      <div style="font-size:11px; font-weight:700; color:{TEXT_MUTED}; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Company Profile</div>
      <div style="font-size:12px; color:{TEXT_WHITE}; margin-bottom:4px;">{profile['description']}</div>
      <div style="font-size:11px; color:{TEXT_MUTED}; margin-top:8px;">Industry: {profile['industry']}</div>
      <div style="font-size:11px; color:{TEXT_MUTED};">Founded: {profile['founded']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px;'>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:11px; font-weight:700; color:{TEXT_MUTED}; letter-spacing:1px; text-transform:uppercase; margin-bottom:10px;">Date Range</div>', unsafe_allow_html=True)
    month_range = st.slider("Months to display", min_value=6, max_value=24, value=24, step=3,
                            label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:32px; padding-top:20px; border-top:1px solid {BORDER};">
      <div style="font-size:10px; color:{TEXT_MUTED}; line-height:1.6;">
        Built with Python · Pandas · Streamlit · Plotly<br>
        Data is entirely synthetic for demo purposes.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Data Pipeline ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(company: str) -> pd.DataFrame:
    return calculate_kpis(generate_company_data(company))


df_full = load_data(selected_company)
df = df_full.tail(month_range).copy().reset_index(drop=True)
kpis = get_latest_kpis(df)
scorecard = build_scorecard(kpis)
insights = generate_insights(scorecard, df, kpis)

rag_counts = {"Green": 0, "Amber": 0, "Red": 0}
for row in scorecard:
    rag_counts[row["Status"]] += 1

overall_status = (
    "Green" if rag_counts["Red"] == 0 and rag_counts["Amber"] <= 1 else
    "Red"   if rag_counts["Red"] >= 2 else "Amber"
)
overall_color = RAG_COLORS[overall_status]


# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <div style="padding: 4px 0 20px 0;">
      <div class="dash-title">SMB Financial Health Dashboard</div>
      <div class="dash-subtitle">Consulting Analytics · 24-Month Synthetic Data · {kpis['month_label']} (Latest)</div>
    </div>
    """, unsafe_allow_html=True)
with col_status:
    r, g, b = tuple(int(overall_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    st.markdown(f"""
    <div style="text-align:right; padding-top:6px;">
      <div style="font-size:11px; color:{TEXT_MUTED}; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px;">Overall Health</div>
      <div style="display:inline-block; background:rgba({r},{g},{b},0.15);
           border:1px solid {overall_color}; border-radius:8px; padding:8px 18px;">
        <span style="font-size:20px; font-weight:800; color:{overall_color};">{overall_status.upper()}</span>
      </div>
      <div style="font-size:11px; color:{TEXT_MUTED}; margin-top:6px;">
        {rag_counts['Green']}G · {rag_counts['Amber']}A · {rag_counts['Red']}R
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)


# ── Section 1: Company Overview ───────────────────────────────────────────────
st.markdown('<div class="section-header">01 · Company Overview</div>', unsafe_allow_html=True)

prev_revenue = df.iloc[-2]["revenue"] if len(df) >= 2 else kpis["revenue"]
rev_delta = ((kpis["revenue"] - prev_revenue) / prev_revenue) * 100

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(metric_card("Monthly Revenue", fmt_currency(kpis["revenue"]),
                            delta=f"{rev_delta:+.1f}% MoM", delta_pos=rev_delta >= 0), unsafe_allow_html=True)
with c2:
    runway_sub = (f"{kpis['runway_months']:.0f} mo runway"
                  if kpis["runway_months"] < 999 else "Cash flow positive")
    st.markdown(metric_card("Cash Balance", fmt_currency(kpis["cash_balance"]), sub=runway_sub), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Gross Margin", f"{kpis['gross_margin_pct']:.1f}%", sub="Benchmark: 70%"), unsafe_allow_html=True)
with c4:
    burn = kpis["burn_rate"]
    burn_str = f"+{fmt_currency(burn)}" if burn >= 0 else f"-{fmt_currency(abs(burn))}"
    st.markdown(metric_card("Net Cash Flow", burn_str,
                            delta="Cash flow positive" if burn >= 0 else "Burning cash",
                            delta_pos=burn >= 0), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("Headcount", str(int(kpis["headcount"])),
                            sub=f"{fmt_currency(kpis['revenue_per_employee'])}/employee/mo"), unsafe_allow_html=True)

st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)


# ── Section 2: Financial Trends ───────────────────────────────────────────────
st.markdown('<div class="section-header">02 · Financial Trends</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Revenue & Profitability", "Cost Structure", "Headcount & Productivity"])

with tab1:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("Revenue vs. Gross Profit", "Revenue Growth MoM %"))

    fig.add_trace(go.Scatter(x=df["month_label"], y=df["revenue"], name="Revenue", mode="lines",
                             line=dict(color=ACCENT, width=2.5),
                             fill="tozeroy", fillcolor="rgba(79,142,247,0.07)",
                             hovertemplate="$%{y:,.0f}"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["month_label"], y=df["gross_profit"], name="Gross Profit", mode="lines",
                             line=dict(color=TEAL, width=2.5),
                             fill="tozeroy", fillcolor="rgba(0,200,150,0.06)",
                             hovertemplate="$%{y:,.0f}"), row=1, col=1)

    bar_colors = [TEAL if v >= 5 else AMBER if v >= 2 else RED
                  for v in df["revenue_growth_mom"].fillna(0)]
    fig.add_trace(go.Bar(x=df["month_label"], y=df["revenue_growth_mom"], name="Growth MoM %",
                         marker_color=bar_colors, opacity=0.85, hovertemplate="%{y:.1f}%"), row=2, col=1)
    fig.add_hline(y=5, line_dash="dash", line_color=TEAL, line_width=1,
                  annotation_text="Benchmark 5%", annotation_font_color=TEAL,
                  annotation_font_size=10, row=2, col=1)

    fig.update_layout(**CHART_LAYOUT, height=440, showlegend=True)
    fig.update_yaxes(tickprefix="$", tickformat=",.0f", row=1, col=1)
    fig.update_yaxes(ticksuffix="%", row=2, col=1)
    fig.update_annotations(font_color=TEXT_MUTED, font_size=11)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tab2:
    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                         subplot_titles=("Revenue vs. COGS vs. OpEx", "Operating Expense Ratio (%)"))

    fig2.add_trace(go.Scatter(x=df["month_label"], y=df["revenue"], name="Revenue", mode="lines",
                              line=dict(color=ACCENT, width=2.5), hovertemplate="$%{y:,.0f}"), row=1, col=1)
    fig2.add_trace(go.Scatter(x=df["month_label"], y=df["cogs"], name="COGS", mode="lines",
                              line=dict(color=AMBER, width=2, dash="dot"), hovertemplate="$%{y:,.0f}"), row=1, col=1)
    fig2.add_trace(go.Scatter(x=df["month_label"], y=df["opex"], name="OpEx", mode="lines",
                              line=dict(color=RED, width=2, dash="dash"), hovertemplate="$%{y:,.0f}"), row=1, col=1)

    opex_colors = [TEAL if v <= 40 else AMBER if v <= 55 else RED for v in df["opex_ratio"]]
    fig2.add_trace(go.Bar(x=df["month_label"], y=df["opex_ratio"], name="OpEx Ratio",
                          marker_color=opex_colors, opacity=0.85, hovertemplate="%{y:.1f}%"), row=2, col=1)
    fig2.add_hline(y=40, line_dash="dash", line_color=TEAL, line_width=1,
                   annotation_text="Benchmark 40%", annotation_font_color=TEAL,
                   annotation_font_size=10, row=2, col=1)
    fig2.add_hline(y=55, line_dash="dash", line_color=RED, line_width=1,
                   annotation_text="Red threshold 55%", annotation_font_color=RED,
                   annotation_font_size=10, row=2, col=1)

    fig2.update_layout(**CHART_LAYOUT, height=440, showlegend=True)
    fig2.update_yaxes(tickprefix="$", tickformat=",.0f", row=1, col=1)
    fig2.update_yaxes(ticksuffix="%", row=2, col=1)
    fig2.update_annotations(font_color=TEXT_MUTED, font_size=11)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

with tab3:
    fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                         subplot_titles=("Headcount Over Time", "Revenue per Employee ($/month)"))

    fig3.add_trace(go.Scatter(x=df["month_label"], y=df["headcount"], name="Headcount",
                              mode="lines+markers", line=dict(color=ACCENT, width=2.5),
                              marker=dict(size=5, color=ACCENT),
                              hovertemplate="%{y} employees"), row=1, col=1)

    rpe_colors = [TEAL if v >= 15000 else AMBER if v >= 10000 else RED
                  for v in df["revenue_per_employee"]]
    fig3.add_trace(go.Bar(x=df["month_label"], y=df["revenue_per_employee"], name="Rev/Employee",
                          marker_color=rpe_colors, opacity=0.85, hovertemplate="$%{y:,.0f}"), row=2, col=1)
    fig3.add_hline(y=15000, line_dash="dash", line_color=TEAL, line_width=1,
                   annotation_text="Benchmark $15K", annotation_font_color=TEAL,
                   annotation_font_size=10, row=2, col=1)

    fig3.update_layout(**CHART_LAYOUT, height=440, showlegend=True)
    fig3.update_yaxes(tickprefix="$", tickformat=",.0f", row=2, col=1)
    fig3.update_annotations(font_color=TEXT_MUTED, font_size=11)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)


# ── Section 3: KPI Scorecard ──────────────────────────────────────────────────
st.markdown('<div class="section-header">03 · KPI Scorecard</div>', unsafe_allow_html=True)

col_score, col_radar = st.columns([3, 2])

with col_score:
    rows_html = ""
    for row in scorecard:
        rows_html += f"""
        <tr>
          <td><strong>{row['KPI']}</strong><br>
              <span style="font-size:11px; color:{TEXT_MUTED};">{row['_description']}</span></td>
          <td style="font-weight:700; font-size:15px;">{row['Value']}</td>
          <td style="font-size:12px; color:{TEXT_MUTED};">{row['Benchmark']}</td>
          <td><span class="rag-badge badge-{row['Status']}">{row['Status'].upper()}</span></td>
        </tr>
        """
    st.markdown(f"""
    <table class="rag-table">
      <thead><tr>
        <th style="width:35%;">KPI</th>
        <th style="width:18%;">Current Value</th>
        <th style="width:32%;">Benchmark</th>
        <th style="width:15%;">Status</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

with col_radar:
    def normalize_kpi(key, value):
        bm = BENCHMARKS[key]
        if bm.higher_is_better:
            score = min(1.0, max(0.0, (value - bm.amber_threshold) /
                                      max(0.01, bm.green_threshold - bm.amber_threshold + bm.green_threshold * 0.3)))
        else:
            score = min(1.0, max(0.0, (bm.amber_threshold - value) /
                                      max(0.01, bm.amber_threshold - bm.green_threshold + bm.green_threshold * 0.3)))
        return round(score, 3)

    radar_keys   = ["gross_margin_pct", "revenue_growth_mom", "opex_ratio",
                    "revenue_per_employee", "burn_rate", "runway_months"]
    radar_labels = ["Gross Margin", "Rev Growth", "OpEx Efficiency",
                    "Rev/Employee", "Cash Flow", "Runway"]
    radar_scores = [normalize_kpi(k, kpis[k]) for k in radar_keys]

    fig_radar = go.Figure(go.Scatterpolar(
        r=radar_scores + [radar_scores[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        fillcolor="rgba(79,142,247,0.15)",
        line=dict(color=ACCENT, width=2),
        name=selected_company,
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[0.7] * (len(radar_labels) + 1),
        theta=radar_labels + [radar_labels[0]],
        mode="lines",
        line=dict(color=TEAL, width=1.5, dash="dash"),
        name="Benchmark",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False,
                            gridcolor=BORDER, linecolor=BORDER),
            angularaxis=dict(tickfont=dict(size=11, color=TEXT_WHITE),
                             gridcolor=BORDER, linecolor=BORDER),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_WHITE),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        margin=dict(l=20, r=20, t=30, b=20),
        height=320,
        title=dict(text="Health Score Radar", font=dict(size=13, color=TEXT_MUTED), x=0.5),
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)


# ── Section 4: Consultant Findings ────────────────────────────────────────────
st.markdown('<div class="section-header">04 · Consultant Findings</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="font-size:13px; color:{TEXT_MUTED}; margin-bottom:20px; line-height:1.6;">
  The following findings are auto-generated based on current KPI performance relative to SaaS SMB
  industry benchmarks. Red and Amber items require management attention; Green findings represent
  areas of strength.
</div>
""", unsafe_allow_html=True)

for i, insight in enumerate(insights, 1):
    status = insight["status"]
    icon = "🔴" if status == "Red" else "🟡" if status == "Amber" else "🟢"
    st.markdown(f"""
    <div class="insight-card insight-{status}">
      <div class="insight-title insight-title-{status}">{icon} Finding {i}: {insight['title']}</div>
      <div class="insight-body">{insight['body']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)


# ── Section 5: Cash Flow & Burn Analysis ─────────────────────────────────────
st.markdown('<div class="section-header">05 · Cash Flow & Burn Analysis</div>', unsafe_allow_html=True)

col_wf, col_cash = st.columns(2)

with col_wf:
    latest = df.iloc[-1]
    fig_wf = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Revenue", "COGS", "OpEx", "Net Income"],
        y=[latest["revenue"], -latest["cogs"], -latest["opex"], latest["net_income"]],
        connector=dict(line=dict(color=BORDER, width=1.5)),
        increasing=dict(marker_color=TEAL),
        decreasing=dict(marker_color=RED),
        totals=dict(marker_color=ACCENT),
        texttemplate="$%{y:,.0f}",
        textposition="outside",
        textfont=dict(size=11, color=TEXT_WHITE),
    ))
    fig_wf.update_layout(
        **CHART_LAYOUT, height=320, showlegend=False,
        title=dict(text=f"P&L Waterfall — {latest['month_label']}", font=dict(size=13, color=TEXT_MUTED)),
        yaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor="#1a2460"),
    )
    st.plotly_chart(fig_wf, use_container_width=True, config={"displayModeBar": False})

with col_cash:
    fig_cash = go.Figure()
    fig_cash.add_trace(go.Scatter(
        x=df["month_label"], y=df["cash_balance"], name="Cash Balance", mode="lines",
        line=dict(color=ACCENT, width=2.5),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.08)",
        hovertemplate="$%{y:,.0f}",
    ))
    burn_colors = [TEAL if v >= 0 else RED for v in df["burn_rate"]]
    fig_cash.add_trace(go.Bar(
        x=df["month_label"], y=df["burn_rate"], name="Net Cash Flow",
        marker_color=burn_colors, opacity=0.6, yaxis="y2",
        hovertemplate="$%{y:,.0f}",
    ))
    fig_cash.update_layout(
        **CHART_LAYOUT, height=320, showlegend=True,
        title=dict(text="Cash Balance & Monthly Net Flow", font=dict(size=13, color=TEXT_MUTED)),
        yaxis=dict(tickprefix="$", tickformat=",.0f", title="Cash Balance", gridcolor="#1a2460"),
        yaxis2=dict(tickprefix="$", tickformat=",.0f", title="Net Cash Flow",
                    overlaying="y", side="right", showgrid=False,
                    zeroline=True, zerolinecolor=BORDER),
    )
    st.plotly_chart(fig_cash, use_container_width=True, config={"displayModeBar": False})


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding:32px 0 16px 0; border-top:1px solid {BORDER}; margin-top:24px;">
  <div style="font-size:12px; color:{TEXT_MUTED};">
    SMB Financial Health Dashboard · Built as a tech consulting portfolio project
    · All data is entirely synthetic · No real company is represented
  </div>
</div>
""", unsafe_allow_html=True)

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
from src.template import read_uploaded_file, get_template_csv_bytes, validate_uploaded_df

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SMB Financial Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design Tokens ─────────────────────────────────────────────────────────────
NAVY       = "#0d1117"   # near-black charcoal
NAVY_LIGHT = "#161b22"   # sidebar / secondary bg
CARD_BG    = "#1c2333"   # card surfaces
BORDER     = "#30363d"   # neutral gray — no blue tint
TEXT_WHITE = "#e6edf3"   # primary text
TEXT_MUTED = "#8b949e"   # muted gray — neutral, not blue
ACCENT     = "#3b82f6"   # clean blue — reserved for accent only
TEAL       = "#00c896"   # RAG green (unchanged)
AMBER      = "#f5a623"   # RAG amber (unchanged)
RED        = "#e84545"   # RAG red (unchanged)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@500;600;700;800&display=swap');

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
  /* Force sidebar always open and remove collapse control */
  [data-testid="stSidebar"] {{
    transform: none !important;
    width: 21rem !important;
    min-width: 21rem !important;
  }}
  [data-testid="stSidebar"] > div:first-child {{
    width: 21rem !important;
  }}
  /* Hide ALL sidebar collapse/expand controls */
  [data-testid="collapsedControl"],
  [data-testid="stSidebarCollapse"],
  [data-testid="stSidebarCollapseButton"],
  section[data-testid="stSidebar"] button:has(svg) {{
    display: none !important;
    visibility: hidden !important;
  }}

  /* ── Metric Cards ── */
  .metric-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 22px 24px 18px;
    height: 100%;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    cursor: default;
  }}
  .metric-card:hover {{
    border-color: rgba(59,130,246,0.5);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
  }}
  .metric-label {{
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    margin-bottom: 10px;
  }}
  .metric-value {{
    font-family: 'Poppins', 'Inter', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: {TEXT_WHITE};
    line-height: 1.1;
    letter-spacing: -0.5px;
  }}
  .metric-sub {{ font-size: 13px; color: {TEXT_MUTED}; margin-top: 8px; }}
  .metric-delta-pos {{ color: {TEAL}; font-weight: 600; }}
  .metric-delta-neg {{ color: {RED}; font-weight: 600; }}

  /* ── Section Headers ── */
  .section-header {{
    font-family: 'Poppins', 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {ACCENT};
    padding: 0 0 10px 14px;
    border-bottom: 1px solid {BORDER};
    border-left: 3px solid {ACCENT};
    margin-bottom: 24px;
    margin-top: 8px;
  }}

  /* ── Dashboard Title ── */
  .dash-title {{
    font-family: 'Poppins', 'Inter', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: {TEXT_WHITE};
    letter-spacing: -0.5px;
  }}
  .dash-subtitle {{ font-size: 14px; color: {TEXT_MUTED}; margin-top: 6px; line-height: 1.5; }}

  /* ── Insight Cards ── */
  .insight-card {{
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 12px;
    border: 1px solid {BORDER};
    border-left: 4px solid;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}
  .insight-card:hover {{
    transform: translateX(3px);
    box-shadow: 0 2px 16px rgba(0,0,0,0.25);
  }}
  .insight-Green {{ border-color: {TEAL};  background: rgba(0,200,150,0.05); }}
  .insight-Amber {{ border-color: {AMBER}; background: rgba(245,166,35,0.05); }}
  .insight-Red   {{ border-color: {RED};   background: rgba(232,69,69,0.05); }}
  .insight-title {{
    font-family: 'Poppins', 'Inter', sans-serif;
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 8px;
  }}
  .insight-title-Green {{ color: {TEAL}; }}
  .insight-title-Amber {{ color: {AMBER}; }}
  .insight-title-Red   {{ color: {RED}; }}
  .insight-body {{ font-size: 14px; color: {TEXT_MUTED}; line-height: 1.7; }}

  .styled-divider {{ border: none; border-top: 1px solid {BORDER}; margin: 36px 0; }}
</style>
""", unsafe_allow_html=True)

# ── Chart Theme ───────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Poppins, Inter, Segoe UI, sans-serif", color=TEXT_WHITE, size=13),
    margin=dict(l=12, r=12, t=40, b=12),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(size=12),
    ),
    xaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(size=11, color=TEXT_MUTED), showgrid=False),
    yaxis=dict(gridcolor="#21262d", linecolor=BORDER, tickfont=dict(size=11, color=TEXT_MUTED)),
    hovermode="x unified",
)


def fmt_currency(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    elif abs(v) >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"


def metric_card(label: str, value: str, sub: str = "", delta: str = "", delta_pos: bool | None = None, top_color: str = None) -> str:
    if delta:
        cls = "metric-delta-pos" if delta_pos is True else "metric-delta-neg" if delta_pos is False else "metric-sub"
        extra = f'<div class="metric-sub"><span class="{cls}">{delta}</span></div>'
    else:
        extra = f'<div class="metric-sub">{sub}</div>' if sub else ""
    border_top = f"border-top: 3px solid {top_color or ACCENT};"
    return f"""
    <div class="metric-card" style="{border_top}">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      {extra}
    </div>
    """


# ── Session State ─────────────────────────────────────────────────────────────
st.session_state.setdefault("uploaded_companies", {})
st.session_state.setdefault("_upload_success", None)
st.session_state.setdefault("_pending_select", None)

# Apply pending company selection BEFORE the selectbox widget is instantiated
if st.session_state._pending_select:
    st.session_state.company_select = st.session_state._pending_select
    st.session_state._pending_select = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 8px 0 20px 0;">
      <div style="font-size:18px; font-weight:800; color:{TEXT_WHITE};">SMB Financial</div>
      <div style="font-size:12px; color:{TEXT_MUTED}; letter-spacing:1.2px; text-transform:uppercase;">Health Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # Build unified company list: sample companies + any uploaded companies
    _sample_companies = get_all_companies()
    _uploaded_keys = list(st.session_state.uploaded_companies.keys())
    # Disambiguate if an uploaded name collides with a sample name
    _uploaded_display = [
        (f"{k} (uploaded)" if k in _sample_companies else k)
        for k in _uploaded_keys
    ]
    companies = _sample_companies + _uploaded_display
    selected_company = st.selectbox("Select Company", companies,
                                    key="company_select",
                                    help="Switch between fictional company profiles or select an uploaded company")

    compare_mode = st.checkbox("Compare two companies", key="compare_mode",
                               help="Show two companies side by side")
    if compare_mode:
        _compare_choices = [c for c in companies if c != selected_company]
        compare_company = st.selectbox("Compare with", _compare_choices, key="compare_select",
                                       help="Select a second company to compare against")
    else:
        compare_company = None

    # Show success message when a company was just uploaded
    if st.session_state._upload_success:
        _success_name = st.session_state._upload_success
        st.success(f"✓ \"{_success_name}\" added! Available in the dropdown above and persists if you upload more companies.")
        st.session_state._upload_success = None

    # Upload section — defined before data pipeline so uploaded_file is available
    st.markdown(f'<div style="font-size:11px; font-weight:700; color:{TEXT_MUTED}; letter-spacing:1px; text-transform:uppercase; margin-bottom:10px; margin-top:24px;">Upload Your Data</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls"],
        key="file_upload",
        help="Upload a file matching the template format",
    )
    st.download_button(
        label="Download Template CSV",
        data=get_template_csv_bytes(),
        file_name="smb_financial_template.csv",
        mime="text/csv",
    )
    st.markdown(
        f'<div style="font-size:12px; color:{TEXT_MUTED}; margin-top:6px; line-height:1.5;">'
        "Upload your company's monthly financials. Download the template to see the required format."
        "</div>",
        unsafe_allow_html=True,
    )

    # Error container placed right after upload widget so errors appear here,
    # not at the bottom of the sidebar
    upload_errors = st.container()

    # Company profile card — shows sample profile or uploaded file name
    # Resolve the internal key: strip " (uploaded)" suffix if present for session_state lookup
    _selected_key = selected_company.removesuffix(" (uploaded)")
    if _selected_key in st.session_state.uploaded_companies:
        st.markdown(f"""
    <div style="background:{CARD_BG}; border:1px solid {BORDER}; border-radius:10px; padding:14px 16px; margin-top:8px;">
      <div style="font-size:11px; font-weight:700; color:{TEXT_MUTED}; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Uploaded File</div>
      <div style="font-size:14px; color:{TEXT_WHITE}; margin-bottom:4px;">{_selected_key}</div>
      <div style="font-size:13px; color:{TEXT_MUTED}; margin-top:8px;">Source: User upload</div>
    </div>
        """, unsafe_allow_html=True)
    else:
        profile = get_company_profile(selected_company)
        st.markdown(f"""
    <div style="background:{CARD_BG}; border:1px solid {BORDER}; border-radius:10px; padding:14px 16px; margin-top:8px;">
      <div style="font-size:11px; font-weight:700; color:{TEXT_MUTED}; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Company Profile</div>
      <div style="font-size:14px; color:{TEXT_WHITE}; margin-bottom:4px;">{profile['description']}</div>
      <div style="font-size:13px; color:{TEXT_MUTED}; margin-top:8px;">Industry: {profile['industry']}</div>
      <div style="font-size:13px; color:{TEXT_MUTED};">Founded: {profile['founded']}</div>
    </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px;'>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:11px; font-weight:700; color:{TEXT_MUTED}; letter-spacing:1px; text-transform:uppercase; margin-bottom:10px;">Date Range</div>', unsafe_allow_html=True)
    month_range = st.slider("Months to display", min_value=6, max_value=24, value=24, step=3,
                            label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:32px; padding-top:20px; border-top:1px solid {BORDER};">
      <div style="font-size:13px; color:{TEXT_MUTED}; line-height:1.6;">
        Built with Python · Pandas · Streamlit · Plotly<br>
        Data is entirely synthetic for demo purposes.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Data Pipeline ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(company: str, v: str = "v2") -> pd.DataFrame:
    return calculate_kpis(generate_company_data(company))


# Process the upload widget: parse, validate, store in session_state
if uploaded_file is not None:
    try:
        df_uploaded = read_uploaded_file(uploaded_file)
        errors = validate_uploaded_df(df_uploaded)
        if errors:
            with upload_errors:
                for msg in errors:
                    st.error(msg)
            # Do NOT store invalid data in session_state
        else:
            display_name = uploaded_file.name.rsplit(".", 1)[0]
            is_new = display_name not in st.session_state.uploaded_companies
            st.session_state.uploaded_companies[display_name] = df_uploaded
            if is_new:
                # Auto-select the newly uploaded company in the dropdown
                _select_name = f"{display_name} (uploaded)" if display_name in _sample_companies else display_name
                st.session_state._pending_select = _select_name
                st.session_state._upload_success = display_name
                st.rerun()
    except Exception as e:
        with upload_errors:
            st.error(f"Could not read file: {e}")

# Unified data pipeline: load from session_state or sample based on selected_company
# Resolve internal key (strip " (uploaded)" suffix used for disambiguation)
_pipeline_key = selected_company.removesuffix(" (uploaded)")
if _pipeline_key in st.session_state.uploaded_companies:
    df_full = calculate_kpis(st.session_state.uploaded_companies[_pipeline_key])
else:
    df_full = load_data(selected_company, v="v2")

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

# ── Comparison data pipeline ───────────────────────────────────────────────────
if compare_mode and compare_company:
    # Rename company A variables for clarity
    df_a      = df
    kpis_a    = kpis
    scorecard_a = scorecard
    insights_a  = insights

    # Load company B data using the same unified pipeline logic
    _cmp_key = compare_company.removesuffix(" (uploaded)")
    if _cmp_key in st.session_state.uploaded_companies:
        df_full_b = calculate_kpis(st.session_state.uploaded_companies[_cmp_key])
    else:
        df_full_b = load_data(compare_company, v="v2")

    df_b      = df_full_b.tail(month_range).copy().reset_index(drop=True)
    kpis_b    = get_latest_kpis(df_b)
    scorecard_b = build_scorecard(kpis_b)
    insights_b  = generate_insights(scorecard_b, df_b, kpis_b)

    rag_counts_b = {"Green": 0, "Amber": 0, "Red": 0}
    for _row in scorecard_b:
        rag_counts_b[_row["Status"]] += 1

    overall_status_b = (
        "Green" if rag_counts_b["Red"] == 0 and rag_counts_b["Amber"] <= 1 else
        "Red"   if rag_counts_b["Red"] >= 2 else "Amber"
    )
    overall_color_b = RAG_COLORS[overall_status_b]


# ── Comparison View ───────────────────────────────────────────────────────────
if compare_mode and compare_company:

    # ── Comparison Header ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="padding: 4px 0 8px 0;">
      <div class="dash-title">Company Comparison</div>
      <div class="dash-subtitle">Side-by-side KPI analysis · {month_range}-month window</div>
    </div>
    """, unsafe_allow_html=True)

    def _rag_badge(status, color, rag_c):
        r_, g_, b_ = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        return (f"<div style='display:inline-block; background:rgba({r_},{g_},{b_},0.15); "
                f"border:1px solid {color}; border-radius:8px; padding:6px 14px;'>"
                f"<span style='font-size:16px; font-weight:800; color:{color};'>{status.upper()}</span></div>"
                f"<div style='font-size:12px; color:{TEXT_MUTED}; margin-top:4px;'>"
                f"{rag_c['Green']}G · {rag_c['Amber']}A · {rag_c['Red']}R</div>")

    h_a, h_b = st.columns(2)
    with h_a:
        st.markdown(f"""
        <div style="background:{CARD_BG}; border:1px solid {ACCENT}; border-top:3px solid {ACCENT};
                    border-radius:10px; padding:16px 20px; text-align:center;">
          <div style="font-size:15px; font-weight:700; color:{TEXT_WHITE}; margin-bottom:8px;">{selected_company}</div>
          {_rag_badge(overall_status, overall_color, rag_counts)}
        </div>
        """, unsafe_allow_html=True)
    with h_b:
        st.markdown(f"""
        <div style="background:{CARD_BG}; border:1px solid {TEAL}; border-top:3px solid {TEAL};
                    border-radius:10px; padding:16px 20px; text-align:center;">
          <div style="font-size:15px; font-weight:700; color:{TEXT_WHITE}; margin-bottom:8px;">{compare_company}</div>
          {_rag_badge(overall_status_b, overall_color_b, rag_counts_b)}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── Section 1: KPI Comparison Table ───────────────────────────────────────
    st.markdown('<div class="section-header">01 · KPI Comparison</div>', unsafe_allow_html=True)

    RAG_COLOR_MAP = {"Green": TEAL, "Amber": AMBER, "Red": RED}
    RAG_BG_MAP    = {"Green": "rgba(0,200,150,0.15)", "Amber": "rgba(245,166,35,0.15)", "Red": "rgba(232,69,69,0.15)"}

    hstyle = f"font-size:11px; color:{TEXT_MUTED}; font-weight:600; text-transform:uppercase; letter-spacing:.8px; margin:0;"
    th1, th2, th3, th4, th5, th6 = st.columns([2.5, 1.5, 1.2, 1.5, 1.2, 0.8])
    th1.markdown(f"<p style='{hstyle}'>KPI</p>", unsafe_allow_html=True)
    th2.markdown(f"<p style='{hstyle}'>{selected_company[:14]}</p>", unsafe_allow_html=True)
    th3.markdown(f"<p style='{hstyle}'>Status</p>", unsafe_allow_html=True)
    th4.markdown(f"<p style='{hstyle}'>{compare_company[:14]}</p>", unsafe_allow_html=True)
    th5.markdown(f"<p style='{hstyle}'>Status</p>", unsafe_allow_html=True)
    th6.markdown(f"<p style='{hstyle}'>Better</p>", unsafe_allow_html=True)
    st.divider()

    _rag_order = {"Green": 0, "Amber": 1, "Red": 2}

    for row_a, row_b in zip(scorecard_a, scorecard_b):
        col_a_better = _rag_order[row_a["Status"]] < _rag_order[row_b["Status"]]
        col_b_better = _rag_order[row_b["Status"]] < _rag_order[row_a["Status"]]
        color_a = RAG_COLOR_MAP[row_a["Status"]]
        bg_a    = RAG_BG_MAP[row_a["Status"]]
        color_b = RAG_COLOR_MAP[row_b["Status"]]
        bg_b    = RAG_BG_MAP[row_b["Status"]]
        winner  = (f"<span style='color:{ACCENT}; font-weight:700;'>A</span>" if col_a_better
                   else f"<span style='color:{TEAL}; font-weight:700;'>B</span>" if col_b_better
                   else "<span style='color:{TEXT_MUTED};'>—</span>")

        tc1, tc2, tc3, tc4, tc5, tc6 = st.columns([2.5, 1.5, 1.2, 1.5, 1.2, 0.8])
        tc1.markdown(f"**{row_a['KPI']}**")
        tc2.markdown(f"**{row_a['Value']}**")
        tc3.markdown(f"<span style='background:{bg_a}; color:{color_a}; border:1px solid {color_a}; "
                     f"padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700;'>"
                     f"{row_a['Status'].upper()}</span>", unsafe_allow_html=True)
        tc4.markdown(f"**{row_b['Value']}**")
        tc5.markdown(f"<span style='background:{bg_b}; color:{color_b}; border:1px solid {color_b}; "
                     f"padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700;'>"
                     f"{row_b['Status'].upper()}</span>", unsafe_allow_html=True)
        tc6.markdown(winner, unsafe_allow_html=True)
        st.divider()

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── Section 2: Dual Radar Chart ───────────────────────────────────────────
    st.markdown('<div class="section-header">02 · Health Score Radar</div>', unsafe_allow_html=True)

    def normalize_kpi_cmp(key, value):
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

    scores_a = [normalize_kpi_cmp(k, kpis_a[k]) for k in radar_keys]
    scores_b = [normalize_kpi_cmp(k, kpis_b[k]) for k in radar_keys]

    fig_cmp_radar = go.Figure()
    fig_cmp_radar.add_trace(go.Scatterpolar(
        r=scores_a + [scores_a[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        fillcolor="rgba(59,130,246,0.12)",
        line=dict(color=ACCENT, width=2.5),
        name=selected_company,
    ))
    fig_cmp_radar.add_trace(go.Scatterpolar(
        r=scores_b + [scores_b[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        fillcolor="rgba(0,200,150,0.10)",
        line=dict(color=TEAL, width=2.5),
        name=compare_company,
    ))
    fig_cmp_radar.add_trace(go.Scatterpolar(
        r=[0.7] * (len(radar_labels) + 1),
        theta=radar_labels + [radar_labels[0]],
        mode="lines",
        line=dict(color=AMBER, width=1.5, dash="dash"),
        name="Benchmark",
    ))
    fig_cmp_radar.update_layout(
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
        margin=dict(l=20, r=20, t=40, b=20),
        height=380,
        title=dict(text="Health Score Radar — Both Companies", font=dict(size=13, color=TEXT_MUTED), x=0.5),
    )
    st.plotly_chart(fig_cmp_radar, use_container_width=True, config={"displayModeBar": False})
    st.caption("Each axis = one KPI, normalized 0 (worst) → 1 (best). Dashed line = benchmark.")

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── Section 3: Revenue Trend Comparison ───────────────────────────────────
    st.markdown('<div class="section-header">03 · Revenue Trend Comparison</div>', unsafe_allow_html=True)

    # Use month index (Month 1, 2, ...) so companies with different date ranges align
    _months_a = [f"Month {i+1}" for i in range(len(df_a))]
    _months_b = [f"Month {i+1}" for i in range(len(df_b))]

    fig_rev_cmp = go.Figure()
    fig_rev_cmp.add_trace(go.Scatter(
        x=_months_a, y=df_a["revenue"],
        name=selected_company, mode="lines",
        line=dict(color=ACCENT, width=2.5),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
        customdata=df_a["month_label"],
        hovertemplate="%{customdata}: $%{y:,.0f}<extra></extra>",
    ))
    fig_rev_cmp.add_trace(go.Scatter(
        x=_months_b, y=df_b["revenue"],
        name=compare_company, mode="lines",
        line=dict(color=TEAL, width=2.5, dash="dash"),
        fill="tozeroy", fillcolor="rgba(0,200,150,0.05)",
        customdata=df_b["month_label"],
        hovertemplate="%{customdata}: $%{y:,.0f}<extra></extra>",
    ))
    fig_rev_cmp.update_layout(**CHART_LAYOUT, height=300, showlegend=True,
        title=dict(text="Monthly Revenue (aligned from start)", font=dict(size=13, color=TEXT_MUTED)))
    fig_rev_cmp.update_yaxes(tickprefix="$", tickformat=",.0f", gridcolor="#21262d")
    st.plotly_chart(fig_rev_cmp, use_container_width=True, config={"displayModeBar": False})

    # Show alignment explanation when date ranges differ
    _dates_match = (len(df_a) == len(df_b) and
                    df_a["month_label"].iloc[0] == df_b["month_label"].iloc[0] and
                    df_a["month_label"].iloc[-1] == df_b["month_label"].iloc[-1])
    if not _dates_match:
        st.info(
            f"**Different date ranges detected.** "
            f"{selected_company} spans {df_a['month_label'].iloc[0]}–{df_a['month_label'].iloc[-1]} "
            f"({len(df_a)} months), while {compare_company} spans "
            f"{df_b['month_label'].iloc[0]}–{df_b['month_label'].iloc[-1]} ({len(df_b)} months). "
            f"The chart aligns both from Month 1 so you can compare performance at the same stage "
            f"of growth. Hover over any point to see the actual date.",
            icon="ℹ️"
        )

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    # ── Section 4: Side-by-side Metric Cards ──────────────────────────────────
    st.markdown('<div class="section-header">04 · Key Metrics</div>', unsafe_allow_html=True)

    def _build_metric_cards(kpis_x, df_x, company_label, accent_col):
        prev_rev = df_x.iloc[-2]["revenue"] if len(df_x) >= 2 else kpis_x["revenue"]
        rev_d    = ((kpis_x["revenue"] - prev_rev) / prev_rev) * 100
        gm_c   = TEAL if kpis_x["gross_margin_pct"] >= 70 else AMBER if kpis_x["gross_margin_pct"] >= 60 else RED
        burn_c = TEAL if kpis_x["burn_rate"] >= 0 else AMBER if kpis_x["burn_rate"] > -30_000 else RED
        rev_c  = TEAL if rev_d >= 5 else AMBER if rev_d >= 2 else RED
        rpe_c  = TEAL if kpis_x["revenue_per_employee"] >= 15_000 else AMBER if kpis_x["revenue_per_employee"] >= 10_000 else RED
        rwy_c  = TEAL if kpis_x["runway_months"] >= 18 or kpis_x["runway_months"] >= 999 else AMBER if kpis_x["runway_months"] >= 12 else RED

        st.markdown(f"<div style='font-size:13px; font-weight:600; color:{accent_col}; "
                    f"margin-bottom:12px; letter-spacing:0.5px;'>{company_label}</div>",
                    unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(metric_card("Monthly Revenue", fmt_currency(kpis_x["revenue"]),
                                    delta=f"{rev_d:+.1f}% MoM", delta_pos=rev_d >= 0,
                                    top_color=rev_c), unsafe_allow_html=True)
            st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
            st.markdown(metric_card("Gross Margin", f"{kpis_x['gross_margin_pct']:.1f}%",
                                    sub="Benchmark: 70%", top_color=gm_c), unsafe_allow_html=True)
            st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
            runway_sub = (f"{kpis_x['runway_months']:.0f} mo runway"
                          if kpis_x["runway_months"] < 999 else "Cash flow positive")
            st.markdown(metric_card("Cash Balance", fmt_currency(kpis_x["cash_balance"]),
                                    sub=runway_sub, top_color=rwy_c), unsafe_allow_html=True)
        with m2:
            burn_x = kpis_x["burn_rate"]
            burn_str = f"+{fmt_currency(burn_x)}" if burn_x >= 0 else f"-{fmt_currency(abs(burn_x))}"
            st.markdown(metric_card("Net Cash Flow", burn_str,
                                    delta="Cash flow positive" if burn_x >= 0 else "Burning cash",
                                    delta_pos=burn_x >= 0, top_color=burn_c), unsafe_allow_html=True)
            st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
            st.markdown(metric_card("Headcount", str(int(kpis_x["headcount"])),
                                    sub=f"{fmt_currency(kpis_x['revenue_per_employee'])}/employee/mo",
                                    top_color=rpe_c), unsafe_allow_html=True)

    card_a, card_b = st.columns(2)
    with card_a:
        _build_metric_cards(kpis_a, df_a, selected_company, ACCENT)
    with card_b:
        _build_metric_cards(kpis_b, df_b, compare_company, TEAL)

    # ── Comparison Footer ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding:32px 0 16px 0; border-top:1px solid {BORDER}; margin-top:24px;">
      <div style="font-size:12px; color:{TEXT_MUTED};">
        SMB Financial Health Dashboard · Built as a tech consulting portfolio project
        · All data is entirely synthetic · No real company is represented
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Single-company mode (original 5-section layout) ────────────────────────

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
          <div style="font-size:13px; color:{TEXT_MUTED}; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px;">Overall Health</div>
          <div style="display:inline-block; background:rgba({r},{g},{b},0.15);
               border:1px solid {overall_color}; border-radius:8px; padding:8px 18px;">
            <span style="font-size:20px; font-weight:800; color:{overall_color};">{overall_status.upper()}</span>
          </div>
          <div style="font-size:13px; color:{TEXT_MUTED}; margin-top:6px;">
            {rag_counts['Green']}G · {rag_counts['Amber']}A · {rag_counts['Red']}R
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(79,142,247,0.06); border:1px solid rgba(79,142,247,0.25);
                border-left:3px solid {ACCENT}; border-radius:8px; padding:18px 24px; margin-bottom:4px;">
      <div style="font-size:11px; font-weight:700; color:{ACCENT}; letter-spacing:1.8px;
                  text-transform:uppercase; margin-bottom:14px;">Dashboard Guide</div>
      <div style="display:flex; gap:40px; flex-wrap:wrap;">
        <div style="flex:2; min-width:220px;">
          <div style="font-size:13px; color:{TEXT_WHITE}; font-weight:600; margin-bottom:4px;">What this is</div>
          <div style="font-size:13px; color:{TEXT_MUTED}; line-height:1.7; margin-bottom:12px;">
            A simulated financial health review for two fictional SaaS companies. Upload your own
            CSV/Excel data via the sidebar, or explore two fictional SaaS companies. Use the month
            slider to adjust the analysis window.
          </div>
          <div style="font-size:13px; color:{TEXT_WHITE}; font-weight:600; margin-bottom:4px;">RAG Status</div>
          <div style="font-size:13px; color:{TEXT_MUTED}; line-height:1.7;">
            Each KPI is scored against SaaS SMB benchmarks.
            <span style="color:{TEAL}; font-weight:600;">Green</span> = healthy &nbsp;·&nbsp;
            <span style="color:{AMBER}; font-weight:600;">Amber</span> = watch closely &nbsp;·&nbsp;
            <span style="color:{RED}; font-weight:600;">Red</span> = action required.
          </div>
        </div>
        <div style="flex:1.5; min-width:200px;">
          <div style="font-size:13px; color:{TEXT_WHITE}; font-weight:600; margin-bottom:8px;">The two companies</div>
          <div style="font-size:13px; color:{TEXT_MUTED}; line-height:1.8;">
            <span style="color:{TEAL}; font-weight:600;">NovaSaaS</span> — healthy, profitable,
            strong margins. See what good looks like.<br>
            <span style="color:{RED}; font-weight:600;">CloudForge</span> — burning cash,
            thin margins. See how risk surfaces.
          </div>
        </div>
        <div style="flex:1.5; min-width:180px;">
          <div style="font-size:13px; color:{TEXT_WHITE}; font-weight:600; margin-bottom:8px;">Sections</div>
          <div style="font-size:12px; color:{TEXT_MUTED}; line-height:2.0;">
            01 · Company Overview<br>
            02 · Financial Trends<br>
            03 · KPI Scorecard<br>
            04 · Consultant Findings<br>
            05 · Cash Flow &amp; Burn
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Section 1: Company Overview ───────────────────────────────────────────────
    st.markdown('<div class="section-header">01 · Company Overview</div>', unsafe_allow_html=True)

    prev_revenue = df.iloc[-2]["revenue"] if len(df) >= 2 else kpis["revenue"]
    rev_delta = ((kpis["revenue"] - prev_revenue) / prev_revenue) * 100

    gm_color  = TEAL if kpis["gross_margin_pct"] >= 70 else AMBER if kpis["gross_margin_pct"] >= 60 else RED
    burn_color = TEAL if kpis["burn_rate"] >= 0 else AMBER if kpis["burn_rate"] > -30_000 else RED
    rev_color  = TEAL if rev_delta >= 5 else AMBER if rev_delta >= 2 else RED
    rpe_color  = TEAL if kpis["revenue_per_employee"] >= 15_000 else AMBER if kpis["revenue_per_employee"] >= 10_000 else RED
    runway_color = TEAL if kpis["runway_months"] >= 18 or kpis["runway_months"] >= 999 else AMBER if kpis["runway_months"] >= 12 else RED

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(metric_card("Monthly Revenue", fmt_currency(kpis["revenue"]),
                                delta=f"{rev_delta:+.1f}% MoM", delta_pos=rev_delta >= 0,
                                top_color=rev_color), unsafe_allow_html=True)
    with c2:
        runway_sub = (f"{kpis['runway_months']:.0f} mo runway"
                      if kpis["runway_months"] < 999 else "Cash flow positive")
        st.markdown(metric_card("Cash Balance", fmt_currency(kpis["cash_balance"]),
                                sub=runway_sub, top_color=runway_color), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Gross Margin", f"{kpis['gross_margin_pct']:.1f}%",
                                sub="Benchmark: 70%", top_color=gm_color), unsafe_allow_html=True)
    with c4:
        burn = kpis["burn_rate"]
        burn_str = f"+{fmt_currency(burn)}" if burn >= 0 else f"-{fmt_currency(abs(burn))}"
        st.markdown(metric_card("Net Cash Flow", burn_str,
                                delta="Cash flow positive" if burn >= 0 else "Burning cash",
                                delta_pos=burn >= 0, top_color=burn_color), unsafe_allow_html=True)
    with c5:
        st.markdown(metric_card("Headcount", str(int(kpis["headcount"])),
                                sub=f"{fmt_currency(kpis['revenue_per_employee'])}/employee/mo",
                                top_color=rpe_color), unsafe_allow_html=True)

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
        RAG_COLOR = {"Green": TEAL, "Amber": AMBER, "Red": RED}
        RAG_BG    = {"Green": "rgba(0,200,150,0.15)", "Amber": "rgba(245,166,35,0.15)", "Red": "rgba(232,69,69,0.15)"}
        COLS      = [3, 1.5, 2.5, 1.5]
        hstyle    = f"font-size:11px; color:{TEXT_MUTED}; font-weight:600; text-transform:uppercase; letter-spacing:.8px; margin:0;"

        h1, h2, h3, h4 = st.columns(COLS)
        h1.markdown(f"<p style='{hstyle}'>KPI</p>", unsafe_allow_html=True)
        h2.markdown(f"<p style='{hstyle}'>Value</p>", unsafe_allow_html=True)
        h3.markdown(f"<p style='{hstyle}'>Benchmark</p>", unsafe_allow_html=True)
        h4.markdown(f"<p style='{hstyle}'>Status</p>", unsafe_allow_html=True)
        st.divider()

        for row in scorecard:
            color = RAG_COLOR[row['Status']]
            bg    = RAG_BG[row['Status']]
            c1, c2, c3, c4 = st.columns(COLS)
            c1.markdown(f"**{row['KPI']}**  \n<span style='font-size:13px; color:{TEXT_MUTED};'>{row['_description']}</span>",
                        unsafe_allow_html=True)
            c2.markdown(f"**{row['Value']}**")
            c3.markdown(f"<span style='font-size:13px; color:{TEXT_MUTED};'>{row['Benchmark']}</span>",
                        unsafe_allow_html=True)
            c4.markdown(f"<span style='background:{bg}; color:{color}; border:1px solid {color}; "
                        f"padding:3px 8px; border-radius:4px; font-size:12px; font-weight:700;'>"
                        f"{row['Status'].upper()}</span>", unsafe_allow_html=True)
            st.divider()

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
        st.caption("Each axis = one KPI, normalized 0 (worst) → 1 (best). "
                   "Dashed line = SaaS SMB benchmark. A full outer shape = all KPIs at benchmark or above.")

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
        )
        fig_wf.update_layout(yaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor="#21262d"))
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
        )
        fig_cash.update_layout(
            margin=dict(l=12, r=80, t=40, b=12),
            legend=dict(
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                x=0.01, y=0.99, xanchor="left", yanchor="top",
                font=dict(size=12),
            ),
            yaxis=dict(tickprefix="$", tickformat=",.0f", title="Cash Balance", gridcolor="#21262d"),
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

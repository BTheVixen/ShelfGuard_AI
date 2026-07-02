import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
import subprocess

# 1. Page Configuration
st.set_page_config(
    page_title="ShelfGuard AI - Reporting Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Theme State Management
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# 3. Dynamic CSS Injection
CSS_VARIABLES = f"""
:root {{
    --bg: {"#09090b" if IS_DARK else "#ffffff"};
    --bg-subtle: {"#0c0c0f" if IS_DARK else "#f9fafb"};
    --card: {"#0c0c0f" if IS_DARK else "#ffffff"};
    --card-hover: {"#131316" if IS_DARK else "#f4f4f5"};
    --border: {"#1e1e24" if IS_DARK else "#e4e4e7"};
    --border-subtle: {"#16161a" if IS_DARK else "#f0f0f2"};
    --text: {"#fafafa" if IS_DARK else "#09090b"};
    --text-muted: #71717a;
    --text-dim: {"#52525b" if IS_DARK else "#a1a1aa"};
    --accent: #2563eb;
    --accent-muted: #1d4ed8;
    --green: {"#22c55e" if IS_DARK else "#16a34a"};
    --green-muted: {"rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)"};
    --red: {"#ef4444" if IS_DARK else "#dc2626"};
    --red-muted: {"rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)"};
    --amber: {"#f59e0b" if IS_DARK else "#d97706"};
    --amber-muted: {"rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)"};
    --shadow: {"none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"};
    --radius: 10px;
}}
"""

CUSTOM_STYLE = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* Hide Streamlit chrome */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
div[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* Base styles */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}

.block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1360px !important;
}

/* Brand header */
.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0.5rem;
}
.brand-badge {
    background: var(--bg-subtle);
    border: 1px solid var(--border);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.brand-name {
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--text);
}
.brand-sub {
    font-size: 0.82rem;
    color: var(--text-muted);
    border-left: 1px solid var(--border);
    padding-left: 12px;
    margin-left: 4px;
    font-weight: 400;
}

/* Metric card */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    height: 100%;
}
.metric-label {
    font-size: 0.76rem;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
    font-family: 'JetBrains Mono', monospace;
}
.metric-desc {
    font-size: 0.74rem;
    color: var(--text-dim);
    margin-top: 0.4rem;
}

/* Chart container wrapper */
.chart-wrap {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem 0.8rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.25rem;
}
.chart-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.1rem;
}
.chart-subtitle {
    font-size: 0.74rem;
    color: var(--text-dim);
    margin-bottom: 1.2rem;
}

/* Table styling */
.table-wrap {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.25rem;
}
.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.78rem;
    margin-top: 0.5rem;
}
.data-table th {
    text-align: left;
    padding: 0.7rem 0.9rem;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--border);
    background: var(--bg-subtle);
}
.data-table th:first-child {
    border-top-left-radius: 6px;
}
.data-table th:last-child {
    border-top-right-radius: 6px;
}
.data-table td {
    padding: 0.75rem 0.9rem;
    color: var(--text);
    border-bottom: 1px solid var(--border-subtle);
    font-family: 'DM Sans', sans-serif;
}
.data-table td.mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
}
.data-table tr:hover td {
    background: var(--card-hover);
}
.data-table tr:last-child td {
    border-bottom: none;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 5px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}
.badge-green { color: var(--green); background: var(--green-muted); border: 1px solid rgba(34,197,94,0.2); }
.badge-red { color: var(--red); background: var(--red-muted); border: 1px solid rgba(239,68,68,0.2); }
.badge-amber { color: var(--amber); background: var(--amber-muted); border: 1px solid rgba(245,158,11,0.2); }
.badge-blue { color: var(--accent); background: rgba(37,99,235,0.1); border: 1px solid rgba(37,99,235,0.15); }

/* Tabs overrides */
button[data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    border: 1px solid transparent !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
}
button[data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background: var(--card-hover) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--text) !important;
    background: var(--card) !important;
    border-color: var(--border) !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {
    display: none !important;
}
[data-baseweb="tab-list"] {
    gap: 6px !important;
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    margin-bottom: 1.5rem !important;
}

/* Horizontal gaps */
[data-testid="stHorizontalBlock"] { gap: 1.25rem !important; }

/* Custom Progress Meter */
.health-score-container {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 0.5rem 0;
}
.health-score-ring {
    position: relative;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: conic-gradient(var(--accent) 0%, var(--border) 0%);
    display: flex;
    align-items: center;
    justify-content: center;
}
.health-score-ring::after {
    content: "";
    position: absolute;
    width: 66px;
    height: 66px;
    border-radius: 50%;
    background: var(--card);
}
.health-score-value {
    position: absolute;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    z-index: 10;
}
</style>
"""

st.markdown(f"<style>{CSS_VARIABLES}</style>", unsafe_allow_html=True)
st.markdown(CUSTOM_STYLE, unsafe_allow_html=True)

# 4. Helper to trigger reporting agent run
def run_agent_pipeline():
    try:
        # Run generator and reporter in sequence
        subprocess.run([sys.executable, "mock_data_generator.py"], check=True)
        subprocess.run([sys.executable, "reporting_agent.py"], check=True)
        st.cache_data.clear()
        st.success("Successfully executed reporting agent. Data refreshed!")
        st.rerun()
    except Exception as e:
        st.error(f"Error running pipeline: {str(e)}")

# 5. Load data function
@st.cache_data
def load_report_data():
    if not os.path.exists('report_data.json'):
        return None
    try:
        with open('report_data.json', 'r') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError):
        return None

# Build Header Layout
head_left, head_right = st.columns([7, 2])
with head_left:
    st.markdown("""
    <div class="brand">
        <span class="brand-badge">🛡️ Agentic</span>
        <span class="brand-name">ShelfGuard AI</span>
        <span class="brand-sub">Reporting & Risk Intelligence</span>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
        st.button(theme_label, on_click=toggle_theme, use_container_width=True, key="theme_toggle_btn")
    with btn_col2:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_agent_btn"):
            with st.spinner("Agent running..."):
                run_agent_pipeline()

report_data = load_report_data()

if report_data is None:
    st.warning("⚠️ No report data found. Click below to run the reporting agent pipeline for the first time.")
    if st.button("🚀 Initialize Reporting Agent & Mock Data", type="primary"):
        with st.spinner("Initializing agent outputs..."):
            run_agent_pipeline()
            st.rerun()
else:
    # Set Plotly Layout Configuration
    PLOT_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#71717a" if not IS_DARK else "#a1a1aa", size=11),
        margin=dict(l=0, r=0, t=25, b=0),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
            zerolinecolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
            tickfont=dict(size=10, color="#71717a"),
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
            zerolinecolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.04)",
            tickfont=dict(size=10, color="#71717a"),
        ),
    )

    metrics = report_data["health_metrics"]
    
    # Render KPI Ribbon
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        # Dynamic conic gradient background for health score
        color = "var(--green)" if metrics["overall_score"] >= 80 else ("var(--amber)" if metrics["overall_score"] >= 60 else "var(--red)")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Inventory Health Score</div>
            <div class="health-score-container">
                <div class="health-score-ring" style="background: conic-gradient({color} {metrics["overall_score"]}%, var(--border) 0%);">
                    <div class="health-score-value">{metrics["overall_score"]}%</div>
                </div>
                <div style="font-size: 0.72rem; color: var(--text-muted); line-height: 1.3;">
                    Compliance & expiry risk weighted index
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        val = f"${metrics['total_inventory_cost']:,.2f}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Inventory Value</div>
            <div class="metric-value">{val}</div>
            <div class="metric-desc">Valued across {metrics['total_inventory_qty']:,} units</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        val = f"${metrics['total_waste_cost']:,.2f}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Cost at Expiry Risk</div>
            <div class="metric-value" style="color: var(--red);">{val}</div>
            <div class="metric-desc">Value projected to expire before sale</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Compliance Violations</div>
            <div class="metric-value" style="color: var(--amber);">{metrics['total_violations_count']}</div>
            <div class="metric-desc">Expired batches or buffer breaches</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 6. Set up Tabs
    t_overview, t_expiry, t_risk, t_near, t_compliance = st.tabs([
        "📊 Dashboard Overview", 
        "📅 Daily Expiry Summary", 
        "⚖️ Weekly Risk Report",
        "🕒 Products Near Expiry",
        "⚠️ Compliance Violations"
    ])

    # --- TAB 1: OVERVIEW ---
    with t_overview:
        st.markdown("""
        <div style="margin-bottom: 1rem;">
            <p style="font-size: 0.82rem; color: var(--text-muted);">
                ShelfGuard AI continuously scans warehouse inventory states and aligns them with e-commerce velocity patterns to forecast shelf life problems. The overview highlights core performance metrics.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        c_left, c_right = st.columns([1, 1])
        
        with c_left:
            # Chart 1: Stock Value vs Waste Risk Cost by Category
            batches_list = report_data.get("batches", [])
            if batches_list:
                batches = pd.DataFrame(batches_list)
                cat_agg = batches.groupby("category").agg({"total_cost": "sum", "waste_cost": "sum"}).reset_index()
                
                fig_cat = go.Figure()
                fig_cat.add_trace(go.Bar(
                    name="Total Stock Value",
                    x=cat_agg["category"],
                    y=cat_agg["total_cost"],
                    marker_color="#2563eb" if not IS_DARK else "#3b82f6"
                ))
                fig_cat.add_trace(go.Bar(
                    name="Projected Waste Cost",
                    x=cat_agg["category"],
                    y=cat_agg["waste_cost"],
                    marker_color="#dc2626" if not IS_DARK else "#ef4444"
                ))
                fig_cat.update_layout(
                    barmode='group',
                    height=300,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    **PLOT_LAYOUT
                )
                
                st.markdown("""
                <div class="chart-wrap">
                    <div class="chart-title">Stock Value vs. Expiry Waste Risk by Category</div>
                    <div class="chart-subtitle">Cost at risk represents stock projected to expire before sale based on daily order velocities.</div>
                """, unsafe_allow_html=True)
                st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="chart-wrap">
                    <div class="chart-title">Stock Value vs. Expiry Waste Risk by Category</div>
                    <div class="chart-subtitle">No inventory data available for category breakdown.</div>
                    <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: var(--text-muted);">
                        No category data.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
        with c_right:
            # Chart 2: Cumulative Expiry Schedule
            if batches_list:
                batches = pd.DataFrame(batches_list)
                # Filter remaining days > 0
                batches_future = batches[batches["remaining_days"] > 0].copy()
                
                if not batches_future.empty:
                    # Aggregate by day first to avoid multiple points per day in line chart
                    day_agg = batches_future.groupby("remaining_days")["total_cost"].sum().reset_index().sort_values("remaining_days")
                    day_agg["cum_cost"] = day_agg["total_cost"].cumsum()
                    
                    fig_timeline = px.line(
                        day_agg, 
                        x="remaining_days", 
                        y="cum_cost",
                        labels={"remaining_days": "Days until Expiry", "cum_cost": "Cumulative Inventory Cost ($)"}
                    )
                    fig_timeline.update_traces(
                        line_color="#2563eb" if not IS_DARK else "#3b82f6",
                        line_width=3
                    )
                    fig_timeline.update_layout(
                        height=300,
                        **PLOT_LAYOUT
                    )
                    
                    st.markdown("""
                    <div class="chart-wrap">
                        <div class="chart-title">Cumulative Expiry Schedule Timeline</div>
                        <div class="chart-subtitle">Shows cumulative inventory cost ($) expiring over the next 90 days.</div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="chart-wrap">
                        <div class="chart-title">Cumulative Expiry Schedule Timeline</div>
                        <div class="chart-subtitle">No upcoming expirations detected.</div>
                        <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: var(--text-muted);">
                            No future stock expirations.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="chart-wrap">
                    <div class="chart-title">Cumulative Expiry Schedule Timeline</div>
                    <div class="chart-subtitle">No upcoming expirations detected.</div>
                    <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: var(--text-muted);">
                        No future stock expirations.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        # Sub-score breakdown cards
        st.markdown("<h4 style='font-size: 0.95rem; font-weight: 600; margin-bottom: 0.8rem; color: var(--text);'>Inventory Health Component Breakdown</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            color = "var(--green)" if metrics["expiry_risk_score"] >= 80 else ("var(--amber)" if metrics["expiry_risk_score"] >= 60 else "var(--red)")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label" style="font-size: 0.7rem;">Expiry Risk Score ({metrics["expiry_risk_score"]}%)</div>
                <div style="height: 6px; background-color: var(--border); border-radius: 3px; margin: 0.5rem 0;">
                    <div style="width: {metrics["expiry_risk_score"]}%; height: 100%; background-color: {color}; border-radius: 3px;"></div>
                </div>
                <div style="font-size: 0.72rem; color: var(--text-dim);">
                    Proportion of inventory value protected from high-risk expiry.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            color = "var(--green)" if metrics["compliance_score"] >= 80 else ("var(--amber)" if metrics["compliance_score"] >= 60 else "var(--red)")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label" style="font-size: 0.7rem;">Compliance Score ({metrics["compliance_score"]}%)</div>
                <div style="height: 6px; background-color: var(--border); border-radius: 3px; margin: 0.5rem 0;">
                    <div style="width: {metrics["compliance_score"]}%; height: 100%; background-color: {color}; border-radius: 3px;"></div>
                </div>
                <div style="font-size: 0.72rem; color: var(--text-dim);">
                    Percentage of inventory volume meeting strict retail shelf-life guidelines.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            color = "var(--green)" if metrics["waste_risk_score"] >= 80 else ("var(--amber)" if metrics["waste_risk_score"] >= 60 else "var(--red)")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label" style="font-size: 0.7rem;">Waste Control Score ({metrics["waste_risk_score"]}%)</div>
                <div style="height: 6px; background-color: var(--border); border-radius: 3px; margin: 0.5rem 0;">
                    <div style="width: {metrics["waste_risk_score"]}%; height: 100%; background-color: {color}; border-radius: 3px;"></div>
                </div>
                <div style="font-size: 0.72rem; color: var(--text-dim);">
                    Efficiency of stock turnover vs. remaining expiry windows.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 2: DAILY EXPIRY SUMMARY ---
    with t_expiry:
        st.markdown("""
        <div style="margin-bottom: 1.25rem;">
            <p style="font-size: 0.82rem; color: var(--text-muted);">
                The Daily Expiry Summary aggregates stock volumes and valuation based on time remaining before expiration.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        sum_data = report_data["expiry_summary"]
        
        # Display 4 grid blocks
        es1, es2, es3, es4 = st.columns(4)
        with es1:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 3px solid var(--red);">
                <div class="metric-label">Expired / At Expiry Today</div>
                <div class="metric-value" style="color: var(--red);">{sum_data["expired"]["count"]} <span style="font-size: 1rem; color: var(--text-muted);">batches</span></div>
                <div class="metric-desc">
                    <b>Total Cost:</b> ${sum_data["expired"]["cost"]:,.2f}<br>
                    <b>Total Qty:</b> {sum_data["expired"]["quantity"]:,} units
                </div>
            </div>
            """, unsafe_allow_html=True)
        with es2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 3px solid var(--amber);">
                <div class="metric-label">Expiring in 7 Days</div>
                <div class="metric-value" style="color: var(--amber);">{sum_data["expiring_7d"]["count"]} <span style="font-size: 1rem; color: var(--text-muted);">batches</span></div>
                <div class="metric-desc">
                    <b>Total Cost:</b> ${sum_data["expiring_7d"]["cost"]:,.2f}<br>
                    <b>Total Qty:</b> {sum_data["expiring_7d"]["quantity"]:,} units
                </div>
            </div>
            """, unsafe_allow_html=True)
        with es3:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 3px solid var(--accent);">
                <div class="metric-label">Expiring in 30 Days</div>
                <div class="metric-value" style="color: var(--accent);">{sum_data["expiring_30d"]["count"]} <span style="font-size: 1rem; color: var(--text-muted);">batches</span></div>
                <div class="metric-desc">
                    <b>Total Cost:</b> ${sum_data["expiring_30d"]["cost"]:,.2f}<br>
                    <b>Total Qty:</b> {sum_data["expiring_30d"]["quantity"]:,} units
                </div>
            </div>
            """, unsafe_allow_html=True)
        with es4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Expiring in 90 Days</div>
                <div class="metric-value">{sum_data["expiring_90d"]["count"]} <span style="font-size: 1rem; color: var(--text-muted);">batches</span></div>
                <div class="metric-desc">
                    <b>Total Cost:</b> ${sum_data["expiring_90d"]["cost"]:,.2f}<br>
                    <b>Total Qty:</b> {sum_data["expiring_90d"]["quantity"]:,} units
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Draw Bar chart showing comparison of counts and values
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Build DataFrame for plot
        periods = ["Expired Today", "Expiring 7 Days", "Expiring 30 Days", "Expiring 90 Days"]
        counts = [sum_data["expired"]["count"], sum_data["expiring_7d"]["count"], sum_data["expiring_30d"]["count"], sum_data["expiring_90d"]["count"]]
        costs = [sum_data["expired"]["cost"], sum_data["expiring_7d"]["cost"], sum_data["expiring_30d"]["cost"], sum_data["expiring_90d"]["cost"]]
        
        fig_agg_exp = go.Figure()
        fig_agg_exp.add_trace(go.Bar(
            x=periods,
            y=costs,
            name="Total Cost ($)",
            marker_color="#3b82f6",
            yaxis="y"
        ))
        fig_agg_exp.add_trace(go.Scatter(
            x=periods,
            y=counts,
            name="Batch Count",
            marker_color="#f59e0b",
            mode="lines+markers",
            yaxis="y2"
        ))
        
        fig_agg_exp.update_layout(
            height=300,
            yaxis=dict(title="Stock Cost ($)", side="left"),
            yaxis2=dict(title="Batch Count", side="right", overlaying="y", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            **PLOT_LAYOUT
        )
        
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Expiry Time Horizon Aggregations</div>
            <div class="chart-subtitle">Comparison of inventory value vs batch count expiring over the next 90 days.</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_agg_exp, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 3: WEEKLY RISK REPORT ---
    with t_risk:
        st.markdown("""
        <div style="margin-bottom: 1.25rem;">
            <p style="font-size: 0.82rem; color: var(--text-muted);">
                The Weekly Risk Report classifies inventory stock items based on remaining shelf life and sales runout rate to determine projected financial losses.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        risk_data = report_data["risk_summary"]
        
        rs1, rs2, rs3 = st.columns(3)
        with rs1:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid var(--red);">
                <div class="metric-label" style="color: var(--red);">High Risk Inventory</div>
                <div class="metric-value">{risk_data["High"]["count"]} <span style="font-size: 1.1rem; color: var(--text-muted);">batches</span></div>
                <div class="metric-desc">
                    <b>Total Cost:</b> ${risk_data["High"]["cost"]:,.2f}<br>
                    <b>Financial Waste Risk:</b> <span style="color:var(--red); font-weight:600;">${risk_data["High"]["waste_cost"]:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with rs2:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid var(--amber);">
                <div class="metric-label" style="color: var(--amber);">Medium Risk Inventory</div>
                <div class="metric-value">{risk_data["Medium"]["count"]} <span style="font-size: 1.1rem; color: var(--text-muted);">batches</span></div>
                <div class="metric-desc">
                    <b>Total Cost:</b> ${risk_data["Medium"]["cost"]:,.2f}<br>
                    <b>Financial Waste Risk:</b> <span style="color:var(--amber); font-weight:600;">${risk_data["Medium"]["waste_cost"]:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with rs3:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid var(--green);">
                <div class="metric-label" style="color: var(--green);">Low Risk Inventory</div>
                <div class="metric-value">{risk_data["Low"]["count"]} <span style="font-size: 1.1rem; color: var(--text-muted);">batches</span></div>
                <div class="metric-desc">
                    <b>Total Cost:</b> ${risk_data["Low"]["cost"]:,.2f}<br>
                    <b>Financial Waste Risk:</b> $0.00
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Risk Table detailing high risk batches
        st.markdown("<h4 style='font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text);'>Critical Risk Batches Detail</h4>", unsafe_allow_html=True)
        
        high_risk_batches = [b for b in report_data["batches"] if b["risk_level"] == "High"]
        
        if high_risk_batches:
            rows_html = ""
            for b in high_risk_batches:
                r_days = b["remaining_days"]
                days_label = f"{r_days} days left" if r_days > 0 else (f"Expired {abs(r_days)} days ago" if r_days < 0 else "Expires TODAY")
                days_class = "badge-red" if r_days <= 7 else "badge-amber"
                
                rows_html += f"""
                <tr>
                    <td class="mono">{b["sku"]}</td>
                    <td><b>{b["product_name"]}</b></td>
                    <td><span class="badge badge-blue">{b["category"]}</span></td>
                    <td class="mono">{b["batch_number"]}</td>
                    <td class="mono">{b["stock_quantity"]:,}</td>
                    <td class="mono">${b["total_cost"]:,.2f}</td>
                    <td class="mono">${b["waste_cost"]:,.2f}</td>
                    <td><span class="badge {days_class}">{days_label}</span></td>
                    <td><span style="font-size: 0.74rem; color: var(--text-dim);">{b["risk_reason"]}</span></td>
                </tr>
                """
                
            st.markdown(f"""
            <div class="table-wrap">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>SKU</th>
                            <th>Product Name</th>
                            <th>Category</th>
                            <th>Batch</th>
                            <th>Stock Qty</th>
                            <th>Stock Cost</th>
                            <th>Waste Cost</th>
                            <th>Expiry</th>
                            <th>Risk Assessment Reason</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("No High Risk batches identified in the current reporting window.")

    # --- TAB 4: PRODUCTS NEAR EXPIRY ---
    with t_near:
        st.markdown("""
        <div style="margin-bottom: 1rem;">
            <p style="font-size: 0.82rem; color: var(--text-muted);">
                A comprehensive catalog of active items expiring within the next 30 days. Use the search bar to query by product name or SKU.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        search_query = st.text_input("🔍 Search near-expiry products (by name or SKU):", "").strip().lower()
        
        near_expiry_list = report_data["near_expiry"]
        if search_query:
            near_expiry_list = [
                b for b in near_expiry_list 
                if search_query in b["product_name"].lower() or search_query in b["sku"].lower()
            ]
            
        if near_expiry_list:
            rows_html = ""
            for b in near_expiry_list:
                r_days = b["remaining_days"]
                doc = b["days_of_coverage"]
                doc_str = f"{doc:.1f} days" if doc < 900 else "N/A"
                
                # Expiry status badges
                if r_days <= 3:
                    days_badge = f"<span class='badge badge-red'>Expires in {r_days}d (Critical)</span>"
                elif r_days <= 10:
                    days_badge = f"<span class='badge badge-amber'>Expires in {r_days}d (Warning)</span>"
                else:
                    days_badge = f"<span class='badge badge-blue'>Expires in {r_days}d</span>"
                    
                # Coverage vs Expiry Alert badge
                if doc > r_days:
                    coverage_badge = "<span class='badge badge-red' title='Stock will expire before sales clear it'>Overstock Waste</span>"
                else:
                    coverage_badge = "<span class='badge badge-green' title='Sales velocity will clear stock'>Safe Turnover</span>"
                    
                rows_html += f"""
                <tr>
                    <td class="mono">{b["sku"]}</td>
                    <td><b>{b["product_name"]}</b></td>
                    <td><span class="badge badge-blue">{b["category"]}</span></td>
                    <td class="mono">{b["batch_number"]}</td>
                    <td class="mono">{b["stock_quantity"]:,}</td>
                    <td class="mono">${b["unit_cost"]:.2f}</td>
                    <td class="mono">${b["total_cost"]:,.2f}</td>
                    <td>{days_badge}</td>
                    <td class="mono">{doc_str}</td>
                    <td>{coverage_badge}</td>
                </tr>
                """
                
            st.markdown(f"""
            <div class="table-wrap">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>SKU</th>
                            <th>Product Name</th>
                            <th>Category</th>
                            <th>Batch</th>
                            <th>Qty</th>
                            <th>Unit Cost</th>
                            <th>Total Cost</th>
                            <th>Days to Expiry</th>
                            <th>Coverage (DoC)</th>
                            <th>Sales Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No matching near-expiry products (expiring within 30 days) were found.")

    # --- TAB 5: COMPLIANCE VIOLATIONS ---
    with t_compliance:
        st.markdown("""
        <div style="margin-bottom: 1.25rem;">
            <p style="font-size: 0.82rem; color: var(--text-muted);">
                ShelfGuard AI flags batches that fail regulatory buffers (e.g. food display standards or pharmacy thresholds) or have already expired.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        violations_list = report_data["violations"]
        
        if violations_list:
            # Group violations by type
            expired_batches = [b for b in violations_list if b["compliance_status"] == "Expired"]
            buffer_violations = [b for b in violations_list if b["compliance_status"] == "Violation"]
            
            # Expired Stock Warning Box
            if expired_batches:
                st.markdown("""
                <div style="background-color: var(--red-muted); border: 1px solid var(--red); padding: 1rem; border-radius: 8px; margin-bottom: 1.25rem;">
                    <h5 style="color: var(--red); margin: 0 0 0.5rem; font-size: 0.9rem; font-weight: 700;">⚠️ IMMEDIATE ACTION REQUIRED: EXPIRED PRODUCTS ON SHELF</h5>
                    <p style="margin: 0; font-size: 0.78rem; line-height: 1.4; color: var(--text);">
                        The batches listed below have reached or passed their expiration date. They must be removed from public shelves immediately to comply with health safety regulations.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                rows_html = ""
                for b in expired_batches:
                    rows_html += f"""
                    <tr>
                        <td class="mono">{b["sku"]}</td>
                        <td><b>{b["product_name"]}</b></td>
                        <td><span class="badge badge-red">{b["category"]}</span></td>
                        <td class="mono">{b["batch_number"]}</td>
                        <td class="mono">{b["stock_quantity"]:,}</td>
                        <td class="mono">${b["total_cost"]:,.2f}</td>
                        <td class="mono">{b["expiry_date"]}</td>
                        <td style="color: var(--red); font-weight: 500;">Expired ({abs(b["remaining_days"])} days ago)</td>
                    </tr>
                    """
                
                st.markdown(f"""
                <div class="table-wrap" style="border: 1px solid var(--red);">
                    <div style="font-size: 0.8rem; font-weight: 600; color: var(--red); margin-bottom: 0.4rem;">Expired Stock List</div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>SKU</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Batch Number</th>
                                <th>Stock Qty</th>
                                <th>Stock Cost</th>
                                <th>Expiry Date</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
            # Buffer Violations Table
            if buffer_violations:
                st.markdown("""
                <div style="margin-top: 1.5rem; margin-bottom: 0.5rem;">
                    <h5 style="color: var(--amber); margin: 0; font-size: 0.9rem; font-weight: 700;">⚠️ Safety Buffer Violations</h5>
                    <p style="margin: 0.2rem 0; font-size: 0.78rem; color: var(--text-muted);">
                        Batches that are still active but have dropped below category safety thresholds (e.g., minimum days remaining or percent remaining shelf life).
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                rows_html = ""
                for b in buffer_violations:
                    rows_html += f"""
                    <tr>
                        <td class="mono">{b["sku"]}</td>
                        <td><b>{b["product_name"]}</b></td>
                        <td><span class="badge badge-blue">{b["category"]}</span></td>
                        <td class="mono">{b["batch_number"]}</td>
                        <td class="mono">{b["stock_quantity"]:,}</td>
                        <td class="mono">{b["remaining_days"]} days left</td>
                        <td class="mono">{(b["percent_shelf_life"]*100):.1f}% left</td>
                        <td><span style="font-size: 0.74rem; color: var(--amber); font-weight: 500;">{b["compliance_details"]}</span></td>
                    </tr>
                    """
                    
                st.markdown(f"""
                <div class="table-wrap" style="border: 1px solid var(--amber);">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>SKU</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Batch Number</th>
                                <th>Stock Qty</th>
                                <th>Days Left</th>
                                <th>Shelf Life % Left</th>
                                <th>Violation Reason Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 Compliance scans completed. Zero compliance violations found across active warehouse stock.")
            
        # Category Storage Compliance Rules Box
        st.markdown("<h5 style='font-size: 0.85rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.5rem;'>Category Safety Standards References</h5>", unsafe_allow_html=True)
        
        with open("compliance_rules.json", "r") as f:
            rules_data = json.load(f)
            
        rules_rows = ""
        for cat, r in rules_data.items():
            rules_rows += f"""
            <tr>
                <td><b>{cat}</b></td>
                <td class="mono">{r["min_days_before_expiry"]} days</td>
                <td class="mono">{(r["min_shelf_life_percent"]*100):.0f}% of total shelf life</td>
                <td><span class="badge badge-blue">{r["required_temp_range"]}</span></td>
            </tr>
            """
            
        st.markdown(f"""
        <div class="table-wrap" style="max-width: 600px;">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Min Days Buffer</th>
                        <th>Min Shelf Life %</th>
                        <th>Storage Standard Temp</th>
                    </tr>
                </thead>
                <tbody>
                    {rules_rows}
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

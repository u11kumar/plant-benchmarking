import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ----------------------------------------------------------------------------
# Page config & style
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="UPRVUNL Thermal Plants | Technical & Financial Benchmarking",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#1f6feb"
GREEN = "#1a7f37"
AMBER = "#d29922"
RED = "#cf222e"
GREY = "#8b949e"

st.markdown("""
<style>
    .stMetric {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        border-radius: 8px;
        padding: 12px 16px 6px 16px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
    h1, h2, h3 { font-weight: 700; }
    .plant-card {
        border: 1px solid #d0d7de;
        border-radius: 10px;
        padding: 14px 18px;
        background: #ffffff;
    }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    ts = pd.read_csv("data/timeseries.csv")
    bm = pd.read_csv("data/benchmark_9plants.csv")
    return ts, bm


ts, bm = load_data()
latest = ts[ts["year"] == "FY 2023-24"].copy()

COLOR_MAP = {
    "Anpara-A": "#1f6feb",
    "Parichha Extn.": "#8250df",
    "Obra-B": "#cf222e",
}


def rag_color(value, good_thresh, bad_thresh, lower_is_better=True):
    if pd.isna(value):
        return GREY
    if lower_is_better:
        if value <= good_thresh:
            return GREEN
        elif value >= bad_thresh:
            return RED
        return AMBER
    else:
        if value >= good_thresh:
            return GREEN
        elif value <= bad_thresh:
            return RED
        return AMBER


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
st.sidebar.title("⚡ Plant Benchmarking")
st.sidebar.caption("UPRVUNL Coal Thermal Power Stations")

page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Overview",
        "🔧 Technical Analysis",
        "💰 Financial Analysis",
        "🏭 9-Plant Benchmarking",
        "📈 Trends (FY20–FY24)",
        "🗂️ Raw Data",
    ],
)

st.sidebar.divider()
all_plants = sorted(ts["plant"].unique())
selected_plants = st.sidebar.multiselect(
    "Filter plants (workbook data)", all_plants, default=all_plants
)
st.sidebar.divider()
st.sidebar.markdown(
    "**Data source:** `Book2.xlsx`\n\n"
    "3 plants with full FY2019-20 → FY2023-24 technical & financial records: "
    "Anpara-A, Parichha Extn., Obra-B.\n\n"
    "The *9-Plant Benchmarking* page adds 6 reference plants from the "
    "regulatory benchmarking exercise for wider peer comparison."
)

ts_f = ts[ts["plant"].isin(selected_plants)]
latest_f = latest[latest["plant"].isin(selected_plants)]

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================
if page == "📊 Overview":
    st.title("⚡ Technical & Financial Benchmarking Dashboard")
    st.caption("UPRVUNL Coal-based Thermal Power Stations — FY 2023-24 snapshot")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Plants Analyzed", f"{latest_f['plant'].nunique()}")
    c2.metric("Total Capacity", f"{latest_f['capacity_mw'].sum():,.0f} MW")
    c3.metric("Total Energy Generated", f"{latest_f['energy_generated_mu'].sum():,.0f} MU")
    c4.metric("Total Capital Cost", f"₹{latest_f['capital_cost_cr'].sum():,.0f} Cr")

    st.divider()

    best_shr = latest_f.loc[latest_f["shr_kcal_kwh"].idxmin()]
    worst_shr = latest_f.loc[latest_f["shr_kcal_kwh"].idxmax()]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏆 Best Technical Performer")
        st.markdown(f"""
        <div class="plant-card">
        <h4>{best_shr['plant']} ({best_shr['units_config']})</h4>
        <b>SHR:</b> {best_shr['shr_kcal_kwh']:.0f} Kcal/kWh &nbsp;|&nbsp;
        <b>APC:</b> {best_shr['apc_pct']:.2f}% &nbsp;|&nbsp;
        <b>SCC:</b> {best_shr['scc_kg_kwh']:.3f} kg/kWh<br>
        <b>PLF:</b> {best_shr['plf_pct']:.1f}% &nbsp;|&nbsp;
        <b>Variable Cost:</b> {best_shr['total_variable_cost_paise_per_unit']:.1f} paise/unit
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("#### ⚠️ Needs Attention")
        st.markdown(f"""
        <div class="plant-card">
        <h4>{worst_shr['plant']} ({worst_shr['units_config']})</h4>
        <b>SHR:</b> {worst_shr['shr_kcal_kwh']:.0f} Kcal/kWh &nbsp;|&nbsp;
        <b>APC:</b> {worst_shr['apc_pct']:.2f}% &nbsp;|&nbsp;
        <b>SCC:</b> {worst_shr['scc_kg_kwh']:.3f} kg/kWh<br>
        <b>PLF:</b> {worst_shr['plf_pct']:.1f}% &nbsp;|&nbsp;
        <b>Variable Cost:</b> {worst_shr['total_variable_cost_paise_per_unit']:.1f} paise/unit
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Snapshot Comparison — FY 2023-24")

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Specific Heat Rate (Kcal/kWh)", "Auxiliary Power Consumption (%)", "Plant Load Factor (%)"),
    )
    for i, col in enumerate(["shr_kcal_kwh", "apc_pct", "plf_pct"], start=1):
        fig.add_trace(
            go.Bar(
                x=latest_f["plant"], y=latest_f[col],
                marker_color=[COLOR_MAP.get(p, PRIMARY) for p in latest_f["plant"]],
                text=latest_f[col].round(2), textposition="outside",
                showlegend=False,
            ),
            row=1, col=i,
        )
    fig.update_layout(height=380, margin=dict(t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Generation Cost Build-up (paise/unit) — FY 2023-24")
    cost_df = latest_f.melt(
        id_vars="plant",
        value_vars=["coal_cost_paise_per_unit", "oil_cost_paise_per_unit", "om_cost_paise_per_unit"],
        var_name="component", value_name="paise_per_unit",
    )
    cost_df["component"] = cost_df["component"].map({
        "coal_cost_paise_per_unit": "Coal",
        "oil_cost_paise_per_unit": "Oil",
        "om_cost_paise_per_unit": "O&M",
    })
    fig2 = px.bar(
        cost_df, x="plant", y="paise_per_unit", color="component",
        text_auto=".1f", barmode="stack",
        color_discrete_map={"Coal": "#57606a", "Oil": AMBER, "O&M": PRIMARY},
    )
    fig2.update_layout(height=420, yaxis_title="paise / kWh", xaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================================
# PAGE: TECHNICAL ANALYSIS
# ============================================================================
elif page == "🔧 Technical Analysis":
    st.title("🔧 Technical Performance Analysis")
    st.caption("FY 2023-24 normative/actual technical parameters (from Book2.xlsx)")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Heat Rate & Fuel", "Auxiliary Power & PLF", "Coal/Oil Consumption", "Composite Score"]
    )

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            d = latest_f.sort_values("shr_kcal_kwh")
            colors = [rag_color(v, 2200, 2600) for v in d["shr_kcal_kwh"]]
            fig = go.Figure(go.Bar(
                x=d["shr_kcal_kwh"], y=d["plant"], orientation="h",
                marker_color=colors, text=d["shr_kcal_kwh"], textposition="outside",
            ))
            fig.add_vline(x=2100, line_dash="dash", line_color="black",
                           annotation_text="Supercritical benchmark ~2100")
            fig.update_layout(title="Specific Heat Rate — lower is better (Kcal/kWh)",
                               height=380, xaxis_title="Kcal/kWh")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            d = latest_f.sort_values("scc_kg_kwh")
            colors = [rag_color(v, 0.62, 0.72) for v in d["scc_kg_kwh"]]
            fig = go.Figure(go.Bar(
                x=d["scc_kg_kwh"], y=d["plant"], orientation="h",
                marker_color=colors, text=d["scc_kg_kwh"].round(3), textposition="outside",
            ))
            fig.update_layout(title="Specific Coal Consumption — lower is better (kg/kWh)",
                               height=380, xaxis_title="kg/kWh")
            st.plotly_chart(fig, use_container_width=True)

        fig = px.bar(latest_f.sort_values("gcv_coal_kcal_kg"), x="plant", y="gcv_coal_kcal_kg",
                     text_auto=".0f", color="plant", color_discrete_map=COLOR_MAP)
        fig.update_layout(title="Gross Calorific Value of Coal — higher is better (Kcal/kg)",
                           height=350, showlegend=False, yaxis_title="Kcal/kg", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            d = latest_f.sort_values("apc_pct")
            colors = [rag_color(v, 7, 9) for v in d["apc_pct"]]
            fig = go.Figure(go.Bar(
                x=d["apc_pct"], y=d["plant"], orientation="h",
                marker_color=colors, text=d["apc_pct"].round(2), textposition="outside",
            ))
            fig.add_vline(x=7.0, line_dash="dash", line_color="black", annotation_text="Regulatory norm 7%")
            fig.update_layout(title="Auxiliary Power Consumption — lower is better (%)",
                               height=380, xaxis_title="APC %")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            d = latest_f.copy()
            colors = [rag_color(v, 85, 70, lower_is_better=False) for v in d["plf_pct"]]
            fig = go.Figure(go.Bar(
                x=d["plant"], y=d["plf_pct"],
                marker_color=colors, text=d["plf_pct"].round(1), textposition="outside",
            ))
            fig.add_hline(y=85, line_dash="dash", line_color="black", annotation_text="Target PLF 85%")
            fig.update_layout(title="Plant Load Factor — capacity utilization (%)",
                               height=380, yaxis_title="PLF %", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        st.info(
            "💡 Auxiliary power consumption above the ~7% regulatory norm signals scope for VFD "
            "retrofits on ID/FD fans and boiler feed pumps, and condenser vacuum improvement."
        )

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(latest_f, x="plant", y="coal_consumption_mt", text_auto=",.0f",
                         color="plant", color_discrete_map=COLOR_MAP)
            fig.update_layout(title="Annual Coal Consumption (MT)", height=380, showlegend=False,
                               yaxis_title="MT", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(latest_f, x="plant", y="specific_oil_consumption_ml_kwh", text_auto=".2f",
                         color="plant", color_discrete_map=COLOR_MAP)
            fig.update_layout(title="Specific Oil Consumption (ml/kWh)", height=380, showlegend=False,
                               yaxis_title="ml/kWh", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("Composite ranking across four normalized technical parameters "
                     "(SHR, APC, SCC — lower is better; PLF — higher is better).")
        d = latest_f.copy()
        for col, higher_better in [("shr_kcal_kwh", False), ("apc_pct", False),
                                     ("scc_kg_kwh", False), ("plf_pct", True)]:
            rng = d[col].max() - d[col].min()
            if rng == 0:
                d[col + "_score"] = 100.0
            elif higher_better:
                d[col + "_score"] = 100 * (d[col] - d[col].min()) / rng
            else:
                d[col + "_score"] = 100 * (d[col].max() - d[col]) / rng
        d["composite_score"] = d[[c + "_score" for c in
                                    ["shr_kcal_kwh", "apc_pct", "scc_kg_kwh", "plf_pct"]]].mean(axis=1)
        d = d.sort_values("composite_score", ascending=False)
        fig = px.bar(d, x="plant", y="composite_score", text_auto=".1f", color="composite_score",
                     color_continuous_scale=["#cf222e", "#d29922", "#1a7f37"])
        fig.update_layout(title="Composite Technical Performance Score (0–100, higher = better)",
                           height=400, xaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        radar_fig = go.Figure()
        for _, row in latest_f.iterrows():
            radar_fig.add_trace(go.Scatterpolar(
                r=[
                    100 * (latest_f["shr_kcal_kwh"].max() - row["shr_kcal_kwh"]) / (latest_f["shr_kcal_kwh"].max() - latest_f["shr_kcal_kwh"].min() + 1e-9),
                    100 * (latest_f["apc_pct"].max() - row["apc_pct"]) / (latest_f["apc_pct"].max() - latest_f["apc_pct"].min() + 1e-9),
                    100 * (latest_f["scc_kg_kwh"].max() - row["scc_kg_kwh"]) / (latest_f["scc_kg_kwh"].max() - latest_f["scc_kg_kwh"].min() + 1e-9),
                    100 * (row["plf_pct"] - latest_f["plf_pct"].min()) / (latest_f["plf_pct"].max() - latest_f["plf_pct"].min() + 1e-9),
                ],
                theta=["SHR", "APC", "SCC", "PLF"], fill="toself", name=row["plant"],
                line_color=COLOR_MAP.get(row["plant"], PRIMARY),
            ))
        radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                 height=450, title="Multi-parameter Radar Comparison")
        st.plotly_chart(radar_fig, use_container_width=True)

# ============================================================================
# PAGE: FINANCIAL ANALYSIS
# ============================================================================
elif page == "💰 Financial Analysis":
    st.title("💰 Financial Analysis")
    st.caption("Capital structure, O&M cost trends & generation economics")

    tab1, tab2, tab3 = st.tabs(["Capital Structure", "O&M & Cost of Generation", "Receivables & Depreciation"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(latest_f, x="plant", y="capital_cost_cr", text_auto=",.0f",
                         color="plant", color_discrete_map=COLOR_MAP)
            fig.update_layout(title="Total Capital Cost (₹ Cr)", height=380, showlegend=False,
                               yaxis_title="₹ Cr", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(latest_f, x="plant", y="capital_cost_per_mw_cr", text_auto=".2f",
                         color="plant", color_discrete_map=COLOR_MAP)
            fig.update_layout(title="Capital Cost Intensity (₹ Cr / MW)", height=380, showlegend=False,
                               yaxis_title="₹ Cr/MW", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        eq_debt = latest_f.melt(id_vars="plant", value_vars=["equity_cr", "loan_cr"],
                                 var_name="component", value_name="value")
        eq_debt["component"] = eq_debt["component"].map({"equity_cr": "Equity", "loan_cr": "Loan"})
        fig = px.bar(eq_debt, x="plant", y="value", color="component", barmode="stack",
                     text_auto=",.0f", color_discrete_map={"Equity": GREEN, "Loan": AMBER})
        fig.update_layout(title="Equity vs Loan Financing (₹ Cr) — FY 2023-24", height=400,
                           yaxis_title="₹ Cr", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Anpara-A (1987) carries zero residual loan — fully depreciated financing structure typical of a 35+ year old asset.")

    with tab2:
        fig = px.line(ts_f, x="year", y="om_actual_cr", color="plant", markers=True,
                      color_discrete_map=COLOR_MAP)
        fig.update_layout(title="O&M Cost Trend, FY2019-20 → FY2023-24 (₹ Cr)", height=400,
                           yaxis_title="₹ Cr", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(ts_f, x="year", y="om_cost_paise_per_unit", color="plant", markers=True,
                          color_discrete_map=COLOR_MAP)
            fig.update_layout(title="O&M Cost per Unit Generated (paise/kWh)", height=380,
                               yaxis_title="paise/unit", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(latest_f.sort_values("total_variable_cost_paise_per_unit"),
                         x="plant", y="total_variable_cost_paise_per_unit", text_auto=".1f",
                         color="plant", color_discrete_map=COLOR_MAP)
            fig.update_layout(title="Total Variable Cost of Generation (paise/unit)", height=380,
                               showlegend=False, yaxis_title="paise/unit", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        st.info(
            "💡 O&M cost per unit is rising steadily for all three plants year-on-year as generation "
            "stays flat while absolute O&M spend grows — a sign of ageing-asset maintenance load."
        )

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(ts_f, x="year", y="avg_receivables_cr", color="plant", markers=True,
                          color_discrete_map=COLOR_MAP)
            fig.update_layout(title="Average Receivables Trend (₹ Cr)", height=380,
                               yaxis_title="₹ Cr", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.line(ts_f, x="year", y="net_block_pct_of_capital", color="plant", markers=True,
                          color_discrete_map=COLOR_MAP)
            fig.update_layout(title="Net Depreciated Block (% of Original Capital Cost)", height=380,
                               yaxis_title="%", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Parichha Extn. and Obra-B show a fast-declining net block, reflecting continued asset "
            "depreciation; Anpara-A's net block is already a small residual share, consistent with its 1987 vintage."
        )

# ============================================================================
# PAGE: 9-PLANT BENCHMARKING
# ============================================================================
elif page == "🏭 9-Plant Benchmarking":
    st.title("🏭 UPRVUNL Fleet-wide Benchmarking (9 Plants)")
    st.caption("FY 2023-24 snapshot — includes 6 reference plants beyond the workbook for full fleet context")

    st.dataframe(
        bm[["plant", "units_config", "capacity_mw", "technology", "plf_pct", "shr_kcal_kwh",
            "apc_pct", "gcv_coal_kcal_kg", "scc_kg_kwh", "energy_generated_mu", "com_year", "in_workbook"]]
        .rename(columns={
            "plant": "Plant", "units_config": "Config", "capacity_mw": "Capacity (MW)",
            "technology": "Technology", "plf_pct": "PLF (%)", "shr_kcal_kwh": "SHR (Kcal/kWh)",
            "apc_pct": "APC (%)", "gcv_coal_kcal_kg": "GCV (Kcal/kg)", "scc_kg_kwh": "SCC (kg/kWh)",
            "energy_generated_mu": "Energy (MU)", "com_year": "COM Year", "in_workbook": "In Book2.xlsx",
        }).sort_values("SHR (Kcal/kWh)"),
        use_container_width=True, hide_index=True,
    )

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        d = bm.sort_values("shr_kcal_kwh")
        colors = ["#1a7f37" if not v else "#1f6feb" for v in d["in_workbook"]]
        fig = go.Figure(go.Bar(x=d["shr_kcal_kwh"], y=d["plant"], orientation="h",
                                marker_color=colors, text=d["shr_kcal_kwh"], textposition="outside"))
        fig.add_vline(x=2100, line_dash="dash", line_color="black", annotation_text="Benchmark 2100")
        fig.update_layout(title="SHR — All 9 Plants (blue = in workbook)", height=420, xaxis_title="Kcal/kWh")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        d = bm.sort_values("scc_kg_kwh")
        colors = ["#1a7f37" if not v else "#1f6feb" for v in d["in_workbook"]]
        fig = go.Figure(go.Bar(x=d["scc_kg_kwh"], y=d["plant"], orientation="h",
                                marker_color=colors, text=d["scc_kg_kwh"].round(3), textposition="outside"))
        fig.update_layout(title="Specific Coal Consumption — All 9 Plants", height=420, xaxis_title="kg/kWh")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("#### Technology-wise Performance: Supercritical vs Subcritical")
    tech_summary = bm.groupby("technology").agg(
        avg_shr=("shr_kcal_kwh", "mean"), avg_apc=("apc_pct", "mean"),
        avg_plf=("plf_pct", "mean"), avg_scc=("scc_kg_kwh", "mean"),
    ).reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=tech_summary["technology"], y=tech_summary["avg_shr"],
                          name="Avg SHR (Kcal/kWh)", marker_color=PRIMARY), secondary_y=False)
    fig.add_trace(go.Scatter(x=tech_summary["technology"], y=tech_summary["avg_apc"],
                              name="Avg APC (%)", mode="lines+markers",
                              line=dict(color=RED, width=3)), secondary_y=True)
    fig.update_layout(title="Supercritical vs Subcritical: Avg SHR & APC", height=400)
    fig.update_yaxes(title_text="SHR (Kcal/kWh)", secondary_y=False)
    fig.update_yaxes(title_text="APC (%)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Plant Age vs Thermal Efficiency")
    fig = px.scatter(bm, x="age_years", y="shr_kcal_kwh", size="capacity_mw", color="technology",
                     text="plant", trendline="ols",
                     color_discrete_map={"Supercritical": GREEN, "Subcritical": AMBER})
    fig.update_traces(textposition="top center")
    fig.update_layout(title="Older plants tend to run at higher (worse) heat rate",
                       height=480, xaxis_title="Plant Age (years)", yaxis_title="SHR (Kcal/kWh)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Capacity Mix by Technology")
    cap_mix = bm.groupby("technology")["capacity_mw"].sum().reset_index()
    fig = px.pie(cap_mix, names="technology", values="capacity_mw", hole=0.5,
                color="technology", color_discrete_map={"Supercritical": GREEN, "Subcritical": AMBER})
    fig.update_layout(title="Installed Capacity Share — Supercritical vs Subcritical", height=380)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📝 Key observations"):
        st.markdown("""
- **Jawaharpur (2×660 MW supercritical)** is the fleet's efficiency benchmark: lowest SHR (2,049 Kcal/kWh) and lowest APC (5.75%).
- **Obra-B (5×200 MW, commissioned 1980)** is the weakest performer — 34.5% higher heat rate than Jawaharpur and the highest specific oil consumption, consistent with an ageing, undersized-unit configuration.
- **Harduaganj (1×110 MW)** shows a striking anomaly: despite tied-best coal quality (GCV 3,715), its heat rate remains poor — pointing to combustion/boiler inefficiency rather than fuel quality as the constraint.
- Supercritical units average **~360 Kcal/kWh lower heat rate** and **~2.7 percentage points lower APC** than subcritical units in this fleet — the clearest lever for future capacity additions.
- SHR rises with plant age across the fleet (see scatter above), supporting a phased R&M or retirement review for pre-1990 units.
        """)

# ============================================================================
# PAGE: TRENDS
# ============================================================================
elif page == "📈 Trends (FY20–FY24)":
    st.title("📈 Five-Year Trends")
    st.caption("FY 2019-20 → FY 2023-24, workbook plants only")

    metric_options = {
        "Energy Generated (MU)": "energy_generated_mu",
        "O&M Cost (₹ Cr)": "om_actual_cr",
        "O&M Cost per Unit (paise/kWh)": "om_cost_paise_per_unit",
        "Total Variable Cost (paise/kWh)": "total_variable_cost_paise_per_unit",
        "Average Receivables (₹ Cr)": "avg_receivables_cr",
        "Net Block % of Capital Cost": "net_block_pct_of_capital",
        "Debt-Equity Ratio": "debt_equity_ratio",
    }
    metric_label = st.selectbox("Select metric to trend", list(metric_options.keys()))
    metric = metric_options[metric_label]

    fig = px.line(ts_f, x="year", y=metric, color="plant", markers=True,
                 color_discrete_map=COLOR_MAP)
    fig.update_layout(title=f"{metric_label} — 5 Year Trend", height=480, xaxis_title="", yaxis_title=metric_label)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Compare two metrics side by side")
    c1, c2 = st.columns(2)
    with c1:
        m1 = st.selectbox("Metric A", list(metric_options.keys()), index=1, key="m1")
    with c2:
        m2 = st.selectbox("Metric B", list(metric_options.keys()), index=4, key="m2")

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        fig = px.line(ts_f, x="year", y=metric_options[m1], color="plant", markers=True,
                     color_discrete_map=COLOR_MAP)
        fig.update_layout(title=m1, height=380, xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with fcol2:
        fig = px.line(ts_f, x="year", y=metric_options[m2], color="plant", markers=True,
                     color_discrete_map=COLOR_MAP)
        fig.update_layout(title=m2, height=380, xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: RAW DATA
# ============================================================================
elif page == "🗂️ Raw Data":
    st.title("🗂️ Underlying Data")

    st.markdown("#### Cleaned Time-series (from Book2.xlsx, with derived metrics)")
    st.dataframe(ts_f, use_container_width=True, hide_index=True)
    st.download_button("Download timeseries CSV", ts_f.to_csv(index=False),
                        file_name="plant_timeseries.csv", mime="text/csv")

    st.markdown("#### 9-Plant Benchmark Snapshot (FY 2023-24)")
    st.dataframe(bm, use_container_width=True, hide_index=True)
    st.download_button("Download benchmark CSV", bm.to_csv(index=False),
                        file_name="benchmark_9plants.csv", mime="text/csv")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import utils

try:
    st.set_page_config(
        page_title="State Overview | Child Health Risk Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    pass

# Load data
df = utils.load_data("district_data.csv")
benchmarks = utils.get_national_benchmarks(df)

st.title("📊 State-Level Child Health Risk Overview")
st.caption("Aggregated risk distributions, state benchmarks, and highest-risk district identification across NFHS-5.")

# ==============================================================================
# STATE SELECTION DROPDOWN
# ==============================================================================
states_list = sorted(df["State/UT"].unique().tolist())
default_state_idx = states_list.index("Maharashtra") if "Maharashtra" in states_list else 0

selected_state = st.selectbox(
    "📍 Select State / UT for Overview:",
    options=states_list,
    index=default_state_idx,
    help="Select a state to evaluate its district risk distributions and critical priorities"
)

state_df = df[df["State/UT"] == selected_state].copy()
total_districts = len(state_df)
state_avg_chrs = state_df["CHRS"].mean()
high_risk_count = state_df["Risk Label"].isin(["High Risk", "Very High Risk"]).sum()
pct_high_risk = (high_risk_count / total_districts) * 100.0 if total_districts > 0 else 0

st.markdown("---")

# ==============================================================================
# SUMMARY METRIC CARDS
# ==============================================================================
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.metric(
        label="Total Districts",
        value=f"{total_districts}"
    )

with m_col2:
    nat_avg_chrs = 33.63
    st.metric(
        label="State Mean CHRS",
        value=f"{state_avg_chrs:.2f} / 100",
        delta=f"{state_avg_chrs - nat_avg_chrs:+.2f} vs National",
        delta_color="inverse"
    )

with m_col3:
    st.metric(
        label="High / Very High Risk Districts",
        value=f"{high_risk_count} ({pct_high_risk:.1f}%)",
        help="Districts categorized as High Risk or Very High Risk in this State"
    )

with m_col4:
    highest_dist = state_df.sort_values(by="CHRS", ascending=False).iloc[0]
    st.metric(
        label="Most Vulnerable District",
        value=f"{highest_dist['District Names']}",
        delta=f"CHRS {highest_dist['CHRS']:.1f}",
        delta_color="off"
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# RISK CATEGORY DISTRIBUTION CHART
# ==============================================================================
st.markdown("### 🥧 Risk Category Distribution")

risk_order = ["Low Risk", "Medium Risk", "High Risk", "Very High Risk"]
color_map = {
    "Low Risk": "#28a745",
    "Medium Risk": "#f59e0b",
    "High Risk": "#ea580c",
    "Very High Risk": "#dc2626"
}

# Count districts per risk label in state
risk_counts = state_df["Risk Label"].value_counts().reindex(risk_order, fill_value=0).reset_index()
risk_counts.columns = ["Risk Label", "District Count"]
risk_counts["Percentage"] = (risk_counts["District Count"] / total_districts) * 100.0

col_chart1, col_chart2 = st.columns([1, 1.2])

with col_chart1:
    # Donut chart
    fig_donut = go.Figure(data=[go.Pie(
        labels=risk_counts["Risk Label"],
        values=risk_counts["District Count"],
        hole=0.45,
        marker=dict(colors=[color_map[k] for k in risk_counts["Risk Label"]]),
        textinfo='label+percent',
        insidetextorientation='radial',
        hoverinfo='label+value+percent'
    )])
    fig_donut.update_layout(
        title=f"Risk Breakdown in {selected_state}",
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_chart2:
    # Bar chart of distribution
    fig_bar = go.Figure(data=[go.Bar(
        x=risk_counts["Risk Label"],
        y=risk_counts["District Count"],
        marker=dict(color=[color_map[k] for k in risk_counts["Risk Label"]]),
        text=[f"{cnt} dist ({pct:.1f}%)" if cnt > 0 else "" for cnt, pct in zip(risk_counts["District Count"], risk_counts["Percentage"])],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Count: %{y} districts<extra></extra>"
    )])
    fig_bar.update_layout(
        title=f"Districts per Risk Tier ({selected_state})",
        height=380,
        yaxis=dict(title="Number of Districts", gridcolor="#f1f5f9"),
        xaxis=dict(title="Risk Category"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ==============================================================================
# TOP 5 HIGHEST-RISK DISTRICTS IN THE STATE
# ==============================================================================
st.markdown("---")
st.markdown(f"### 🚨 Top 5 Highest-Risk Districts in {selected_state}")
st.write("Districts requiring immediate programmatic focus and resource allocation:")

top_5_df = state_df.sort_values(by="CHRS", ascending=False).head(5).copy()

# Add top problem area and recommended action for each of the top 5 districts
top_5_details = []
for rank, (_, row) in enumerate(top_5_df.iterrows(), 1):
    rec_d = utils.get_district_recommendation(row, df, benchmarks)
    top_prob = rec_d["top_3_indicators"][0]
    top_action = rec_d["mapped_actions"][0] if rec_d["mapped_actions"] else "Targeted health support"
    
    top_5_details.append({
        "Rank": f"#{rank}",
        "District Name": row["District Names"],
        "CHRS Score": f"{row['CHRS']:.2f}",
        "Risk Category": row["Risk Label"],
        "Primary Problem Area": f"{top_prob['clean_name']} ({top_prob['raw_value']:.1f}%)",
        "Recommended Priority Action": top_action
    })

top_5_display_df = pd.DataFrame(top_5_details)

# Horizontal Bar Chart for Top 5
fig_top5 = go.Figure()
bar_colors = [color_map.get(lbl, "#ea580c") for lbl in top_5_df["Risk Label"]]

fig_top5.add_trace(go.Bar(
    y=top_5_df["District Names"][::-1],
    x=top_5_df["CHRS"][::-1],
    orientation='h',
    marker=dict(color=bar_colors[::-1]),
    text=[f"{score:.2f} ({lbl})" for score, lbl in zip(top_5_df["CHRS"][::-1], top_5_df["Risk Label"][::-1])],
    textposition='outside',
    hovertemplate="<b>%{y}</b><br>CHRS Score: <b>%{x:.2f}</b><extra></extra>"
))

fig_top5.update_layout(
    title=f"Highest Risk CHRS Scores in {selected_state}",
    height=320,
    xaxis=dict(title="CHRS Score (0-100)", range=[0, max(top_5_df["CHRS"].max() * 1.15, 60)], gridcolor="#f1f5f9"),
    yaxis=dict(gridcolor="#f1f5f9"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=20, r=40, t=40, b=30)
)
st.plotly_chart(fig_top5, use_container_width=True)

# Table display
st.dataframe(top_5_display_df, use_container_width=True, hide_index=True)

# ==============================================================================
# COMPLETE DISTRICT RANKING TABLE FOR SELECTED STATE
# ==============================================================================
st.markdown("---")
st.markdown(f"### 📋 All Districts in {selected_state} (Ranked by Vulnerability)")

all_state_districts = state_df.sort_values(by="CHRS", ascending=False).reset_index(drop=True)
all_state_districts.index = all_state_districts.index + 1
all_state_districts.index.name = "Rank"

display_cols = ["District Names", "Risk Label", "CHRS"] + utils.RISK_INDICATORS + utils.PROTECTIVE_INDICATORS

# Format dataframe for clean display
formatted_table = all_state_districts[display_cols].copy()

# Add download button for CSV
csv_data = formatted_table.to_csv(index=True).encode("utf-8")
st.download_button(
    label=f"📥 Download {selected_state} District Data (CSV)",
    data=csv_data,
    file_name=f"{selected_state}_nfhs5_child_health_data.csv",
    mime="text/csv",
)

st.dataframe(formatted_table, use_container_width=True)

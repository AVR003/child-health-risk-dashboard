import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import utils

# Guard against multiple set_page_config calls
try:
    st.set_page_config(
        page_title="District Explorer | Child Health Risk Dashboard",
        page_icon="👶",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    pass

# Custom styling for clean, professional cards and badges
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .problem-box {
        background-color: #fff7ed;
        border-left: 5px solid #f97316;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .recommendation-banner {
        background-color: #f0fdf4;
        border-left: 5px solid #22c55e;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 14px 0 24px 0;
    }
    .badge-pill {
        display: inline-block;
        padding: 6px 16px;
        font-weight: 700;
        font-size: 0.95rem;
        border-radius: 9999px;
        text-align: center;
        letter-spacing: 0.025em;
    }
</style>
""", unsafe_allow_html=True)

# Load data
df = utils.load_data("district_data.csv")
benchmarks = utils.get_national_benchmarks(df)

# Page Title & Subheader
st.title("👶 Child Health Risk Mapping: District Explorer")
st.caption("NFHS-5 District-Level Analysis (707 Districts across 36 States & UTs)")

# ==============================================================================
# SELECTION CONTROLS (State & District Dropdowns)
# ==============================================================================
states_list = sorted(df["State/UT"].unique().tolist())

col_state, col_dist = st.columns([1, 1])

with col_state:
    # Default to Maharashtra if available, else first state
    default_state_idx = states_list.index("Maharashtra") if "Maharashtra" in states_list else 0
    selected_state = st.selectbox(
        "📍 Step 1: Select State / UT",
        options=states_list,
        index=default_state_idx,
        help="Choose a State or Union Territory to filter districts"
    )

state_df = df[df["State/UT"] == selected_state]
districts_list = sorted(state_df["District Names"].unique().tolist())

with col_dist:
    # Remember previously chosen district if valid, else first
    prev_dist = st.session_state.get("selected_district")
    default_dist_idx = districts_list.index(prev_dist) if prev_dist in districts_list else 0
    selected_district = st.selectbox(
        "🏙️ Step 2: Select District",
        options=districts_list,
        index=default_dist_idx,
        help="Choose a district to view its child health risk profile"
    )
    st.session_state["selected_district"] = selected_district

# Get district data row
dist_row = state_df[state_df["District Names"] == selected_district].iloc[0]

# Generate rule-based recommendation
rec = utils.get_district_recommendation(dist_row, df, benchmarks)
risk_label = rec["risk_label"]
chrs_score = rec["chrs"]
color_info = utils.RISK_COLORS.get(risk_label, utils.RISK_COLORS["Medium Risk"])

st.markdown("---")

# ==============================================================================
# DISTRICT HEADER & KEY METRICS
# ==============================================================================
header_col1, header_col2, header_col3 = st.columns([1.8, 1, 1.2])

with header_col1:
    st.subheader(f"{selected_district}, {selected_state}")
    badge_html = f"""
    <span class="badge-pill" style="background-color: {color_info['badge_bg']}; color: {color_info['badge_text']}; border: 1.5px solid {color_info['border']};">
        {color_info['emoji']} {risk_label}
    </span>
    """
    st.markdown(badge_html, unsafe_allow_html=True)
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.write(f"Vulnerability Tier: **{risk_label}** based on 12 NFHS-5 maternal and child indicators.")

with header_col2:
    state_avg_chrs = state_df["CHRS"].mean()
    delta_chrs = chrs_score - state_avg_chrs
    st.metric(
        label="Child Health Risk Score (CHRS)",
        value=f"{chrs_score:.2f} / 100",
        delta=f"{delta_chrs:+.2f} vs State Avg",
        delta_color="inverse"
    )

with header_col3:
    nat_avg_chrs = float(benchmarks["nat_mean"].mean())  # around 33.6
    nat_delta = chrs_score - 33.63
    st.metric(
        label="State Average CHRS",
        value=f"{state_avg_chrs:.2f} / 100",
        delta=f"{nat_delta:+.2f} vs National Avg",
        delta_color="inverse"
    )

# Visual Progress Gauge for CHRS
st.markdown("**Risk Score Spectrum (0 = Low Risk, 100 = Critical Vulnerability):**")
progress_val = min(max(chrs_score / 100.0, 0.0), 1.0)
st.progress(progress_val)
st.caption(f"Score: **{chrs_score:.2f} / 100** | Defined Ranges: Low (0–25) · Medium (25–50) · High (50–75) · Very High (75–100)")


# ==============================================================================
# MAIN PROBLEM AREAS & RULE-BASED POLICY DIRECTIVE
# ==============================================================================
st.markdown("### 🚨 Main Problem Areas & Priority Policy Actions")

# Top 3 problem cards
prob_cols = st.columns(3)
for idx, item in enumerate(rec["top_3_indicators"]):
    with prob_cols[idx]:
        # Calculate plain-English difference vs national average
        raw_val = item["raw_value"]
        nat_avg = item["nat_raw_mean"]
        diff = raw_val - nat_avg
        if diff >= 0:
            diff_label = f"(+{diff:.1f}% above average)"
        else:
            diff_label = f"({diff:.1f}% below average)"

        st.markdown(f"""
        <div class="problem-box">
            <div style="font-size: 0.85rem; font-weight: 700; color: #c2410c; text-transform: uppercase;">
                Priority #{idx + 1} Risk Factor
            </div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #1e293b; margin: 4px 0;">
                {item['clean_name']}
            </div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #ea580c;">
                {raw_val:.2f}%
            </div>
            <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">
                National Average: <b>{nat_avg:.1f}%</b> {diff_label}
            </div>
            <hr style="margin: 8px 0; border: none; border-top: 1px dashed #fdba74;">
            <div style="font-size: 0.85rem; color: #334155;">
                🎯 <b>Target Action:</b> {item['action'].capitalize()}
            </div>
        </div>
        """, unsafe_allow_html=True)



# Generated Rule-based Summary Directive
st.markdown(f"""
<div class="recommendation-banner">
    <div style="font-size: 0.9rem; font-weight: 700; color: #15803d; text-transform: uppercase; margin-bottom: 6px;">
        📋 Rule-Based Policy Recommendation (Auto-Generated)
    </div>
    <div style="font-size: 1.05rem; line-height: 1.6; color: #0f172a; font-weight: 500;">
        {rec['summary_paragraph']}
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# COMPARATIVE BAR CHART: DISTRICT VS STATE AVERAGE
# ==============================================================================
st.markdown("### 📊 Indicator Comparison: District vs. State Average")

chart_filter = st.radio(
    "Filter Indicators:",
    options=["All 12 Indicators", "4 Child Risk Indicators (Lower is Better)", "8 Protective Health Indicators (Higher is Better)"],
    horizontal=True
)

if chart_filter == "4 Child Risk Indicators (Lower is Better)":
    selected_indicators = utils.RISK_INDICATORS
elif chart_filter == "8 Protective Health Indicators (Higher is Better)":
    selected_indicators = utils.PROTECTIVE_INDICATORS
else:
    selected_indicators = utils.ALL_INDICATORS

# Prepare data for plotting
labels = [col.replace(" (%)", "") for col in selected_indicators]
district_vals = [float(dist_row[col]) for col in selected_indicators]
state_vals = [float(state_df[col].mean()) for col in selected_indicators]

# Build Plotly Grouped Bar Chart
fig = go.Figure()

fig.add_trace(go.Bar(
    y=labels,
    x=district_vals,
    name=f"{selected_district} (District)",
    orientation='h',
    marker=dict(color='#0284c7', line=dict(color='#0369a1', width=1)),
    text=[f"{v:.1f}%" for v in district_vals],
    textposition='outside',
    hovertemplate="<b>%{y}</b><br>" + f"{selected_district}: " + "<b>%{x:.2f}%</b><extra></extra>"
))

fig.add_trace(go.Bar(
    y=labels,
    x=state_vals,
    name=f"{selected_state} (State Average)",
    orientation='h',
    marker=dict(color='#94a3b8', line=dict(color='#64748b', width=1)),
    text=[f"{v:.1f}%" for v in state_vals],
    textposition='outside',
    hovertemplate="<b>%{y}</b><br>" + f"{selected_state} Avg: " + "<b>%{x:.2f}%</b><extra></extra>"
))

chart_height = 420 if len(selected_indicators) <= 4 else 600

fig.update_layout(
    barmode='group',
    height=chart_height,
    margin=dict(l=20, r=40, t=30, b=30),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis=dict(
        title="Coverage / Prevalence Percentage (%)",
        range=[0, 115],
        ticksuffix="%",
        gridcolor="#f1f5f9"
    ),
    yaxis=dict(
        autorange="reversed",
        gridcolor="#f1f5f9"
    ),
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# DETAILED INDICATOR DATA BREAKDOWN (TABULAR)
# ==============================================================================
with st.expander("🔍 View Complete 12-Indicator Numerical Table"):
    comparison_records = []
    for col in utils.ALL_INDICATORS:
        d_val = float(dist_row[col])
        s_val = float(state_df[col].mean())
        n_val = float(benchmarks["raw_nat_mean"][col])
        diff_state = d_val - s_val
        clean_name = col.replace(" (%)", "")
        ind_type = "Risk (lower is better)" if col in utils.RISK_INDICATORS else "Protective (higher is better)"
        comparison_records.append({
            "Indicator": clean_name,
            "Type": ind_type,
            f"{selected_district} (%)": round(d_val, 2),
            f"{selected_state} Avg (%)": round(s_val, 2),
            "Diff vs State (% pts)": round(diff_state, 2),
            "National Avg (%)": round(n_val, 2),
        })

    comp_df = pd.DataFrame(comparison_records)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

# ==============================================================================
# INTERACTIVE CHATBOT (POLICY ASSISTANT)
# ==============================================================================
st.markdown("---")
st.markdown("### 💬 Child Health Policy Chatbot")
st.caption(f"Ask questions about child health status and priority actions for **{selected_district}**")

# Optional LLM integration settings (Groq / Gemini / Offline)
with st.expander("⚙️ Connect Groq API or Gemini API (Optional)", expanded=False):
    st.write(
        "By default, the chatbot runs **100% offline using the rule-based engine**. "
        "You can optionally connect a free **Groq API Key** (Llama 3.3 70B) or **Gemini API Key** (Gemini 1.5 Flash) for free-form conversational answers:"
    )
    llm_col1, llm_col2 = st.columns([1, 2])
    with llm_col1:
        custom_provider = st.selectbox(
            "AI Provider",
            options=["Auto-Detect", "Groq", "Gemini", "OpenAI"],
            index=0,
            key="llm_provider_choice",
            help="Auto-detects from key prefix (gsk_ = Groq, AIza = Gemini, sk- = OpenAI)"
        )
    with llm_col2:
        custom_key_input = st.text_input(
            "Enter API Key",
            type="password",
            value=st.session_state.get("custom_llm_key", ""),
            placeholder="Paste Groq key (gsk_...) or Gemini key (AIza...)",
            help="Key is stored only in session memory during your visit",
            key="llm_key_input_field"
        )
        if custom_key_input:
            st.session_state["custom_llm_key"] = custom_key_input.strip()

    # Display active engine status
    active_prov, _, active_model = utils.get_active_llm_provider(
        st.session_state.get("custom_llm_key"),
        custom_provider
    )
    if active_prov == "Groq":
        st.success(f"🚀 **Active Engine: Groq Cloud ({active_model})** — Ultra-fast AI answers enabled!")
    elif active_prov == "Gemini":
        st.success(f"✨ **Active Engine: Google Gemini ({active_model})** — Google AI Studio connected!")
    elif active_prov == "OpenAI":
        st.success(f"🧠 **Active Engine: OpenAI ({active_model})**")
    else:
        st.info("⚡ **Active Engine: Offline Rule-Based Engine** (Deterministic, instant & runs without any key).")

# Manage district chat session state
session_chat_key = f"chat_messages_{selected_district}"
if session_chat_key not in st.session_state:
    # Initialize greeting message
    initial_greeting = (
        f"👋 Hello! I am your Child Health Policy Assistant for **{selected_district} ({selected_state})**.\n\n"
        f"- **Child Health Risk Score (CHRS):** **{chrs_score:.2f} / 100**\n"
        f"- **Current Vulnerability Level:** **{risk_label}**\n\n"
        f"**Recommendation Summary:**\n"
        f"> {rec['summary_paragraph']}\n\n"
        f"How can I assist you with district planning today?"
    )
    st.session_state[session_chat_key] = [
        {"role": "assistant", "content": initial_greeting}
    ]

# Display conversation messages
for msg in st.session_state[session_chat_key]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Quick question suggestion buttons
st.write("💡 *Quick questions:*")
q_col1, q_col2, q_col3 = st.columns(3)
quick_query = None

with q_col1:
    if st.button("Why is this district at risk?", use_container_width=True, key=f"q1_{selected_district}"):
        quick_query = "Why is this district at risk?"

with q_col2:
    if st.button("What should be improved first?", use_container_width=True, key=f"q2_{selected_district}"):
        quick_query = "What should be improved first?"

with q_col3:
    if st.button("Compare with state average", use_container_width=True, key=f"q3_{selected_district}"):
        quick_query = "How does it compare to the state average?"

# Handle user input via chat input or quick buttons
user_input = st.chat_input(f"Ask about {selected_district}'s health profile or policy interventions...")

query_to_process = user_input or quick_query

if query_to_process:
    # Append user question
    st.session_state[session_chat_key].append({"role": "user", "content": query_to_process})
    with st.chat_message("user"):
        st.markdown(query_to_process)

    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Analyzing district indicators..."):
            reply = utils.answer_district_query(
                query_to_process,
                dist_row,
                df,
                benchmarks,
                custom_key=st.session_state.get("custom_llm_key"),
                custom_provider=st.session_state.get("llm_provider_choice", "Auto-Detect")
            )
            st.markdown(reply)
            st.session_state[session_chat_key].append({"role": "assistant", "content": reply})


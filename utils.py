import os
import pandas as pd
import numpy as np
import streamlit as st

# ==============================================================================
# CONFIGURATION & POLICY ACTION MAPPING
# Keep mapping here for easy editing and custom phrasing.
# ==============================================================================
POLICY_ACTION_MAP = {
    "Stunting (%)": "integrated nutrition programs: supplementary feeding, growth monitoring, community nutrition rehabilitation centres",
    "Wasting (%)": "integrated nutrition programs: supplementary feeding, growth monitoring, community nutrition rehabilitation centres",
    "Underweight (%)": "integrated nutrition programs: supplementary feeding, growth monitoring, community nutrition rehabilitation centres",
    "Child Anaemia (%)": "iron-folic acid supplementation, deworming, dietary diversity programs",
    "Children Fully Immunized (%)": "immunization outreach camps, mobile vaccination units, tracking of dropouts",
    "Early Initiation of Breastfeeding (%)": "counselling by frontline health workers, postnatal home visits",
    "Exclusive Breastfeeding (%)": "counselling by frontline health workers, postnatal home visits",
    "Institutional Delivery (%)": "more birthing facilities, transport support for pregnant women, delivery incentives",
    "Mothers with 4+ ANC Visits (%)": "antenatal care outreach, ASHA worker follow-ups",
    "Women's Education 10+ Years Schooling (%)": "girls' education retention programs, maternal health literacy",
    "Improved Sanitation Facility (%)": "toilet construction, hygiene awareness campaigns",
    "Improved Drinking Water Source (%)": "safe water supply infrastructure, household water treatment",
}

# 4 Risk Indicators (higher percentage = worse child outcome)
RISK_INDICATORS = [
    "Stunting (%)",
    "Wasting (%)",
    "Underweight (%)",
    "Child Anaemia (%)",
]

# 8 Protective Indicators (higher percentage = better child outcome)
PROTECTIVE_INDICATORS = [
    "Children Fully Immunized (%)",
    "Early Initiation of Breastfeeding (%)",
    "Exclusive Breastfeeding (%)",
    "Institutional Delivery (%)",
    "Mothers with 4+ ANC Visits (%)",
    "Women's Education 10+ Years Schooling (%)",
    "Improved Sanitation Facility (%)",
    "Improved Drinking Water Source (%)",
]

ALL_INDICATORS = RISK_INDICATORS + PROTECTIVE_INDICATORS

# Indicator clean labels for human display
INDICATOR_LABELS = {
    "Stunting (%)": "Child Stunting",
    "Wasting (%)": "Child Wasting",
    "Underweight (%)": "Child Underweight",
    "Child Anaemia (%)": "Child Anaemia",
    "Children Fully Immunized (%)": "Full Immunization",
    "Early Initiation of Breastfeeding (%)": "Early Breastfeeding Initiation",
    "Exclusive Breastfeeding (%)": "Exclusive Breastfeeding (0-5m)",
    "Institutional Delivery (%)": "Institutional Delivery",
    "Mothers with 4+ ANC Visits (%)": "Mothers with 4+ ANC Visits",
    "Women's Education 10+ Years Schooling (%)": "Women's Education (10+ Yrs)",
    "Improved Sanitation Facility (%)": "Improved Sanitation Facility",
    "Improved Drinking Water Source (%)": "Improved Drinking Water Source",
}

# Color palette for Risk Labels
RISK_COLORS = {
    "Low Risk": {
        "badge_bg": "#d4edda",
        "badge_text": "#155724",
        "border": "#28a745",
        "hex": "#28a745",
        "emoji": "🟢",
    },
    "Medium Risk": {
        "badge_bg": "#fff3cd",
        "badge_text": "#856404",
        "border": "#ffc107",
        "hex": "#f59e0b",
        "emoji": "🟡",
    },
    "High Risk": {
        "badge_bg": "#ffe5d0",
        "badge_text": "#a04000",
        "border": "#fd7e14",
        "hex": "#ea580c",
        "emoji": "🟠",
    },
    "Very High Risk": {
        "badge_bg": "#f8d7da",
        "badge_text": "#721c24",
        "border": "#dc3545",
        "hex": "#dc2626",
        "emoji": "🔴",
    },
}

# ==============================================================================
# DATA LOADING (CACHED)
# ==============================================================================
@st.cache_data
def load_data(csv_path="district_data.csv"):
    """
    Loads district-level NFHS-5 data from CSV.
    Corrects 'Maharastra' -> 'Maharashtra' once right after loading.
    Strips accidental trailing/leading whitespaces on names.
    Never invents data.
    """
    if not os.path.isabs(csv_path):
        # Allow locating CSV relative to current file or directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(base_dir, csv_path)
        if os.path.exists(alt_path):
            csv_path = alt_path

    df = pd.read_csv(csv_path)

    # State name correction: Maharastra -> Maharashtra
    df["State/UT"] = df["State/UT"].astype(str).str.strip().replace("Maharastra", "Maharashtra")
    df["District Names"] = df["District Names"].astype(str).str.strip()

    # Ensure numerical types
    for col in ALL_INDICATORS + ["CHRS"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


@st.cache_data
def get_national_benchmarks(df):
    """
    Computes national mean and std for all risk values across all 707 districts.
    Step 1: Convert protective to risk using (100 - value).
    Step 2: Compute mean and std for z-score calculation.
    """
    risk_matrix = pd.DataFrame(index=df.index)

    for col in RISK_INDICATORS:
        risk_matrix[col] = df[col]

    for col in PROTECTIVE_INDICATORS:
        risk_matrix[col] = 100.0 - df[col]

    nat_mean = risk_matrix.mean()
    nat_std = risk_matrix.std(ddof=0)
    # Avoid zero division
    nat_std = nat_std.replace(0, 1.0)

    # Calculate Z-score matrix for all districts
    z_matrix = (risk_matrix - nat_mean) / nat_std

    return {
        "risk_matrix": risk_matrix,
        "nat_mean": nat_mean,
        "nat_std": nat_std,
        "z_matrix": z_matrix,
        "raw_nat_mean": df[ALL_INDICATORS].mean(),
    }


# ==============================================================================
# RULE-BASED RECOMMENDATION ENGINE
# ==============================================================================
def get_district_recommendation(district_row, df, benchmarks=None):
    """
    Executes the 5-step rule-based recommendation engine for a district:
    Step 1: Convert 8 protective indicators to risk values (100 - value).
    Step 2: Compute z-score of each risk value against national mean/std.
    Step 3: Top 3 indicators with highest z-scores are main problem areas.
    Step 4: Map indicators to policy actions.
    Step 5: Output structured dictionary and formatted summary paragraph.
    """
    if benchmarks is None:
        benchmarks = get_national_benchmarks(df)

    dist_name = str(district_row["District Names"])
    state_name = str(district_row["State/UT"])
    risk_label = str(district_row["Risk Label"])
    chrs_score = float(district_row["CHRS"])

    # Compute risk values and z-scores for this district
    district_z_scores = {}
    district_raw_values = {}
    district_risk_values = {}

    for col in ALL_INDICATORS:
        raw_val = float(district_row[col])
        district_raw_values[col] = raw_val

        if col in RISK_INDICATORS:
            risk_val = raw_val
        else:
            risk_val = 100.0 - raw_val

        district_risk_values[col] = risk_val
        mean_val = benchmarks["nat_mean"][col]
        std_val = benchmarks["nat_std"][col]
        z = (risk_val - mean_val) / std_val
        district_z_scores[col] = z

    # Step 3: Top 3 indicators with highest z-scores
    sorted_by_z = sorted(district_z_scores.items(), key=lambda x: x[1], reverse=True)
    top_3_indicators = sorted_by_z[:3]

    # Step 4: Map each indicator to policy actions
    top_3_problems_detail = []
    mapped_actions = []
    seen_actions = set()

    for col, z_val in top_3_indicators:
        raw_val = district_raw_values[col]
        clean_name = col.replace(" (%)", "")
        action = POLICY_ACTION_MAP.get(col, "targeted health intervention")

        top_3_problems_detail.append({
            "indicator": col,
            "clean_name": clean_name,
            "raw_value": raw_val,
            "risk_value": district_risk_values[col],
            "z_score": z_val,
            "action": action,
            "is_risk_type": col in RISK_INDICATORS,
            "nat_raw_mean": benchmarks["raw_nat_mean"][col],
        })

        if action not in seen_actions:
            mapped_actions.append(action)
            seen_actions.add(action)

    # Step 5: Output short paragraph
    # Format: "[District] is [Risk Label], mainly due to [top 3 problems with their actual values]. Recommended priority actions: [mapped actions, most severe first]."
    problems_phrasing = []
    for item in top_3_problems_detail:
        problems_phrasing.append(f"{item['clean_name']} ({item['raw_value']:.2f}%)")

    if len(problems_phrasing) == 3:
        problems_str = f"{problems_phrasing[0]}, {problems_phrasing[1]}, and {problems_phrasing[2]}"
    else:
        problems_str = ", ".join(problems_phrasing)

    actions_str = "; ".join(mapped_actions)

    summary_paragraph = (
        f"{dist_name} is {risk_label}, mainly due to {problems_str}. "
        f"Recommended priority actions: {actions_str}."
    )

    return {
        "district": dist_name,
        "state": state_name,
        "risk_label": risk_label,
        "chrs": chrs_score,
        "top_3_indicators": top_3_problems_detail,
        "mapped_actions": mapped_actions,
        "summary_paragraph": summary_paragraph,
        "z_scores": district_z_scores,
        "raw_values": district_raw_values,
    }


# ==============================================================================
# CHATBOT INTELLIGENCE (OFFLINE RULE-BASED + OPTIONAL LLM ROUTING)
# ==============================================================================
def answer_district_query(user_query, district_row, df, benchmarks=None, custom_key=None, custom_provider="Auto-Detect"):
    """
    Answers user queries about the selected district.
    Version 1: Offline rule-based matching based on district data, state avg, and recommendation engine.
    Optional: If an API key exists in st.secrets or user input (Groq / Gemini / OpenAI), routes to LLM.
    """
    rec = get_district_recommendation(district_row, df, benchmarks)
    dist_name = rec["district"]
    state_name = rec["state"]
    risk_label = rec["risk_label"]
    chrs = rec["chrs"]
    top_3 = rec["top_3_indicators"]

    # Calculate state averages
    state_df = df[df["State/UT"] == state_name]
    state_avg_chrs = state_df["CHRS"].mean()
    state_indicators_mean = state_df[ALL_INDICATORS].mean()

    # Check for Optional LLM Key (Groq / Gemini / OpenAI)
    llm_response = try_llm_generation(user_query, district_row, rec, state_df, benchmarks, custom_key, custom_provider)
    if llm_response:
        return llm_response


    # ================= Offline Rule-Based Engine =================
    q = user_query.lower().strip()

    # 1. Why is this district high / medium / low risk?
    if any(k in q for k in ["why", "reason", "cause", "risk factor", "why high", "why low", "why medium"]):
        text = (
            f"**Risk Assessment for {dist_name} ({state_name}):**\n\n"
            f"- **CHRS Score:** {chrs:.2f} / 100 ({risk_label})\n"
            f"- **State Average CHRS:** {state_avg_chrs:.2f} / 100\n\n"
            f"Compared across all 707 districts in India, **{dist_name}** exhibits the highest vulnerability in three critical areas:\n"
        )
        for i, item in enumerate(top_3, 1):
            nat_avg = item["nat_raw_mean"]
            text += f"{i}. **{item['clean_name']}**: Current level is **{item['raw_value']:.1f}%** (National avg: {nat_avg:.1f}%).\n"
        text += f"\n💡 *Recommendation summary:* {rec['summary_paragraph']}"
        return text

    # 2. What should be improved first / priority actions / what to do
    if any(k in q for k in ["improve", "priority", "first", "action", "do first", "intervene", "policy", "recommend"]):
        text = (
            f"**Recommended Action Priorities for {dist_name}:**\n\n"
            f"Based on the greatest deficits relative to national standards, targeted interventions should be prioritized in this exact order:\n\n"
        )
        for i, item in enumerate(top_3, 1):
            text += f"**Priority {i}: Address {item['clean_name']} (Currently {item['raw_value']:.1f}%)**\n"
            text += f"- *Mandated policy response:* {item['action'].capitalize()}.\n\n"
        text += f"📌 **Full Policy Directive:**\n> {rec['summary_paragraph']}"
        return text


    # 3. How does it compare to state average / state comparison
    if any(k in q for k in ["compare", "state average", "state avg", "state", "benchmark", "better or worse"]):
        chrs_diff = chrs - state_avg_chrs
        status = "higher risk than" if chrs_diff > 0 else "lower risk than"
        text = (
            f"**Comparison: {dist_name} vs {state_name} Average:**\n\n"
            f"- **District CHRS:** {chrs:.2f}\n"
            f"- **State Average CHRS:** {state_avg_chrs:.2f} (Difference: {chrs_diff:+.2f}, {status} state average)\n\n"
            f"**Indicator Comparison:**\n"
        )
        for col in ALL_INDICATORS:
            d_val = district_row[col]
            s_val = state_indicators_mean[col]
            diff = d_val - s_val
            c_name = col.replace(" (%)", "")
            if col in RISK_INDICATORS:
                verdict = "⚠️ Higher Risk" if diff > 0 else "✅ Better"
            else:
                verdict = "✅ Better" if diff > 0 else "⚠️ Lagging"
            text += f"- **{c_name}**: {dist_name} **{d_val:.1f}%** vs {state_name} **{s_val:.1f}%** ({diff:+.1f}%) — {verdict}\n"
        return text

    # 4. Specific indicator queries (anaemia, stunting, water, immunization, etc.)
    for col in ALL_INDICATORS:
        clean = col.replace(" (%)", "").lower()
        keywords = clean.split()
        if any(w in q for w in keywords if len(w) > 3):
            val = district_row[col]
            s_val = state_indicators_mean[col]
            nat_val = benchmarks["raw_nat_mean"][col]
            clean_name = col.replace(" (%)", "")
            action = POLICY_ACTION_MAP.get(col, "targeted maternal and child health intervention")
            return (
                f"**{clean_name} Profile for {dist_name}:**\n\n"
                f"- **District Level:** **{val:.2f}%**\n"
                f"- **State Average ({state_name}):** {s_val:.2f}%\n"
                f"- **National Average:** {nat_val:.2f}%\n\n"
                f"**Policy Action:** {action.capitalize()}."
            )

    # 5. General / Default Greeting & Recommendation
    return (
        f"**District Overview for {dist_name}, {state_name}:**\n\n"
        f"- **Child Health Risk Score (CHRS):** {chrs:.2f} / 100\n"
        f"- **Risk Classification:** **{risk_label}**\n\n"
        f"**Summary:**\n{rec['summary_paragraph']}\n\n"
        f"*You can ask me questions like:*\n"
        f"- *'Why is this district high risk?'*\n"
        f"- *'What should be improved first?'*\n"
        f"- *'How does it compare to the state average?'*\n"
        f"- *'What is the anaemia situation?'*"
    )


def get_active_llm_provider(custom_key=None, custom_provider="Auto-Detect"):
    """
    Detects which LLM provider and API key to use.
    Priority: custom_key > st.secrets > secrets.toml file > os.environ
    Bulletproof against StreamlitSecretNotFoundError.
    """
    key = custom_key
    if not key and hasattr(st, "session_state"):
        key = st.session_state.get("custom_llm_key", "").strip()

    groq_key = None
    gemini_key = None
    openai_key = None

    # 1. Safely read from st.secrets (handles missing secrets.toml without throwing StreamlitSecretNotFoundError)
    try:
        if hasattr(st, "secrets"):
            groq_key = st.secrets.get("GROQ_API_KEY")
            gemini_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
            openai_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass

    # 2. Fallback: Manually read from secrets.toml if placed in project root or .streamlit/
    if not groq_key and not gemini_key and not openai_key:
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            candidate_paths = [
                os.path.join(base_dir, ".streamlit", "secrets.toml"),
                os.path.join(base_dir, "secrets.toml"),
            ]
            for p in candidate_paths:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if "=" in line and not line.startswith("#"):
                                k, v = line.split("=", 1)
                                k = k.strip()
                                v = v.strip().strip('"').strip("'")
                                if k == "GROQ_API_KEY" and not groq_key:
                                    groq_key = v
                                elif k in ("GEMINI_API_KEY", "GOOGLE_API_KEY") and not gemini_key:
                                    gemini_key = v
                                elif k == "OPENAI_API_KEY" and not openai_key:
                                    openai_key = v
        except Exception:
            pass

    # 3. Environment variables
    if not groq_key:
        groq_key = os.environ.get("GROQ_API_KEY")
    if not gemini_key:
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not openai_key:
        openai_key = os.environ.get("OPENAI_API_KEY")

    # If user provided a custom key in the UI
    if key:
        if custom_provider == "Groq" or key.startswith("gsk_"):
            return "Groq", key, "llama-3.3-70b-versatile"
        elif custom_provider == "Gemini" or key.startswith("AIza") or key.startswith("AQ."):
            return "Gemini", key, "gemini-flash-latest"
        elif custom_provider == "OpenAI" or key.startswith("sk-"):
            return "OpenAI", key, "gpt-4o-mini"
        else:
            if key.startswith("AQ.") or key.startswith("AIza"):
                return "Gemini", key, "gemini-flash-latest"
            return "Groq", key, "llama-3.3-70b-versatile"

    # From secrets / env
    if groq_key:
        return "Groq", groq_key, "llama-3.3-70b-versatile"
    if gemini_key:
        return "Gemini", gemini_key, "gemini-flash-latest"
    if openai_key:
        return "OpenAI", openai_key, "gpt-4o-mini"

    return "Offline", None, None



def try_llm_generation(user_query, district_row, rec, state_df, benchmarks, custom_key=None, custom_provider="Auto-Detect"):
    """
    Routes user query to Groq API, Gemini API, or OpenAI API if an API key is available.
    Falls back gracefully to None (triggering offline engine) if no key or error occurs.
    """
    provider, api_key, model_name = get_active_llm_provider(custom_key, custom_provider)

    if not api_key or provider == "Offline":
        return None

    # Structured context for LLM
    dist_name = rec["district"]
    state_name = rec["state"]

    top_problems_list = []
    for p in rec["top_3_indicators"]:
        top_problems_list.append(f"{p['clean_name']} ({p['raw_value']:.1f}%)")
    top_problems_str = ", ".join(top_problems_list)

    indicators_list = []
    for c in ALL_INDICATORS:
        c_clean = c.replace(" (%)", "")
        indicators_list.append(f"{c_clean}: {district_row[c]:.1f}%")
    district_indicators_str = ", ".join(indicators_list)
    
    context_str = (
        f"District: {dist_name}, State: {state_name}\n"
        f"Child Health Risk Score (CHRS): {rec['chrs']:.2f} / 100\n"
        f"Risk Category: {rec['risk_label']}\n"
        f"State Average CHRS: {state_df['CHRS'].mean():.2f}\n"
        f"National Average CHRS: 33.63\n"
        f"Top 3 Identified Deficits (by national Z-score): {top_problems_str}\n"
        f"Rule-Based Recommended Actions: {rec['summary_paragraph']}\n"
        f"District Indicators: {district_indicators_str}\n"
    )


    prompt = (
        "You are an expert, empathetic Public Health Policy Assistant for India's NFHS-5 Child Health Dashboard. "
        "Answer the user's question accurately using ONLY the district data and recommendation engine context provided below. "
        "Provide actionable, culturally relevant public health advice in plain English. Avoid ML jargon. Cite exact percentages when helpful.\n\n"
        f"--- CONTEXT DATA ---\n{context_str}\n\n"
        f"USER QUESTION: {user_query}\n\n"
        "ANSWER:"
    )

    # 1. GROQ API (Llama 3.3 70B / Llama 3.1 8B) - Fast & Free
    if provider == "Groq":
        try:
            import json
            import urllib.request
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "StreamlitChildHealthApp/1.0"
            }
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are an expert Public Health Policy Assistant for India's NFHS-5 Child Health Dashboard."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4,
                "max_tokens": 600
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                result = json.loads(response.read().decode("utf-8"))
                ans = result["choices"][0]["message"]["content"]
                return f"{ans}\n\n---\n*🚀 Powered by Groq Llama-3 AI*"
        except Exception:
            pass

    # 2. GOOGLE GEMINI API (Gemini Flash) - Free Tier
    if provider == "Gemini":
        gemini_models_to_try = [model_name, "gemini-flash-latest", "gemini-2.5-flash", "gemini-1.5-flash"]
        for m in gemini_models_to_try:
            try:
                import json
                import urllib.request
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 600}
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=12) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    ans = result["candidates"][0]["content"]["parts"][0]["text"]
                    return f"{ans}\n\n---\n*✨ Powered by Google Gemini AI*"
            except Exception:
                continue

    # 3. OPENAI API (GPT-4o mini)

    if provider == "OpenAI":
        try:
            import json
            import urllib.request
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are an expert Public Health Policy Assistant for India's NFHS-5 Child Health Dashboard."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4,
                "max_tokens": 600
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            pass

    return None


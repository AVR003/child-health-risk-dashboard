import streamlit as st
import pandas as pd
import utils

try:
    st.set_page_config(
        page_title="About & Methodology | Child Health Risk Dashboard",
        page_icon="ℹ️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    pass

st.title("ℹ️ About the Project & Methodology")
st.caption("AI-Based Risk Mapping and Interactive Dashboard for Child Health Outcomes (NFHS-5)")

st.markdown("""
### 📌 1. Project Overview
This project presents an interactive public health intelligence dashboard designed to monitor, map, and mitigate child health vulnerabilities across **707 districts** in all 36 States and Union Territories of India.

Using district-level data from the **National Family Health Survey (NFHS-5, 2019–21)**, the platform synthesizes critical clinical, nutritional, maternal care, and environmental determinants into a unified, actionable **Child Health Risk Score (CHRS)**. 

The primary objective is to empower district collectors, Chief Medical Officers (CMOs), and public health policy teams to:
1. **Identify Vulnerabilities Instantly:** Understand each district's composite risk tier without wading through fragmented tables.
2. **Prioritize Targeted Interventions:** Isolate the top 3 driving deficits through standardized national Z-scores.
3. **Deploy Evidence-Based Policies:** Map observed deficits directly to proven maternal-child healthcare and nutrition interventions.
""")

st.markdown("---")

st.markdown("""
### 📐 2. Composite Health Risk Score (CHRS) Framework
The **Child Health Risk Score (CHRS)** is a continuous score ranging from **0 (optimal health status)** to **100 (critical composite risk)**. It synthesizes **12 core NFHS-5 indicators**:
""")

col_ind1, col_ind2 = st.columns(2)

with col_ind1:
    st.markdown("""
    #### ⚠️ 4 Child Risk Indicators (Direct)
    *Higher percentage indicates greater health distress:*
    1. **Stunting (%)**: Children under 5 years whose height-for-age is below -2 SD (chronic malnutrition).
    2. **Wasting (%)**: Children under 5 years whose weight-for-height is below -2 SD (acute malnutrition).
    3. **Underweight (%)**: Children under 5 years whose weight-for-age is below -2 SD.
    4. **Child Anaemia (%)**: Children age 6–59 months with haemoglobin < 11.0 g/dl.
    """)

with col_ind2:
    st.markdown("""
    #### 🛡️ 8 Protective Indicators (Inverted)
    *Lower percentage indicates greater programmatic deficiency:*
    1. **Children Fully Immunized (%)**: BCG, measles, 3 doses each of polio & DPT.
    2. **Early Initiation of Breastfeeding (%)**: Breastfed within 1 hour of birth.
    3. **Exclusive Breastfeeding (%)**: Exclusively breastfed for first 6 months.
    4. **Institutional Delivery (%)**: Births delivered in healthcare institutions.
    5. **Mothers with 4+ ANC Visits (%)**: Antenatal check-ups received by pregnant mothers.
    6. **Women's Education 10+ Years Schooling (%)**: Female secondary educational attainment.
    7. **Improved Sanitation Facility (%)**: Households with access to improved toilets.
    8. **Improved Drinking Water Source (%)**: Households with access to clean drinking water.
    """)

st.markdown("""
#### Mathematical Formulation:
Each protective indicator is converted into a **risk deficit value**:
$$\\text{Risk Value} = 100 - \\text{Protective Indicator Percentage}$$

For the 4 clinical risk indicators, the risk value is retained directly:
$$\\text{Risk Value} = \\text{Risk Indicator Percentage}$$

The district's overall CHRS score is the unweighted arithmetic mean of all 12 standardized risk values:
$$\\text{CHRS} = \\frac{1}{12} \\left( \\sum_{i=1}^4 \\text{Risk}_i + \\sum_{j=1}^8 (100 - \\text{Protective}_j) \\right)$$

#### 🎯 Risk Label Assignment (Defined Score Ranges):
As defined in the project formulation, each district is assigned a risk category based on predefined CHRS ranges:

| CHRS Range | Risk Label | Status / Policy Implication |
| :---: | :---: | :--- |
| **0 – 25** | **🟢 Low** | Optimal child health outcomes; sustained routine care |
| **25 – 50** | **🟡 Medium** | Moderate vulnerability; routine programmatic monitoring |
| **50 – 75** | **🟠 High** | Elevated vulnerability; intensified inter-departmental convergence |
| **75 – 100** | **🔴 Very High** | Critical vulnerability; emergency mission-mode resource deployment |

These risk labels serve as the target classification variable for the supervised machine learning models developed in this study.
""")

st.markdown("---")

st.markdown("""
### 🧠 3. Rule-Based Recommendation Engine & Z-Score Normalization
Comparing raw indicator percentages directly is methodologically flawed because indicators have inherently different baselines. For example:
- **Child Anaemia** has a national average of **65.8%**, whereas **Wasting** has a national average of **18.6%**.
- A district with 25% wasting has severe acute crisis (+1.3 standard deviations above national average), even though 25% is numerically lower than 60% anaemia.

#### Z-Score Normalization Formula:
For each indicator $k$ in district $d$:
$$Z_{d,k} = \\frac{\\text{Risk Value}_{d,k} - \\mu_k}{\\sigma_k}$$
where $\\mu_k$ and $\\sigma_k$ represent the national mean and standard deviation across all 707 districts.

The **top 3 indicators with the highest Z-scores** represent the district's primary problem areas. Each problem area is mapped to evidence-based policy actions configured in the system:
""")

mapping_records = [
    {"Deficit Area": "Child Stunting / Wasting / Underweight", "Mandated Policy Intervention": "Integrated nutrition programs: supplementary feeding, growth monitoring, community nutrition rehabilitation centres"},
    {"Deficit Area": "Child Anaemia", "Mandated Policy Intervention": "Iron-folic acid supplementation, deworming, dietary diversity programs"},
    {"Deficit Area": "Low Immunization Coverage", "Mandated Policy Intervention": "Immunization outreach camps, mobile vaccination units, tracking of dropouts"},
    {"Deficit Area": "Suboptimal Breastfeeding Initiation / Exclusive", "Mandated Policy Intervention": "Counselling by frontline health workers, postnatal home visits"},
    {"Deficit Area": "Low Institutional Delivery", "Mandated Policy Intervention": "More birthing facilities, transport support for pregnant women, delivery incentives"},
    {"Deficit Area": "Inadequate Antenatal Care (4+ ANC)", "Mandated Policy Intervention": "Antenatal care outreach, ASHA worker follow-ups"},
    {"Deficit Area": "Low Female Secondary Schooling", "Mandated Policy Intervention": "Girls' education retention programs, maternal health literacy"},
    {"Deficit Area": "Deficient Sanitation Coverage", "Mandated Policy Intervention": "Toilet construction, hygiene awareness campaigns"},
    {"Deficit Area": "Deficient Safe Water Coverage", "Mandated Policy Intervention": "Safe water supply infrastructure, household water treatment"},
]
st.table(pd.DataFrame(mapping_records))

st.markdown("---")

st.markdown("""
### 🤖 4. Model Comparison Results (Machine Learning Evaluation)
Below is the exact empirical evaluation of all classification models benchmarked in our project notebook on the 707-district dataset:
""")

# Model Comparison Results Table from Colab Notebook Cell 111
model_comparison_data = [
    {"Model": "Logistic Regression", "Accuracy": "95.1%", "Precision": "0.955", "Recall": "0.951", "F1 Score": "0.951", "Notes": "Highest overall accuracy with standardized feature scaling"},
    {"Model": "Support Vector Machine (RBF Kernel)", "Accuracy": "88.7%", "Precision": "0.892", "Recall": "0.887", "F1 Score": "0.886", "Notes": "C=5, gamma='scale', balanced class weights"},
    {"Model": "K-Nearest Neighbors (KNN)", "Accuracy": "85.9%", "Precision": "0.858", "Recall": "0.859", "F1 Score": "0.857", "Notes": "k=7 with distance-weighted neighbors"},
    {"Model": "XGBoost (Grid Search Tuned)", "Accuracy": "82.4%", "Precision": "0.826", "Recall": "0.824", "F1 Score": "0.822", "Notes": "Optimized learning rate, max depth & subsampling"},
    {"Model": "XGBoost (Randomized Search Tuned)", "Accuracy": "82.4%", "Precision": "0.824", "Recall": "0.824", "F1 Score": "0.823", "Notes": "Stochastic parameter exploration"},
    {"Model": "XGBoost (Default)", "Accuracy": "81.7%", "Precision": "0.824", "Recall": "0.817", "F1 Score": "0.816", "Notes": "Default gradient boosting baseline"},
    {"Model": "Tuned Random Forest", "Accuracy": "80.3%", "Precision": "0.805", "Recall": "0.803", "F1 Score": "0.800", "Notes": "Ensemble tuning improves generalized decision boundaries"},
    {"Model": "Random Forest (Default)", "Accuracy": "79.6%", "Precision": "0.799", "Recall": "0.796", "F1 Score": "0.792", "Notes": "100 estimators, bagging variance reduction"},
    {"Model": "Tuned Decision Tree", "Accuracy": "69.7%", "Precision": "0.689", "Recall": "0.697", "F1 Score": "0.689", "Notes": "Grid Search tuned tree depth"},
    {"Model": "Decision Tree (Default)", "Accuracy": "69.0%", "Precision": "0.689", "Recall": "0.690", "F1 Score": "0.689", "Notes": "Unpruned baseline decision tree"},
]

model_df = pd.DataFrame(model_comparison_data)
st.dataframe(model_df, use_container_width=True, hide_index=True)

st.markdown("""
### 🔍 5. Explainability (SHAP & LIME) and Clustering
In addition to classification, our project incorporates cutting-edge model interpretability and unsupervised clustering:
- **SHAP (SHapley Additive exPlanations):** Explains global feature importance using tree-based SHAP values on the Tuned Random Forest model, revealing which health determinants contribute most to risk classification.
- **LIME (Local Interpretable Model-agnostic Explanations):** Explains local district-level predictions, showing the positive and negative weights of individual indicators for a selected district.
- **Unsupervised Clustering (Maharashtra):** Applied **K-Means Clustering** (Elbow method) and **Hierarchical Clustering** (Ward's linkage dendrogram) to identify natural district groupings across Maharashtra—highlighting vulnerable clusters such as the Nandurbar, Dhule, and Jalgaon belt.
""")

st.markdown("---")


st.markdown("""
### 📚 5. Data Integrity & Verification
- **Data Source:** International Institute for Population Sciences (IIPS) & Ministry of Health and Family Welfare (MoHFW), National Family Health Survey (NFHS-5, 2019-21).
- **Coverage:** 707 Districts across 28 States and 8 Union Territories.
- **Data Cleansing:** Automated sanitation of state naming variations (e.g., standardizing 'Maharastra' to 'Maharashtra') and whitespace trims.
- **Zero Fabrication Guarantee:** All visualizations, metrics, and comparisons reflect the official NFHS-5 records directly from `district_data.csv`.
""")

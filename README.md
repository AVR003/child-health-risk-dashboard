# 👶 AI-Based Risk Mapping and Interactive Dashboard for Child Health Outcomes

A production-ready Streamlit web application developed as a final-year project for public health vulnerability assessment, policy prioritization, and evidence-based decision-making using **NFHS-5 (National Family Health Survey 2019–21)** district-level data across all **707 districts** of India.

---

## 🌟 Key Features

1. **District Explorer (Main Core Flow):**
   - **Two-Tier Filter Dropdown:** Select any State/Union Territory, with instant cascading filtering of districts.
   - **State Name Sanitation:** Automatic cleaning and normalization of state names (including correcting *"Maharastra"* to *"Maharashtra"*).
   - **Color-Coded Risk Badge:** Highlighting district vulnerability tier:
     - 🟢 **Low Risk**
     - 🟡 **Medium Risk**
     - 🟠 **High Risk**
     - 🔴 **Very High Risk**
   - **Child Health Risk Score (CHRS):** Continuous composite score from 0 to 100 with state and national benchmark comparisons.
   - **Interactive Comparative Bar Chart:** Side-by-side Plotly bar chart comparing the district's 12 indicators against its state average, with toggles for Child Risk Indicators and Protective Health Indicators.
   - **Main Problem Areas Identification:** Mathematical identification of the district's top 3 vulnerabilities using national Z-score normalization against all 707 districts.
   - **Rule-Based Recommendation Engine:** Auto-generated evidence-based policy directives mapping specific deficits to targeted healthcare, nutrition, water, sanitation, and educational interventions.
   - **Interactive Policy Chatbot:** Conversational assistant answering questions like *"Why is this district high risk?"*, *"What should be improved first?"*, and *"How does it compare to the state average?"*. Operates 100% offline with zero dependencies on external LLMs, with optional routing to an LLM if an API key is provided in secrets.

2. **State Overview:**
   - Aggregated state-level summary metrics (Total districts, state mean CHRS, high-risk percentage).
   - **Risk Category Distribution Visualizations:** Interactive Donut Chart and Bar Chart breaking down vulnerability distribution.
   - **Top 5 Highest-Risk Districts:** Ranked bar chart and priority table highlighting critical districts within the chosen state.
   - **Complete District Ranking Table:** Searchable, sortable table of all districts with CSV export.

3. **About & Methodology:**
   - Mathematical formulation of the Composite Health Risk Score (CHRS) synthesized across 12 clinical and protective indicators.
   - Quartile stratification methodology (Low, Medium, High, Very High Risk).
   - Z-score normalization rationale for comparing heterogeneous percentage distributions.
   - **Model Comparison Table:** Evaluation benchmarks comparing Logistic Regression, Support Vector Classifier, Random Forest, LightGBM, XGBoost, and Multi-Layer Perceptron (MLP) architectures.

---

## 📁 Repository Structure

```
child_health_dashboard/
├── app.py                     # Primary Streamlit application entrypoint & navigation
├── utils.py                   # Data loading, Z-score computation, rule-based recommendation engine & chatbot logic
├── district_data.csv          # Official NFHS-5 dataset (707 districts, 16 columns)
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation & deployment guide
├── .streamlit/
│   └── config.toml            # UI theme configuration (modern healthcare aesthetic)
└── pages/
    ├── 1_District_Explorer.py # Core interactive district exploration flow & chatbot
    ├── 2_State_Overview.py    # State-level distributions & top 5 vulnerable districts
    └── 3_About_and_Methodology.py # Research methodology, math formulations & ML model table
```

---

## 🚀 Local Installation & Execution

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git (optional)

### 2. Setup Virtual Environment (Recommended)
```bash
# Clone or navigate to the project directory
cd child_health_dashboard

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deployment on Streamlit Community Cloud

Deploying this application to Streamlit Community Cloud is 100% free and takes under 3 minutes:

### Step 1: Push to GitHub
1. Create a new repository on [GitHub](https://github.com/) (e.g., `child-health-risk-dashboard`).
2. Push your project files to the repository:
```bash
git init
git add .
git commit -m "Initial commit: Child Health Risk Mapping Dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/child-health-risk-dashboard.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Community Cloud
1. Sign in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
2. Click **"New app"**.
3. Fill in the deployment details:
   - **Repository:** `<your-username>/child-health-risk-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy!"**.

### Step 3: (Optional) Configure Free Groq or Gemini API Key
The application runs **100% offline without any API key**. However, if you wish to route conversational chatbot queries through an LLM, both **Groq API** and **Google Gemini API** provide free keys:
- **Groq API (Free & Ultra-Fast):** Get a free key at [console.groq.com](https://console.groq.com/keys) (uses Llama 3.3 70B).
- **Google Gemini API (Free):** Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey) (uses Gemini 1.5 Flash).

You can either:
- **Option A (Instant in the Web UI):** Paste your key directly into the **"⚙️ Connect Groq API or Gemini API"** dropdown on the District Explorer page.
- **Option B (Permanent via Streamlit Secrets):** In your Streamlit Cloud dashboard, click **Settings (⚙️) -> Secrets** and add:
```toml
GROQ_API_KEY = "gsk_your_groq_api_key_here"
# OR:
GEMINI_API_KEY = "AIza_your_gemini_api_key_here"
```
The chatbot automatically detects the key and enhances responses. If omitted, it seamlessly falls back to the deterministic offline rule-based engine.


---

## 🚀 Deployment on Render (Render.com)

You can also deploy this application as a free **Web Service** on [Render](https://render.com/).

### Method A: 1-Click Blueprint (Recommended)
Because the repository includes [`render.yaml`](file:///C:/Users/aakas/.gemini/antigravity/scratch/child_health_dashboard/render.yaml), Render can automatically configure the service:
1. Push your repository to GitHub.
2. Log in to [dashboard.render.com](https://dashboard.render.com/).
3. Click **"New +" -> "Blueprint"**.
4. Select your GitHub repository and click **"Apply"**.
5. Render will automatically configure the build command, start command, and port binding!

### Method B: Manual Web Service Setup
1. On your Render dashboard, click **"New +" -> "Web Service"**.
2. Connect your GitHub repository.
3. Configure the settings:
   - **Name:** `child-health-risk-dashboard`
   - **Language:** `Python 3`
   - **Branch:** `main`
   - **Region:** Any (e.g., Singapore or Oregon)
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false
     ```
   - **Instance Type:** `Free`
4. **Environment Variables:**
   Click **"Advanced" -> "Add Environment Variable"**:
   - `PYTHON_VERSION` = `3.11.9`
   - *(Optional)* `GEMINI_API_KEY` = your Gemini API key (e.g. `AQ...` or `AIza...`)
   - *(Optional)* `GROQ_API_KEY` = your Groq API key (e.g. `gsk_...`)
5. Click **"Create Web Service"**.
6. Render will build and deploy the app. Once ready, you'll receive a live public URL (e.g. `https://child-health-risk-dashboard.onrender.com`).

---


## 📊 Dataset & Indicators Summary

| Indicator Name | Category | Direction | Policy Action Target |
| :--- | :--- | :--- | :--- |
| **Stunting (%)** | Clinical Risk | Lower is Better | Supplementary nutrition & growth monitoring |
| **Wasting (%)** | Clinical Risk | Lower is Better | Community nutrition rehabilitation centres |
| **Underweight (%)** | Clinical Risk | Lower is Better | Growth monitoring & nutrition outreach |
| **Child Anaemia (%)** | Clinical Risk | Lower is Better | Iron-folic acid supplementation & deworming |
| **Children Fully Immunized (%)** | Protective Care | Higher is Better | Mobile immunization camps & dropout tracking |
| **Early Initiation of Breastfeeding (%)** | Protective Care | Higher is Better | Frontline worker counselling within 1st hour |
| **Exclusive Breastfeeding (%)** | Protective Care | Higher is Better | Postnatal home visits & ASHA guidance |
| **Institutional Delivery (%)** | Protective Care | Higher is Better | Birthing infrastructure & JSY incentives |
| **Mothers with 4+ ANC Visits (%)** | Protective Care | Higher is Better | Antenatal checkup camps & tracking |
| **Women's Education 10+ Years Schooling (%)** | Social Determinant | Higher is Better | Retention schemes & health literacy |
| **Improved Sanitation Facility (%)** | Environmental | Higher is Better | Toilet infrastructure & hygiene drives |
| **Improved Drinking Water Source (%)** | Environmental | Higher is Better | Safe piped water supply & treatment |

---

## 📜 License
Developed for academic, research, and non-commercial public health planning purposes under the MIT License.

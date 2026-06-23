import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px

# ----------------------------------------------------------------------------
# PAGE CONFIG + GOVERNMENT-SITE STYLE
# ----------------------------------------------------------------------------
st.set_page_config(page_title="H-1B Wage Tier Explorer for Data Roles", layout="wide", page_icon="📋")

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, p, span, label {
        font-family: 'Public Sans', -apple-system, sans-serif !important;
    }

    /* Force light backgrounds everywhere, including the app shell */
    .stApp {
        background-color: #FFFFFF !important;
    }
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
    }
    [data-testid="stMainBlockContainer"] {
        background-color: #FFFFFF !important;
    }

    /* Kill border radius everywhere -- sharp, official, not "app-like" */
    div, button, textarea, .stSelectbox div, .stNumberInput input, .stTextInput input {
        border-radius: 0px !important;
    }

    /* Top banner strip, like a .gov site */
    .gov-banner {
        background-color: #0B1F3A;
        color: #FFFFFF;
        padding: 8px 0px;
        font-size: 13px;
        font-weight: 500;
        text-align: center;
        letter-spacing: 0.3px;
        margin: -1rem -1rem 24px -1rem;
    }

    .main-header {
        border-bottom: 3px solid #0B1F3A;
        padding-bottom: 16px;
        margin-bottom: 24px;
    }

    .main-header h1 {
        color: #0B1F3A !important;
        font-weight: 700;
        font-size: 30px;
        margin-bottom: 6px;
        letter-spacing: -0.3px;
    }

    .main-header p {
        color: #3D4750 !important;
        font-size: 14px;
        margin: 0;
    }

    /* Metric cards -- flat, bordered, no shadow */
    [data-testid="stMetric"] {
        background-color: #F4F5F7 !important;
        border: 1px solid #D5D9DD;
        padding: 14px 18px;
    }
    [data-testid="stMetricLabel"] {
        color: #5B6770 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        color: #0B1F3A !important;
        font-weight: 700 !important;
    }

    /* Tabs -- plain underline, not pill-shaped */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #D5D9DD;
        background-color: #FFFFFF;
    }
    .stTabs [data-baseweb="tab"] {
        color: #5B6770 !important;
        font-weight: 600;
        font-size: 14px;
        padding-bottom: 10px;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"] p {
        color: inherit !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0B1F3A !important;
        border-bottom: 3px solid #0B1F3A !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #FFFFFF;
    }

    /* Inputs -- light, bordered, readable text (fixes dark dropdown bug) */
    .stTextInput input, .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #0B1F3A !important;
        caret-color: #0B1F3A !important;
        border: 1px solid #A6ADB4 !important;
    }
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #0B1F3A !important;
        border: 1px solid #A6ADB4 !important;
    }
    [data-baseweb="select"] span {
        color: #0B1F3A !important;
    }
    /* Make sure the dropdown arrow icon stays visible (navy, not white-on-white) */
    [data-baseweb="select"] svg {
        fill: #0B1F3A !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    label, .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #0B1F3A !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    /* Dropdown menu (the popover list of options) */
    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #0B1F3A !important;
    }
    li[role="option"]:hover {
        background-color: #F4F5F7 !important;
    }

    /* Buttons -- flat federal navy, no gradient */
    .stButton button {
        background-color: #0B1F3A !important;
        color: #FFFFFF !important;
        border: none;
        font-weight: 600;
        padding: 8px 24px;
    }
    .stButton button:hover {
        background-color: #16335C !important;
        color: #FFFFFF !important;
    }
    .stButton button p {
        color: #FFFFFF !important;
    }

    .source-note {
        color: #5B6770;
        font-size: 12px;
        border-top: 1px solid #D5D9DD;
        margin-top: 40px;
        padding-top: 12px;
    }

    .level-box {
        border: 1px solid #D5D9DD;
        border-left: 6px solid #0B1F3A;
        background-color: #F4F5F7;
        padding: 16px 20px;
        margin-top: 12px;
        color: #0B1F3A;
    }

    /* General body text + markdown inside tabs */
    .stMarkdown p, .stMarkdown li {
        color: #1F2937 !important;
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #5B6770 !important;
    }

    /* Hide Streamlit's default toolbar (Deploy button, menu dots) --
       it has theme-rendering quirks we don't control, and we don't need it */
    [data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
    }
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    '<div class="gov-banner">SOURCE: U.S. DEPARTMENT OF LABOR — OFFICE OF FOREIGN LABOR CERTIFICATION (OFLC) — LCA DISCLOSURE DATA, FY2025</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="main-header">
        <h1>H-1B Wage Tier Explorer for Data Roles</h1>
        <p>Covers Data Scientists, BI Analysts, Database Administrators/Architects, Statisticians, and Operations Research Analysts only — not all H-1B occupations. Built on FY2025 Certified and Certified-Withdrawn LCA filings.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# DATA + MODEL LOADING
# ----------------------------------------------------------------------------
NAICS_LABELS = {
    "11": "Agriculture, Forestry, Fishing",
    "21": "Mining, Oil & Gas",
    "22": "Utilities",
    "23": "Construction",
    "31": "Manufacturing",
    "32": "Manufacturing",
    "33": "Manufacturing",
    "42": "Wholesale Trade",
    "44": "Retail Trade",
    "45": "Retail Trade",
    "48": "Transportation & Warehousing",
    "49": "Transportation & Warehousing",
    "51": "Information & Media",
    "52": "Finance & Insurance",
    "53": "Real Estate",
    "54": "Professional, Scientific & Technical Services",
    "55": "Management of Companies",
    "56": "Administrative & Support Services",
    "61": "Educational Services",
    "62": "Health Care & Social Assistance",
    "71": "Arts, Entertainment & Recreation",
    "72": "Accommodation & Food Services",
    "81": "Other Services",
    "92": "Public Administration",
    "Unknown": "Unknown / Unclassified",
}

LOTTERY_ENTRIES = {"I": 1, "II": 2, "III": 3, "IV": 4}
LEVEL_DESCRIPTIONS = {
    "I": "Entry-level — basic understanding of duties, close supervision",
    "II": "Qualified — moderate experience, some independent judgment",
    "III": "Experienced — significant independence and complexity",
    "IV": "Fully competent — expert-level, often supervisory",
}


@st.cache_data
def load_data():
    df = pd.read_parquet("data/processed/lca_fy2025_cleaned.parquet")
    df["NAICS_SECTOR"] = df["NAICS_CODE"].astype(str).str[:2]
    return df


@st.cache_resource
def load_model():
    model = joblib.load("data/processed/wage_level_model.pkl")
    feature_cols = joblib.load("data/processed/model_features.pkl")
    label_encoder = joblib.load("data/processed/label_encoder.pkl")
    rare_states = joblib.load("data/processed/rare_states.pkl")
    return model, feature_cols, label_encoder, rare_states


df = load_data()
model, feature_cols, label_encoder, rare_states = load_model()

# ----------------------------------------------------------------------------
# TOP-LINE METRICS
# ----------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Filings", f"{len(df):,}")
m2.metric("Unique Employers", f"{df['EMPLOYER_NAME'].nunique():,}")
m3.metric("Median Annual Wage", f"${df['ANNUAL_WAGE'].median():,.0f}")
m4.metric("Reporting Period", "Oct 2024 – Sep 2025")

st.write("")

# ----------------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["SEARCH BY COMPANY", "WAGE LEVEL PREDICTOR", "ABOUT THIS DATA"])

# --- TAB 1: COMPANY SEARCH ---------------------------------------------------
with tab1:
    st.write("")
    company_search = st.text_input(
        "Company name", placeholder="e.g. Amazon, Google, Capital One", label_visibility="visible"
    )

    if company_search:
        matches = df[df["EMPLOYER_NAME"].str.contains(company_search, case=False, na=False)]

        if len(matches) == 0:
            st.warning("No filings found. Try a shorter or differently spelled search term.")
        else:
            st.write(f"**{len(matches):,} filings** matched · {matches['EMPLOYER_NAME'].nunique()} legal entity name(s)")

            c1, c2, c3 = st.columns(3)
            c1.metric("Median Annual Wage", f"${matches['ANNUAL_WAGE'].median():,.0f}")
            mode_role = matches["SOC_TITLE"].mode()
            c2.metric("Most Common Role", mode_role[0] if not mode_role.empty else "N/A")
            entry_friendly = matches["PW_WAGE_LEVEL"].isin(["I", "II"]).mean()
            c3.metric("Share at Entry/Mid Level (I–II)", f"{entry_friendly:.0%}")

            st.write("**Wage level distribution**")
            level_counts = matches["PW_WAGE_LEVEL"].value_counts().reindex(["I", "II", "III", "IV"]).fillna(0)
            fig = go.Figure(
                go.Bar(
                    x=level_counts.index,
                    y=level_counts.values,
                    marker_color="#0B1F3A",
                    text=level_counts.values.astype(int),
                    textposition="outside",
                )
            )
            fig.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis_title="OES Wage Level",
                yaxis_title="Number of Filings",
                font=dict(family="Public Sans, sans-serif", color="#0B1F3A"),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.write("**Filing detail**")
            display_cols = ["JOB_TITLE", "SOC_TITLE", "WORKSITE_CITY", "WORKSITE_STATE", "ANNUAL_WAGE", "PW_WAGE_LEVEL", "FISCAL_QUARTER"]
            st.dataframe(
                matches[display_cols].sort_values("ANNUAL_WAGE", ascending=False).head(50),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Enter a company name above to view its sponsorship history for data roles.")

# --- TAB 2: PREDICTOR ---------------------------------------------------------
with tab2:
    st.write("")
    st.write(
        "Estimate the OES wage level DOL would likely assign to a hypothetical job offer, "
        "based on patterns in FY2025 certified filings. Under the wage-weighted H-1B lottery "
        "(effective Feb 27, 2026), this level determines lottery entry weight."
    )
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        input_role = st.selectbox("Job role (SOC classification)", sorted(df["SOC_TITLE"].unique()))
        input_state = st.selectbox("Work state", sorted(df["WORKSITE_STATE"].unique()))
    with col2:
        input_wage = st.number_input(
            "Offered annual wage ($)", min_value=30000, max_value=600000, value=120000, step=5000
        )
        naics_options = sorted(df["NAICS_SECTOR"].unique())
        input_naics = st.selectbox(
            "Industry sector",
            naics_options,
            format_func=lambda code: f"{code} — {NAICS_LABELS.get(code, 'Unclassified')}",
        )

    predict_clicked = st.button("Predict wage level")

    if predict_clicked:
        state_for_model = "OTHER" if input_state in rare_states else input_state

        input_dict = {col: 0 for col in feature_cols}
        input_dict["PREVAILING_WAGE"] = input_wage
        input_dict["EMPLOYER_FILING_COUNT"] = df["EMPLOYER_NAME"].value_counts().median()

        soc_col = f"SOC_TITLE_{input_role}"
        state_col = f"WORKSITE_STATE_{state_for_model}"
        naics_col = f"NAICS_SECTOR_{input_naics}"

        if soc_col in input_dict:
            input_dict[soc_col] = 1
        if state_col in input_dict:
            input_dict[state_col] = 1
        if naics_col in input_dict:
            input_dict[naics_col] = 1
        input_dict["FULL_TIME_POSITION_Y"] = 1

        input_df = pd.DataFrame([input_dict])[feature_cols]

        prediction = model.predict(input_df)[0]
        predicted_level = label_encoder.inverse_transform([prediction])[0]
        probabilities = model.predict_proba(input_df)[0]
        prob_series = pd.Series(probabilities, index=label_encoder.inverse_transform(range(len(probabilities))))
        prob_series = prob_series.reindex(["I", "II", "III", "IV"])

        st.markdown(
            f"""
            <div class="level-box">
                <div style="font-size:13px; color:#5B6770; text-transform:uppercase; letter-spacing:0.5px;">Predicted OES Wage Level</div>
                <div style="font-size:32px; font-weight:700; color:#0B1F3A; margin:4px 0;">Level {predicted_level}</div>
                <div style="font-size:14px; color:#0B1F3A;">{LEVEL_DESCRIPTIONS[predicted_level]}</div>
                <div style="font-size:14px; color:#5B6770; margin-top:8px;">Lottery weighting: <b>{LOTTERY_ENTRIES[predicted_level]}x</b> entries in the selection pool (effective Feb 27, 2026 rule)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.write("**Model confidence by level**")
        fig2 = go.Figure(
            go.Bar(
                x=prob_series.index,
                y=prob_series.values,
                marker_color=["#A6192E" if lvl != predicted_level else "#0B1F3A" for lvl in prob_series.index],
                text=[f"{v:.0%}" for v in prob_series.values],
                textposition="outside",
            )
        )
        fig2.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis_title="Predicted probability",
            xaxis_title="OES Wage Level",
            font=dict(family="Public Sans, sans-serif", color="#0B1F3A"),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.caption(
            "Model: XGBoost classifier, cross-validated accuracy ≈94%. Trained on offered wage, role, "
            "state, industry sector, and employer filing volume from FY2025 certified LCA filings."
        )

# --- TAB 3: ABOUT --------------------------------------------------------------
with tab3:
    st.write("")
    st.markdown(
        """
        **What this is.** This tool analyzes public Labor Condition Application (LCA) disclosure data
        published by the U.S. Department of Labor's Office of Foreign Labor Certification (OFLC), filtered
        to data-related occupations (Data Scientists, Business Intelligence Analysts, Database Administrators,
        Database Architects, Statisticians, Operations Research Analysts, and Computer & Information Research
        Scientists).

        **What an LCA is.** Before sponsoring an H-1B worker, employers must file an LCA declaring the job
        title, wage, and location they're offering. DOL reviews and certifies these filings. This dataset
        reflects *certified intent to sponsor*, not actual H-1B petition outcomes or lottery results.

        **About wage levels.** Every filing is assigned an OES wage level (I–IV) reflecting the seniority DOL
        associates with the role's required wage, relative to other workers in that occupation and location.
        These levels have existed since the late 1990s. Starting with the 2026 H-1B cap season (effective
        February 27, 2026), DHS will use these levels to weight the H-1B lottery — Level IV filings receive
        4 entries, Level III receive 3, Level II receive 2, and Level I receive 1.

        **Important limitation.** This FY2025 data was filed *before* the wage-weighted lottery rule existed.
        It shows historical filing behavior, not actual lottery outcomes. The wage-level predictor estimates
        what tier a hypothetical offer would likely fall into, based on patterns in this historical data — it
        does not predict selection in the lottery itself.

        **Data scope.** Includes only "Certified" and "Certified-Withdrawn" filings (both indicate DOL approval).
        "Withdrawn" and "Denied" filings are excluded. Company names have been normalized for formatting and
        select well-known subsidiaries (Amazon, Capital One) have been grouped under their parent company.

        **Source:** [U.S. Department of Labor, OFLC Performance Data](https://www.dol.gov/agencies/eta/foreign-labor/performance)
        """
    )

st.markdown(
    '<div class="source-note">Data: U.S. Department of Labor, Office of Foreign Labor Certification — '
    'LCA Disclosure Data FY2025 (Q1–Q4). This is an independent analysis tool, not affiliated with or '
    'endorsed by the Department of Labor.</div>',
    unsafe_allow_html=True,
)

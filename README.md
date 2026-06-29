# H-1B Wage Tier Explorer

**Live app:** [h1b-wage-tier-explorer.streamlit.app](https://h1b-wage-tier-explorer.streamlit.app)

An end-to-end data science project analyzing U.S. Department of Labor H-1B sponsorship data for data-related roles (Data Scientist, Business Intelligence Analyst, Database Administrator/Architect, Statistician, Operations Research Analyst). The tool lets users search company sponsorship history and predict the OES wage tier of a hypothetical job offer — directly relevant to the new wage-weighted H-1B lottery taking effect for the 2026 cap season.

---

## Why this project

As an international student, the hardest part of the U.S. job search isn't finding open roles — it's knowing which companies actually sponsor H-1B visas, and what that means under the rules that now govern the lottery. Starting with the 2026 cap season (effective February 27, 2026), the H-1B lottery moves from a flat random draw to a **wage-weighted system**: Level IV filings receive 4 entries in the selection pool, Level III receive 3, Level II receive 2, and Level I receive 1. This project uses historical DOL filing data to show which companies have tended to file at which wage tiers — a forward-looking signal for where that weighting will matter most.

## What's in this repo

```
├── app.py                          # Streamlit dashboard (deployed app)
├── requirements.txt                # Dependencies for deployment
├── .streamlit/config.toml          # Theme configuration
├── data/
│   └── processed/                  # Cleaned data, trained model, saved charts
├── notebooks/
│   └── 01_explore_raw_data.ipynb   # Full data cleaning, EDA, and modeling process
└── src/                            # (reserved for future reusable modules)
```

Raw source Excel files are not included in this repo (large, easily re-downloaded from DOL directly — see Data Source below).

## Data

- **Source:** [U.S. DOL, Office of Foreign Labor Certification — LCA Disclosure Data](https://www.dol.gov/agencies/eta/foreign-labor/performance), FY2025 (Q1–Q4)
- **Scope:** Filtered to 7 data-related SOC occupational classifications. Excludes general "Software Developer" and "Computer Systems Analyst" categories — these SOC codes mix general software engineering with data engineering roles with no reliable way to separate them, so including them risked false precision.
- **Filings included:** "Certified" and "Certified-Withdrawn" only (both indicate DOL approval). "Withdrawn" and "Denied" filings excluded.
- **Final dataset:** 59,101 filings across 13,345 unique employers (after entity normalization).

## What an LCA actually is — and isn't

A Labor Condition Application (LCA) is filed by an employer *before* an H-1B petition, declaring intended job title, wage, and location. DOL certifying an LCA means the employer's wage/job terms were approved — **it does not mean a worker was selected in the H-1B lottery or even filed a petition.** This dataset reflects certified sponsorship intent, not lottery outcomes. The FY2025 data here also predates the wage-weighted lottery rule (effective Feb 2026), so it shows historical filing behavior under the old system — used here as a forward-looking proxy, not a backward-looking outcome measure.

## Data cleaning highlights

Real government data has real problems. A few found and fixed during this project:

- **Mislabeled wage units:** ~90 filings reported an annual salary but selected the wrong pay-period unit (e.g., "$160,000" tagged as hourly, implying a $332M/year salary). Fixed with a general plausibility rule rather than per-unit patches.
- **Entity duplication:** The same employer appeared under inconsistent casing and as separate legal subsidiaries (e.g., three distinct Amazon entities). Normalized formatting and manually grouped major known subsidiaries.
- **Malformed field values:** 22 rows had ZIP codes stored in a city-name field. Identified and flagged rather than guessed at.
- **Missing wage levels:** ~6% of filings lacked an OES wage level (likely due to non-OES prevailing wage sources). Flagged explicitly rather than dropped or imputed, and excluded only from model training.

Full process documented in `notebooks/01_explore_raw_data.ipynb`.

## Key findings

- **Amazon is the dominant sponsor by volume** (4,700+ filings) but skews toward lower wage tiers (only 3% at Level IV) — the highest-volume sponsor is not the highest-tier sponsor.
- **Apple is the opposite extreme:** 73% of its data-role filings are Level IV, with almost none at Level I.
- Filing volume spikes sharply in Q3 of the fiscal year (Apr–Jun), consistent with the post-lottery H-1B cap filing season.
- Wage tier is overwhelmingly driven by **offered wage relative to work-state cost of living** — not by company size or industry alone.

## Predictive model

A classifier estimates OES wage level (I–IV) from a hypothetical job offer's wage, role, work state, and industry.

| | |
|---|---|
| **Model** | XGBoost (gradient-boosted trees) |
| **Features** | Prevailing wage, SOC role, work state, NAICS industry sector, employer filing volume |
| **Accuracy** | 94.37% (5-fold cross-validated) |
| **Compared against** | Random Forest (73%), LightGBM (92%), sklearn Gradient Boosting (90%) |

**A deliberate finding, not just a result:** an earlier version of this model, using only company/role/location *without* the offered wage, achieved only 43% accuracy — barely above a 42% "always guess the most common class" baseline. This confirmed that wage tier is driven primarily by the wage itself, not by employer identity — a real, if less flattering, result that's documented rather than hidden.

**A debugging story worth noting:** initial cross-validation showed one fold scoring 70% against four others near 94%. Rather than accept either number, the discrepancy was traced systematically — ruling out overfitting and feature leakage before finding the actual cause: the dataset was concatenated in fiscal-quarter order, and an *unshuffled* k-fold split isolated a non-representative slice of data into one fold. Enabling shuffling resolved it, producing a stable 94.37% average with 0.27% standard deviation across folds.

## Tech stack

Python · pandas · scikit-learn · XGBoost · Plotly · Streamlit · Parquet/PyArrow · Jupyter · Git/GitHub · Streamlit Community Cloud

## Running locally

```bash
git clone https://github.com/saisuhasearla/h1b-wage-tier-explorer.git
cd h1b-wage-tier-explorer
pip install -r requirements.txt
streamlit run app.py
```

## Limitations

- Subsidiary/parent-company grouping was done manually for major known cases (Amazon, Capital One) — not a complete, systematic entity-resolution pass.
- "Data roles" are defined by SOC classification, which does not capture data engineers filed under general "Software Developer" codes.
- The wage-tier model predicts tier *given* an offered wage — it does not predict whether an applicant would be selected in the lottery itself, nor wage tier from company/role alone (see Key Findings).
- Built on a single fiscal year (FY2025); year-over-year trends are not yet covered.

## Author

Sai Suhas Earla — [LinkedIn](https://linkedin.com/in/suhas-earla) · [GitHub](https://github.com/saisuhasearla)

This is an independent analysis tool and is not affiliated with or endorsed by the U.S. Department of Labor.

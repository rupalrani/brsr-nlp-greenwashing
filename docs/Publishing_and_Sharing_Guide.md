# Where and How to Share This Project
## Publishing & Distribution Guide for the BRSR Greenwashing Screener

---

## 1. GitHub — Primary Repository (Do This First)

**Repo name suggestion:** `brsr-nlp-greenwashing`  
**Visibility:** Public (the entire value is discoverability)

### Recommended folder structure to push
```
brsr-nlp-greenwashing/
├── README.md                         ← Copy from docs/GitHub_README.md
├── LICENSE                           ← MIT
├── requirements.txt
├── .gitignore
├── src/
│   ├── nlp_pipeline.py               ← The full pipeline
│   └── brsr_sql_schema.sql           ← SQL schema + 9 queries
├── notebooks/
│   └── FinBERT_Colab.ipynb           ← Click-to-open Colab badge in README
├── data/
│   └── raw/                          ← All 15 .txt corpus files
├── outputs/
│   ├── nlp_results.csv
│   ├── lda_topics.csv
│   ├── doc_topic_matrix.csv
│   ├── tfidf_by_sector.csv
│   ├── statistical_tests.csv
│   ├── BRSR_NLP_Analysis_Workbook.xlsx
│   └── fig1_*.png … fig7_*.png
└── reports/
    └── BRSR_Research_Report.md
```

### GitHub setup commands
```bash
git init
git add .
git commit -m "Initial commit: BRSR NLP greenwashing screener (15 reports, 5 sectors)"
git remote add origin https://github.com/rupalrani/brsr-nlp-greenwashing.git
git push -u origin main
```

### GitHub Actions tip (optional, impressive)
Add a `.github/workflows/run_pipeline.yml` that automatically re-runs `nlp_pipeline.py` on push, confirming reproducibility to any visitor.

---

## 2. LinkedIn (Post Within 48 Hours of GitHub Push)

Use the two post options in `LinkedIn_Post.md`. Key rules:
- Post the GitHub link in the **first comment**, not the body (LinkedIn algo deprioritises outbound links in body text)
- Use **fig2_grs_scores.png** or **fig4_sr_vs_grs.png** as the image — both are visually clear and self-explanatory
- Tag 2–3 people (professors, mentors, colleagues who can authentically engage early)
- Post on **Tuesday or Wednesday, 8:30–10am IST**
- Reply to every comment within the first 2 hours — this signals the algo to distribute further

---

## 3. SSRN — Student / Early Research Track

**URL:** https://papers.ssrn.com/sol3/SSRN_Author_Submit.asp  
**Category:** Finance > Corporate Finance > ESG / Sustainability  
**Co-category:** Computer Science > Machine Learning / NLP

SSRN accepts working papers and does not require journal acceptance. A well-formatted working paper on BRSR + NLP in India is genuinely rare — it is likely to get downloads from ESG researchers and Indian finance academics.

**What to submit:** `BRSR_Research_Report.docx` converted to PDF.  
**Title:** *Greenwashing Risk Detection in Indian BRSR Disclosures: A Multi-Sector NLP Analysis (FY2022–2025)*  
**Abstract:** Use the Abstract from the research report verbatim.  
**Keywords:** greenwashing, BRSR, ESG disclosure, NLP, India, SEBI, specificity ratio, FinBERT, LDA, Loughran-McDonald

**Honest expectation:** SSRN submissions go live within 1–3 business days and generate a citable link (e.g., https://ssrn.com/abstract=XXXXXXX). Add this DOI link to your GitHub README and LinkedIn post.

---

## 4. Student Journals and Competitions

| Venue | Suitability | Notes |
|---|---|---|
| **ICAI Student Journal** (ICSI/ICAI) | High | BRSR + Indian regulatory focus is ideal fit |
| **IIM Ahmedabad / Calcutta Student Research** | Medium-High | MBA/finance research festivals welcome working papers |
| **Emerge Research (IIT Bombay)** | Medium | Interdisciplinary; NLP + finance fits |
| **Analytics Vidhya Blog** | High (reach) | High discoverability; technical audience |
| **Towards Data Science (Medium)** | High (reach) | Write a 1,200-word accessible version of the findings |
| **SEBI NISM Research Paper** | Medium | NISM (National Institute of Securities Markets) publishes student and practitioner papers on capital markets |

---

## 5. Kaggle Dataset / Notebook

Publish the `nlp_results.csv` + the 15 corpus `.txt` files as a **Kaggle Dataset** titled *"Indian BRSR ESG Disclosures — NLP Analysis Dataset (2022-25)"*. Then publish `nlp_pipeline.py` as a **Kaggle Notebook**.

Benefits:
- Kaggle has a large data science audience that specifically looks for financial NLP datasets
- The BRSR corpus is genuinely novel — no equivalent dataset currently exists on Kaggle
- Upvotes and forks add to your public portfolio

---

## 6. Hugging Face Hub (Dataset Card)

Once the corpus reaches 30+ reports (after extending to top-100 filers), publish as a Hugging Face Dataset:  
```
datasets-preview.huggingface.co/datasets/rupalrani/india-brsr-corpus
```

This is a stretch goal, but it is the step that transitions the project from a portfolio piece to infrastructure that other researchers cite.

---

## 7. Job Application Attachments

When applying for Data Analyst or ESG Analytics roles, attach:

| Document | When to attach |
|---|---|
| `GitHub_README.md` (as PDF) | Every DA / analytics application |
| `BRSR_Research_Report.docx` | ESG, sustainability, finance, investment roles |
| `BRSR_NLP_Analysis_Workbook.xlsx` | Roles that ask for Excel proficiency examples |
| `nlp_pipeline.py` | Roles that ask for Python code samples |
| `brsr_sql_schema.sql` | Roles that test SQL skills |

**Resume bullet point:**
> Built an end-to-end NLP pipeline to quantify greenwashing risk in 15 Indian BRSR filings across 5 sectors; derived a Composite Greenwashing Risk Score from Specificity Ratio, LM Sentiment, and LDA topics; 40% of reports scored HIGH risk; r = −0.725 (p = 0.002) between SR and GRS. Open-sourced on GitHub.

---

## 8. Conference Posters (Future)

Target FY2025-26 academic year:
- **India Finance Conference (IFC)** — annual, IIM-hosted, welcomes empirical finance + ESG
- **CAFRAL (RBI)** — Centre for Advanced Financial Research and Learning; ESG data focus
- **IIMB Finance Research Day** — student poster sessions
- **FICCI ESG Summit** — industry audience; applied findings more relevant than methodology

For a poster, the fig4_sr_vs_grs.png scatter and the sector boxplot (fig3) will form the visual centrepiece.

---

## 9. Timeline Recommendation

| Week | Action |
|---|---|
| **Week 1** | Push GitHub repo. Add Colab badge to README. |
| **Week 1** | Post on LinkedIn (Version A). Share in 2–3 WhatsApp groups of data/finance peers. |
| **Week 2** | Submit to SSRN. Add SSRN link to GitHub README and LinkedIn profile. |
| **Week 2** | Publish Kaggle dataset + notebook. |
| **Week 3** | Write a 1,200-word blog post for Analytics Vidhya or Towards Data Science. |
| **Month 2** | Extend corpus to top-30 filers (add ~15 more companies). Update all results. |
| **Month 3** | Submit to a student journal or NISM research paper competition. |


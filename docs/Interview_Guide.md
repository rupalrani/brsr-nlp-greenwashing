# Interview Preparation Guide
## BRSR Greenwashing Risk Screener — How to Present This Project

---

## The 60-Second Pitch (memorise this)

> "I built a greenwashing risk screener for Indian companies' mandatory ESG reports — the BRSR — using NLP. I fetched 15 real public filings across five sectors, computed a Specificity Ratio to measure how many sentences actually contain quantifiable claims versus just aspirational language, combined that with finance sentiment and boilerplate detection into a Composite Risk Score, ran LDA topic modelling, and built a FinBERT extension for sentence-level transformer scoring. The key finding was that 40% of reports scored HIGH risk, manufacturing sectors had near-zero specificity despite strong climate language, and Specificity Ratio alone had a Pearson r of −0.725 with the composite score. Everything is open source, reproducible, and I've honestly documented every limitation."

---

## Common Interview Questions & How to Answer Them

### "Walk me through this project."

**Structure:** Problem → Data → Method → Finding → Limitation → So what?

- **Problem:** SEBI mandates BRSR filings, but nobody systematically checks whether the language is credible or vague.
- **Data:** 15 public BRSR PDFs, five sectors, fetched directly from NSE/BSE and company IR pages.
- **Method:** Specificity Ratio, LM Sentiment, Action-Vague Verb Ratio, Boilerplate Density → combined into a GRS. LDA for topic structure, TF-IDF for sector vocabulary, FinBERT for sentence-level sentiment.
- **Finding:** No company scored LOW. 40% HIGH. Manufacturing gap: high climate ambition, near-zero specificity.
- **Limitation:** n=15, extract-based for 8 reports, GRS weights are theoretical not fitted.
- **So what:** An investor screening BRSR reports could use SR as a fast filter; a regulator could prioritise inspection of HIGH-scoring filers.

---

### "Why this topic?"

> "SEBI's BRSR mandate creates a unique, standardised, public corpus of ESG disclosures in India — something that didn't exist before 2022. Every analyst who covers Indian equities will increasingly deal with this data. I wanted to build a rigorous, reproducible tool for evaluating it, rather than reading reports manually. The greenwashing angle is timely: SEBI introduced BRSR Core with mandatory third-party assurance in FY2023-24, which suggests even the regulator recognises the disclosure-quality problem."

---

### "What is a Specificity Ratio and why does it matter?"

> "It's the fraction of sentences in a document that contain at least one quantified claim — a number paired with a meaningful unit like a percentage, a tonne, a year, or a crore. The intuition is simple: a sentence like 'Scope 1 emissions reduced 27% vs 2017 baseline, SBTi-validated' is fundamentally more verifiable than 'We strive to reduce our carbon footprint.' SR operationalises that difference at scale. It was inspired by Clarkson et al. (2008) who showed that companies with stronger environmental performance use more concrete, quantified language."

---

### "Why not just use FinBERT for everything?"

> "Two reasons. First, FinBERT was trained on financial market news — earnings announcements, analyst commentary — not sustainability reports. Its 'positive' label reflects market-positive language, not truthful claims. A statement like 'We achieved carbon neutrality in 2020' scores positive whether it's verified or not. Second, FinBERT requires downloading 440MB of model weights from Hugging Face, which wasn't available in my analysis environment. So I built the rule-based pipeline as the primary analysis and documented FinBERT as a fully working Colab extension. More importantly, for an entry-level analyst role, a transparent, explainable pipeline you can defend to a non-technical audience is often more valuable than a black-box transformer."

---

### "Your sample is only 15 companies. Isn't that too small to mean anything?"

> "Yes, and I say so explicitly — it's the first thing in my limitations section. The Kruskal-Wallis test returns p = 0.188, which is not significant at n=15 with 6 groups. I treat all sector-level differences as descriptive and directional, not causal. What the project demonstrates is the pipeline and methodology. The same code runs on the full top-100 or top-1,000 BRSR filer universe — anyone can extend it. I'd rather document that limitation clearly than overstep what the data supports."

---

### "How did you choose your GRS weights (40/25/20/15)?"

> "They're theoretically motivated, not data-fitted. SR gets 40% because Clarkson et al. (2008) and Bingler et al. (2022) both establish quantitative specificity as the primary signal of disclosure quality. AVVR gets 25% because the action-vs-aspiration distinction is the most intuitive conceptual dimension of greenwashing. BD at 20% captures copy-paste regulatory compliance versus original disclosure. LM Negative at 15% is a supporting signal. I'm transparent that these are my judgment calls — there's no labelled BRSR greenwashing dataset to fit weights against empirically. If one existed, I'd use logistic regression or a random forest to fit them."

---

### "What would you do next if you had more time?"

Strong answers (pick two):
1. **Scale to full corpus:** NSE has 1,000+ BRSR filers. Run the same pipeline, produce a sector-by-sector national benchmark.
2. **Cross-reference with CDP data:** Compare GRS scores against actual CDP-reported emission figures to test whether low-SR companies also have worse real-world performance — that's the true greenwashing test.
3. **Longitudinal analysis:** Companies have now filed 3 years of BRSRs. Is specificity improving over time? Are HIGH-GRS companies responding to BRSR Core assurance requirements?
4. **ClimateBERT instead of FinBERT:** Bingler et al.'s ClimateBERT was trained specifically on climate disclosures and would be a domain-stronger model than FinBERT.

---

### "What SQL skills does this project show?"

> "The SQL schema creates a normalised relational structure for the analysis: companies table, nlp_metrics table, LDA topic and doc-topic weight tables. The nine analysis queries demonstrate window functions (CTEs for sector averages), CASE statements for derived categories, GROUP BY aggregations, JOINs, and a sensitivity analysis query showing how much SR improvement each HIGH-risk company needs to move to MEDIUM. This mirrors how I'd structure an actual analytics data warehouse for ESG monitoring."

---

### "How did you ensure data quality / that the results are reproducible?"

> "Four things. First, every corpus file includes a source header with the URL, access date, and extraction method — the same transparency you'd expect in academic data documentation. Second, the pipeline is a single Python script with no hardcoded outputs — re-run it and you get the same numbers from the same inputs. Third, the SQL schema inserts the actual pipeline outputs, not manually typed numbers. Fourth, the Excel workbook has zero hardcoded analysis cells — all summary rows use formulas referencing the data. I also ran node --check on the Word document build script before submission."

---

## Honest Things to Know (don't oversell)

- **You cannot claim to have 'detected greenwashing'** — you measured textual credibility risk. Say that precisely.
- **The Infosys HIGH result is a pipeline gap, not a finding about Infosys** — say so if asked about the specific company.
- **FinBERT was not run on the full corpus** — it's a Colab notebook. Be honest about this.
- **The GRS weights are your judgment** — they're reasonable and literature-grounded, but they're not empirically validated.

These honest acknowledgements will make you look *more* credible, not less.

---

## Talking Points for Data Analyst Roles Specifically

- "This project exercises the complete analytics workflow: problem definition, data sourcing, cleaning, EDA, statistical testing, visualisation, and business interpretation."
- "I used Python for NLP, SQL for structured querying, Excel for stakeholder-ready reporting, and Seaborn/Matplotlib for publication-quality charts."
- "The research report is written for a general business audience, not just technical readers — which is what most analyst jobs require."
- "I actively looked for and documented weaknesses in my own analysis. That's an uncommon skill that matters in high-stakes business contexts."

---

## For ESG / Sustainability Analyst Roles

- Know the 9 NGRBC principles (ethical governance, sustainable products, employee well-being, stakeholder engagement, human rights, environmental, policy advocacy, inclusive growth, customer value)
- Know BRSR Core vs. non-core disclosure and why third-party assurance matters
- Know the difference between Scope 1, 2, and 3 emissions
- Know what SBTi validation means (Science Based Targets initiative — independent validation of corporate GHG targets)
- Know the gap between voluntary (GRI, TCFD) and mandatory (BRSR, CSRD) ESG reporting


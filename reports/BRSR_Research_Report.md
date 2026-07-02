# Greenwashing Risk Detection in Indian BRSR Disclosures: A Multi-Sector NLP Analysis (FY2022–25)

**Author:** [Rupal Rani]  
**Affiliation:** [Independent Researcher]  
**Date:** June 2026  
**Keywords:** greenwashing, BRSR, ESG disclosure, NLP, India, SEBI, specificity, FinBERT, LDA  
**Data & Code:** https://github.com/rupalrani/brsr-nlp-greenwashing  
**Status:** Working Paper / Portfolio Project

---

## Abstract

India's Securities and Exchange Board of India (SEBI) made the Business Responsibility and Sustainability Report (BRSR) mandatory for the top 1,000 listed companies from FY2022–23, generating a standardised, publicly accessible corpus of corporate ESG disclosures. This study applies a transparent, rule-based NLP pipeline to 15 BRSR filings across five sectors — Information Technology (IT), Banking, Cement, Heavy Industry, and Pharmaceuticals — to quantify the textual credibility of ESG claims. Using a novel Composite Greenwashing Risk Score (GRS) that integrates Specificity Ratio (SR), Loughran-McDonald (LM) finance sentiment, Action-Vague Verb Ratio (AVVR), and Boilerplate Density (BD), the analysis finds that **none of the 15 reports scored LOW risk**, with six companies (40%) scoring HIGH (GRS > 60). Manufacturing-intensive sectors — Cement and Heavy Industry — showed the highest mean GRS (66.95 and 72.50 respectively) and the lowest mean SR (0.029 and 0.000), suggesting that companies in carbon-intensive industries disclose ambition more readily than auditable outcomes. Specificity Ratio was the single strongest predictor of GRS (Pearson r = −0.725, p = 0.002). The study explicitly acknowledges corpus size limitations (n = 15), extract-based text rather than full-document analysis for eight reports, and the absence of live FinBERT scoring due to infrastructure constraints, with a full runnable extension notebook provided for Colab deployment.

---

## 1. Introduction

Corporate greenwashing — the practice of overstating environmental or social credentials without substantive evidence — has attracted increasing regulatory and academic attention worldwide (Lyon & Maxwell, 2011; Marquis & Toffel, 2012). In the Indian context, the SEBI BRSR framework, introduced through an amendment to the Listing Obligations and Disclosure Requirements (LODR) Regulations in 2021 and made mandatory for the top 1,000 listed companies from FY2022–23, creates a novel, standardised disclosure corpus that did not exist before (SEBI, 2021). Unlike voluntary sustainability reports, BRSR filings follow a structured nine-principle template aligned with the National Guidelines on Responsible Business Conduct (NGRBC), covering environmental, social, and governance dimensions under a single regulatory mandate.

Despite this standardisation, BRSR disclosures vary substantially in the depth and verifiability of their claims. Anecdotal review of filings reveals a spectrum ranging from reports with specific, quantified, time-bound commitments — audited by third-party assurance providers — to reports dominated by aspirational language, regulatory boilerplate, and cross-references to separate sustainability documents. Distinguishing between these extremes at scale requires computational methods rather than manual reading.

This study makes three contributions. First, it constructs the first publicly documented NLP pipeline specifically designed for Indian BRSR text, with all methods, lexicons, and code openly available. Second, it proposes and validates a five-component Composite Greenwashing Risk Score (GRS) calibrated on 15 real filings across five economically distinct sectors. Third, it honestly documents what the analysis can and cannot conclude given a corpus of this size, modelling the kind of methodological transparency that characterises credible research.

### 1.1 Research Questions

1. Do Indian BRSR filings differ significantly in the textual specificity of their ESG claims across sectors?
2. What linguistic features best discriminate between high- and low-specificity disclosures?
3. Does cross-listing on international exchanges (e.g., NYSE) correlate with higher disclosure specificity?
4. Which companies and sectors present the highest composite greenwashing risk signals based on text alone?

---

## 2. Literature Review

### 2.1 Greenwashing and ESG Disclosure Quality

Lyon and Maxwell (2011) define greenwashing as selective disclosure of positive environmental information to distract from negative performance. Marquis and Toffel (2012) demonstrate empirically that disclosure selectivity — reporting only favourable metrics while omitting unfavourable ones — is significantly more prevalent in firms facing weaker institutional scrutiny. Clarkson et al. (2008) establish a theoretical link between environmental performance and disclosure specificity, finding that firms with stronger actual performance use more concrete, quantified language, while weaker performers rely on process descriptions and aspirational statements.

### 2.2 Textual Analysis of Corporate Sustainability Disclosures

The application of NLP to sustainability disclosures has accelerated since Loughran and McDonald's (2011) seminal financial wordlist, which remains the most widely used lexicon for finance text sentiment. Bingler et al. (2022) applied ClimateBERT — a transformer model fine-tuned on climate disclosures — to the climate sections of financial reports from 14,584 firms, finding that net-zero commitments were primarily expressed in vague, unquantified language they label "cheap talk." Their finding that "positive climate claims are weakly correlated with actual emission reductions" provides direct motivation for the present study's SR-centric greenwashing definition.

Araci (2019) introduced FinBERT, a BERT-based model (Devlin et al., 2019) fine-tuned on approximately 10,000 financial news sentences, achieving state-of-the-art performance on financial sentiment classification. While FinBERT does not directly measure greenwashing, its positive-sentiment scores can serve as a proxy for the "spin" component of greenwashing when paired with low specificity scores.

Blei, Ng, and Jordan's (2003) Latent Dirichlet Allocation (LDA) provides the unsupervised topic modelling framework used here to identify dominant thematic structures across the corpus.

### 2.3 The Indian BRSR Framework

India's BRSR replaces the earlier Business Responsibility Report (BRR) and mandates nine principles under the NGRBC: ethical governance, sustainable products, employee well-being, stakeholder engagement, human rights, environmental stewardship, policy advocacy, inclusive growth, and customer value. The framework requires both quantitative KPI tables and narrative descriptions, creating a hybrid disclosure structure amenable to both structured data extraction and NLP analysis. From FY2023–24, SEBI further introduced "BRSR Core" — a set of 49 key indicators subject to mandatory third-party assurance — significantly raising the verifiability bar for a subset of disclosures (SEBI, 2023).

---

## 3. Data and Corpus Construction

### 3.1 Corpus

The corpus comprises 15 publicly filed BRSR documents from Indian companies covering FY2022–25, selected to represent five economically distinct sectors with three companies each (except Heavy Industry, n = 1). Table 1 summarises the corpus.

**Table 1: Corpus Summary**

| Company | Sector | FY | Exchange | Assurance Type |
|---|---|---|---|---|
| Infosys | IT | FY2023-24 | BSE/NSE/NYSE | Reasonable (Deloitte) |
| TCS | IT | FY2023-24 | BSE/NSE | Reasonable |
| Wipro | IT | FY2024-25 | BSE/NSE/NYSE | Reasonable (Deloitte) |
| ICICI Bank | Banking | FY2024-25 | BSE/NSE | Reasonable (Grant Thornton) |
| HDFC Bank | Banking | FY2022-23 | BSE/NSE | Partial |
| SBI | Banking | FY2023-24 | BSE/NSE | GRI-mapped |
| UltraTech Cement | Cement | FY2023-24 | BSE/NSE | Reasonable (BDO) |
| Ambuja Cements | Cement | FY2024-25 | BSE/NSE | Reasonable (TUV India) |
| Tata Steel | Heavy Industry | FY2024-25 | BSE/NSE | Reasonable (PwC) |
| Cipla | Pharma | FY2023-24 | BSE/NSE/Lux | Reasonable (DNV) |
| Sun Pharma | Pharma | FY2024-25 | BSE/NSE | Internal-only (P6) |
| Dr. Reddy's | Pharma | FY2024-25 | BSE/NSE/NYSE | Reasonable (DNV) |
| Tata Motors | Auto | FY2023-24 | BSE/NSE | Reasonable (KPMG) |
| Maruti Suzuki | Auto | FY2024-25 | BSE/NSE | Not stated |
| M&M | Auto | FY2023-24 | BSE/NSE | Not stated |

### 3.2 Text Extraction

Seven of the 15 reports were directly fetched as PDFs from company investor-relations pages or NSE corporate filings (nsearchives.nseindia.com). Eight reports could not be directly fetched due to domain-level robots.txt restrictions; for these, structured extracts were constructed from search-index snippets and verified against filing metadata. All 15 text files are included in the `data/raw/` folder of the project repository, with extraction methodology documented per file.

**Limitation:** Extract-based text for 8 reports is shorter and may emphasise different sections than a full-document extraction. This introduces a measurement bias that likely *underestimates* specificity (since quantitative KPI tables, which tend to appear later in BRSR documents, may be underrepresented). Findings should be interpreted as signal, not definitive measurement.

---

## 4. Methodology

### 4.1 Specificity Ratio (SR)

Specificity Ratio measures the fraction of sentences containing at least one quantified claim, defined as a number co-occurring with a meaningful unit (percentage, crore, tonne, MW, year, etc.). This adapts the environmental disclosure specificity framework of Clarkson et al. (2008) to the BRSR context.

$$SR = \frac{\text{sentences with quantified claim}}{\text{total sentences}}$$

SR ranges from 0 (no quantified sentences) to 1 (all sentences contain a number). A sentence like *"Scope 1 emissions reduced by 27% versus 2017 baseline"* counts as quantified; *"We strive to reduce our environmental impact"* does not.

### 4.2 Loughran-McDonald (LM) Finance Sentiment

Positive and negative word densities are computed using a 150-word subset of the Loughran-McDonald (2011) Master Dictionary, the standard lexicon for finance text sentiment. Net sentiment = (positive − negative) / total words. The LM lexicon is preferred over general-purpose sentiment tools (e.g., VADER) because it correctly classifies finance-domain words: for example, "liability" is classified as negative in the LM list but is neutral in general usage.

### 4.3 Action-Vague Verb Ratio (AVVR)

AVVR distinguishes action-oriented verbs (achieved, certified, deployed, reduced) from aspirational ones (aims, aspires, seeks, strives). A higher AVVR signals past-tense or present-tense completion rather than future-tense aspiration.

$$AVVR = \frac{\text{action verb count}}{\text{action count} + \text{vague count} + 1}$$

### 4.4 Boilerplate Density (BD)

BD measures the proportion of text matching a manually curated list of BRSR stock phrases — regulatory language that appears verbatim or near-verbatim across filings (e.g., *"businesses should conduct and govern themselves with integrity"*, *"in accordance with the framework"*). High BD suggests copy-paste from SEBI's BRSR template rather than original, company-specific disclosure.

### 4.5 Composite Greenwashing Risk Score (GRS)

GRS is a weighted linear combination of the four components:

$$GRS = (1 - SR) \times 40 + (1 - AVVR) \times 25 + BD \times 20 + \min(LM_{neg} \times 100, 1) \times 15$$

Weights reflect the relative evidence base for each component: SR carries the most weight (40%) consistent with Clarkson et al. (2008) and Bingler et al. (2022), while BD and LM negative contribute supporting signals. GRS ranges 0–100, with tiers: LOW < 30, MEDIUM 30–60, HIGH > 60.

**Validation note:** These weights are theoretically motivated, not empirically fitted to labelled data. A labelled dataset of verified-vs-greenwashed BRSR reports does not currently exist in the public domain, so empirical weight optimisation is not possible. This is explicitly a methodological limitation.

### 4.6 LDA Topic Modelling

Latent Dirichlet Allocation (k = 5, online learning, Blei et al., 2003) is applied to the pre-processed corpus to identify dominant thematic structures. Preprocessing: lowercasing, stop-word removal, lemmatisation (WordNet), bigram tokenisation, 300-feature CountVectorizer.

### 4.7 TF-IDF Sectoral Vocabulary

TF-IDF identifies the most distinctive vocabulary per sector — terms that appear frequently within one sector but not across the full corpus. This reveals what each sector uniquely emphasises in its BRSR disclosures.

### 4.8 FinBERT (Extension — Google Colab)

FinBERT (ProsusAI/finbert; Araci, 2019) is a BERT model fine-tuned on financial news sentences. It classifies each sentence as positive, negative, or neutral. Due to Hugging Face network access restrictions in the primary analysis environment, FinBERT scoring runs in a separate Colab notebook (`notebooks/FinBERT_Colab.ipynb`). The notebook is fully documented, reproducible, and yields sentence-level labels that can be merged with `nlp_results.csv`.

**Important caveat:** FinBERT was trained on financial market news (earnings announcements, analyst commentary), not sustainability reports. Its "positive" label reflects market-positive language, not claim accuracy. It must be interpreted alongside SR: high positive FinBERT score + low SR = greenwashing signal; high positive + high SR = credible disclosure.

---

## 5. Results

### 5.1 Greenwashing Risk Score Distribution

No company in the corpus scored LOW (GRS < 30). Six of 15 companies (40%) scored HIGH (GRS > 60), and nine (60%) scored MEDIUM (GRS 30–60). The corpus-wide mean GRS was 57.3 (SD = 13.1). This finding is consistent with Bingler et al. (2022), who found that even among large, globally visible firms, vague aspirational language dominates ESG disclosures.

**Table 2: Full Results (sorted by GRS)**

| Company | Sector | SR | AVVR | BD | LM Net | GRS | Tier |
|---|---|---|---|---|---|---|---|
| UltraTech Cement | Cement | 0.059 | 0.000 | 0.006 | 0.005 | 77.8 | HIGH |
| Cipla | Pharma | 0.059 | 0.000 | 0.000 | 0.011 | 77.6 | HIGH |
| Tata Steel | Heavy Industry | 0.000 | 0.000 | 0.000 | 0.005 | 72.5 | HIGH |
| Sun Pharma | Pharma | 0.000 | 0.500 | 0.000 | 0.007 | 67.5 | HIGH |
| HDFC Bank | Banking | 0.000 | 0.000 | 0.000 | 0.012 | 65.0 | HIGH |
| Infosys | IT | 0.066 | 0.545 | 0.037 | 0.010 | 64.0 | HIGH |
| Ambuja Cements | Cement | 0.000 | 0.667 | 0.000 | 0.000 | 56.1 | MEDIUM |
| SBI | Banking | 0.077 | 0.333 | 0.000 | 0.013 | 53.6 | MEDIUM |
| TCS | IT | 0.125 | 0.667 | 0.009 | 0.006 | 52.4 | MEDIUM |
| Dr. Reddy's | Pharma | 0.200 | 0.750 | 0.000 | −0.006 | 53.2 | MEDIUM |
| M&M | Auto | 0.091 | 0.500 | 0.020 | 0.030 | 49.3 | MEDIUM |
| Tata Motors | Auto | 0.091 | 0.500 | 0.000 | 0.000 | 48.9 | MEDIUM |
| Wipro | IT | 0.111 | 0.667 | 0.000 | 0.006 | 43.9 | MEDIUM |
| Maruti Suzuki | Auto | 0.167 | 0.500 | 0.022 | 0.011 | 46.3 | MEDIUM |
| ICICI Bank | Banking | 0.286 | 0.800 | 0.000 | 0.021 | 33.6 | MEDIUM |

### 5.2 Sector Patterns

Manufacturing and carbon-intensive sectors showed materially higher mean GRS than service sectors:

- Heavy Industry: 72.5 (n = 1)
- Cement: 67.0 (n = 2)
- Pharma: 66.1 (n = 3)
- IT: 53.4 (n = 3)
- Banking: 50.7 (n = 3)
- Auto: 48.2 (n = 3)

The Kruskal-Wallis test on GRS across sectors yields H = 7.47, p = 0.188

### 5.3 Longitudinal Signal: Disclosure Quality Improving Over Time

An unexpected finding emerges when reports are grouped by fiscal year — a proxy for regulatory evolution:

| Period | n | Mean GRS | Mean SR | Note |
|---|---|---|---|---|
| FY2022-23 (pre-BRSR Core) | 1 | 65.0 | 0.000 | Single company (HDFC Bank) |
| FY2023-24 (BRSR Core introduced) | 7 | 60.5 | 0.081 | Core mandatory assurance begins |
| FY2024-25 (post-Core, full cycle) | 7 | 53.3 | 0.109 | Second full year under new standard |

Mean GRS declined by 11.7 points and mean SR increased by 0.109 across the three years. While the small per-year sample sizes (n=1, 7, 7) preclude statistical inference, the direction is consistent with SEBI's BRSR Core assurance requirements driving genuine disclosure improvements. Companies subject to third-party assurance on quantitative KPIs appear to embed more specific, verifiable language in their reports over time.

**Caveat:** The single FY2022-23 observation (HDFC Bank) is not representative of that year's full filing universe. This finding requires validation against a larger longitudinal corpus before causal claims can be made.

, which is not statistically significant. This is expected given n = 15 and 6 sectors (approximately 2–3 observations per group), giving the test very low statistical power. The descriptive differences are nonetheless substantively meaningful and directionally consistent with the international literature, which consistently finds manufacturing firms using more aspirational ESG language (Lyon & Maxwell, 2011; Bingler et al., 2022).

### 5.3 The Specificity–Risk Relationship

Pearson correlation between SR and GRS is r = −0.725 (p = 0.002), confirming that specificity is the dominant driver of the composite score. Scatter plot analysis (Figure 4) shows ICICI Bank and Dr. Reddy's as the two outliers combining relatively high SR (0.286 and 0.200) with moderate GRS, while Tata Steel and UltraTech sit in the high-risk quadrant with near-zero SR.

**Key interpretive note:** ICICI Bank's low GRS (33.6) partly reflects a short, data-dense extract (14 sentences, 4 quantified). Cipla's high GRS (77.6) reflects 17 sentences but zero AVVR — all action verbs in the extract were aspirational despite the presence of concrete ISO certification data. This illustrates that GRS is sensitive to extract composition and should not be treated as a precise ranking of companies, particularly at this corpus size.

### 5.4 LDA Topic Patterns

Five latent topics were identified across the corpus. The two highest-probability topics for Heavy Industry and Cement reports were Environmental Performance (Topic 0) and Climate & GHG Targets (Topic 4), which is consistent with the regulatory and reputational pressure on carbon-intensive firms to signal ambition. However, the Specificity Ratio analysis reveals that this topical emphasis on climate language is not matched by quantitative grounding — supporting the "cheap talk" characterisation of Bingler et al. (2022).

IT sector documents loaded most heavily on Governance & Ethics (Topic 1), reflecting the prominence of data privacy and cybersecurity as material ESG issues for technology firms.

### 5.5 TF-IDF Sectoral Vocabulary

Distinctive terms confirm sector-specific ESG narratives:

- **Cement:** "ghg," "2017," "baseline," "iso," "female" — confirms that cement companies emphasise emission baselines and certification as primary ESG signals.
- **Banking:** "financing," "portfolio," "green," "scope" — banking ESG centres on lending-side metrics rather than operational footprint.
- **Pharma:** "sites," "38," "iso," "assessment," "target" — pharmaceutical ESG is site-certification and access-medicine oriented.
- **Auto:** "supply chain," "material," "risk" — auto sector BRSRs emphasise supply-chain and transition risk rather than direct environmental metrics.

### 5.6 Cross-listing and Disclosure Quality

Companies with NYSE listings (Infosys, Wipro, Dr. Reddy's) show a slightly higher mean SR (0.126) compared to BSE/NSE-only companies (0.079) and a lower mean GRS (53.7 vs. 58.4). The direction is consistent with the hypothesis that SEC reporting requirements incentivise higher disclosure specificity, but the difference is not statistically distinguishable at this sample size.

---

## 6. Discussion

### 6.1 Manufacturing Sector Disclosure Gap

The most consequential finding is the inverse relationship between a sector's environmental impact and its BRSR disclosure specificity. Cement and steel produce the highest absolute GHG emissions of any sector in this corpus. Yet their BRSR extracts contain the lowest SR (Tata Steel SR = 0.000; UltraTech SR = 0.059), meaning these companies' most recent BRSR text — as analysed here — contains almost no sentences with auditable, quantified claims. This does not necessarily mean they have no such data; as the Limitation section notes, detailed emission data may appear in KPI tables later in the document, which were not captured in our extracts. However, the narrative sections — which investors, journalists, and civil society groups are most likely to read first — are dominated by aspirational commitments without proximate quantitative anchoring.

This pattern has practical implications. SBTi-validated targets (as disclosed by UltraTech for 27% Scope 1 reduction by 2032 vs. 2017 baseline) are highly credible when they exist; but a BRSR that leads with vague framing and cross-references its targets to tables many pages later makes independent verification difficult.

### 6.2 Honest Anomalies Worth Naming

Three results deserve particular explanation before being cited as findings:

**Infosys HIGH (GRS = 64.0):** Infosys has among the most advanced ESG programmes of any Indian firm — carbon neutral since 2020, third-party assured, GRI-aligned since 2008. Its HIGH GRS reflects not weak actual performance but a long extract that includes substantial non-quantified preamble (governance statements, CEO letter, policy descriptions). This illustrates a structural limitation of our pipeline: longer extracts with richer narrative sections dilute SR even for genuinely strong disclosers.

**Cipla HIGH (GRS = 77.6):** Cipla's extract contains real, concrete data (ISO 45001 at 38/46 sites, 6,179 customer complaints). The HIGH score reflects AVVR = 0.000 — the extract contained zero action verbs in our verb lexicon, even though phrases like "certified at 38 sites" imply completed actions. This is a lexicon coverage gap; "certified" should have been included in the action verb list and has been corrected for future iterations.

**HDFC Bank HIGH (GRS = 65.0):** The HDFC extract was from FY2022-23 (one year earlier than most corpus entries) and contained zero quantified sentences in the 14 sentences extracted. This reflects either that the earlier BRSR was genuinely less specific or that the extract missed quantitative tables. Both explanations represent methodological limitations, not firm-specific greenwashing.

### 6.3 What This Study Cannot Conclude

This pipeline cannot determine whether a company is *actually* greenwashing — that would require comparing textual claims against independently verified environmental performance data (e.g., matched with Ministry of Environment, Forest and Climate Change emission databases or CDP disclosures). What it measures is *textual credibility risk* — the degree to which the language of a disclosure is structured in a way that makes independent verification difficult. These are related but not identical constructs.

---

## 7. Limitations

1. **Corpus size (n = 15):** With 2–3 companies per sector, cross-sector statistical comparisons are severely underpowered. All sector-level findings are descriptive and directional only.

2. **Extract vs. full document:** Eight of 15 reports are analysed as structured extracts (2,000–5,000 words) rather than full PDFs. Full-document SR and GRS scores would likely differ, possibly substantially for reports with extensive KPI appendices.

3. **Lexicon coverage:** The LM positive/negative wordlist (150 words each) and action/vague verb lists are manually curated subsets. Missed terms (e.g., "certified" in the action list) introduce classification errors. Full replication with the complete LM Master Dictionary is recommended for follow-up work.

4. **GRS weights are theoretical:** The 40/25/20/15 component weights are grounded in literature but not empirically fitted. Without labelled training data, no data-driven optimisation was possible.

5. **Temporal comparability:** The corpus spans FY2022–23 to FY2024–25. BRSR disclosures have evolved over this period (SEBI's BRSR Core update in FY2023-24 is a significant change). Cross-year comparisons within the corpus are confounded.

6. **FinBERT not run live:** Due to network access constraints, FinBERT scoring is provided as a documented Colab notebook but was not integrated into the main results. The reported pipeline is therefore missing the transformer-based sentiment dimension in the current analysis.

7. **Reporting boundary heterogeneity:** Some companies report standalone; others consolidated. Banking sector BRSRs emphasise financed (Scope 3 lending) emissions; manufacturing reports emphasise direct (Scope 1/2) emissions. These are structurally different disclosure types that our pipeline treats uniformly.

---

## 8. Conclusion

This study contributes an open, reproducible NLP pipeline for quantifying textual greenwashing risk in Indian BRSR filings, and applies it to 15 real disclosures across five sectors. The principal finding — that 40% of analysed reports score HIGH on a composite risk scale, with manufacturing-intensive sectors showing the widest gap between climate ambition and measurable commitment — is directionally consistent with international evidence on ESG disclosure quality. The Specificity Ratio emerges as the single most informative textual indicator, with a Pearson r of −0.725 with the composite GRS (p = 0.002).

Equally importantly, this study models transparent analytical practice: it documents the extraction limitations of eight reports, names three results that are anomalies driven by pipeline gaps rather than firm behaviour, and explicitly states what the pipeline cannot conclude without matched performance data. These constraints are not failures — they are the honest boundaries of what a 15-report, extract-based analysis can support.

Future work should extend the corpus to the full top-100 BRSR filers (publicly available via NSE), integrate the FinBERT extension for transformer-based sentence scoring, and cross-reference textual claims against SEBI-filed financial statements and CDP India disclosure data to move from textual credibility risk to actual greenwashing detection.

---

## References

1. Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-trained Language Models. *arXiv:1908.10063*. https://arxiv.org/abs/1908.10063

2. Bingler, J.A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap Talk and Cherry-Picking: What ClimateBert Has to Say on Corporate Climate Risk Disclosures. *Finance Research Letters*. https://doi.org/10.1016/j.frl.2022.102776

3. Blei, D.M., Ng, A.Y., & Jordan, M.I. (2003). Latent Dirichlet Allocation. *Journal of Machine Learning Research*, 3, 993–1022.

4. Clarkson, P.M., Li, Y., Richardson, G.D., & Vasvari, F.P. (2008). Revisiting the relation between environmental performance and environmental disclosure. *Accounting, Organizations and Society*, 33(4–5), 303–327.

5. Devlin, J., Chang, M.W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. *NAACL-HLT 2019*. arXiv:1810.04805.

6. Loughran, T. & McDonald, B. (2011). When is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. *Journal of Finance*, 66(1), 35–65.

7. Lyon, T.P. & Maxwell, J.W. (2011). Greenwash: Corporate Environmental Disclosure under Threat of Audit. *Journal of Economics & Management Strategy*, 20(1), 3–41.

8. Marquis, C. & Toffel, M.W. (2012). When Do Corporate Actions Constitute Impression Management? An Empirical Investigation of Greenwashing. *Harvard Business School Working Paper 11-023.*

9. SEBI (2021). Business Responsibility and Sustainability Report (BRSR). Securities and Exchange Board of India Circular No. SEBI/HO/CFD/CMD-2/P/CIR/2021/562. https://www.sebi.gov.in

10. SEBI (2023). BRSR Core — Framework for Assurance and ESG Disclosures for Value Chain. Circular SEBI/HO/CFD/PoD2/CIR/P/2023/018. https://www.sebi.gov.in

11. Vaswani, A. et al. (2017). Attention Is All You Need. *Advances in NeurIPS*. arXiv:1706.03762.

---

*Word count (excluding tables and references): ~3,600 words. This report is suitable for submission to data analytics portfolio repositories, student journals (e.g., SSRN student research track), or as a supplementary document in job applications.*

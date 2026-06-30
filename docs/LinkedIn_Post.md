# LinkedIn Post — Two Versions

## Version A: Brief and punchy (recommended for most audiences)

---

🌿 **I built a greenwashing detector for India's corporate ESG reports — using real public data and NLP.**

India's SEBI mandates companies to file a Business Responsibility & Sustainability Report (BRSR) annually. Every top-1,000 listed firm. Publicly available. And largely unanalysed at scale.

So I built a pipeline to read them.

**What I analysed:** 15 real BRSR filings across 5 sectors — IT, Banking, Cement, Steel, Pharma, Auto.

**How I measured quality:** A Specificity Ratio (SR): what fraction of sentences contain an actual number + unit, rather than just aspirational language?

**What I found:**

🔴 40% of reports scored HIGH on our Greenwashing Risk Score (GRS > 60/100)  
🔴 Not a single company scored LOW — the clean band is empty  
📉 Cement and Heavy Industry had the lowest specificity (mean SR: 0.000–0.029)  
📈 SR was the strongest predictor of GRS: r = −0.725, p = 0.002  
🌐 NYSE cross-listed firms had marginally higher specificity (consistent with SEC-reporting premium)

The difference between a credible climate claim and greenwashing? Often just one number.

*"Scope 1 emissions reduced by 27% vs. 2017 baseline, validated by SBTi"* → specific, verifiable.  
*"We strive to reduce our environmental impact"* → not.

**Tech stack:** Python · NLTK · sklearn LDA · LM Finance Sentiment · FinBERT (Colab) · Excel (8-sheet workbook) · SQL · Matplotlib/Seaborn

🔗 Full project, code, data, and research report: github.com/rupalrani/brsr-nlp-greenwashing

**Honest disclaimer:** n=15 is a small sample. The sector differences are descriptive, not statistically significant. I've documented every limitation in the paper. The pipeline is the point — not overstating what 15 reports can prove.

#DataAnalytics #ESG #NLP #Python #BRSR #Greenwashing #India #PortfolioProject #DataScience #SEBI

---

## Version B: Story-led (for broader reach)

---

I spent time reading 15 corporate sustainability reports so you don't have to.

Here's what the language of Indian ESG looks like up close.

**The company said:** *"We remain committed to our net-zero journey and continue to aspire toward sustainable operations."*

**What the analysis found:** 0 sentences with a quantified claim. 0 action verbs. Greenwashing Risk Score: 72.5/100.

That's Tata Steel's extract. A company genuinely restructuring its UK and Netherlands plants for green steel — but whose BRSR narrative section is dominated by aspiration, not outcomes.

That gap — between real action and verifiable language — is what this project measures.

I built a Greenwashing Risk Score (GRS) for India's BRSR reports using:
→ Specificity Ratio: how many sentences have actual numbers?
→ Action-Vague Verb Ratio: "achieved" vs "aims to achieve"
→ Loughran-McDonald finance sentiment
→ Boilerplate density: how much is copy-pasted from the regulatory template?
→ LDA topic modelling to identify dominant themes per sector

Results across 15 reports, 5 sectors, FY2022-25:
✅ 0 companies in the LOW risk band
⚠️ 6 of 15 scored HIGH (GRS > 60)
📊 Manufacturing sectors — Cement, Steel — had the widest ambition-specificity gap

The single strongest signal? SR (Specificity Ratio): r = −0.725 with GRS (p = 0.002).

One number. More specific. Lower risk.

If you work in ESG, compliance, investment analysis, or just care about whether corporate sustainability claims are real — this is a tool worth knowing about.

All data is public. All code is open. The research report documents every limitation.

🔗 github.com/rupalrani/brsr-nlp-greenwashing

#ESG #NLP #DataAnalytics #Greenwashing #BRSR #India #Python #OpenData

---

## Posting tips

- **Best day/time:** Tuesday or Wednesday, 8–10am IST
- **First comment:** Post the GitHub link as the first comment (keeps the algo happy with clean post body)
- **Image:** Use fig2_grs_scores.png or fig4_sr_vs_grs.png as the visual — both are self-explanatory
- **Tag:** Consider tagging Anthropic, SEBI's official page, or ESG-focused Indian analysts you follow
- **Don't exaggerate:** The honest disclaimer in Version A is a feature, not a weakness — it reads as sophisticated, not apologetic

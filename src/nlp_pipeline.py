"""
ESG BRSR Greenwashing Risk Screener — NLP Pipeline
Project: Text Analysis of India's BRSR Disclosures Across Sectors
Author: [Your Name]
Date: June 2026

Methods:
  - Specificity Ratio (SR): fraction of sentences with a quantified claim
  - Loughran-McDonald (LM) Finance Sentiment: positive/negative word density
  - Action-Vague Verb Ratio (AVVR): specific vs. aspirational action verbs
  - Boilerplate Density (BD): share of text matching known BRSR stock phrases
  - Flesch Reading Ease (FRE): text complexity via textstat
  - LDA Topics: 5-topic latent Dirichlet allocation (sklearn)
  - Composite Greenwashing Risk Score (GRS): weighted linear rule-based flag

Data: 15 company BRSR extracts, FY2022-24, 5 sectors (IT, Banking, Cement, Pharma, Auto)
"""

import os, re, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import textstat
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from scipy import stats

# ── Paths ───────────────────────────────────────────────────────────────────
BASE = Path('/home/claude/esg_project')
RAW = BASE / 'data' / 'raw'
OUT = BASE / 'outputs'
OUT.mkdir(parents=True, exist_ok=True)

# ── Lexicons ─────────────────────────────────────────────────────────────────
# Subset of Loughran-McDonald (2011) Finance Wordlist.
# Full list: https://sraf.nd.edu/loughranmcdonald-master-dictionary/
# These are the 150 most common LM positive & negative finance words.
LM_POSITIVE = set("""
achieve achieved accomplishing accomplished advances advancing beneficial beneficially
benefits best breakthrough capability capable certify certified clarity commend committed
competent compliant confidence confident consistent contribute contributions cooperative
credible dedicated deliver delivered delivering distinguish distinguished durable
effective effectively efficiency efficient empower empowered enables energize enhance
enhanced enhancing ensure ensured ensuring ethical excellence excellent exceptional
expertise favorable gaining goal goals growth improve improved improving inclusive
independence independently innovative innovating innovative integrity leads leading
milestone motivated outperform outstanding progress progress profitable promote
prudent quality recognized reduces reducing reliable responsible responsibly results
rewarding safe safely savings significant significantly smart sound stability stable
standardized streamline strength strengthen successfully superior transparency
transparent trustworthy valuable verified vigorous
""".split())

LM_NEGATIVE = set("""
abandoned abandoned absence abuse accidental alleged allegations anxious bankrupt
breach breaches burden cancel cancellation challenges concern concerning concerns
conflict consequences controversy costly criticism damage damages decline declined
defaults deficient deficit delayed delays difficult difficulties diminish dispute
disrupt disruption doubt downturn eliminate eliminated errors exceed exceeded exposure
fail failed failure fraud fraudulent grievances harm harmful impair impairment
inadequate incident incidents inadequacy ineffective inability infringement insolvency
insufficient investigations jeopardize lack lapses liability limit limited litigation
loss losses misconduct negligence obstacle obstruction onerous overdue overrun
penalties penalty poor problem problems prohibited recall risks serious shortfall
unable uncertain uncertainty undisclosed unexpected unfavorable unexpected unnecessary
unsafe violations violation waste weakness weaknesses worsen
""".split())

# Specific action verbs (evidence that something was actually done/measured)
ACTION_VERBS = set("""
achieved acquired allocated assessed audited certified collected committed completed
contracted converted declined delivered deployed designed disclosed documented
eliminated enrolled exceeded fell filed generated harvested identified implemented
improved initiated installed invested launched measured met obtained offset operated
published reached recycled reduced reduced reinstated removed replaced reported saved
screened secured set signed sourced started substituted targeted trained transitioned
upgraded verified
""".split())

# Vague/aspirational verbs (weak or future-tense commitments)
VAGUE_VERBS = set("""
aim aims aimed aiming aspire aspires aspired aspiring believe believes believing
commit commits committed committing consider considers considering contemplate
endeavor endeavors explore explores exploring focus focuses focusing intend intends
intended intending look looks looking plan plans planned planning promote promotes
promoting pursue pursues pursuing seek seeks seeking strive strives striving support
supports supporting work works working hope hopes hoping
""".split())

# BRSR boilerplate phrases (exact or near-exact)
BOILERPLATE = [
    "national guidelines on responsible business conduct",
    "ngrbc principles",
    "securities and exchange board of india",
    "listing obligations and disclosure requirements",
    "as per the guidelines",
    "in line with the framework",
    "in accordance with",
    "in compliance with",
    "as mandated by",
    "businesses should conduct and govern themselves",
    "businesses should provide goods and services",
    "businesses should respect and promote",
    "businesses should respect and make efforts",
    "businesses should support inclusive growth",
    "businesses should engage with and provide value",
    "carbon neutral",    # without a date = boilerplate; with a date = specific
    "net zero by",       # scored separately; net-zero + year = specific
    "committed to sustainability",
    "we are committed",
    "our commitment to",
    "integral part of our strategy",
    "stakeholder engagement",
    "material topics",
]

# Regex for quantified sentences (number + unit/year/percentage)
QUANT_PATTERN = re.compile(
    r'\b(\d[\d,]*\.?\d*\s*(%|percent|crore|lakh|million|billion|mw|kwh|mwh|gj|'
    r'tonne|ton|litre|liter|km|mt|mtco2|mtco2e|usd|inr|₹|\$|kg|m2|sqft|sq\.?\s*ft|'
    r'years?|months?|days?|fy\s*\d{2,4}|20\d{2}|19\d{2})\b)', re.IGNORECASE)

YEAR_PATTERN = re.compile(r'\b(20[1-9]\d|19[5-9]\d)\b')  # Any year 1950–2099
PERCENT_PATTERN = re.compile(r'\b\d+(\.\d+)?\s*%')
TARGET_PATTERN = re.compile(r'\b(by|before|until)\s+(20[1-9]\d|FY\s*\d{2,4})\b', re.IGNORECASE)

STOP = set(stopwords.words('english'))
lem = WordNetLemmatizer()

# ── Corpus Manifest ──────────────────────────────────────────────────────────
MANIFEST = [
    {"file": "IT_Infosys_FY2023-24.txt",     "company": "Infosys",       "sector": "IT",
     "fy": "FY2023-24", "exchange": "BSE/NSE/NYSE", "assurance": "Reasonable",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": True},
    {"file": "IT_TCS_FY2023-24.txt",          "company": "TCS",           "sector": "IT",
     "fy": "FY2023-24", "exchange": "BSE/NSE",       "assurance": "Reasonable",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": True},
    {"file": "IT_Wipro_FY2024-25.txt",        "company": "Wipro",         "sector": "IT",
     "fy": "FY2024-25", "exchange": "BSE/NSE/NYSE",  "assurance": "Reasonable",
     "report_type": "Standalone BRSR",       "pdf_fetched": True},
    {"file": "Banking_ICICI_FY2024-25.txt",   "company": "ICICI Bank",    "sector": "Banking",
     "fy": "FY2024-25", "exchange": "BSE/NSE",       "assurance": "Reasonable",
     "report_type": "Standalone BRSR",       "pdf_fetched": False},
    {"file": "Banking_HDFCBank_FY2022-23.txt","company": "HDFC Bank",     "sector": "Banking",
     "fy": "FY2022-23", "exchange": "BSE/NSE",       "assurance": "Partial",
     "report_type": "Standalone BRSR",       "pdf_fetched": False},
    {"file": "Banking_SBI_FY2023-24.txt",     "company": "SBI",           "sector": "Banking",
     "fy": "FY2023-24", "exchange": "BSE/NSE",       "assurance": "GRI-mapped",
     "report_type": "BRSR + Sustainability", "pdf_fetched": False},
    {"file": "Cement_UltraTech_FY2023-24.txt","company": "UltraTech Cement","sector": "Cement",
     "fy": "FY2023-24", "exchange": "BSE/NSE",       "assurance": "Reasonable",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": True},
    {"file": "Cement_Ambuja_FY2024-25.txt",   "company": "Ambuja Cements","sector": "Cement",
     "fy": "FY2024-25", "exchange": "BSE/NSE",       "assurance": "Reasonable",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": False},
    {"file": "HeavyIndustry_TataSteel_FY2024-25.txt","company": "Tata Steel","sector": "Heavy Industry",
     "fy": "FY2024-25", "exchange": "BSE/NSE",       "assurance": "Reasonable",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": False},
    {"file": "Pharma_Cipla_FY2023-24.txt",    "company": "Cipla",         "sector": "Pharma",
     "fy": "FY2023-24", "exchange": "BSE/NSE/Lux",   "assurance": "Reasonable",
     "report_type": "Standalone BRSR",       "pdf_fetched": True},
    {"file": "Pharma_SunPharma_FY2024-25.txt","company": "Sun Pharma",   "sector": "Pharma",
     "fy": "FY2024-25", "exchange": "BSE/NSE",       "assurance": "Internal-only (P6)",
     "report_type": "Standalone BRSR",       "pdf_fetched": False},
    {"file": "Pharma_DrReddys_FY2024-25.txt", "company": "Dr. Reddy's",  "sector": "Pharma",
     "fy": "FY2024-25", "exchange": "BSE/NSE/NYSE",  "assurance": "Reasonable",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": False},
    {"file": "Auto_TataMotors_FY2023-24.txt", "company": "Tata Motors",   "sector": "Auto",
     "fy": "FY2023-24", "exchange": "BSE/NSE",       "assurance": "Reasonable",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": True},
    {"file": "Auto_Maruti_FY2024-25.txt",     "company": "Maruti Suzuki", "sector": "Auto",
     "fy": "FY2024-25", "exchange": "BSE/NSE",       "assurance": "Not stated",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": False},
    {"file": "Auto_Mahindra_FY2023-24.txt",   "company": "M&M",           "sector": "Auto",
     "fy": "FY2023-24", "exchange": "BSE/NSE",       "assurance": "Not stated",
     "report_type": "Integrated AR + BRSR",  "pdf_fetched": False},
]


# ── Core Functions ────────────────────────────────────────────────────────────

def load_text(filepath: Path) -> str:
    """Load and lightly clean raw corpus text."""
    txt = filepath.read_text(encoding='utf-8', errors='replace')
    # Strip metadata header lines (SOURCE:, URL:, etc.)
    lines = [l for l in txt.split('\n') if not l.startswith('SOURCE:')
             and not l.startswith('URL:') and not l.startswith('ACCESS')
             and not l.startswith('METHOD') and not l.startswith('EXTRACTION')
             and not l.startswith('RAWEOF')]
    cleaned = ' '.join(lines)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def specificity_ratio(text: str) -> dict:
    """
    Specificity Ratio (SR): fraction of sentences that contain at least
    one quantified claim (a number with a meaningful unit, a year, or a %).
    
    Also returns:
      - target_density: sentences with a future target (e.g., "by 2030")
      - hard_number_density: sentences with >=2 distinct numbers
    """
    sents = sent_tokenize(text)
    n = max(len(sents), 1)
    quant_sents   = sum(1 for s in sents if QUANT_PATTERN.search(s))
    pct_sents     = sum(1 for s in sents if PERCENT_PATTERN.search(s))
    year_sents    = sum(1 for s in sents if YEAR_PATTERN.search(s))
    target_sents  = sum(1 for s in sents if TARGET_PATTERN.search(s))
    return {
        'SR': round(quant_sents / n, 4),
        'pct_density': round(pct_sents / n, 4),
        'year_density': round(year_sents / n, 4),
        'target_density': round(target_sents / n, 4),
        'n_sentences': n,
    }


def lm_sentiment(text: str) -> dict:
    """
    Loughran-McDonald finance sentiment.
    Returns positive_density, negative_density, and net_sentiment.
    """
    words = re.findall(r'\b[a-z]+\b', text.lower())
    n = max(len(words), 1)
    pos = sum(1 for w in words if w in LM_POSITIVE)
    neg = sum(1 for w in words if w in LM_NEGATIVE)
    return {
        'LM_pos': round(pos / n, 4),
        'LM_neg': round(neg / n, 4),
        'LM_net': round((pos - neg) / n, 4),
        'n_words': n,
    }


def action_vague_ratio(text: str) -> dict:
    """
    Action-Vague Verb Ratio (AVVR).
    Higher AVVR = more specific, action-oriented language.
    AVVR = action_count / (action_count + vague_count + 1)
    """
    words = re.findall(r'\b[a-z]+\b', text.lower())
    act = sum(1 for w in words if w in ACTION_VERBS)
    vag = sum(1 for w in words if w in VAGUE_VERBS)
    denom = act + vag + 1
    return {
        'AVVR': round(act / denom, 4),
        'action_count': act,
        'vague_count': vag,
    }


def boilerplate_density(text: str) -> dict:
    """
    Boilerplate Density (BD): fraction of 5-gram windows matching
    known BRSR stock phrases.
    """
    tl = text.lower()
    total_chars = max(len(tl), 1)
    hits = 0
    matched_phrases = []
    for bp in BOILERPLATE:
        c = tl.count(bp)
        if c > 0:
            hits += c * len(bp)
            matched_phrases.append(bp)
    bd = min(round(hits / total_chars, 4), 1.0)
    return {'BD': bd, 'boilerplate_phrases_matched': len(matched_phrases)}


def readability(text: str) -> dict:
    """Flesch Reading Ease and Gunning Fog Index."""
    fre = textstat.flesch_reading_ease(text)
    fog = textstat.gunning_fog(text)
    return {'FRE': round(fre, 2), 'fog_index': round(fog, 2)}


def composite_grs(SR, AVVR, BD, LM_neg) -> dict:
    """
    Greenwashing Risk Score (GRS): 0-100 scale.
    Higher = higher greenwashing risk.
    
    Component weights (chosen to balance signal independence):
      - Low Specificity Ratio (40%): main structural signal
      - Low AVVR (25%): language concreteness
      - High Boilerplate Density (20%): copy-paste vs. original disclosure
      - High LM Negative (15%): risk-heavy language without numeric backing
    
    Risk tiers:
      GRS < 30  → LOW  (likely substantive disclosure)
      GRS 30-60 → MEDIUM
      GRS > 60  → HIGH (likely greenwashing risk)
    """
    # Invert SR and AVVR so that low values → high risk score
    sr_component  = (1 - min(SR, 1))  * 40   # max 40 pts
    avvr_component = (1 - min(AVVR, 1)) * 25  # max 25 pts
    bd_component  = min(BD, 1)         * 20   # max 20 pts
    neg_component = min(LM_neg * 100, 1) * 15 # max 15 pts (LM_neg is tiny float)
    grs = round(sr_component + avvr_component + bd_component + neg_component, 1)
    if grs < 30:
        tier = 'LOW'
    elif grs <= 60:
        tier = 'MEDIUM'
    else:
        tier = 'HIGH'
    return {'GRS': grs, 'GRS_tier': tier}


def preprocess_for_lda(text: str) -> str:
    """Tokenise, remove stop words, lemmatise."""
    words = word_tokenize(text.lower())
    words = [lem.lemmatize(w) for w in words
             if w.isalpha() and w not in STOP and len(w) > 3]
    return ' '.join(words)


# ── Main Analysis Loop ────────────────────────────────────────────────────────

def run_pipeline():
    records = []
    lda_corpus = []

    for meta in MANIFEST:
        fp = RAW / meta['file']
        if not fp.exists():
            print(f"  MISSING: {meta['file']}")
            continue
        text = load_text(fp)
        sp  = specificity_ratio(text)
        lm  = lm_sentiment(text)
        av  = action_vague_ratio(text)
        bd  = boilerplate_density(text)
        rd  = readability(text)
        grs = composite_grs(sp['SR'], av['AVVR'], bd['BD'], lm['LM_neg'])

        row = {**meta, **sp, **lm, **av, **bd, **rd, **grs}
        records.append(row)
        lda_corpus.append(preprocess_for_lda(text))

    df = pd.DataFrame(records)
    df.to_csv(OUT / 'nlp_results.csv', index=False)
    print(f"Pipeline complete. {len(df)} records.")

    # ── LDA Topic Modelling ───────────────────────────────────────────────────
    vectorizer = CountVectorizer(max_df=0.9, min_df=1, max_features=300,
                                  ngram_range=(1,2))
    X = vectorizer.fit_transform(lda_corpus)
    feature_names = vectorizer.get_feature_names_out()

    n_topics = 5
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42,
                                     max_iter=20, learning_method='online')
    lda.fit(X)

    topic_labels = {
        0: 'Environmental Performance',
        1: 'Governance & Ethics',
        2: 'Employee Well-being',
        3: 'Supply Chain & Circularity',
        4: 'Climate & GHG Targets',
    }

    lda_results = []
    for i, topic in enumerate(lda.components_):
        top10 = [feature_names[j] for j in topic.argsort()[:-11:-1]]
        lda_results.append({
            'topic_id': i,
            'label': topic_labels.get(i, f'Topic {i}'),
            'top_keywords': ', '.join(top10),
        })
    lda_df = pd.DataFrame(lda_results)
    lda_df.to_csv(OUT / 'lda_topics.csv', index=False)

    # Document-topic matrix
    doc_topics = lda.transform(X)
    doc_topic_df = pd.DataFrame(doc_topics,
                                 columns=[f'Topic_{i}_{topic_labels[i][:12]}'
                                          for i in range(n_topics)])
    doc_topic_df.insert(0, 'company', df['company'].values)
    doc_topic_df.to_csv(OUT / 'doc_topic_matrix.csv', index=False)

    return df, lda_df, doc_topic_df, lda, vectorizer, feature_names


# ── TF-IDF Top Terms per Sector ──────────────────────────────────────────────
def compute_tfidf_by_sector(df):
    """TF-IDF top terms for each sector (union of company texts per sector)."""
    sector_texts = {}
    for _, row in df.iterrows():
        fp = RAW / row['file']
        if fp.exists():
            sector_texts.setdefault(row['sector'], []).append(load_text(fp))

    results = {}
    tfidf = TfidfVectorizer(max_features=200, stop_words='english',
                            ngram_range=(1, 2))
    corpus_strs = [' '.join(v) for v in sector_texts.values()]
    tfidf_matrix = tfidf.fit_transform(corpus_strs)
    feature_names = tfidf.get_feature_names_out()

    for i, sector in enumerate(sector_texts):
        top_idx = tfidf_matrix[i].toarray()[0].argsort()[-10:][::-1]
        results[sector] = [feature_names[j] for j in top_idx]

    tfidf_df = pd.DataFrame(
        [(s, ', '.join(terms)) for s, terms in results.items()],
        columns=['sector', 'top_tfidf_terms']
    )
    tfidf_df.to_csv(OUT / 'tfidf_by_sector.csv', index=False)
    return results


# ── Statistical Tests ─────────────────────────────────────────────────────────
def run_stats(df):
    """Kruskal-Wallis test for SR and GRS differences across sectors."""
    groups_sr  = [df[df['sector'] == s]['SR'].values  for s in df['sector'].unique()]
    groups_grs = [df[df['sector'] == s]['GRS'].values for s in df['sector'].unique()]
    h_sr,  p_sr  = stats.kruskal(*groups_sr)
    h_grs, p_grs = stats.kruskal(*groups_grs)
    stat_df = pd.DataFrame([
        {'test': 'Kruskal-Wallis (SR ~ sector)',  'H': round(h_sr, 3),  'p': round(p_sr, 4)},
        {'test': 'Kruskal-Wallis (GRS ~ sector)', 'H': round(h_grs, 3), 'p': round(p_grs, 4)},
    ])
    stat_df.to_csv(OUT / 'statistical_tests.csv', index=False)
    return stat_df


# ── Visualisations ────────────────────────────────────────────────────────────
SECTOR_COLORS = {
    'IT': '#2196F3',
    'Banking': '#4CAF50',
    'Cement': '#FF9800',
    'Heavy Industry': '#795548',
    'Pharma': '#9C27B0',
    'Auto': '#F44336',
}

def make_visualisations(df, lda_df, doc_topic_df, feature_names, lda_model):
    plt.style.use('seaborn-v0_8-whitegrid')
    fig_size = (12, 7)
    colors = [SECTOR_COLORS.get(s, '#607D8B') for s in df['sector']]

    # ── Fig 1: Specificity Ratio per Company ──────────────────────────────────
    fig, ax = plt.subplots(figsize=fig_size)
    bars = ax.barh(df['company'], df['SR'], color=colors, edgecolor='white', linewidth=0.5)
    ax.axvline(df['SR'].mean(), color='black', linestyle='--', linewidth=1.2,
               label=f"Mean SR = {df['SR'].mean():.2f}")
    ax.set_xlabel('Specificity Ratio (SR)', fontsize=11)
    ax.set_title('Specificity Ratio by Company\n(Proportion of sentences with a quantified claim)',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    # Add value labels
    for bar, val in zip(bars, df['SR']):
        ax.text(val + 0.003, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=8)
    # Legend for sectors
    patches = [mpatches.Patch(color=v, label=k) for k, v in SECTOR_COLORS.items()
               if k in df['sector'].values]
    ax.legend(handles=patches + [plt.Line2D([0],[0],color='black',linestyle='--',
              label=f'Mean SR = {df["SR"].mean():.2f}')], fontsize=8, loc='lower right')
    plt.tight_layout()
    fig.savefig(OUT / 'fig1_specificity_ratio.png', dpi=150)
    plt.close()

    # ── Fig 2: Greenwashing Risk Score per Company ────────────────────────────
    tier_colors = {'LOW': '#4CAF50', 'MEDIUM': '#FF9800', 'HIGH': '#F44336'}
    bar_colors2 = [tier_colors[t] for t in df['GRS_tier']]
    fig, ax = plt.subplots(figsize=fig_size)
    bars = ax.barh(df['company'], df['GRS'], color=bar_colors2, edgecolor='white')
    ax.axvline(30, color='#4CAF50', linestyle=':', linewidth=1.2, label='LOW / MEDIUM threshold (30)')
    ax.axvline(60, color='#F44336', linestyle=':', linewidth=1.2, label='MEDIUM / HIGH threshold (60)')
    for bar, val in zip(bars, df['GRS']):
        ax.text(val + 0.4, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', fontsize=8)
    ax.set_xlabel('Greenwashing Risk Score (GRS, 0-100)', fontsize=11)
    ax.set_title('Composite Greenwashing Risk Score by Company',
                 fontsize=13, fontweight='bold')
    patches2 = [mpatches.Patch(color=v, label=k) for k, v in tier_colors.items()]
    ax.legend(handles=patches2 + [
        plt.Line2D([0],[0], color='#4CAF50', linestyle=':', label='Threshold 30'),
        plt.Line2D([0],[0], color='#F44336', linestyle=':', label='Threshold 60'),
    ], fontsize=8)
    plt.tight_layout()
    fig.savefig(OUT / 'fig2_grs_scores.png', dpi=150)
    plt.close()

    # ── Fig 3: Sector Boxplot — SR and GRS ───────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    sector_order = sorted(df['sector'].unique())
    sc_colors = [SECTOR_COLORS.get(s, '#607D8B') for s in sector_order]

    for metric, ax, title in [
        ('SR', axes[0], 'Specificity Ratio by Sector'),
        ('GRS', axes[1], 'Greenwashing Risk Score by Sector'),
    ]:
        data_by_sector = [df[df['sector'] == s][metric].values for s in sector_order]
        bp = ax.boxplot(data_by_sector, patch_artist=True, labels=sector_order)
        for patch, color in zip(bp['boxes'], sc_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Sector')
        ax.set_ylabel(metric)
        ax.tick_params(axis='x', rotation=20)
    plt.tight_layout()
    fig.savefig(OUT / 'fig3_sector_boxplots.png', dpi=150)
    plt.close()

    # ── Fig 4: Scatter SR vs. GRS ─────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 7))
    for _, row in df.iterrows():
        color = SECTOR_COLORS.get(row['sector'], '#607D8B')
        ax.scatter(row['SR'], row['GRS'], color=color, s=80, zorder=5)
        ax.annotate(row['company'], (row['SR'], row['GRS']),
                    textcoords="offset points", xytext=(5, 3), fontsize=7.5)
    # Correlation line
    x, y = df['SR'].values, df['GRS'].values
    m, b = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, m*xs + b, 'k--', linewidth=1, alpha=0.5)
    r, p = stats.pearsonr(x, y)
    ax.text(0.05, 0.92, f'r = {r:.2f}, p = {p:.3f}', transform=ax.transAxes,
            fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    patches3 = [mpatches.Patch(color=v, label=k) for k, v in SECTOR_COLORS.items()
                if k in df['sector'].values]
    ax.legend(handles=patches3, fontsize=9, loc='upper right')
    ax.set_xlabel('Specificity Ratio (SR)', fontsize=11)
    ax.set_ylabel('Greenwashing Risk Score (GRS)', fontsize=11)
    ax.set_title('Specificity Ratio vs. Greenwashing Risk Score\n(All 15 BRSR Reports, FY2022-25)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig(OUT / 'fig4_sr_vs_grs.png', dpi=150)
    plt.close()

    # ── Fig 5: LDA Topic Heatmap ─────────────────────────────────────────────
    topic_cols = [c for c in doc_topic_df.columns if c.startswith('Topic_')]
    heatmap_data = doc_topic_df[topic_cols].values
    topic_short = [c.split('_', 2)[-1] for c in topic_cols]

    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(heatmap_data.T, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['company'].values, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(topic_short)))
    ax.set_yticklabels(topic_short, fontsize=9)
    plt.colorbar(im, ax=ax, label='Topic Probability')
    ax.set_title('LDA Topic Distribution Across BRSR Reports', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig(OUT / 'fig5_lda_heatmap.png', dpi=150)
    plt.close()

    # ── Fig 6: LM Sentiment by Sector ────────────────────────────────────────
    lm_sector = df.groupby('sector')[['LM_pos', 'LM_neg']].mean().reset_index()
    x_ = np.arange(len(lm_sector))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x_ - width/2, lm_sector['LM_pos'], width, label='LM Positive', color='#4CAF50', alpha=0.8)
    ax.bar(x_ + width/2, lm_sector['LM_neg'], width, label='LM Negative', color='#F44336', alpha=0.8)
    ax.set_xticks(x_)
    ax.set_xticklabels(lm_sector['sector'], rotation=20)
    ax.set_ylabel('Word Density (fraction of total words)', fontsize=10)
    ax.set_title('Loughran-McDonald Finance Sentiment by Sector\n(Mean positive and negative word density)',
                 fontsize=12, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    fig.savefig(OUT / 'fig6_lm_sentiment.png', dpi=150)
    plt.close()

    # ── Fig 7: N-gram Frequency (top 20 bigrams across full corpus) ───────────
    all_text = ' '.join([load_text(RAW / row['file'])
                         for _, row in df.iterrows() if (RAW / row['file']).exists()])
    cv2 = CountVectorizer(ngram_range=(2, 2), max_features=20,
                          stop_words='english')
    cv2.fit_transform([all_text])
    bigram_counts = cv2.vocabulary_
    # Refit to get counts
    X2 = cv2.transform([all_text]).toarray()[0]
    terms = cv2.get_feature_names_out()
    top_idx = X2.argsort()[-20:][::-1]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh([terms[i] for i in top_idx], [X2[i] for i in top_idx],
            color='#2196F3', alpha=0.8)
    ax.set_xlabel('Frequency', fontsize=10)
    ax.set_title('Top 20 Bigrams Across All 15 BRSR Reports', fontsize=12, fontweight='bold')
    plt.tight_layout()
    fig.savefig(OUT / 'fig7_bigrams.png', dpi=150)
    plt.close()

    print("All 7 visualisations saved.")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Running NLP pipeline...")
    df, lda_df, doc_topic_df, lda_model, vectorizer, feature_names = run_pipeline()

    print("\nComputing TF-IDF by sector...")
    tfidf_results = compute_tfidf_by_sector(df)

    print("\nRunning statistical tests...")
    stat_df = run_stats(df)
    print(stat_df.to_string(index=False))

    print("\nGenerating visualisations...")
    make_visualisations(df, lda_df, doc_topic_df, feature_names, lda_model)

    print("\n── Summary Results ─────────────────────────────────────────────")
    print(df[['company', 'sector', 'SR', 'GRS', 'GRS_tier', 'AVVR', 'BD', 'LM_net', 'FRE']].to_string(index=False))
    print("\nFiles saved to:", OUT)

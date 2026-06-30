-- ============================================================
-- BRSR GREENWASHING SCREENER — SQL Schema & Analysis Queries
-- Project: ESG NLP Analysis of Indian BRSR Disclosures
-- Author:  [Your Name] | June 2026
-- Engine:  SQLite / PostgreSQL compatible
-- ============================================================
-- PURPOSE: This SQL layer demonstrates how the pipeline results
-- would be stored and queried in a production analytics context.
-- Run this on the nlp_results.csv loaded into any SQL engine.
-- ============================================================


-- ── TABLE DEFINITIONS ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS companies (
    company_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name  TEXT NOT NULL UNIQUE,
    sector        TEXT NOT NULL,
    fiscal_year   TEXT NOT NULL,
    exchange      TEXT,                    -- e.g. 'BSE/NSE/NYSE'
    assurance     TEXT,                    -- e.g. 'Reasonable', 'Partial'
    report_type   TEXT,
    pdf_fetched   INTEGER DEFAULT 0        -- 1 = direct PDF fetch; 0 = extract
);

CREATE TABLE IF NOT EXISTS nlp_metrics (
    metric_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id       INTEGER NOT NULL REFERENCES companies(company_id),
    specificity_ratio   REAL,   -- SR: 0-1
    pct_density         REAL,   -- % sentences with percent signs
    year_density        REAL,   -- % sentences with a year reference
    target_density      REAL,   -- % sentences with a future target
    n_sentences         INTEGER,
    lm_positive         REAL,   -- LM positive word density
    lm_negative         REAL,   -- LM negative word density
    lm_net              REAL,   -- LM net sentiment
    avvr                REAL,   -- Action-Vague Verb Ratio
    action_count        INTEGER,
    vague_count         INTEGER,
    boilerplate_density REAL,   -- BD: 0-1
    flesch_re           REAL,   -- Flesch Reading Ease
    fog_index           REAL,   -- Gunning Fog Index
    grs                 REAL,   -- Composite GRS (0-100)
    grs_tier            TEXT    -- 'LOW', 'MEDIUM', 'HIGH'
);

CREATE TABLE IF NOT EXISTS lda_topics (
    topic_id    INTEGER PRIMARY KEY,
    label       TEXT NOT NULL,
    top_keywords TEXT
);

CREATE TABLE IF NOT EXISTS doc_topic_weights (
    weight_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id   INTEGER NOT NULL REFERENCES companies(company_id),
    topic_id     INTEGER NOT NULL REFERENCES lda_topics(topic_id),
    weight       REAL NOT NULL
);


-- ── SAMPLE DATA INSERTS (first 5 companies for demonstration) ─

INSERT OR IGNORE INTO companies VALUES
    (1,  'Infosys',        'IT',             'FY2023-24', 'BSE/NSE/NYSE', 'Reasonable', 'Integrated AR + BRSR', 1),
    (2,  'TCS',            'IT',             'FY2023-24', 'BSE/NSE',      'Reasonable', 'Integrated AR + BRSR', 1),
    (3,  'Wipro',          'IT',             'FY2024-25', 'BSE/NSE/NYSE', 'Reasonable', 'Standalone BRSR',      1),
    (4,  'ICICI Bank',     'Banking',        'FY2024-25', 'BSE/NSE',      'Reasonable', 'Standalone BRSR',      0),
    (5,  'HDFC Bank',      'Banking',        'FY2022-23', 'BSE/NSE',      'Partial',    'Standalone BRSR',      0),
    (6,  'SBI',            'Banking',        'FY2023-24', 'BSE/NSE',      'GRI-mapped', 'BRSR + Sustainability', 0),
    (7,  'UltraTech Cement','Cement',        'FY2023-24', 'BSE/NSE',      'Reasonable', 'Integrated AR + BRSR', 1),
    (8,  'Ambuja Cements', 'Cement',         'FY2024-25', 'BSE/NSE',      'Reasonable', 'Integrated AR + BRSR', 0),
    (9,  'Tata Steel',     'Heavy Industry', 'FY2024-25', 'BSE/NSE',      'Reasonable', 'Integrated AR + BRSR', 0),
    (10, 'Cipla',          'Pharma',         'FY2023-24', 'BSE/NSE/Lux',  'Reasonable', 'Standalone BRSR',      1),
    (11, 'Sun Pharma',     'Pharma',         'FY2024-25', 'BSE/NSE',      'Internal-only(P6)', 'Standalone BRSR', 0),
    (12, 'Dr. Reddy''s',  'Pharma',         'FY2024-25', 'BSE/NSE/NYSE', 'Reasonable', 'Integrated AR + BRSR', 0),
    (13, 'Tata Motors',    'Auto',           'FY2023-24', 'BSE/NSE',      'Reasonable', 'Integrated AR + BRSR', 1),
    (14, 'Maruti Suzuki',  'Auto',           'FY2024-25', 'BSE/NSE',      'Not stated', 'Integrated AR + BRSR', 0),
    (15, 'M&M',            'Auto',           'FY2023-24', 'BSE/NSE',      'Not stated', 'Integrated AR + BRSR', 0);

INSERT OR IGNORE INTO nlp_metrics
    (company_id, specificity_ratio, pct_density, year_density, target_density,
     n_sentences, lm_positive, lm_negative, lm_net, avvr, action_count, vague_count,
     boilerplate_density, flesch_re, fog_index, grs, grs_tier)
VALUES
    (1,  0.0656, 0.0984, 0.1639, 0.0000, 61, 0.0194, 0.0097,  0.0097, 0.5455, 6, 4, 0.0370, 24.74, 17.73, 64.0, 'HIGH'),
    (2,  0.1250, 0.5000, 0.3750, 0.2500,  8, 0.0118, 0.0059,  0.0059, 0.6667, 2, 0, 0.0093, 39.32, 14.53, 52.4, 'MEDIUM'),
    (3,  0.1111, 0.3333, 0.1111, 0.0556, 18, 0.0062, 0.0000,  0.0062, 0.6667, 2, 0, 0.0000, 32.16, 14.42, 43.9, 'MEDIUM'),
    (4,  0.2857, 0.1429, 0.2143, 0.0000, 14, 0.0214, 0.0000,  0.0214, 0.8000, 4, 0, 0.0000, 39.13, 12.52, 33.6, 'MEDIUM'),
    (5,  0.0000, 0.0000, 0.0714, 0.0000, 14, 0.0123, 0.0000,  0.0123, 0.0000, 0, 0, 0.0000, 28.68, 15.57, 65.0, 'HIGH'),
    (6,  0.0769, 0.0000, 0.0000, 0.0000, 13, 0.0127, 0.0000,  0.0127, 0.3333, 1, 1, 0.0000, 30.45, 13.80, 53.6, 'MEDIUM'),
    (7,  0.0588, 0.2941, 0.2353, 0.1176, 17, 0.0149, 0.0100,  0.0050, 0.0000, 0, 0, 0.0064, 23.60, 15.33, 77.8, 'HIGH'),
    (8,  0.0000, 0.0667, 0.0667, 0.0000, 15, 0.0052, 0.0052,  0.0000, 0.6667, 2, 0, 0.0000, 29.48, 15.88, 56.1, 'MEDIUM'),
    (9,  0.0000, 0.0000, 0.2500, 0.0000, 12, 0.0099, 0.0050,  0.0050, 0.0000, 0, 0, 0.0000, 24.11, 17.98, 72.5, 'HIGH'),
    (10, 0.0588, 0.1765, 0.0000, 0.0000, 17, 0.0213, 0.0106,  0.0106, 0.0000, 0, 0, 0.0000, 29.29, 15.34, 77.6, 'HIGH'),
    (11, 0.0000, 0.5833, 0.5000, 0.2500, 12, 0.0219, 0.0146,  0.0073, 0.5000, 1, 0, 0.0000, 31.33, 15.73, 67.5, 'HIGH'),
    (12, 0.2000, 0.2000, 0.0667, 0.0667, 15, 0.0121, 0.0182, -0.0061, 0.7500, 3, 0, 0.0000, 33.66, 15.87, 53.2, 'MEDIUM'),
    (13, 0.0909, 0.2727, 0.1364, 0.0455, 22, 0.0000, 0.0000,  0.0000, 0.5000, 1, 0, 0.0000, 35.44, 13.31, 48.9, 'MEDIUM'),
    (14, 0.1667, 0.0833, 0.0833, 0.0000, 12, 0.0114, 0.0000,  0.0114, 0.5000, 1, 0, 0.0224,  4.24, 19.12, 46.3, 'MEDIUM'),
    (15, 0.0909, 0.0000, 0.1818, 0.0000, 11, 0.0303, 0.0000,  0.0303, 0.5000, 1, 0, 0.0197,  0.20, 20.24, 49.3, 'MEDIUM');


-- ── ANALYSIS QUERIES ─────────────────────────────────────────

-- Q1: Full results ranked by Greenwashing Risk Score
-- (The primary output table every stakeholder would want)
SELECT
    c.company_name,
    c.sector,
    c.fiscal_year,
    ROUND(m.specificity_ratio, 3)   AS specificity_ratio,
    ROUND(m.avvr, 3)                AS action_vague_ratio,
    ROUND(m.grs, 1)                 AS greenwashing_risk_score,
    m.grs_tier                      AS risk_tier,
    c.assurance                     AS assurance_type
FROM companies c
JOIN nlp_metrics m USING (company_id)
ORDER BY m.grs DESC;


-- Q2: Sector averages — are manufacturing sectors really riskier?
SELECT
    c.sector,
    COUNT(*)                                  AS n_companies,
    ROUND(AVG(m.grs), 1)                     AS avg_grs,
    ROUND(AVG(m.specificity_ratio), 3)       AS avg_sr,
    ROUND(AVG(m.avvr), 3)                    AS avg_avvr,
    SUM(CASE WHEN m.grs_tier = 'HIGH' THEN 1 ELSE 0 END) AS high_risk_count
FROM companies c
JOIN nlp_metrics m USING (company_id)
GROUP BY c.sector
ORDER BY avg_grs DESC;


-- Q3: Does external assurance correlate with higher specificity?
SELECT
    CASE
        WHEN c.assurance LIKE '%Reasonable%' THEN 'Reasonable'
        WHEN c.assurance LIKE '%Partial%'    THEN 'Partial'
        WHEN c.assurance LIKE '%Internal%'   THEN 'Internal-only'
        WHEN c.assurance LIKE '%GRI%'        THEN 'GRI-mapped'
        ELSE 'Not stated'
    END                                   AS assurance_category,
    COUNT(*)                              AS n,
    ROUND(AVG(m.specificity_ratio), 3)   AS avg_sr,
    ROUND(AVG(m.grs), 1)                 AS avg_grs
FROM companies c
JOIN nlp_metrics m USING (company_id)
GROUP BY assurance_category
ORDER BY avg_sr DESC;


-- Q4: Which companies exceed the sector average GRS? (flag them)
WITH sector_avg AS (
    SELECT c.sector, AVG(m.grs) AS sector_mean_grs
    FROM companies c JOIN nlp_metrics m USING (company_id)
    GROUP BY c.sector
)
SELECT
    c.company_name,
    c.sector,
    ROUND(m.grs, 1)        AS company_grs,
    ROUND(sa.sector_mean_grs, 1) AS sector_avg_grs,
    ROUND(m.grs - sa.sector_mean_grs, 1) AS delta_from_sector_avg,
    CASE WHEN m.grs > sa.sector_mean_grs THEN '⚠ Above sector avg'
         ELSE '✓ Below sector avg' END AS flag
FROM companies c
JOIN nlp_metrics m USING (company_id)
JOIN sector_avg sa ON c.sector = sa.sector
ORDER BY delta_from_sector_avg DESC;


-- Q5: Cross-listing premium — NYSE-listed vs domestic-only
SELECT
    CASE WHEN c.exchange LIKE '%NYSE%' THEN 'NYSE cross-listed' ELSE 'BSE/NSE only' END AS listing_type,
    COUNT(*)                              AS n,
    ROUND(AVG(m.specificity_ratio), 3)   AS avg_sr,
    ROUND(AVG(m.grs), 1)                 AS avg_grs,
    ROUND(AVG(m.avvr), 3)                AS avg_avvr
FROM companies c
JOIN nlp_metrics m USING (company_id)
GROUP BY listing_type;


-- Q6: Companies where AVVR = 0 (purely aspirational language)
-- These are candidates for further manual review
SELECT
    c.company_name,
    c.sector,
    m.avvr,
    m.grs,
    m.grs_tier,
    'Zero action verbs — all language aspirational' AS flag
FROM companies c
JOIN nlp_metrics m USING (company_id)
WHERE m.avvr = 0.0
ORDER BY m.grs DESC;


-- Q7: Readability analysis
-- (Low FRE = harder to read = less investor-accessible)
SELECT
    c.company_name,
    c.sector,
    ROUND(m.flesch_re, 1)  AS flesch_reading_ease,
    ROUND(m.fog_index, 1)  AS gunning_fog,
    CASE
        WHEN m.flesch_re >= 60 THEN 'Readable (Standard)'
        WHEN m.flesch_re >= 30 THEN 'Difficult'
        ELSE 'Very Difficult'
    END AS readability_category
FROM companies c
JOIN nlp_metrics m USING (company_id)
ORDER BY m.flesch_re DESC;


-- Q8: Risk tier breakdown with sector context
SELECT
    m.grs_tier                             AS risk_tier,
    COUNT(*)                               AS n_companies,
    ROUND(100.0 * COUNT(*) / 15, 1)       AS pct_of_corpus,
    GROUP_CONCAT(c.company_name, ' | ')   AS companies
FROM companies c
JOIN nlp_metrics m USING (company_id)
GROUP BY m.grs_tier
ORDER BY
    CASE m.grs_tier WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END;


-- Q9: What would change the risk tier? (sensitivity analysis)
-- How much SR improvement would move each HIGH company to MEDIUM?
-- Breakpoint: GRS <= 60 means SR >= (GRS_current - 60 + 40*SR_current) / 40
SELECT
    c.company_name,
    ROUND(m.grs, 1) AS current_grs,
    m.grs_tier,
    ROUND(m.specificity_ratio, 3) AS current_sr,
    ROUND((m.grs - 60.0) / 40.0 + m.specificity_ratio, 3) AS sr_needed_for_medium,
    ROUND(((m.grs - 60.0) / 40.0 + m.specificity_ratio) - m.specificity_ratio, 3)
        AS sr_improvement_needed
FROM companies c
JOIN nlp_metrics m USING (company_id)
WHERE m.grs_tier = 'HIGH'
ORDER BY m.grs DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- ADVANCED SQL EXTENSION — Window Functions, Pivots, and Analytical Patterns
-- ══════════════════════════════════════════════════════════════════════════════

-- Q10: Running rank of GRS within each sector (window function)
-- Shows which company is 1st / 2nd / 3rd worst in its own sector
SELECT
    c.company_name,
    c.sector,
    ROUND(m.grs, 1)                                   AS grs,
    m.grs_tier,
    RANK() OVER (PARTITION BY c.sector ORDER BY m.grs DESC)
                                                       AS sector_rank,
    COUNT(*) OVER (PARTITION BY c.sector)              AS sector_size
FROM companies c
JOIN nlp_metrics m USING (company_id)
ORDER BY c.sector, sector_rank;


-- Q11: Percentile position of each company in the corpus (window function)
-- Useful for normalised benchmarking in a larger future dataset
SELECT
    c.company_name,
    c.sector,
    ROUND(m.grs, 1)                                   AS grs,
    ROUND(m.specificity_ratio, 3)                     AS sr,
    ROUND(
        100.0 * RANK() OVER (ORDER BY m.grs) / COUNT(*) OVER ()
    , 1)                                              AS grs_percentile,
    ROUND(
        100.0 * RANK() OVER (ORDER BY m.specificity_ratio DESC) / COUNT(*) OVER ()
    , 1)                                              AS sr_percentile
FROM companies c
JOIN nlp_metrics m USING (company_id)
ORDER BY grs_percentile DESC;


-- Q12: Year-over-year BRSR quality trend
-- Groups by fiscal year to see if disclosures improved as SEBI raised standards
SELECT
    m.fiscal_year_group,
    COUNT(*)                              AS n_companies,
    ROUND(AVG(sr.specificity_ratio), 3)  AS avg_sr,
    ROUND(AVG(sr.grs), 1)                AS avg_grs,
    ROUND(AVG(sr.avvr), 3)               AS avg_avvr,
    GROUP_CONCAT(c.company_name, ', ')   AS companies
FROM (
    SELECT company_id,
           CASE
               WHEN fiscal_year = 'FY2022-23' THEN 'FY2022-23 (pre-Core)'
               WHEN fiscal_year = 'FY2023-24' THEN 'FY2023-24 (Core intro)'
               ELSE                                'FY2024-25 (post-Core)'
           END AS fiscal_year_group
    FROM companies
) m
JOIN nlp_metrics sr  USING (company_id)
JOIN companies c     USING (company_id)
GROUP BY m.fiscal_year_group
ORDER BY m.fiscal_year_group;


-- Q13: Composite flag — companies that are HIGH risk on 3+ individual signals
-- A stricter greenwashing flag requiring convergent evidence
WITH signals AS (
    SELECT
        c.company_name,
        c.sector,
        ROUND(m.grs, 1)                               AS grs,
        CASE WHEN m.specificity_ratio  < 0.05  THEN 1 ELSE 0 END AS flag_low_sr,
        CASE WHEN m.avvr               < 0.25  THEN 1 ELSE 0 END AS flag_low_avvr,
        CASE WHEN m.lm_negative        > 0.008 THEN 1 ELSE 0 END AS flag_high_neg,
        CASE WHEN m.boilerplate_density> 0.005 THEN 1 ELSE 0 END AS flag_boilerplate,
        CASE WHEN m.flesch_re          < 20    THEN 1 ELSE 0 END AS flag_unreadable
    FROM companies c
    JOIN nlp_metrics m USING (company_id)
)
SELECT
    company_name,
    sector,
    grs,
    flag_low_sr + flag_low_avvr + flag_high_neg + flag_boilerplate + flag_unreadable
                                                       AS signals_triggered,
    CASE WHEN flag_low_sr      = 1 THEN 'SR<0.05; '      ELSE '' END ||
    CASE WHEN flag_low_avvr    = 1 THEN 'AVVR<0.25; '    ELSE '' END ||
    CASE WHEN flag_high_neg    = 1 THEN 'LM_neg>0.8%; '  ELSE '' END ||
    CASE WHEN flag_boilerplate = 1 THEN 'Boilerplate; '  ELSE '' END ||
    CASE WHEN flag_unreadable  = 1 THEN 'FRE<20; '       ELSE '' END  AS triggered_flags
FROM signals
WHERE flag_low_sr + flag_low_avvr + flag_high_neg + flag_boilerplate + flag_unreadable >= 2
ORDER BY signals_triggered DESC, grs DESC;


-- Q14: Pivot — GRS by sector × assurance type
-- Shows whether the assurance tier within each sector matters
SELECT
    c.sector,
    ROUND(AVG(CASE WHEN c.assurance LIKE '%Reasonable%' THEN m.grs END), 1) AS reasonable_grs,
    ROUND(AVG(CASE WHEN c.assurance NOT LIKE '%Reasonable%' THEN m.grs END), 1) AS other_grs,
    COUNT(CASE WHEN c.assurance LIKE '%Reasonable%' THEN 1 END)              AS n_reasonable,
    COUNT(CASE WHEN c.assurance NOT LIKE '%Reasonable%' THEN 1 END)          AS n_other
FROM companies c
JOIN nlp_metrics m USING (company_id)
GROUP BY c.sector
HAVING COUNT(*) > 0
ORDER BY reasonable_grs DESC NULLS LAST;


-- Q15: Tier transition simulation
-- If every LOW-SR company added 2 quantified sentences per 10 (SR +0.2),
-- how many would move from HIGH to MEDIUM?
WITH simulated AS (
    SELECT
        c.company_name,
        m.grs_tier                         AS current_tier,
        ROUND(m.grs, 1)                    AS current_grs,
        ROUND(m.specificity_ratio, 3)      AS current_sr,
        -- Simulate SR +0.20 improvement; GRS component reduces accordingly
        ROUND(m.grs - (0.20 * 40.0), 1)   AS simulated_grs,
        CASE
            WHEN m.grs - (0.20 * 40.0) < 30 THEN 'LOW'
            WHEN m.grs - (0.20 * 40.0) < 60 THEN 'MEDIUM'
            ELSE 'HIGH'
        END                                AS simulated_tier
    FROM companies c
    JOIN nlp_metrics m USING (company_id)
    WHERE m.grs_tier = 'HIGH'
)
SELECT
    company_name,
    current_grs,
    current_tier,
    simulated_grs,
    simulated_tier,
    CASE WHEN simulated_tier != current_tier
         THEN '✓ Would improve tier' ELSE '✗ Still HIGH' END AS verdict
FROM simulated
ORDER BY current_grs DESC;

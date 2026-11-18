# content_ms_hcuv.py — 43 HCUV title, keywords, highlights, tables and figure captions (numbered-reference edition). Numbers = numbers_hcuv.json; table inputs = 04_분석/HCUV, HCUVI, HCUVO results.
import os, re, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
N = json.load(open(os.path.join(HERE, "numbers_hcuv.json"), encoding="utf-8"))
TITLE = "Medical Aid enrolment rather than physician supply marks the Korean districts with the heaviest health care use"
RUNNING_TITLE = "Medical Aid, supply and district health care use in Korea"
KEYWORDS = "Health care utilization; Small-area variation; Supply-sensitive care; Medical Aid; Spatio-temporal analysis; Korea"
HIGHLIGHTS = [
    "Standardised health care use varied modestly but stably across Korean districts",
    "Almost all variation lay in days per treated resident, not in who was treated",
    "Heavier-use districts had more Medical Aid enrolment, not more physicians",
    "Within districts, beds tracked inpatient days and clinics outpatient visits",
]
def _irr(T):
    d = pd.read_csv(os.path.join(AN, T, "results_std3", "S3_main_IRR.csv")); d["cov"] = d["cov"].str.replace("ext__", ""); return d.set_index("cov")
def _f(r): return f"{r.IRR:.3f} ({r.lo:.3f}-{r.hi:.3f})" + ("\u2020" if bool(r.cred) else "")
VARS = [("Need", "medical_aid1_patients_per_100k", "Medical Aid type 1 beneficiaries per 100,000"), ("Need", "basic_livelihood_rate", "Basic livelihood security recipients, %"),
        ("Need", "older_single_household_share", "Older adults living alone, %"), ("Need", "good_self_rated_health_rate", "Good self-rated health, %"),
        ("Need", "screening_suspected_diabetes_share", "Suspected diabetes at screening, %"), ("Need", "screening_suspected_hypertension_share", "Suspected hypertension at screening, %"),
        ("Supply", "physicians_per_1000", "Physicians per 1,000<sup>\u2021</sup>"), ("Supply", "clinics_per_100k", "Clinics per 100,000"), ("Supply", "beds_per_1000", "Hospital beds per 1,000"),
        ("Supply", "ltc_hospitals_per_100k_65", "Long-term care hospitals per 100,000 aged 65+"),
        ("Physical activity", "walking_practice_rate", "Walking practice, %"), ("Physical activity", "moderate_pa_rate", "Moderate-intensity activity, %"), ("Physical activity", "public_sports_facilities_per_100k", "Public sports facilities per 100,000")]
def table1():
    P = pd.read_csv(os.path.join(AN, "HCUV", "panel_HCUV_std3.csv"), encoding="utf-8-sig")
    W = {"2011-2015": (2011, 2015), "2016-2019": (2016, 2019), "2020-2024": (2020, 2024), "2011-2024": (2011, 2024)}
    rows = [["__H__", "Health care use"]]
    def col(fn): return [fn(P[P.year.between(*w)]) for w in W.values()]
    rows.append(["  District-years, n"] + col(lambda d: f"{len(d):,}"))
    rows.append(["  Visit-days, billion"] + col(lambda d: f"{d.cases.sum()/1e9:.2f}"))
    rows.append(["  Visit-days per resident per year"] + col(lambda d: f"{d.cases.sum()/d.population.sum():.1f}"))
    def sur(d):
        s = d.groupby("fbd_region").apply(lambda g: g.cases.sum() / g.E.sum()); return s
    rows.append(["  District SUR, median (10th-90th percentile)"] + col(lambda d: f"{sur(d).median():.2f} ({sur(d).quantile(.1):.2f}-{sur(d).quantile(.9):.2f})"))
    rows.append(["__H__", "District characteristics, mean (SD)"])
    for grp, c, lab in VARS + [("Adjustment", "pop80_share", "Residents aged 80 years or older, %"), ("Adjustment", "urban_population_share", "Urban population share, %")]:
        rc = [x for x in (f"ext__{c}_raw", f"{c}_raw") if x in P.columns][0]
        mx = P[rc].abs().max(); dp = 0 if mx >= 100 else 1
        rows.append([f"  {re.sub(r'<sup>.*?</sup>', '', lab)}"] + col(lambda d, rc=rc, dp=dp: f"{d[rc].mean():,.{dp}f} ({d[rc].std():,.{dp}f})"))
    foot = ("SD, standard deviation; SUR, standardised use ratio (observed over expected visit-days summed over the period; expected counts from each year's national rates in 18 sex-by-age strata). "
            "Visit-days are inpatient days plus outpatient visit days for all diagnoses among National Health Insurance and Medical Aid beneficiaries, by district of residence. Characteristics are district-year values before standardisation.")
    return ("Table 1. Health care use and district characteristics by period, 229 districts, Korea, 2011-2024", ["Characteristic"] + list(W), rows, foot)
def table2():
    M, MI, MO = _irr("HCUV"), _irr("HCUVI"), _irr("HCUVO")
    MV = pd.read_csv(os.path.join(AN, "HCUV", "results_std3", "S7_multiverse_summary.csv")); MV["cov"] = MV["cov"].str.replace("ext__", ""); MV = MV.set_index("cov")
    rows = []; g0 = None
    for grp, c, lab in VARS:
        if grp != g0: rows.append(["__H__", grp]); g0 = grp
        mv = f"{100*MV.loc[c,'cred_frac']:.0f} / {100*MV.loc[c,'sign_agree']:.0f}" if c in MV.index else "-"
        rows.append([f"  {lab}", _f(M.loc[c]), mv, _f(MI.loc[c]), _f(MO.loc[c])])
    foot = ("Rate ratios (95% credible intervals) per one standard deviation from Bayesian negative binomial models with a BYM2 district effect, a first-order random walk over years and a district-year effect; offset, log expected visit-days. "
            "All models contain the twelve hypothesised exposures, physician density and the urban population share, the sex ratio, fiscal independence and the share aged 80 years or older. "
            f"Multiverse, percentage of the models containing the exposure in which it was credible / had the same sign ({N['mv_n']} distinct models, each exposure included independently with probability one half, plus the fixed adjustments). "
            "Inpatient and outpatient models use the main expected count multiplied by the national component share of each year. <sup>\u2020</sup>95% credible interval excludes 1, judged before rounding to three decimals. <sup>\u2021</sup>Fixed adjustment variable, not part of the multiverse.")
    return ("Table 2. Rate ratios of standardised all visit-days, inpatient days and outpatient visit-days by district characteristic, 229 districts, Korea, 2011-2024",
            ["Characteristic", "All visit-days", "Multiverse, %", "Inpatient days", "Outpatient visit-days"], rows, foot)
TABLES = {1: table1, 2: table2}
FIGCAP = {
 1: "Geography and stability of standardised health care use, 229 districts, Korea, 2011-2024. (A) Standardised use ratio (observed over expected visit-days, expected counts from each year's national rates in 18 sex-by-age strata) summed over 2011-2024; solid outlines mark hot spots and dashed outlines cold spots (Getis-Ord Gi*, 593-edge contact graph, P < 0.05). (B) National visit-days per resident and the inpatient share of visit-days. (C) Global Moran's I of the annual log standardised use ratio and the Spearman rank correlation of each year's ratios with 2011. Map lines delineate study areas and do not necessarily depict accepted national boundaries.",
 2: "Rate ratios per one standard deviation for need, supply and physical activity characteristics. (A) All visit-days. (B) Inpatient days. (C) Outpatient visit-days. Lines show 95% credible intervals; filled markers, credible intervals excluding 1. All models adjust for the urban population share, the sex ratio, fiscal independence and the share aged 80 years or older; physician density is one of the fixed adjustment variables.",
 3: "Between-district and within-district associations and the composition of use in hot and cold spots. (A) Rate ratios per one standard deviation of the district mean (between districts) and of the yearly deviation from it (within districts), from one model containing both terms for the exposures shown and the main-model terms for the others; lines, 95% credible intervals; filled markers, credible intervals excluding 1. (B) Median district share of visit-days used by Medical Aid beneficiaries and median share used outside the district of residence, 2011-2024 means, by Gi* class.",
}

# esm_ms_hcuv.py — 43 HCUV Supporting Information (single anonymised file: Appendix A, Tables S1-S10, Appendix B STROBE). Numbers from result files only; † marks credible intervals.
import os, re, subprocess, json, pandas as pd
import content_ms_hcuv as C
from build_ms_hcuv import TX, TITLE as DTITLE, foot_row
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out_ijhpm"); B = os.path.dirname(MSD); AN = os.path.dirname(B)
RS = lambda v="std3", T="HCUV": os.path.join(AN, T, f"results_{v}")
N = C.N
J = TX(cite="sup")
def TF(title, header, rows, foot="", fs=8):
    J.page_break(); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=True)
    if foot: foot_row(J, foot, 8, 12)
def cl(d): d = d.copy(); d["cov"] = d["cov"].astype(str).str.replace("ext__", ""); return d
def st(r):
    if r is None: return "Not estimated"
    return f"{r['IRR']:.3f} ({r['lo']:.3f}-{r['hi']:.3f})" + ("\u2020" if (bool(r['cred']) if 'cred' in r.index and pd.notna(r['cred']) else (r['lo'] > 1 or r['hi'] < 1)) else "")
LAB = {c: l.replace("<sup>a</sup>", "") for g, c, l in C.VARS}
LAB.update({"urban_population_share": "Urban population share, %", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal independence", "pop80_share": "Residents aged 80 years or older, %"})
J.para("<b>Supporting Information</b>"); J.para(f"Supporting Information for the manuscript entitled \"{DTITLE}\"")
J.para("Contents. Appendix A (additional methods); Table S1 (district characteristics); Table S2 (multiverse analysis); Table S3 (between-district and within-district associations); Table S4 (sensitivity analyses); Table S5 (space-time and spatial structure models); Table S6 (period-specific associations); Table S7 (decomposition and composition of use); Table S8 (region-specific slopes); Table S9 (residual autocorrelation, parsimonious and accessibility models); Table S10 (data checks); Appendix B (STROBE checklist).")
MT = pd.read_csv(os.path.join(B, "panel_META_HCUV_std3.csv"), encoding="utf-8-sig"); MT["variable"] = MT.variable.str.replace("ext__", ""); MT = MT.set_index("variable")
imp = lambda v: int(MT.loc[v, "n_imputed_interp"] + MT.loc[v, "n_imputed_sgg_mean"] + MT.loc[v, "n_imputed_year_mean"])
gate = [f for f in os.listdir(B) if f.startswith("data_gate_HCUV_std3")][0]; nwarn = int(re.search(r"경고 (\d+)건", open(os.path.join(B, gate), encoding="utf-8").read()).group(1))
J.page_break(); J.head("Appendix A. Additional methods", 2)
SM = [("Outcome.", "Visit-days are the National Health Insurance Service count of inpatient days plus outpatient visit days for all diagnoses, for National Health Insurance and Medical Aid beneficiaries, by district of residence, published by sex and ten-year age group (0-9 to 80 years and over). The 2012-2024 data for Sejong are published only at the province level because Sejong is a single-tier city; they were used as the district value. Inpatient and outpatient days came from the residence-based series of the same source, as days of care inside plus outside the district of residence; district-years with a suppressed within-district inpatient count (44 of 3,206) were excluded from the component models rather than set to zero. Visit-days of Medical Aid beneficiaries came from the series by type of insurance."),
      ("Expected counts.", "For each year, national visit-day rates in 2 sexes by 9 age groups were computed from the district sums and applied to district populations in the same strata; expected counts were rescaled so that their national total equalled the observed total in that year. Age-only expected counts used rates in 9 age groups for both sexes combined. The standardised share of residents treated used the number of people treated in the same strata and the same method. Reach and intensity were combined multiplicatively (log SUR = log reach + log intensity), and the between-district variance of the fourteen-year log SUR was split so that each term received its own variance plus the covariance of the two terms, Var(log SUR) = Var(log reach) + Var(log intensity) + 2 Cov."),
      ("Panel checks before modelling.", f"Checks on the analytic panel before any model was fitted found only known artefacts: standardised columns whose yearly means were near zero (a ratio artefact), the post-2020 indicator (constant within years) and covariates with no long-term care hospital or general hospital in some districts. No flag required a change to the data."),
      ("Covariates.", "All covariates came from a harmonised national district-year panel built from public statistics (Table S1). Basic livelihood security recipient rates for 2021-2023 below one-fifth or above five times the 2020-2024 mean of the same district (three district-years) were set to missing and interpolated within the district. Other gaps were filled by within-district linear interpolation, then by district means and then by national year means."),
      ("Models.", "All models were fitted with integrated nested Laplace approximation (R-INLA) using one thread. The BYM2 term used a 593-edge contact graph in which six island districts were linked to their nearest mainland neighbour; penalised complexity priors were P(σ > 0.5) = 0.01 for all standard deviations and P(φ < 0.5) = 2/3 for the BYM2 mixing parameter. Knorr-Held type II-IV interactions used a scaled first-order random walk and a scaled intrinsic conditional autoregressive structure with sum-to-zero constraints. The between-within model replaced each exposure with its fourteen-year district mean and the yearly deviation from that mean; exposures with no between-district variation of interest were kept as in the main model."),
      ("Negative controls and comparison outcomes.", "Negative-control exposures were cardiopulmonary resuscitation awareness, the road paving rate and fires per 10,000 residents, each added in turn to the main model. Comparison outcomes were the numbers of people treated for infectious and parasitic diseases (A00-B99) and for stomach cancer (C16) in the same insurance statistics, fitted with the main model.")]
for h, t in SM: J.para(f"<b>{h}</b> {t}")
SRC = {"medical_aid1_patients_per_100k": "National Health Insurance Service", "basic_livelihood_rate": "KOSIS local statistics", "older_single_household_share": "KOSIS local indicators", "good_self_rated_health_rate": "Community Health Survey",
       "screening_suspected_diabetes_share": "National health screening statistics", "screening_suspected_hypertension_share": "National health screening statistics", "physicians_per_1000": "KOSIS local indicators",
       "clinics_per_100k": "National Health Insurance Service", "beds_per_1000": "KOSIS local indicators", "ltc_hospitals_per_100k_65": "National Health Insurance Service", "walking_practice_rate": "Community Health Survey",
       "moderate_pa_rate": "Community Health Survey", "public_sports_facilities_per_100k": "Public sports facility register", "urban_population_share": "KOSIS local indicators", "sex_ratio": "KOSIS local indicators",
       "fiscal_independence": "KOSIS local indicators", "pop80_share": "Resident registration"}
DIRS = {"medical_aid1_patients_per_100k": "+", "basic_livelihood_rate": "+", "older_single_household_share": "+", "good_self_rated_health_rate": "−", "screening_suspected_diabetes_share": "+", "screening_suspected_hypertension_share": "+",
        "clinics_per_100k": "+", "beds_per_1000": "+", "ltc_hospitals_per_100k_65": "+", "walking_practice_rate": "−", "moderate_pa_rate": "−", "public_sports_facilities_per_100k": "−"}
rows = []; g0 = None
for g, c, l in C.VARS + [("Fixed adjustment", x, LAB[x]) for x in ("urban_population_share", "sex_ratio", "fiscal_independence", "pop80_share")]:
    if c == "physicians_per_1000": g = "Fixed adjustment (read as supply)"
    if g != g0: rows.append(["__H__", g]); g0 = g
    m = MT.loc[c]; rows.append([f"  {LAB[c]}", SRC[c], f"{int(m.obs_year_min)}-{int(m.obs_year_max)}", DIRS.get(c, "Fixed"), f"{imp(c) + (3 if c == 'basic_livelihood_rate' else 0):,}", f"{m.vif_final:.2f}"])
TF("Table S1. Source, observed years, expected direction, filled cells and variance inflation factor of each district characteristic, 229 districts, Korea, 2011-2024", ["Characteristic", "Source", "Years", "Expected direction", "Filled cells", "VIF"], rows,
   "KOSIS, Korean Statistical Information Service; VIF, variance inflation factor in the main model (values above 10 were retained and reported). Filled cells of 3,206 district-years: interpolation within districts, district means or national year means; basic livelihood security recipients include the three implausible 2021-2023 values replaced by interpolation. Community Health Survey rates are age-standardised district estimates.", fs=7.5)
MV = cl(pd.read_csv(os.path.join(RS(), "S7_multiverse_summary.csv"))).set_index("cov")
rows = [[f"  {LAB[c]}", f"{int(MV.loc[c,'n_specs'])}", f"{100*MV.loc[c,'cred_frac']:.0f}", f"{100*MV.loc[c,'sign_agree']:.0f}", f"{MV.loc[c,'IRR_median']:.3f} ({MV.loc[c,'IRR_min']:.3f}-{MV.loc[c,'IRR_max']:.3f})", "Yes" if MV.loc[c, "robust"] else "No"] for g, c, l in C.VARS if c in MV.index]
TF("Table S2. Multiverse analysis of the twelve hypothesised characteristics, 200 models, Korea, 2011-2024", ["Characteristic", "Models containing it", "Credible, %", "Same sign, %", "Median rate ratio (range)", "Stable"], rows,
   "Each of the 200 distinct models included each of the twelve hypothesised characteristics independently with probability one half (six on average) and always the five fixed adjustment variables. Stable, credible in at least 75% and same sign in at least 95% of the models containing the characteristic.")
BW = cl(pd.read_csv(os.path.join(RS(), "S41_part_bw_twoway.csv"))).set_index("cov")
rows = []
for g, c, l in C.VARS:
    if f"{c}__between" in BW.index: rows.append([f"  {LAB[c]}", st(BW.loc[f"{c}__between"]), st(BW.loc[f"{c}__within"])])
TF("Table S3. Between-district and within-district rate ratios per 1 standard deviation, Korea, 2011-2024", ["Characteristic", "Between districts", "Within districts"], rows,
   "Between, the district's fourteen-year mean; within, its yearly deviation from that mean, both standardised and entered in one model with the other main-model terms. Rate ratios (95% credible intervals); \u2020interval excludes 1 (judged before rounding, so a limit printed as 1.000 can still exclude 1). Characteristics without a split were kept as single terms (not shown).")
KEY = ["medical_aid1_patients_per_100k", "clinics_per_100k", "beds_per_1000", "older_single_household_share", "walking_practice_rate", "public_sports_facilities_per_100k"]
def part(f):
    p = os.path.join(RS(), f)
    return cl(pd.read_csv(p)).set_index("cov") if os.path.exists(p) else None
def mainv(v):
    p = os.path.join(RS(v), "S3_main_IRR.csv"); return cl(pd.read_csv(p)).set_index("cov") if os.path.exists(p) else None
ALT = [("Main model", mainv("std3")), ("Queen contiguity graph (577 edges)", mainv("s577")), ("Without the 80-and-over adjustment", mainv("s2")), ("Age-only expected counts", mainv("sage")),
       ("Poisson with district-year effects", part("S41_part_C1_poisson_lognormal.csv")), ("Second-order random walk over years", part("S41_part_C2_rw2_year.csv")), ("First-order autoregressive year effect", part("S41_part_C3_ar1_year.csv")),
       ("Province-by-year effects", part("S41_part_C4_sido_year_iid.csv")), ("Spatial+ adjustment", part("S41_part_D1_spatial_plus.csv")), ("Covariates lagged 1 year", part("S41_part_E1_lag1.csv")),
       ("Covariates lagged 2 years", part("S41_part_E2_lag2.csv")), ("Survey covariates as 3-year moving averages", part("S41_part_G1_kchs_ma3.csv")), ("Even years only", part("S41_part_H4_even_years.csv")), ("Odd years only", part("S41_part_H4_odd_years.csv")),
       ("Comparison outcome, infectious disease care", part("S41_part_H1_nco_INFECT.csv")), ("Comparison outcome, stomach cancer care", part("S41_part_H1_nco_GCA.csv"))]
rows = [[lab] + [(st(d.loc[c]) if (d is not None and c in d.index) else "Not estimated") for c in KEY] for lab, d in ALT]
SHORT = {"medical_aid1_patients_per_100k": "Medical Aid type 1", "clinics_per_100k": "Clinics", "beds_per_1000": "Hospital beds", "older_single_household_share": "Older adults alone", "walking_practice_rate": "Walking", "public_sports_facilities_per_100k": "Public sports facilities"}
_S4F = ("Rate ratios (95% credible intervals); \u2020interval excludes 1 (judged before rounding, so a limit printed as 1.000 can still exclude 1). Comparison outcomes are refits of the main model to people treated for infectious and parasitic diseases (A00-B99) and for stomach cancer (C16) in the same insurance statistics; associations that are specific to total use are not expected to appear there.")
for _k, (_t, _cols) in enumerate([("Table S4. Sensitivity analyses for selected characteristics, rate ratios per 1 standard deviation, Korea, 2011-2024 (Medical Aid, clinics, hospital beds)", range(0, 3)),
                                  ("Table S4 (continued). Sensitivity analyses for selected characteristics, rate ratios per 1 standard deviation, Korea, 2011-2024 (older adults living alone, walking, public sports facilities)", range(3, 6))]):
    TF(_t, ["Analysis"] + [SHORT[KEY[i]] for i in _cols], [[r[0]] + [r[1 + i] for i in _cols] for r in rows], _S4F if _k == 1 else "Continued on the next page.", fs=8)
KH = []
KEY5 = KEY[:3] + ["older_single_household_share", "walking_practice_rate", "public_sports_facilities_per_100k", "screening_suspected_hypertension_share"]
for t, lab in (("main_queen", "Main model"), ("KH_typeII", "Knorr-Held type II"), ("KH_typeIII", "Knorr-Held type III"), ("KH_typeIV", "Knorr-Held type IV"), ("no_spatial", "No district effect (year effects only)"), ("iid_only", "Unstructured district effect only"), ("icar_besag", "Besag (ICAR) district effect"),
               ("knn4", "4-nearest-neighbour graph"), ("pc_phi_flat", "Flatter mixing prior"), ("pc_relaxA", "Relaxed precision prior A"), ("pc_relaxB", "Relaxed precision prior B")):
    d = part(f"S43_part_{t}.csv")
    if d is None: continue
    w = d.WAIC.dropna().iloc[0] if "WAIC" in d.columns and d.WAIC.notna().any() else float("nan")
    KH.append([lab, f"{w:,.1f}"] + [(st(d.loc[c]) if c in d.index else "-") for c in KEY5])
TF("Table S5. Space-time interaction and spatial structure models, Korea, 2011-2024 (Medical Aid, clinics, hospital beds)", ["Model", "WAIC", "Medical Aid type 1", "Clinics", "Hospital beds"], [r[:5] for r in KH], "Continued on the next page.", fs=8)
TF("Table S5 (continued). Space-time interaction and spatial structure models, Korea, 2011-2024 (older adults living alone, walking, public sports facilities, suspected hypertension)", ["Model", "Older adults alone", "Walking", "Public sports facilities", "Suspected hypertension"], [[r[0]] + r[5:] for r in KH],
   "WAIC, widely applicable information criterion (lower is better). Rate ratios per 1 standard deviation (95% credible intervals); \u2020interval excludes 1 (judged before rounding, so a limit printed as 1.000 can still exclude 1). All models contain the main-model covariates.", fs=8)
W = cl(pd.read_csv(os.path.join(RS(), "S4_window_IRR.csv")))
rows = []
for g, c, l in C.VARS:
    r = [f"  {LAB[c]}"]
    for wn in ("W1_2011-15", "W2_2016-19", "W3_2020-24"):
        x = W[(W["cov"] == c) & (W.window == wn)]; r.append(st(x.iloc[0]) if len(x) else "-")
    rows.append(r)
TF("Table S6. Rate ratios per 1 standard deviation by period, Korea, 2011-2024", ["Characteristic", "2011-2015", "2016-2019", "2020-2024"], rows, "Main model refitted separately in each period. Rate ratios (95% credible intervals); \u2020interval excludes 1 (judged before rounding, so a limit printed as 1.000 can still exclude 1).")
rows = [["Share of between-district variance of the log SUR", "", ""], ["  Reach (standardised share of residents treated)", f"{N['reach_share']}%", f"{N['reach_p10']}-{N['reach_p90']}"], ["  Intensity (visit-days per treated resident)", f"{N['intensity_share']}%", f"{N['int_p10']}-{N['int_p90']}"],
        ["__H__", "Median district share of visit-days, 2011-2024 mean"], ["  Medical Aid beneficiaries: hot / other / cold spots", f"{N['medaid_hot']}% / {N['medaid_other']}% / {N['medaid_cold']}%", ""], ["  Used outside the district of residence: hot / other / cold spots", f"{N['outside_hot']}% / {N['outside_other']}% / {N['outside_cold']}%", ""],
        ["__H__", "Negative-control exposures (rate ratio per 1 SD)"], ["  Cardiopulmonary resuscitation awareness", N["nc_cpr"], ""], ["  Road paving rate", N["nc_road"], ""], ["  Fires per 10,000 residents", N["nc_fire"], ""]]
TF("Table S7. Decomposition of district variation, composition of use by hot-spot class and negative controls, Korea, 2011-2024", ["Quantity", "Value", "10th-90th percentile"], rows,
   f"SUR, standardised use ratio. Hot and cold spots, Getis-Ord Gi* classes of the fourteen-year SUR ({N['n_hot']} hot, {N['n_cold']} cold, {229 - N['n_hot'] - N['n_cold']} other districts). The covariance term of the decomposition is split equally between reach and intensity.")
CK = [("Title and abstract", "1", "Title; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, last paragraph"), ("Study design", "4", "Methods, study design"), ("Setting", "5", "Methods, study design"),
      ("Participants", "6", "Methods (all residents of 229 districts)"), ("Variables", "7", "Methods; Table S1"), ("Data sources/measurement", "8", "Methods; Appendix A"), ("Bias", "9", "Methods, statistical analysis; Discussion, limitations"),
      ("Study size", "10", "Results"), ("Quantitative variables", "11", "Methods"), ("Statistical methods", "12", "Methods; Appendix A"), ("Participants (results)", "13", "Results; Table 1"),
      ("Descriptive data", "14", "Table 1"), ("Outcome data", "15", "Results; Figure 1"), ("Main results", "16", "Results; Table 2; Figures 2-3"), ("Other analyses", "17", "Results; Tables S2-S10"),
      ("Key results", "18", "Discussion, first paragraph"), ("Limitations", "19", "Discussion, limitations"), ("Interpretation", "20", "Discussion"), ("Generalisability", "21", "Discussion; Conclusions"), ("Funding", "22", "Title page")]
# 심사 선제 산출물(런북 15 '8호부터'): S8 권역 기울기, S9 사양별 점검, S10 자료 점검
RG = cl(pd.read_csv(os.path.join(RS(), "S50_region_slopes.csv"))); RG["c"] = RG.covariate.str.replace("ext__", "")
REG = [("Capital", "Capital region"), ("Chungcheong", "Chungcheong"), ("Honam", "Honam (south-west)"), ("Yeongnam", "Yeongnam (south-east)"), ("Gangwon_Jeju", "Gangwon and Jeju")]
rows = []
for c in ["medical_aid1_patients_per_100k", "clinics_per_100k", "beds_per_1000", "older_single_household_share", "screening_suspected_hypertension_share", "walking_practice_rate", "public_sports_facilities_per_100k"]:
    g = RG[RG.c == c].set_index("region"); rows.append(["__H__", f"{LAB[c]} (WAIC change {g.dWAIC_vs_common.iloc[0]:+.1f})"])
    for r, l in REG: rows.append([f"  {l}", st(g.loc[r]), f"{int(g.loc[r, 'n_district_years']):,}"])
_h = [k for k, r in enumerate(rows) if r[0] == "__H__"][4]
TF("Table S8. Region-specific rate ratios per 1 standard deviation for the stable characteristics, Korea, 2011-2024", ["Characteristic and region", "Rate ratio (95% CrI)", "District-years"], rows[:_h], "Continued on the next page.", fs=8)
TF("Table S8 (continued). Region-specific rate ratios per 1 standard deviation for the stable characteristics, Korea, 2011-2024", ["Characteristic and region", "Rate ratio (95% CrI)", "District-years"], rows[_h:], "Each row is one model in which the characteristic has a separate slope in each of five regions and the other main-model terms keep common slopes. WAIC change, WAIC of the region-specific model minus WAIC of the main model (positive values mean the region-specific slopes did not improve fit). Rate ratios (95% credible intervals); \u2020interval excludes 1.", fs=8)
PM = pd.read_csv(os.path.join(RS(), "S50_resid_moran_by_spec.csv")).set_index("spec")
SPL = {"principal": "Main model", "forced_only": "Fixed adjustments only", "parsimonious": "Parsimonious (stable exposures and fixed adjustments)", "typeI_interaction": "Knorr-Held type I", "no_spatial": "No district effect", "iid_district": "Unstructured district effect only", "icar_district": "Besag (ICAR) district effect only"}
rows = [[SPL[k], f"{int(PM.loc[k,'n_cov'])}", f"{PM.loc[k,'WAIC']:,.1f}", f"{PM.loc[k,'resid_moran_I']:.3f}", f"{PM.loc[k,'p_perm']:.3f}"] for k in SPL if k in PM.index]
PS = cl(pd.read_csv(os.path.join(RS(), "S50_parsimonious.csv"))).set_index("cov"); AC = cl(pd.read_csv(os.path.join(RS(), "S50_access_sensitivity.csv"))).set_index("cov")
rows += [["__H__", "Rate ratios in the parsimonious and accessibility models"]]
for c in ["medical_aid1_patients_per_100k", "clinics_per_100k", "beds_per_1000"]:
    rows.append([f"  {LAB[c]}", "", st(PS.loc[c]), st(AC.loc[c]), ""])
rows.append(["  Share of visit-days used outside the district", "", "-", st(AC.loc["outside_care_share"]), ""])
TF("Table S9. Residual spatial autocorrelation by model specification, parsimonious model and accessibility sensitivity analysis, Korea, 2011-2024", ["Specification", "Covariates", "WAIC / parsimonious", "Moran's I / accessibility", "P"], rows,
   "Upper rows, Moran's I of district mean residuals with a permutation P value. Lower rows, rate ratios per 1 standard deviation (95% credible intervals) in the parsimonious model and in the main model with the share of visit-days used outside the district of residence added as an accessibility proxy; \u2020interval excludes 1.", fs=7.5)
rows = [["Year with the same value in every district (indicator variables)", "Post-2020 period indicator", "Structural by design; not used as an exposure"],
        ["Ratio-type variable above 100", "Sex ratio (men per 100 women)", "Expected for this unit; kept"],
        ["Year means of standardised columns differing more than twofold", "Most covariates", "Ratios of near-zero means after standardisation; raw-scale trends checked (for example, the share aged 80 or older rose from 3.1% to 7.2%)"],
        ["District with zero in every year", "Long-term care hospitals (16 districts), general hospitals (76 districts)", "True absence of facilities; kept as zero"],
        ["Rate below one-fifth or above five times the district's 2020-2024 mean", "Basic livelihood security recipients, 2021-2023", "3 district-years set to missing and interpolated"],
        ["Population block repeated from the previous year", "Changwon, 2023", "Replaced with the official 2023 figure (1,009,038)"],
        ["Outcome published only at the province level", "Sejong, 2012-2024 (2011 published as a district row)", "Province-level row used as the district value"],
        ["Suppressed component count", "Within-district inpatient days", "44 of 3,206 district-years excluded from the component models only"],
        ["Missing covariate value", "See Table S1", "Within-district interpolation, district mean, then national year mean"]]
J.page_break(); J.para("<b>Table S10. Data checks before modelling: rule, affected variables and handling</b>")
for _r in rows: J.para(f"<b>{_r[0]}.</b> {_r[1]}. {_r[2]}.")
J.para("Checks were run automatically on the analytic panel before any model was fitted.")
J.page_break()
J.table_fit("Appendix B. STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [list(x) for x in CK], "", fs_max=8, title_bold=True)
foot_row(J, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology.", 8, 12)
p = os.path.join(OUT, "Supporting_Information_HCUV.docx"); J.doc_title = ""; J.save(p)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_hcuv_ms", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)
print("ESM saved", p)

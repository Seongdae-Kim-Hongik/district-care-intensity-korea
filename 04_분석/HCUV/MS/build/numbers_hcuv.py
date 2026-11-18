# numbers_hcuv.py — 43호 HCUV 원고 수치(2026-11-13). 입력 = 04_분석/HCUV·HCUVI·HCUVO 결과, 02_패널/HCUV_Estd2.csv·HCUV_comp.csv. 산출 = numbers_hcuv.json(문자열·수치), gi_hcuv.csv
import os, json, unicodedata, numpy as np, pandas as pd
from scipy.stats import spearmanr, norm
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", "..", "..")); ROOT = os.path.dirname(AN); PAN = os.path.join(ROOT, "02_패널")
NFC = lambda s: unicodedata.normalize("NFC", str(s)); R = lambda T, v="std3": os.path.join(AN, T, f"results_{v}")
def h(x, d=3):   # half-up
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(str(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP))
N = {}
P = pd.read_csv(os.path.join(PAN, "HCUV_comp.csv"), encoding="utf-8-sig"); P["fbd_region"] = P.fbd_region.map(NFC)
N["rows"] = f"{len(P):,}"; N["districts"] = P.fbd_region.nunique()
N["visits_total_bn"] = h(P.cases.sum() / 1e9, 1)
pc = P.groupby("year").cases.sum() / P.groupby("year").population_E.sum(); N["pc2011"] = h(pc[2011], 1); N["pc2019"] = h(pc[2019], 1); N["pc2020"] = h(pc[2020], 1); N["pc2024"] = h(pc[2024], 1)
inp = P.groupby("year").inp.sum() / P.groupby("year")[["inp", "outp"]].sum().sum(1); N["inp_share2011"] = h(100 * inp[2011], 1); N["inp_share2020"] = h(100 * inp[2020], 1); N["inp_share2024"] = h(100 * inp[2024], 1)
# 기준 SQLite 대조(99R_next5c_hcu_E 출력 재현)
Z = P.dropna(subset=["tot_ref"]); rr = Z.cases / Z.tot_ref; N["ref_cells"] = f"{len(Z):,}"; N["ref_ratio"] = h(rr.median(), 3)
_H = pd.read_csv(os.path.join(PAN, "HCUV_Estd2.csv"), encoding="utf-8-sig"); _tot = _H.groupby("year").cases.transform("sum")   # 99H_hcuv_build.py와 같은 계산
N["rho80_crude"] = h(spearmanr(_H.cases / (_H.population_E * _tot / _H.groupby("year").population_E.transform("sum")), _H.pop80_share_raw).correlation, 2); N["rho80_std"] = h(spearmanr(_H.cases / _H.E_std, _H.pop80_share_raw).correlation, 2)
L = P.groupby("fbd_region").apply(lambda g: g.cases.sum() / g.E_std.sum()); N["sur_p10"] = h(L.quantile(.1), 2); N["sur_p90"] = h(L.quantile(.9), 2); N["p90p10"] = h(L.quantile(.9) / L.quantile(.1), 2)
N["sur_min"] = h(L.min(), 2); N["sur_max"] = h(L.max(), 2)
# 해마다 순위 지속(Kendall W)
Y = P.pivot_table(index="fbd_region", columns="year", values="SIR").dropna(); rk = Y.rank(); m, n = Y.shape[1], Y.shape[0]
S = ((rk.sum(1) - rk.sum(1).mean()) ** 2).sum(); N["kendall_w"] = h(12 * S / (m ** 2 * (n ** 3 - n)), 2)
yr = pd.Series({y: spearmanr(Y[2011], Y[y]).correlation for y in Y.columns}); N["rho_2011_2024"] = h(yr[2024], 2)
mo = pd.read_csv(os.path.join(R("HCUV"), "S6_moran_year.csv")); N["moran_min"] = h(mo.moran_I.min(), 2); N["moran_max"] = h(mo.moran_I.max(), 2)
rm = pd.read_csv(os.path.join(R("HCUV"), "S8_residual_moran.csv")).set_index("quantity"); N["moran_pooled"] = h(rm.loc["observed_logSIR_pooled", "moran_I"], 2); N["resid_moran"] = h(rm.loc["pearson_residual_area_mean", "moran_I"], 2); N["resid_moran_p"] = h(rm.loc["pearson_residual_area_mean", "p_perm"], 2)
# Gi*(593 그래프, 이진 가중, 자기 포함) — 14년 log SUR
G = open(os.path.join(AN, "HCUV", "graph_593.graph")).read().split("\n"); nreg = int(G[0]); nb = {}
for line in G[1:]:
    t = line.split()
    if len(t) >= 2: nb[int(t[0])] = [int(x) for x in t[2:]]
import geopandas as gpd
SHP = os.environ.get("HCUV_SHP", "final.shp")  # district boundary file (not included)
area = pd.DataFrame({"fbd_region": gpd.read_file(SHP)["region"].values}); area["area_id"] = np.arange(1, len(area) + 1); assert len(area) == nreg
area["fbd_region"] = area.fbd_region.map(NFC); id2r = dict(zip(area.area_id, area.fbd_region))
x = np.log(L.reindex([id2r[i] for i in range(1, nreg + 1)]).values); xb, s = x.mean(), x.std(); gi = []
for i in range(1, nreg + 1):
    w = np.zeros(nreg); w[i - 1] = 1; w[[j - 1 for j in nb.get(i, [])]] = 1; W = w.sum()
    num = (w * x).sum() - xb * W; den = s * np.sqrt((nreg * (w ** 2).sum() - W ** 2) / (nreg - 1)); gi.append(num / den)
GI = pd.DataFrame({"fbd_region": [id2r[i] for i in range(1, nreg + 1)], "SUR": np.exp(x), "z": gi}); GI["p"] = 2 * norm.sf(GI.z.abs())
GI["cls"] = np.where((GI.p < 0.05) & (GI.z > 0), "hot", np.where((GI.p < 0.05) & (GI.z < 0), "cold", "other")); GI.to_csv(os.path.join(HERE, "gi_hcuv.csv"), index=False, encoding="utf-8-sig")
N["n_hot"] = int((GI.cls == "hot").sum()); N["n_cold"] = int((GI.cls == "cold").sum())
SIDO = {"서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi", "강원": "Gangwon", "충청북": "North Chungcheong", "충청남": "South Chungcheong", "전라북": "North Jeolla", "전라남": "South Jeolla", "경상북": "North Gyeongsang", "경상남": "South Gyeongsang", "제주": "Jeju"}
def sido(r): return next(v for k, v in SIDO.items() if r.startswith(k))
GI["sido"] = GI.fbd_region.map(sido)
for c in ("hot", "cold"):
    vc = GI[GI.cls == c].sido.value_counts(); N[f"{c}_sido"] = "; ".join(f"{k} {v}" for k, v in vc.items())
    N[f"{c}_gun"] = int(GI[GI.cls == c].fbd_region.str.endswith("군").sum()); N[f"{c}_gu"] = int(GI[GI.cls == c].fbd_region.str.endswith("구").sum())
    N[f"{c}_sur_med"] = h(GI[GI.cls == c].SUR.median(), 2)
# B2·B3: 의료급여·관외 비중(14년 평균)
B = P.groupby("fbd_region")[["medaid_share", "outside_share"]].mean().join(GI.set_index("fbd_region").cls)
for c in ("hot", "cold", "other"):
    N[f"medaid_{c}"] = h(100 * B[B.cls == c].medaid_share.median(), 1); N[f"outside_{c}"] = h(100 * B[B.cls == c].outside_share.median(), 1)
# B4 분해
Lg = P.groupby("fbd_region")[["SIR", "SIR_pt", "SIR_int"]].mean().apply(np.log); v = Lg.var(); cv = Lg.SIR_pt.cov(Lg.SIR_int)
N["reach_share"] = h(100 * (v.SIR_pt + cv) / v.SIR, 0); N["intensity_share"] = h(100 * (v.SIR_int + cv) / v.SIR, 0)
N["reach_p10"] = h(np.exp(Lg.SIR_pt.quantile(.1)), 2); N["reach_p90"] = h(np.exp(Lg.SIR_pt.quantile(.9)), 2); N["int_p10"] = h(np.exp(Lg.SIR_int.quantile(.1)), 2); N["int_p90"] = h(np.exp(Lg.SIR_int.quantile(.9)), 2)
# 모형
def irr(T, f="S3_main_IRR.csv", v="std3"):
    d = pd.read_csv(os.path.join(R(T, v), f)); d["cov"] = d["cov"].str.replace("ext__", ""); return d.set_index("cov")
def rr(d, c): r = d.loc[c]; return f"{h(r.IRR)} (95% CrI {h(r.lo)}-{h(r.hi)})"
M = irr("HCUV"); MI = irr("HCUVI"); MO = irr("HCUVO")
for k, c in [("aid", "medical_aid1_patients_per_100k"), ("liv", "basic_livelihood_rate"), ("alone", "older_single_household_share"), ("srh", "good_self_rated_health_rate"), ("dm", "screening_suspected_diabetes_share"), ("htn", "screening_suspected_hypertension_share"),
             ("clin", "clinics_per_100k"), ("beds", "beds_per_1000"), ("ltc", "ltc_hospitals_per_100k_65"), ("walk", "walking_practice_rate"), ("mpa", "moderate_pa_rate"), ("fac", "public_sports_facilities_per_100k"), ("phys", "physicians_per_1000"), ("p80", "pop80_share"), ("urb", "urban_population_share")]:
    N[f"rr_{k}"] = rr(M, c); N[f"rri_{k}"] = rr(MI, c); N[f"rro_{k}"] = rr(MO, c)
MV = pd.read_csv(os.path.join(R("HCUV"), "S7_multiverse_summary.csv")); MV["cov"] = MV["cov"].str.replace("ext__", ""); MV = MV.set_index("cov")
N["mv_robust"] = int(MV.robust.sum()); N["mv_n"] = int(MV.n_specs_total.iloc[0])
for k, c in [("aid", "medical_aid1_patients_per_100k"), ("clin", "clinics_per_100k"), ("beds", "beds_per_1000"), ("walk", "walking_practice_rate"), ("fac", "public_sports_facilities_per_100k"), ("alone", "older_single_household_share"), ("liv", "basic_livelihood_rate"), ("ltc", "ltc_hospitals_per_100k_65"), ("htn", "screening_suspected_hypertension_share")]:
    N[f"mv_{k}"] = f"{100 * MV.loc[c, 'cred_frac']:.0f}%"; N[f"mvs_{k}"] = f"{100 * MV.loc[c, 'sign_agree']:.0f}%"   # 표 2·S2와 같은 반올림
BW = pd.read_csv(os.path.join(R("HCUV"), "S41_part_bw_twoway.csv")); BW["cov"] = BW["cov"].str.replace("ext__", ""); BW = BW.set_index("cov")
for k, c in [("aid", "medical_aid1_patients_per_100k"), ("clin", "clinics_per_100k"), ("beds", "beds_per_1000"), ("walk", "walking_practice_rate"), ("fac", "public_sports_facilities_per_100k"), ("alone", "older_single_household_share"), ("htn", "screening_suspected_hypertension_share")]:
    for s_, lab in (("between", "b"), ("within", "w")): N[f"bw{lab}_{k}"] = rr(BW, f"{c}__{s_}")
W = pd.read_csv(os.path.join(R("HCUV"), "S4_window_IRR.csv")); W["cov"] = W["cov"].str.replace("ext__", "")
for k, c in [("aid", "medical_aid1_patients_per_100k"), ("clin", "clinics_per_100k"), ("beds", "beds_per_1000"), ("phys", "physicians_per_1000"), ("liv", "basic_livelihood_rate")]:
    for wn, lab in (("W1_2011-15", "1"), ("W2_2016-19", "2"), ("W3_2020-24", "3")):
        r_ = W[(W["cov"] == c) & (W.window == wn)].iloc[0]; N[f"w{lab}_{k}"] = f"{h(r_.IRR)} ({h(r_.lo)}-{h(r_.hi)})"
NC = pd.read_csv(os.path.join(R("HCUV"), "S3_negcontrol.csv")); NC["cov"] = NC["cov"].str.replace("ext__", ""); NC = NC.set_index("cov")
N["nc_cpr"] = rr(NC, "cpr_awareness_rate"); N["nc_road"] = rr(NC, "road_pavement_rate"); N["nc_fire"] = rr(NC, "fires_per_10000")
hy = pd.read_csv(os.path.join(R("HCUV"), "S3_main_hyper.csv")); N["phi"] = h(hy.iloc[2, 1], 2); N["phi_lo"] = h(hy.iloc[2, 2], 2); N["phi_hi"] = h(hy.iloc[2, 3], 2)
VP = pd.read_csv(os.path.join(R("HCUV"), "S42_variance_partition.csv")).set_index("component"); N["vp_spatial"] = h(100 * VP.loc["spatial_structured", "share_of_linear_predictor_var"], 0); N["vp_hyp"] = h(100 * VP.loc["fixed_hypothesis", "share_of_linear_predictor_var"], 0)
LK = pd.read_csv(os.path.join(R("HCUV"), "S1_likelihood.csv")); N["lik_note"] = LK.to_dict("records")
# 민감도 3개(s577·s2·sage) + KH
for v in ("s577", "s2", "sage"):
    f = os.path.join(R("HCUV", v), "S3_main_IRR.csv")
    if os.path.exists(f):
        d = irr("HCUV", v=v)
        for k, c in [("aid", "medical_aid1_patients_per_100k"), ("clin", "clinics_per_100k"), ("beds", "beds_per_1000"), ("walk", "walking_practice_rate"), ("alone", "older_single_household_share")]: N[f"{v}_{k}"] = rr(d, c)
for t in ("KH_typeII", "KH_typeIII", "KH_typeIV"):
    f = os.path.join(R("HCUV"), f"S43_part_{t}.csv")
    if os.path.exists(f):
        d = pd.read_csv(f); d["cov"] = d["cov"].astype(str).str.replace("ext__", ""); d = d.set_index("cov")
        for k, c in [("aid", "medical_aid1_patients_per_100k"), ("clin", "clinics_per_100k"), ("beds", "beds_per_1000"), ("walk", "walking_practice_rate"), ("fac", "public_sports_facilities_per_100k"), ("alone", "older_single_household_share")]:
            if c in d.index: N[f"{t}_{k}"] = rr(d, c)
        if "WAIC" in d.columns: N[f"{t}_waic"] = h(d.WAIC.dropna().iloc[0], 1)
N["waic_main"] = h(pd.read_csv(os.path.join(R("HCUV"), "S3_main_fit.csv")).filter(like="WAIC").iloc[0, 0], 1) if "WAIC" in "".join(pd.read_csv(os.path.join(R("HCUV"), "S3_main_fit.csv")).columns) else ""
# 3자 검토 반영(2026-11-13): 시 수, KH 범위, 지역 효과 없는 모형
for c in ("hot", "cold"): N[f"{c}_si"] = int((GI.cls == c).sum()) - N[f"{c}_gun"] - N[f"{c}_gu"]
for k, c in [("aid", "medical_aid1_patients_per_100k"), ("clin", "clinics_per_100k"), ("beds", "beds_per_1000")]:
    v = []
    for t in ("KH_typeII", "KH_typeIII", "KH_typeIV"):
        d = pd.read_csv(os.path.join(R("HCUV"), f"S43_part_{t}.csv")); d["cov"] = d["cov"].astype(str).str.replace("ext__", ""); v.append(d.set_index("cov").loc[c, "IRR"])
    N[f"kh_{k}_rng"] = f"{h(min(v))}-{h(max(v))}"
_ns = pd.read_csv(os.path.join(R("HCUV"), "S43_part_no_spatial.csv")); _ns["cov"] = _ns["cov"].astype(str).str.replace("ext__", ""); N["ns_aid"] = rr(_ns.set_index("cov"), "medical_aid1_patients_per_100k")
# 심사 선제 산출물(런북 15 '8호부터'·17 §6): 권역 기울기·간결 모형·접근성 민감도·사양별 잔차 Moran·다중성
_rs = pd.read_csv(os.path.join(R("HCUV"), "S50_region_slopes.csv")); _rs["c"] = _rs.covariate.str.replace("ext__", "")
for _r in _rs.itertuples(): N[f"reg_{_r.c}_{_r.region}"] = f"{h(_r.IRR)} (95% CrI {h(_r.lo)}-{h(_r.hi)})"
N["reg_dwaic_aid"] = h(_rs[_rs.c == "medical_aid1_patients_per_100k"].dWAIC_vs_common.iloc[0], 1)
_pm = pd.read_csv(os.path.join(R("HCUV"), "S50_resid_moran_by_spec.csv")).set_index("spec")
N["rm_nospatial"] = h(_pm.loc["no_spatial", "resid_moran_I"], 2); N["rm_bym_max"] = h(_pm.loc[["principal", "forced_only", "parsimonious", "typeI_interaction"], "resid_moran_I"].abs().max(), 2)
_ac = pd.read_csv(os.path.join(R("HCUV"), "S50_access_sensitivity.csv")); _ac["cov"] = _ac["cov"].str.replace("ext__", ""); _ac = _ac.set_index("cov")
N["acc_aid"] = rr(_ac, "medical_aid1_patients_per_100k"); N["acc_clin"] = rr(_ac, "clinics_per_100k"); N["acc_beds"] = rr(_ac, "beds_per_1000"); N["acc_out"] = rr(_ac, "outside_care_share")
N["n_hyp"] = 12; N["chance_n"] = h(12 * 0.05, 1)
json.dump(N, open(os.path.join(HERE, "numbers_hcuv.json"), "w"), ensure_ascii=False, indent=1, default=str)
print({k: v for k, v in N.items() if k != "lik_note"})

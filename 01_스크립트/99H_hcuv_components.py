#!/usr/bin/env python3
# 99H_hcuv_components — HCUV 사전 고정 보조 분석 B1~B4 입력(2026-11-13, 00_HCUV_사전고정_보조분석_261113.md).
#  B1 입원·외래 결과·E(주 E_std × 그 해 전국 구성 비중, ΣE=Σ관측), B2 의료급여 비중, B3 관외 비중, B4 진료 경험률 E(TX_35003 진료실인원 성×연령)
#  산출: 02_패널/HCUV_comp.csv
import os, sqlite3, unicodedata, numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널")
DB = os.environ.get("ST_SQLITE", "02_체육건강_시공간_GPT버전.sqlite")   # reference SQLite of public statistics
c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cols = {"nhis__관내입원__입내원일수": "ia", "nhis__관외입원__입내원일수": "ib", "nhis__관내외래__입내원일수": "oa", "nhis__관외외래__입내원일수": "ob",
        "nhis__의료급여1종__입내원일수": "m1", "nhis__의료급여2종__입내원일수": "m2", "nhis__전체__입내원일수": "tot_ref"}
R = pd.read_sql("select year, fbd_region, " + ", ".join(f'"{k}"' for k in cols) + " from region_year where year between 2011 and 2024", c).rename(columns=cols); R["fbd_region"] = R.fbd_region.map(NFC)
H = pd.read_csv(os.path.join(PAN, "HCUV_Estd2.csv"), encoding="utf-8-sig"); H["fbd_region"] = H.fbd_region.map(NFC)
P = H.merge(R, on=["year", "fbd_region"], how="left", validate="one_to_one")
P["inp"] = P.ia + P.ib; P["outp"] = P.oa + P.ob     # 관내입원 결측이면 inp 결측(0 채움 안 함)
ok = P.inp.notna() & P.outp.notna(); print("[99Hc] 구성 결과 사용 행", int(ok.sum()), "/", len(P), "제외:", P.loc[~ok, ["year", "fbd_region"]].values.tolist()[:12])
for comp in ["inp", "outp"]:
    sh = P[ok].groupby("year")[comp].sum() / P[ok].groupby("year")[["inp", "outp"]].sum().sum(1)
    e = P.E_std * P.year.map(sh); e[~ok] = np.nan
    P[f"E_{comp}"] = e * P.year.map(P[ok].groupby("year")[comp].sum()) / e.groupby(P.year).transform("sum")
    P[f"{comp}_days"] = P[comp].where(ok).round()
    print(f"[99Hc] {comp} 전국 비중:", sh.round(3).to_dict())
P["medaid_share"] = (P.m1 + P.m2) / P.tot_ref; P["outside_share"] = (P.ib + P.ob) / P.tot_ref
# B4: 진료실인원(TX_35003 pt_) 성×연령 간접 표준화
Hc = pd.read_csv(os.path.join(PAN, "hcuv_counts_fix_261113.csv"), encoding="utf-8-sig"); Hc["fbd_region"] = Hc.fbd_region.map(NFC)
src = open(os.path.join(HERE, "99R_next5b_build_E.py"), encoding="utf-8").read(); cut = src.index("\n", src.index("POP = pd.DataFrame(rows)"))
g = {"__file__": os.path.join(HERE, "99R_next5b_build_E.py"), "__name__": "x"}; exec(compile(src[:cut], "5b_pop", "exec"), g); POP, base = g["POP"].copy(), g["base"]
A10 = ["a0", "a10", "a20", "a30", "a40", "a50", "a60", "a70", "a80"]
for i, a in enumerate(A10[:-1]): lo = 10 * i; POP[a] = POP[f"{lo}-{lo+4}"] + POP[f"{lo+5}-{lo+9}"]
POP["a80"] = POP["80-84"] + POP["85+"]
Q = base.merge(Hc, on=["year", "fbd_region"], how="inner", validate="one_to_one").reset_index(drop=True); yrs = Q.year.values; E = np.zeros(len(Q)); Q["pt"] = 0.0
for sx, s in [("m", "남자"), ("f", "여자")]:
    X = Q[["year", "key"]].merge(POP[POP.sex == s], on=["year", "key"], how="left", validate="one_to_one")
    num = Q[[f"pt_{sx}_{a}" for a in A10]].values.astype(float); pop = X[A10].values.astype(float)
    rate = pd.DataFrame(num, columns=A10).groupby(yrs).sum() / pd.DataFrame(pop, columns=A10).groupby(yrs).sum()
    E += (pop * rate.loc[yrs].values).sum(1); Q["pt"] += num.sum(1)
Q["E_pt"] = E * Q.year.map(Q.groupby("year").pt.sum()) / pd.Series(E).groupby(yrs).transform("sum").values
P = P.merge(Q[["year", "fbd_region", "pt", "E_pt"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
P["SIR"] = P.cases / P.E_std; P["SIR_pt"] = P.pt / P.E_pt; P["SIR_int"] = P.SIR / P.SIR_pt   # 범위(진료 경험) × 강도(1인당 일수)
L = P.groupby("fbd_region")[["SIR", "SIR_pt", "SIR_int"]].mean().apply(np.log)
v = L.var(); cv = L.SIR_pt.cov(L.SIR_int)
print(f"[99Hc] B4 지역 간 로그 SIR 분산 {v.SIR:.5f} = 범위 {v.SIR_pt:.5f} + 강도 {v.SIR_int:.5f} + 2cov {2*cv:.5f} → 범위 몫 {(v.SIR_pt+cv)/v.SIR:.2f}, 강도 몫 {(v.SIR_int+cv)/v.SIR:.2f}")
print(f"[99Hc] SIR_pt P10 {np.exp(L.SIR_pt.quantile(.1)):.3f} P90 {np.exp(L.SIR_pt.quantile(.9)):.3f}; SIR_int P10 {np.exp(L.SIR_int.quantile(.1)):.3f} P90 {np.exp(L.SIR_int.quantile(.9)):.3f}")
P.to_csv(os.path.join(PAN, "HCUV_comp.csv"), index=False, encoding="utf-8-sig")

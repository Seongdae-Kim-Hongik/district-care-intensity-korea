#!/usr/bin/env python3
# 99H_hcu_counts —  원 주석: 건강보험 전체 진료 시군구×성×10세 연령 입내원일수·진료실인원(2026-11-13). 원천 KOSIS TX_35003 연령별 진료현황(4개 권역 × 남·여, 2006-2024, 로컬 00_원천/B_NHIS_진료).
#  시도 = 분류 코드 앞 10자리 → 50.load_source(일반구 합산, 코드표 결합) → 시군구 마스터키. 산출: 02_패널/hcuv_counts_fix_261113.csv
import os, unicodedata, importlib.util, numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널"); SRC = os.path.join(ROOT, "00_원천", "B_NHIS_진료")
FILES = {"남자": ["A036", "A065", "A094", "A123"], "여자": ["A037", "A066", "A095", "A124"]}
SIDO = {"서울", "인천", "경기", "강원", "대전", "세종", "충북", "충남", "부산", "대구", "울산", "경북", "경남", "광주", "전북", "전남", "제주"}
AGE = {"0~9세": "a0", "10~19세": "a10", "20~29세": "a20", "30~39세": "a30", "40~49세": "a40", "50~59세": "a50", "60~69세": "a60", "70~79세": "a70", "80세 이상": "a80"}
IT = {"입내원일수": "vd", "진료실인원수": "pt"}
fr = []
for sx, fs in FILES.items():
    for f in fs:
        d = pd.read_csv(os.path.join(SRC, f"TX_35003_{f}.csv"), encoding="utf-8-sig", dtype=str); d = d[d.PRD_DE != "PRD_DE"]
        d["C1_NM"] = d.C1_NM.map(NFC).str.strip()
        # 시도 = 분류 코드 앞 10자리(11101HJG + 시도 2자리)의 머리행 이름(행 순서에 기대지 않음)
        d["C1"] = d.C1.str.replace(r"^1110HJG", "11101HJG", regex=True)  # 원표 코드 오타(앞 1 누락) 정정
        hd = d[d.C1.str.len() == 10].drop_duplicates("C1").set_index("C1").C1_NM; d["_sido"] = d.C1.str[:10].map(hd).fillna(d.C1.map({"A01": "경기", "BB38": "충남"}))  # 원표 예외 코드 2개(여주시 2013~, 당진군 2006)
        assert d._sido.notna().all() and set(hd) <= SIDO, d[d._sido.isna()].C1.unique()
        sj = (d.C1.str.len() == 10) & (d.C1_NM == "세종"); d.loc[sj, "C1_NM"] = "세종시"   # 세종: 시도 = 시군구(머리행만 존재)
        d = d[((d.C1.str.len() != 10) | sj) & d.C2_NM.isin(AGE) & d.ITM_NM.isin(IT)].copy()
        d["v"] = d.ITM_NM.map(IT) + "_" + ("m" if sx == "남자" else "f") + "_" + d.C2_NM.map(AGE)
        d["DT"] = pd.to_numeric(d.DT.str.replace(",", ""), errors="coerce")
        fr.append(d[["PRD_DE", "_sido", "C1_NM", "v", "DT"]])
L = pd.concat(fr); L = L[L.PRD_DE.astype(int).between(2011, 2024)]
W = L.pivot_table(index=["PRD_DE", "_sido", "C1_NM"], columns="v", values="DT", aggfunc="sum").reset_index().rename(columns={"PRD_DE": "year", "_sido": "sido", "C1_NM": "sigungu"})
tmpf = "_tmp_hcuv_fix_wide.csv"; W.to_csv(os.path.join(PAN, tmpf), index=False, encoding="utf-8-sig")
spec = importlib.util.spec_from_file_location("m50", os.path.join(HERE, "50_build_master_panel.py")); m50 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m50)
mk = pd.read_csv(os.path.join(PAN, "시군구_마스터키.csv"), dtype=str); mk = mk[mk.fbd_sido.notna()].drop_duplicates("key")
log = dict(missing_files=[], level_filter={}, unmatched=[], special=[], overlap=[], sources={})
src = dict(name="hcu5c", prefix="", files=[tmpf], sido="sido", sgg="sigungu", merge_counts=True, level=None, ratio=lambda c: False, label="건보 연령별 진료현황")
agg, meta = m50.load_source(src, set(mk.key), log); os.remove(os.path.join(PAN, tmpf))
um = pd.concat(log["unmatched"]) if log["unmatched"] else pd.DataFrame(); print("[hcu5c] 미결합 시군구:", um[["_sido", "_sgg", "years"]].values.tolist() if len(um) else "없음")
agg = agg.merge(mk[["key", "fbd_region"]], on="key", how="left"); agg["fbd_region"] = agg.fbd_region.map(NFC); agg["year"] = agg.year.astype(int)
V = sorted(c for c in agg.columns if c[:3] in ("vd_", "pt_"))
O = agg[["year", "fbd_region"] + V]; print("[hcu5c] 연도별 시군구:", O.groupby("year").fbd_region.nunique().to_dict()); print("[hcu5c] 결측 칸:", int(O[V].isna().sum().sum()))
O.to_csv(os.path.join(PAN, "hcuv_counts_fix_261113.csv"), index=False, encoding="utf-8-sig")

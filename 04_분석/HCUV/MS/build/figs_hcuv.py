# -*- coding: utf-8 -*-
# figs_hcuv.py — HCUV manuscript figures. Colour, panel letters uppercase at one size, north arrow, no in-figure captions.
#  Fig 1 (A) 14년 SUR 지도 + Gi* (B) 전국 1인당 입내원일수·입원 비중 (C) 연도별 Moran's I · Fig 2 (A-C) 전체·입원·외래 주모형 RR · Fig 3 (A) 지역 간·지역 내 RR (B) 핫·콜드·기타 의료급여·관외 비중
import os, json, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Polygon, Rectangle
from PIL import Image
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", "..", "..")); PAN = os.path.join(os.path.dirname(AN), "02_패널")
FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
SHP = os.environ.get("HCUV_SHP", "final.shp")  # district boundary file (not included)
MM = 1 / 25.4; W = 174 * MM; DPI = 600; LW = 0.3
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "legend.fontsize": 7.5, "legend.title_fontsize": 8, "axes.linewidth": 0.5, "pdf.fonttype": 42})
G = gpd.read_file(SHP); G["region"] = G.region.map(NFC); G["cd"] = G.sigungu_cd.astype(str); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
PANEL_LABEL_PT = 52
def letter(ax, ch, dx=0.0, dy=0.008):
    bb = ax.get_position(); ax.figure.text(bb.x0 + dx, bb.y1 + dy, ch, fontsize=PANEL_LABEL_PT, fontweight="bold", va="bottom", ha="left")
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#404040", linewidth=0.45); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0
    bx, by, bh = x0 + 0.55 * W_, y0 + 0.04 * H_, 0.010 * H_
    ax.add_patch(Rectangle((bx, by), 50000, bh, facecolor="black", edgecolor="black", lw=0.5)); ax.add_patch(Rectangle((bx + 50000, by), 50000, bh, facecolor="white", edgecolor="black", lw=0.5))
    for k, t in ((0, "0"), (50000, "50"), (100000, "100")): ax.text(bx + k, by + bh + 0.008 * H_, t, ha="center", va="bottom", fontsize=6)
    ax.text(bx + 100000 + 0.012 * W_, by + bh / 2, "km", ha="left", va="center", fontsize=6)
    nx, ny, nw, nh = x0 + 0.93 * W_, y0 + 0.40 * H_, 0.054 * W_, 0.21 * H_
    ax.add_patch(Polygon([[nx - nw / 2, ny], [nx, ny + nh], [nx + nw / 2, ny], [nx, ny + 0.25 * nh]], closed=True, facecolor="black", edgecolor="black", lw=0.4))
    ax.text(nx, ny + nh + 0.012 * H_, "N", ha="center", va="bottom", fontsize=24, fontweight="bold")
def save(fig, k, dpi=DPI):
    p = os.path.join(FIG, f"Fig{k}.png"); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(dpi, dpi)); im.save(os.path.join(OUTF, f"Figure{k}.tif"), dpi=(dpi, dpi), compression="tiff_lzw"); return im.size

P = pd.read_csv(os.path.join(PAN, "HCUV_comp.csv"), encoding="utf-8-sig"); P["fbd_region"] = P.fbd_region.map(NFC)
GI = pd.read_csv(os.path.join(HERE, "gi_hcuv.csv"), encoding="utf-8-sig"); GI["fbd_region"] = GI.fbd_region.map(NFC); GI = GI.set_index("fbd_region")
yrs = list(range(2011, 2025))
# Fig 1
gg = G.copy(); assert set(gg.region) == set(GI.index); gg["SUR"] = gg.region.map(GI.SUR); gg["cls"] = gg.region.map(GI.cls)
BR = [0, 0.85, 0.90, 0.95, 1.05, 1.10, 1.15, 9]; LB = ["<0.85", "0.85-0.89", "0.90-0.94", "0.95-1.04", "1.05-1.09", "1.10-1.14", "≥1.15"]
PAL = ["#2166AC", "#67A9CF", "#D1E5F0", "#F7F7F7", "#FDDBC7", "#EF8A62", "#B2182B"]
fig = plt.figure(figsize=(W, 4.8)); am = fig.add_axes([0.0, 0.15, 0.45, 0.68]); a1 = fig.add_axes([0.57, 0.57, 0.33, 0.25]); a2 = fig.add_axes([0.57, 0.09, 0.33, 0.25])
gg.plot(ax=am, column="SUR", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#a0a0a0", linewidth=LW); mapax(am)
gg[gg.cls == "hot"].boundary.plot(ax=am, color="black", linewidth=0.7); gg[gg.cls == "cold"].boundary.plot(ax=am, color="#2171B5", linewidth=0.6, linestyle=(0, (2.0, 1.2)))
h = [Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL, LB)] + [Patch(facecolor="none", edgecolor="black", linewidth=0.8, label="Hot spot"), Patch(facecolor="none", edgecolor="#2171B5", linewidth=0.8, linestyle="--", label="Cold spot")]
fig.legend(handles=h, title="Standardised use ratio, 2011-2024", loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=3, frameon=False, columnspacing=0.8, handlelength=1.3, fontsize=7)
letter(am, "A", dx=0.01)
pc = P.groupby("year").cases.sum() / P.groupby("year").population_E.sum(); ip = 100 * P.groupby("year").inp.sum() / P.groupby("year")[["inp", "outp"]].sum().sum(1)
a1.plot(yrs, pc.loc[yrs], color="#404040", marker="o", ms=2.5, lw=0.9); assert 15 < pc.min() and pc.max() < 26; a1.set_ylim(15, 26); a1.set_ylabel("Visit-days per resident")
b1 = a1.twinx(); b1.plot(yrs, ip.loc[yrs], color="#B2182B", marker="s", ms=2.5, lw=0.9); assert 10 < ip.min() and ip.max() < 18; b1.set_ylim(10, 18); b1.set_ylabel("Inpatient share, %", color="#B2182B"); b1.tick_params(axis="y", colors="#B2182B")
a1.set_xticks([2011, 2014, 2017, 2020, 2024]); a1.spines[["top"]].set_visible(False); b1.spines[["top"]].set_visible(False); letter(a1, "B", dx=-0.09, dy=0.0)
mo = pd.read_csv(os.path.join(AN, "HCUV", "results_std3", "S6_moran_year.csv"))
Y = P.pivot_table(index="fbd_region", columns="year", values="SIR").dropna(); from scipy.stats import spearmanr
rk = [spearmanr(Y[2011], Y[y]).correlation for y in yrs]
a2.plot(mo.year, mo.moran_I, color="#2166AC", marker="o", ms=2.5, lw=0.9, label="Moran's I"); a2.plot(yrs, rk, color="#7B3294", marker="^", ms=2.5, lw=0.9, label="Rank correlation with 2011")
a2.set_ylim(0, 1.05); a2.set_xticks([2011, 2014, 2017, 2020, 2024]); a2.set_xlabel("Year"); a2.spines[["top", "right"]].set_visible(False); a2.legend(frameon=False, loc="lower left", fontsize=7, ncol=1); letter(a2, "C", dx=-0.09, dy=0.0)
s1 = save(fig, 1)

# Fig 2 — 주모형 RR(전체·입원·외래)
VARS = [("Need", "medical_aid1_patients_per_100k", "Medical Aid type 1"), ("Need", "basic_livelihood_rate", "Basic livelihood recipients"), ("Need", "older_single_household_share", "Older adults living alone"),
        ("Need", "good_self_rated_health_rate", "Good self-rated health"), ("Need", "screening_suspected_diabetes_share", "Suspected diabetes"), ("Need", "screening_suspected_hypertension_share", "Suspected hypertension"),
        ("Supply", "physicians_per_1000", "Physicians"), ("Supply", "clinics_per_100k", "Clinics"), ("Supply", "beds_per_1000", "Hospital beds"), ("Supply", "ltc_hospitals_per_100k_65", "Long-term care hospitals"),
        ("Activity", "walking_practice_rate", "Walking"), ("Activity", "moderate_pa_rate", "Moderate activity"), ("Activity", "public_sports_facilities_per_100k", "Public sports facilities")]
COL = {"Need": "#B2182B", "Supply": "#2166AC", "Activity": "#1B7837"}
def irr(T):
    d = pd.read_csv(os.path.join(AN, T, "results_std3", "S3_main_IRR.csv")); d["cov"] = d["cov"].str.replace("ext__", ""); return d.set_index("cov")
fig = plt.figure(figsize=(W, 5.0)); axs = [fig.add_axes([0.205 + i * 0.27, 0.15, 0.235, 0.66]) for i in range(3)]
for i, (T, lim) in enumerate((("HCUV", (0.94, 1.10)), ("HCUVI", (0.94, 1.10)), ("HCUVO", (0.94, 1.10)))):
    d = irr(T); a = axs[i]; yy = np.arange(len(VARS))[::-1]
    for y, (grp, c, lab) in zip(yy, VARS):
        r = d.loc[c]; assert lim[0] < r.lo and r.hi < lim[1], (T, c, r.lo, r.hi)
        a.plot([r.lo, r.hi], [y, y], color=COL[grp], lw=1.2); a.plot(r.IRR, y, "o", color=COL[grp], ms=3.5, mfc=COL[grp] if bool(r.cred) else "white")
    a.axvline(1, color="#808080", lw=0.5, ls=":"); a.set_xlim(*lim); a.set_ylim(-0.7, len(VARS) - 0.3); a.set_xlabel("Rate ratio per 1 SD"); a.spines[["top", "right"]].set_visible(False)
    a.set_yticks(yy); a.set_yticklabels([v[2] for v in VARS] if i == 0 else [], fontsize=7)
    a.set_title(("All visit-days", "Inpatient days", "Outpatient visit-days")[i], fontsize=8); letter(a, "ABC"[i], dx=-0.035 if i else -0.19, dy=0.04)
fig.legend(handles=[Patch(color=COL[k], label=k if k != "Activity" else "Physical activity") for k in COL], loc="lower left", bbox_to_anchor=(0.0, 0.0), ncol=1, frameon=False, fontsize=7)
s2 = save(fig, 2)

# Fig 3 — 지역 간·지역 내 + 핫·콜드 비중
BW = pd.read_csv(os.path.join(AN, "HCUV", "results_std3", "S41_part_bw_twoway.csv")); BW["cov"] = BW["cov"].str.replace("ext__", ""); BW = BW.set_index("cov")
V3 = [("medical_aid1_patients_per_100k", "Medical Aid type 1", "Need"), ("older_single_household_share", "Older adults living alone", "Need"), ("clinics_per_100k", "Clinics", "Supply"), ("beds_per_1000", "Hospital beds", "Supply"),
      ("walking_practice_rate", "Walking", "Activity"), ("public_sports_facilities_per_100k", "Public sports facilities", "Activity")]
fig = plt.figure(figsize=(W, 4.2)); a0 = fig.add_axes([0.21, 0.13, 0.33, 0.58]); a1 = fig.add_axes([0.68, 0.13, 0.29, 0.58])
yy = np.arange(len(V3))[::-1]
for y, (c, lab, grp) in zip(yy, V3):
    for off, part, mk in ((0.17, "between", "s"), (-0.17, "within", "o")):
        r = BW.loc[f"{c}__{part}"]; assert 0.90 < r.lo and r.hi < 1.10
        a0.plot([r.lo, r.hi], [y + off, y + off], color=COL[grp], lw=1.2); a0.plot(r.IRR, y + off, mk, color=COL[grp], ms=3.5, mfc=COL[grp] if bool(r.cred) else "white")
a0.axvline(1, color="#808080", lw=0.5, ls=":"); a0.set_xlim(0.92, 1.08); a0.set_yticks(yy); a0.set_yticklabels([v[1] for v in V3], fontsize=7); a0.set_xlabel("Rate ratio per 1 SD"); a0.spines[["top", "right"]].set_visible(False)
from matplotlib.lines import Line2D
a0.legend(handles=[Line2D([], [], marker="s", color="#404040", ls="", label="Between districts"), Line2D([], [], marker="o", color="#404040", ls="", label="Within districts")], frameon=False, loc="upper left", bbox_to_anchor=(0.0, 1.22), ncol=2, fontsize=7)
letter(a0, "A", dx=-0.19, dy=0.06)
B = P.groupby("fbd_region")[["medaid_share", "outside_share"]].mean().join(GI.cls)
grp = ["hot", "other", "cold"]; lab = ["Hot spots", "Other", "Cold spots"]; cc = ["#B2182B", "#BDBDBD", "#2166AC"]; x = np.arange(2)
for j, g in enumerate(grp):
    v = [100 * B[B.cls == g].medaid_share.median(), 100 * B[B.cls == g].outside_share.median()]
    a1.bar(x + (j - 1) * 0.26, v, width=0.24, color=cc[j], label=lab[j])
a1.set_xticks(x); a1.set_xticklabels(["Medical Aid share", "Outside-district share"], fontsize=7); a1.set_ylabel("Share of visit-days, % (median)"); a1.set_ylim(0, 60); a1.spines[["top", "right"]].set_visible(False)
a1.legend(frameon=False, loc="upper left", ncol=1, fontsize=7); letter(a1, "B", dx=-0.09, dy=0.06)
s3 = save(fig, 3)
for k, s in zip((1, 2, 3), (s1, s2, s3)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/DPI*25.4:.0f} x {s[1]/DPI*25.4:.0f} mm")

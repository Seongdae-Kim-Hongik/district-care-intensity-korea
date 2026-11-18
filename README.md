# Medical Aid, physician supply and standardised health care use across Korean districts, 2011-2024

Analysis code for the manuscript

> Kim S. *Medical Aid enrolment rather than physician supply marks the Korean districts with the heaviest health care use.* Submitted for publication.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24332111 (v1.0.0).

The code is openly available under the MIT License.

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected counts, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/HCUV/`, `04_분석/HCUVI/`, `04_분석/HCUVO/` | Exposures with expected directions, fixed adjustment variables, negative controls, comparison outcomes and model settings for all visit-days, inpatient days and outpatient visit-days, and the sensitivity versions (shared-border graph, without the share aged 80 or older, age-only expected counts) |
| `04_분석/HCUV/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material (the manuscript text source is not included) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Inpatient days, outpatient visit-days and treated persons by district of residence, sex and 10-year age group, all diagnoses, National Health Insurance and Medical Aid beneficiaries: National Health Insurance Service regional medical care statistics (KOSIS TX_35003), 2011-2024. Sejong appears in the source as a single province-level row and is kept as one district (`99H_hcu_counts.py`).
- Within-district use, Medical Aid use and use outside the district of residence: National Health Insurance Service regional statistics (`99H_hcuv_components.py`).
- Population by sex and age: Ministry of the Interior and Safety, resident registration statistics. The 2023 age block of Changwon duplicated the 2022 block and was corrected.
- District characteristics: the Community Health Survey, national health screening statistics, the national public sports facility register, National Health Insurance Service facility and workforce statistics, Medical Aid statistics and Korean Statistical Information Service local indicators. Basic livelihood rates for 2021-2023 that had collapsed or were inflated (33 district-years) were set to missing and interpolated within district.

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1 | `99H_hcu_counts.py` | District visit-days and treated persons by sex and age |
| 2 | `99H_hcuv_build.py` (population block from `99R_next5b_build_E.py`) | Expected visit-days (indirect standardisation, 18 sex-by-age strata) and covariate pool |
| 3 | `99H_hcuv_components.py` | Inpatient and outpatient components, Medical Aid share, share used outside the district, reach and intensity |
| 4 | `80_build_disease_panel_v.py`, `04_분석/HCUV/run_std3_chain.sh` (81-89) | Bayesian models, 200 exposure subsets, Knorr-Held II-IV, between/within decomposition, sensitivity analyses |
| 5 | `04_분석/HCUV/MS/build/run_all_ms_hcuv.sh` | Manuscript numbers, tables, figures and supplementary material |

R/INLA jobs are wrapped by `rslot.sh` to limit concurrent processes; INLA runs single-threaded. Newer INLA versions may shift WAIC by a few points without changing any rate ratio.

## License

MIT (see `LICENSE`).

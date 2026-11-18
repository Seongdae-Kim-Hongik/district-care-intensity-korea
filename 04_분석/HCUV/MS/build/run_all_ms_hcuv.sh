#!/bin/bash
# run_all_ms_hcuv.sh — 43 HCUV manuscript package build: references (network only if cache missing), main document, title page, highlights, Supporting Information, cover letter, sanitising and checks.
#  Figures: figs_hcuv.py (unchanged; output copied to out_ijhpm/Figures). Code DOI read from out_ijhpm/zenodo_doi.txt.
set -e; cd "$(dirname "$0")"
[ -f refs_ms_hcuv.json ] || python3 build_refs_ms_hcuv.py
python3 build_ms_hcuv.py 2>&1 | grep -v -e Warning -e groupby || true
python3 esm_ms_hcuv.py 2>&1 | grep -v -e Warning -e groupby || true
python3 cover_letter_hcuv.py 2>&1 | grep -v -e Warning -e groupby || true
O=../out_ijhpm
python3 sanitize_docx.py $O/Manuscript_HCUV.docx $O/Supporting_Information_HCUV.docx $O/Highlights_HCUV.docx $O/Cover_Letter_HCUV.docx $O/Title_Page_HCUV.docx
for f in Manuscript_HCUV Supporting_Information_HCUV Title_Page_HCUV; do /opt/homebrew/bin/soffice --headless -env:UserInstallation=file:///tmp/lo_hcuv_ms --convert-to pdf --outdir $O $O/$f.docx >/dev/null 2>&1; done   # PDFs from the sanitised (anonymous-metadata) files
python3 check_ms_hcuv.py   # set CITATION_ORDER_CHECKER to the path of check_citation_order.py 2>&1 | grep -v -e Warning -e groupby

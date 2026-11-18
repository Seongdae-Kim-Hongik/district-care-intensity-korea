# cover_letter_hcuv.py — 43 HCUV cover letter (one page, sole author, impersonal voice, signed). Theme stated; ethics approval numbers and code DOI included.
#  Numbers = numbers_hcuv.json; word counts = out_ijhpm/wordcount_ms.txt. Signature image = out_ijhpm/signature_kim.png (not part of the code repository).
import os, re, sys, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out_ijhpm")
sys.path.insert(0, HERE)
import content_ms_hcuv as C
from build_ms_hcuv import ZENODO, ADDRESS, EMAIL, PHONE, ORCID
JOURNAL = "The International Journal of Health Planning and Management"
THEME = "Theme 1, Health financing and economics"
N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_ms.txt")).read().split())
_d = datetime.date.today()
cl = [f"{_d.day} {_d:%B} {_d.year}", "The Editors", JOURNAL, "",
      "Dear Editors,",
      f"Please find enclosed the manuscript entitled \"{C.TITLE}\" by Seongdae Kim, for consideration as a Research Article in {JOURNAL} under {THEME}.",
      f"Korea combines a single-payer insurance scheme, fee-for-service payment of mostly private providers and one of the highest levels of health care use in the OECD. Using National Health Insurance statistics on {N['visits_total_bn']} billion inpatient days and outpatient visit-days for all {N['districts']} districts of South Korea, 2011-2024, standardised for sex and age, the study shows that use differed modestly but persistently between districts (90th to 10th percentile ratio {N['p90p10']}; Kendall's W {N['kendall_w']}) and that almost all of the difference lay in days per treated resident rather than in the share of residents treated.",
      "In Bayesian space-time models, enrolment in Medical Aid, the near-free public programme for the poorest residents, was linked to where use is high, whereas physician density was not. Clinic and bed density were linked instead to change in use within districts relative to national trends, with beds tracking inpatient days and clinics outpatient visits. The distinction between where use is high and where it rises bears directly on cost sharing in public coverage, on the regional planning of beds and clinics, and on the financing of fee-for-service systems, which is why the manuscript is submitted under the health financing and economics theme.",
      "The study used only published aggregate statistics; the Institutional Review Board of Hongik University approved it (7002340-202511-HR-012) and its continuing review (7002340-202611-HR-040). The manuscript is original, has not been published and is not under consideration elsewhere.",
      f"The main text contains {int(W['main_words']):,} words, with an abstract of {int(W['abstract_words'])} words, four highlights, two tables, three figures and {W['refs']} references. Supporting Information, including the STROBE checklist, is provided. The analysis code is openly available on Zenodo (https://doi.org/{ZENODO}).",
      "Thank you for considering this manuscript.", "", "Yours sincerely,", "__SIG__",
      "Seongdae Kim, Ph.D. (corresponding author)", ADDRESS, f"Telephone: {PHONE}. E-mail: {EMAIL}. ORCID: {ORCID}"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
gap = False
for t in cl:
    if t == "": gap = True; continue
    if t == "__SIG__": d.add_paragraph().add_run().add_picture(os.path.join(OUT, "signature_kim.png"), width=Cm(3.2)); continue
    p = d.add_paragraph(t)
    if gap: p.paragraph_format.space_before = Pt(10); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_Letter_HCUV.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_hcuv_cl", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert "PENDING" not in txt or "zenodo.PENDING" in ZENODO, "DOI"
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and re.search(r"7002340-202611-?\s*HR-040", txt), "style or IRB"
assert not re.search(r"(?i)overlap|previously submitted|resubmi|reject|Chun\b|Byung|github|funding|competing", txt), "forbidden content"
pages = subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0]
assert pages == "1", pages; print("cover pages", pages)

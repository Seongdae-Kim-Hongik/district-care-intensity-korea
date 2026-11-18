# check_ms_hcuv.py — 43 HCUV pre-submission checks (numbered-reference edition). FAIL 0 = PASS.
#  Limits: main text <=7,000 words, abstract <=250 without citations, 4 highlights <=80 characters, keywords <=7, references <=50 in first-cite order,
#  no repository links in references, anonymised main document and Supporting Information, three-line tables, † for credible intervals, no version traces.
import os, re, subprocess, zipfile, glob
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
import content_ms_hcuv as C
from build_ms_hcuv import read_draft, TITLE, RUNNING, ORCID, KEYS, KEYWORDS, AI_STATEMENT, FUNDING, IRB, ZENODO, STATEMENTS_ANON
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out_ijhpm")
PB = os.environ.get("CITATION_ORDER_CHECKER", os.path.join(HERE, "check_citation_order.py"))   # external first-cite order checker
N = C.N; R = []
def ok(c, m): R.append(("ok  " if c else "FAIL") + " " + m)
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_ms.txt")).read().split())
D = read_draft(); ab = " ".join(D["Abstract"])
MSF, SUPF, CLF, TPF, HLF = "Manuscript_HCUV.docx", "Supporting_Information_HCUV.docx", "Cover_Letter_HCUV.docx", "Title_Page_HCUV.docx", "Highlights_HCUV.docx"
FIGD = os.path.join(OUT, "Figures")
for f in (MSF, SUPF, CLF, TPF, HLF, MSF.replace(".docx", ".pdf"), SUPF.replace(".docx", ".pdf"), CLF.replace(".docx", ".pdf")): ok(os.path.exists(os.path.join(OUT, f)), f"file {f}")
# 1. journal limits
ok(int(W["main_words"]) <= 7000, f"main text {W['main_words']} words <= 7,000")
ok(int(W["abstract_words"]) <= 250, f"abstract {W['abstract_words']} words <= 250")
ok(not re.search(r"\[@", ab) and len(D["Abstract"]) == 1, "abstract one paragraph, no citations")
KW = [k.strip() for k in KEYWORDS.split(";")]; ok(1 <= len(KW) <= 7, f"keywords {len(KW)} <= 7")
ok(len(C.HIGHLIGHTS) == 4 and all(len(h) <= 80 for h in C.HIGHLIGHTS), f"highlights 4 x <=80 chars {[len(h) for h in C.HIGHLIGHTS]}")
ok(len(RUNNING) < 70, f"running title {len(RUNNING)} < 70 chars")
ok(":" not in TITLE and "229" not in TITLE and "standardi" not in TITLE.lower() and not re.search(r"\b[A-Z]{2,}\b", TITLE), "title: no colon, no series template, no abbreviation")
ok(int(W["refs"]) == len(KEYS) <= 50, f"references {len(KEYS)} <= 50")
for t in (N["sur_p10"], N["sur_p90"], N["kendall_w"]): ok(str(t) in ab, f"abstract number {t} = results")
# 2. citation order (playbook checker)
co = subprocess.run(["python3", PB, os.path.join(OUT, MSF)], capture_output=True, text=True).stdout if os.path.exists(PB) else ""
ok("결과: PASS" in co, "citation order checker PASS " + (co.strip().split("\n")[-1] if co.strip() else ""))
# 3. anonymity
for f in (MSF, SUPF):
    info = subprocess.run(["pdfinfo", os.path.join(OUT, f.replace(".docx", ".pdf"))], capture_output=True, text=True).stdout
    ok(not re.search(r"Author:\s+\S", info), f"{f[:-5]}.pdf author metadata empty")
d = Document(os.path.join(OUT, MSF)); _ps = [p.text.strip() for p in d.paragraphs]; _dx = "\n".join(_ps) + "\n" + "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
sd = Document(os.path.join(OUT, SUPF)); supt = "\n".join(p.text for p in sd.paragraphs) + "\n" + "\n".join(c.text for t in sd.tables for r in t.rows for c in r.cells)
for nm, tx in (("main document", _dx), ("Supporting Information", supt)):
    hit = [t for t in ("Seongdae", "Kim S", "Hongik", "kimsd", ORCID, "7002340", "zenodo", "github", "Biohealth Convergence", "Acknowledg") if t.lower() in tx.lower()]
    ok(not hit, f"{nm} anonymised (no author, institution, IRB number, repository, acknowledgements) {hit}")
for f in (MSF, SUPF, HLF):
    cp = zipfile.ZipFile(os.path.join(OUT, f)).read("docProps/core.xml").decode()
    ok("Seongdae" not in cp and "Kim" not in cp and "Claude" not in cp and "python-docx" not in cp.lower(), f"{f} metadata anonymous, no tool traces")
_tp = "\n".join(p.text for p in Document(os.path.join(OUT, TPF)).paragraphs)
for t in ("Seongdae Kim", "kimsd@hongik.ac.kr", ORCID, "Hongik University", "7002340-202511-HR-012", "7002340-202611-HR-040", RUNNING, TITLE, ZENODO, "Acknowledgements"):
    ok(t in _tp, f"title page has '{t[:50]}'")
ok("Korea University" not in _tp and "Chun" not in _tp and "github" not in _tp.lower(), "title page: Hongik only, no GitHub")
ok("PENDING" not in ZENODO, f"Zenodo DOI filled ({ZENODO})")
# 4. structure
_ord = ["Highlights", "Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusions"] + [h for h, _ in STATEMENTS_ANON] + ["References", "Figure legends"]
pos = [_ps.index(k) if k in _ps else -1 for k in _ord]; ok(all(p >= 0 for p in pos) and pos == sorted(pos), f"section order {pos}")
iT1 = next(i for i, p in enumerate(_ps) if p.startswith("Table 1.")); iT2 = next(i for i, p in enumerate(_ps) if p.startswith("Table 2.")); ok(pos[-1] < iT1 < iT2, "tables after figure legends, each on its own page")
meth = _dx[_dx.find("\nMethods\n"):_dx.find("\nResults\n")]; ok(AI_STATEMENT in meth and "translation and English-language editing" in AI_STATEMENT, "AI use described in Methods (translation and editing only)")
ok(f"{C.HIGHLIGHTS[0]}" in _dx, "highlights in main document")
ok("<w:drawing" not in zipfile.ZipFile(os.path.join(OUT, MSF)).read("word/document.xml").decode(), "no embedded figures in main document")
res = _dx[_dx.find("\nResults\n"):_dx.find("\nDiscussion\n")]
for k in (1, 2, 3): ok(f"Figure {k}" in res, f"Figure {k} cited in Results")
for k in (1, 2): ok(f"Table {k}" in res, f"Table {k} cited in Results")
for k in (1, 2, 3):
    fp = os.path.join(FIGD, f"Figure{k}.tif"); ok(os.path.exists(fp), f"Figure{k}.tif exists")
    if os.path.exists(fp):
        im = Image.open(fp); ok(im.mode == "RGB" and round(im.info.get("dpi", (0, 0))[0]) >= 300, f"Figure{k}.tif colour RGB, {round(im.info.get('dpi',(0,0))[0])} dpi")
# 5. tables
for nm, f in (("main", MSF), ("SI", SUPF)):
    dd = Document(os.path.join(OUT, f))
    for i, t in enumerate(dd.tables):
        b = t._tbl.tblPr.find(qn("w:tblBorders"))
        ok(b is not None and all(b.find(qn(f"w:{s}")) is not None and b.find(qn(f"w:{s}")).get(qn("w:val")) == "nil" for s in ("insideV", "insideH", "left", "right")), f"{nm} table {i+1} three-line")
        bad = [r.text for j, row in enumerate(t.rows) if j > 0 for c in row.cells[1:] for p in c.paragraphs for r in p.runs if r.bold and r.text.strip()]
        ok(not bad, f"{nm} table {i+1} no bold data cells {bad[:2]}")
        cells = "\n".join(c.text for r in t.rows for c in r.cells); ok(not re.search(r"\d\)\*|\*\s*$|\*interval|\*95%", cells, re.M), f"{nm} table {i+1} no asterisk markers (dagger used)")
ok(not re.search(r"(?m)^\s*\S.*:\s", "\n".join(p for p in _ps if p in [h for h, _ in STATEMENTS_ANON] or p.startswith("Table "))), "no colon in headings and table titles")
# 6. style and references
body = re.sub(r"\s+", " ", _dx[_dx.find("\nIntroduction\n"):_dx.find("\nReferences\n")])
cov = subprocess.run(["pdftotext", os.path.join(OUT, CLF.replace(".docx", ".pdf")), "-"], capture_output=True, text=True).stdout
alltxt = _dx + supt + cov
ok(not re.search(r"\b(we|our|us|We|Our)\b", body + " " + ab), "no first person (sole author)")
ok("—" not in alltxt and not re.search(r"[가-힣]", alltxt), "no em dash or Korean")
ok(not re.search(r"\bsignifican", _dx + supt, re.I), "no 'significant'")
US = r"\b(\w*(standardiz|harmoniz|summariz|categoriz|minimiz|randomiz|generaliz|normaliz|prioritiz|organiz|penaliz)\w*|modeled|modeling|centers?|neighbors?\w*|behavior\w*|aging|color\w*|labeled|program|analyze[ds]?)\b"
us = sorted(set(m.group(0) for m in re.finditer(US, body + " " + supt + " " + cov))); ok(not us, f"British spelling {us}")
ok(not re.search(r"\[(@|web:)", _dx) and "{{" not in _dx, "no unresolved citations")
refs = _dx[_dx.find("\nReferences\n"):_dx.find("\nFigure legends\n")]
ok(not re.search(r"github|zenodo", refs, re.I), "no GitHub or Zenodo in references")
rl = [l for l in refs.split("\n")[2:] if l.strip()]; ok(len(rl) == len(KEYS) and all(l.startswith(f"{i}. ") for i, l in enumerate(rl, 1)), f"reference list numbered 1..{len(rl)}")
ok(not re.search(r"�|Gittelsohn \(", refs), "author names intact")
ok(not re.search(r"(?i)acting on|acts on|supply-induced|over-use|overuse|natural experiment", body.replace("Bed supply and hospital utilization: a natural experiment", "") + " " + ab + " " + cov + " ".join(C.HIGHLIGHTS)), "no causal overstatement")
_sn = [int(x) for x in re.findall(r"Tables? S(\d+)", body)]; _f = []; [_f.append(x) for x in _sn if x not in _f]; ok(_f == sorted(_f), f"Supporting tables first-cited in order {_f}")
for k in range(1, 11): ok(f"Table S{k}." in supt or f"Table S{k} " in supt, f"Supporting Information Table S{k}")
ok(not re.search(r"(?i)overlap|previously submitted|resubmi|reject|Byung|Chun\b", cov), "cover letter: no overlap, prior submission or excluded reviewer")
ok(re.search(r"Theme\s+1", cov) is not None, "cover letter states theme")
# 7. version traces in file names and text
fn = " ".join(os.path.basename(x) for x in glob.glob(os.path.join(OUT, "**", "*"), recursive=True))
ok(not re.search(r"(?i)_v\d|v\d\.\d|resub|revised", fn), "no version traces in output file names")
ok(not re.search(r"(?i)\bversion \d|previous submission", alltxt.replace("Version 4.6.0", "")), "no version traces in text")
open(os.path.join(OUT, "check_ms.txt"), "w").write("\n".join(R)); nf = sum(r.startswith("FAIL") for r in R)
print("\n".join(r for r in R if r.startswith("FAIL")) or "", f"\n{len(R)} checks, FAIL {nf}", "PASS" if nf == 0 else "")

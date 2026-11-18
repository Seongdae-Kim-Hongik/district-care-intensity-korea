# build_ms_hcuv.py — 43 HCUV research article: anonymised main document, separate title page and highlights (numbered AMA references).
#  Target format: main text <=7,000 words (abstract, keywords, highlights, tables, figures excluded), unstructured abstract <=250 words without citations,
#   4 highlights of <=80 characters, keywords <=7, AMA numbered references (superscript, first-cite order) <=50, table symbols † ‡ § ¶ (asterisks reserved for P values),
#   running title <70 characters, British spelling, AI use described in Methods, main document without identifying information (title page separate), tables at the end.
#  Sources: ../draft/manuscript_hcuv.md (## sections, [@key] citations, final numbers), content_ms_hcuv.py (title, keywords, highlights, tables, captions), refs_ms_hcuv.json.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from jkms_engine import JKMS
import content_ms_hcuv as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out_ijhpm"); os.makedirs(OUT, exist_ok=True)
REFS = json.load(open(os.path.join(HERE, "refs_ms_hcuv.json"), encoding="utf-8")); N = C.N
DRAFT = os.path.join(MS, "draft", "manuscript_hcuv.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "10.5281/zenodo.PENDING"
TITLE = C.TITLE; RUNNING = C.RUNNING_TITLE; ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
PHONE = "+82-2-320-1114"; EMAIL = "kimsd@hongik.ac.kr"
KEYWORDS = "health care use; small-area variation; supply-sensitive care; Medical Aid; health planning; spatio-temporal analysis; Korea"
AI_STATEMENT = ("Claude (Anthropic) and ChatGPT (OpenAI) were used only for translation and English-language editing of the manuscript. They were not used to design the study, "
                "analyse data, interpret results or select references. The author reviewed and edited all text and takes full responsibility for the content.")
IRB = ("The Institutional Review Board of Hongik University approved the study on 4 November 2025 (7002340-202511-HR-012) and its continuing review on 3 November 2026 "
       "(7002340-202611-HR-040), and waived informed consent because only published aggregate statistics were used.")
IRB_ANON = "The study was approved by the institutional review board of the author's institution, which waived informed consent because only published aggregate statistics were used (approval numbers on the title page)."
FUNDING = "This research did not receive any specific grant from funding agencies in the public, commercial or not-for-profit sectors."
COI = "The author declares no conflicts of interest."
CONTRIB = "Seongdae Kim: conceptualisation, methodology, software, formal analysis, data curation, visualisation, writing (original draft) and writing (review and editing)."
DATA = lambda: ("All source data are publicly available aggregate statistics from the National Health Insurance Service, Statistics Korea, the Ministry of the Interior and Safety, "
                "the national public sports facility register and the Community Health Survey, as cited in the Methods. The analysis code and the scripts that generate every number, "
                f"table and figure are openly available on Zenodo (https://doi.org/{ZENODO}) under the MIT License. The processed district-year analytic data are available from the author on reasonable request.")
DATA_ANON = ("All source data are publicly available aggregate statistics, as cited in the Methods. The analysis code is openly available in a public repository under the MIT License "
             "(the persistent identifier is given on the title page).")

def read_draft():
    md = re.sub(r"<!--.*?-->", "", open(DRAFT, encoding="utf-8").read(), flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def cites(t):   # AMA: superscript numbers after the full stop or comma that follows the cited statement
    return re.sub(r"\s*\[(@[^\]]+)\]([.,;:]?)", lambda m: m.group(2) + "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def strip(t): return re.sub(r"\s*\[@[^\]]+\]", "", t)
def all_keys():
    md = re.sub(r"<!--.*?-->", "", open(DRAFT, encoding="utf-8").read(), flags=re.S)
    return sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", md) for k in g.split(";")})
KEYS = all_keys(); missing = [k for k in KEYS if k not in REFS]; assert not missing, missing

AUTHOR_FIX = {"Gittelsohn": "Gittelsohn A"}
def ref(k):   # AMA 11th: up to 6 authors, otherwise first 3 + et al; NLM abbreviation; year;vol(issue):pages. doi:
    r = REFS[k]
    if k == "oecd2023health": return "OECD. <i>Health at a Glance 2023: OECD Indicators</i>. OECD Publishing; 2023. doi:10.1787/7a7afb35-en"
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. Published {r['year']}. Accessed {r['accessed']}. {r['url']}"
    au = [AUTHOR_FIX.get(a, a) for a in r["authors"]]
    a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al"
    t = r["title"].rstrip("."); t += "" if t.endswith(("?", "!")) else "."
    vol = str(r.get("vol", "")).strip(); iss = str(r.get("issue", "")).strip(); pg = str(r.get("pages", "")).strip().rstrip(".")
    s = f"{a}. {t} <i>{r['jabbr']}</i>. {r['year']}"
    if vol: s += f";{vol}" + (f"({iss})" if iss else "")
    if pg: s += f":{pg}"
    return s + "." + (f" doi:{r['doi']}" if r.get("doi") else "")

class TX(JKMS):
    raw = False; table_bold = False
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for s_ in self.doc.sections:
            ln = s_._sectPr.find(qn("w:lnNumType"))
            if ln is not None: s_._sectPr.remove(ln)
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

def foot_row(J, text, sz=9, ls=15):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3], 8); J.counting = c

STATEMENTS_ANON = (("Conflict of interest statement", COI), ("Funding statement", FUNDING), ("Ethics statement", IRB_ANON), ("Data availability statement", DATA_ANON))
def build():
    D = read_draft(); J = TX(cite="sup")
    J.para(f"<b>{TITLE}</b>"); J.para(f"<b>Running title:</b> {RUNNING}", before=6)
    J.head("Highlights", 1)
    for h in C.HIGHLIGHTS: J.para("\u2022 " + h)
    J.page_break(); J.head("Abstract", 1)
    for p in D["Abstract"]: J.para(p)
    J.para(f"<b>Keywords:</b> {KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    for sec in ("Introduction", "Methods", "Results", "Discussion", "Conclusions"):
        J.head(sec, 1)
        for p in D[sec]:
            if p.startswith("### "): J.head(p[4:].strip(), 2); continue
            m = re.fullmatch(r"\[\[TABLE (\d)\]\]", p)
            if m: continue   # tables at the end of the document
            J.para(cites(p), indent=True)
    J.counting = False
    for h, t in STATEMENTS_ANON: J.head(h, 1); J.para(t)
    assert J.cites == sorted(set(J.cites), key=J.cites.index) and sorted(set(J.cites)) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s_ = ref(k); rl.append(f"{i}. " + re.sub(r"</?i>", "", s_)); J.para(f"{i}. {s_}")
    J.raw = False
    J.page_break(); J.head("Figure legends", 1)
    for k in sorted(C.FIGCAP): J.para(f"<b>Figure {k}.</b> {C.FIGCAP[k]}")
    for k in sorted(C.TABLES): J.page_break(); put_table(J, C.TABLES[k]())
    return J, rl, D

def main_words(path):   # Introduction to Conclusions (statements, references, legends and tables excluded)
    from docx import Document
    ps = [p.text.strip() for p in Document(path).paragraphs]
    i = ps.index("Introduction"); j = ps.index(STATEMENTS_ANON[0][0])
    return sum(len(p.split()) for p in ps[i + 1:j] if p not in ("Methods", "Results", "Discussion", "Conclusions"))

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_HCUV.docx"); J, rl, D = build(); J.doc_title = ""; J.save(p)
    mw = main_words(p); aw = sum(len(strip(x).split()) for x in D["Abstract"])
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_hcuv_ms", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)
    H = TX(cite="sup"); H.para("<b>Highlights</b>")
    for h in C.HIGHLIGHTS: H.para("\u2022 " + h)
    H.doc_title = ""; H.save(os.path.join(OUT, "Highlights_HCUV.docx"))
    T = TX(cite="sup"); T.para("<b>Title page</b>"); T.para(f"<b>{TITLE}</b>", before=6)
    T.para(f"<b>Running title:</b> {RUNNING}", before=6)
    T.para("Seongdae Kim", before=6); T.para(AFFIL); T.para(f"ORCID: {ORCID}")
    T.para(f"<b>Correspondence:</b> Seongdae Kim, {ADDRESS}. Telephone: {PHONE}. E-mail: {EMAIL}", before=6)
    T.para(f"<b>Word count:</b> main text {mw:,} words (Introduction to Conclusions); abstract {aw} words. <b>Tables and figures:</b> {len(C.TABLES)} tables and {len(C.FIGCAP)} figures. <b>References:</b> {len(KEYS)}.", before=6)
    T.para(f"<b>Keywords:</b> {KEYWORDS}", before=6)
    for h, t in (("Acknowledgements", "None."), ("Author contribution", CONTRIB), ("Conflict of interest statement", COI), ("Funding statement", FUNDING), ("Ethics statement", IRB),
                 ("Data availability statement", DATA()), ("Use of artificial intelligence tools", AI_STATEMENT)):
        T.head(h, 1); T.para(t)
    T.doc_title = ""; tp = os.path.join(OUT, "Title_Page_HCUV.docx"); T.save(tp)
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_hcuv_ms", "--convert-to", "pdf", "--outdir", OUT, tp], check=True, capture_output=True)
    open(os.path.join(OUT, "wordcount_ms.txt"), "w").write(f"main_words={mw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables={len(C.TABLES)}\nfigures={len(C.FIGCAP)}\ntitle_chars={len(TITLE)}\nrunning_chars={len(RUNNING)}\n")
    open(os.path.join(OUT, "reference_list.txt"), "w", encoding="utf-8").write("\n".join(rl))
    print(f"main {mw} | abstract {aw} | refs {len(KEYS)} | highlights {[len(h) for h in C.HIGHLIGHTS]} | running {len(RUNNING)} | DOI {ZENODO}")

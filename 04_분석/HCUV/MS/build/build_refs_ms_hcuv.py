# build_refs_ms_hcuv.py — 43 HCUV numbered (AMA) reference cache. Input = refs_hcuv.json (verified PubMed/Crossref metadata) restricted to the keys cited in
#  ../draft/manuscript_hcuv.md; adds NLM journal abbreviations (PubMed esummary "source"; manual map for non-PubMed items). Network use: this script only.
import os, re, json, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE)
R = json.load(open(os.path.join(HERE, "refs_hcuv.json"), encoding="utf-8"))
md = re.sub(r"<!--.*?-->", "", open(os.path.join(MS, "draft", "manuscript_hcuv.md"), encoding="utf-8").read(), flags=re.S)
keys = sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", md) for k in g.split(";")})
miss = [k for k in keys if k not in R]; assert not miss, miss
MANUAL = {"bell2015explaining": "Polit Sci Res Methods", "besag1991bayesian": "Ann Inst Stat Math", "gelman2014understanding": "Stat Comput", "moran1950notes": "Biometrika",
          "ord1995local": "Geogr Anal", "rue2009approximate": "J R Stat Soc Series B Stat Methodol", "simpson2017penalising": "Stat Sci"}
pm = [k for k in keys if R[k].get("pmid")]
d = json.load(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(R[k]["pmid"] for k in pm), timeout=60))["result"]
out = {}
for k in keys:
    v = dict(R[k])
    if k in pm: v["jabbr"] = d[R[k]["pmid"]]["source"].replace(".", "")
    elif k in MANUAL: v["jabbr"] = MANUAL[k]
    out[k] = v
time.sleep(0.3)
TITLEFIX = {   # sentence case for titles indexed in title case
 "kim2026mortality": "Mortality, health care use, and spending patterns during South Korea's trainee physicians' walkout",
 "min2016excess": "Excess medical care costs associated with physical inactivity among Korean adults: retrospective cohort study",
 "shaw2017social": "Social isolation and Medicare spending: among older adults, objective social isolation increases expenditures while loneliness does not",
 "delamater2013more": "Do more hospital beds lead to higher hospitalization rates? A spatial examination of Roemer's Law",
}
for k, t in TITLEFIX.items(): out[k]["title"] = t
json.dump(out, open(os.path.join(HERE, "refs_ms_hcuv.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(keys), "keys;", {k: v.get("jabbr") for k, v in out.items()})

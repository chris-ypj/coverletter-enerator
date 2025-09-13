
import re
from typing import List, Tuple, Set

STOPWORDS: Set[str] = set("""a an the and or with for from to into on in of by at as is are was were be been being
this that these those i you he she it we they my our your their but if then so than too very just
not no nor over under out up down off more most less least only also again still into between among
per via while during about against without within until across because due such etc across""".split())

TECH_HINTS: Set[str] = {
    "python","java",".net","c#","c++","react","next.js","nestjs","node","typescript","javascript","sql",
    "aws","azure","gcp","docker","kubernetes","fastapi","django","flask","spring","mongo","mongodb","postgres",
    "git","ci/cd","k8s","llm","rag","agent","agentic","uipath","power automate","step functions","ipaas"
}


def extract_keywords(jd_text: str, top_k: int = 20) -> List[str]:
    """Very simple keyword extraction mixing tech hints and frequency."""
    txt = jd_text.lower()
    tokens = re.findall(r"[a-zA-Z\.\#\+\-]+", txt)
    freq = {}
    for tok in tokens:
        if tok in STOPWORDS or len(tok) < 2:
            continue
        freq[tok] = freq.get(tok, 0) + 1

    included = []
    for hint in TECH_HINTS:
        if hint in txt:
            included.append(hint)

    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    for w, _ in top:
        if w not in included:
            included.append(w)
        if len(included) >= top_k:
            break
    return included[:top_k]


def jd_match_table(keywords: List[str], letter: str) -> List[Tuple[str, bool]]:
    """Check presence of each keyword in the letter text."""
    L = letter.lower()
    return [(kw, kw.lower() in L) for kw in keywords]

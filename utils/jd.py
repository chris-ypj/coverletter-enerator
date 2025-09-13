
import re
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None


def fetch_url_text(url: str, timeout: int = 15) -> str:
    """Fetch visible text from a job posting URL (best effort)."""
    if not requests or not BeautifulSoup:
        return ""
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = " ".join(t.get_text(separator=" ", strip=True) for t in soup.find_all())
        text = re.sub(r"\s+", " ", text).strip()
        return text[:25000]
    except Exception:
        return ""


def clean_text(t: Optional[str]) -> str:
    """Normalize whitespace and trim."""
    return re.sub(r"\s+", " ", (t or "")).strip()

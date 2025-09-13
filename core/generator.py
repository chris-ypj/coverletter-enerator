
import re
import time
from typing import List, Dict

from core.prompt import build_prompt
from services.llm import generate_letter
from utils.keywords import extract_keywords, jd_match_table


def redact(text: str, enable: bool) -> str:
    if not enable:
        return text
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email]", text)
    text = re.sub(r"\+?\d[\d\-\s]{7,}\d", "[phone]", text)
    return text


def make_email_version(letter: str) -> str:
    lines = [ln.strip() for ln in letter.splitlines() if ln.strip()]
    _ = " ".join(lines)
    _ = re.sub(r"\s+", " ", _)
    email = (
        "Subject: Application for the role\n\n"
        "Hi team,\n\n"
        "I'm reaching out to apply for the role. "
        "I bring relevant hands-on experience and a track record of delivering practical solutions. "
        "I'd love to contribute this summer and learn your stack quickly. "
        "Attached is my CV and cover letter.\n\n"
        "Best regards,\nYour Name"
    )
    return email


def generate_variants(job_ad: str,
                      role_title: str,
                      skills: List[str],
                      projects: List[Dict[str,str]],
                      tone: str,
                      length_hint: str,
                      include_header: bool,
                      candidate_name: str,
                      contact_line: str,
                      city: str,
                      extra_notes: str,
                      privacy: bool,
                      model_choice: str,
                      variants: int = 1):
    prompt = build_prompt(job_ad, role_title, skills, projects, tone, length_hint,
                          include_header, candidate_name, contact_line, city, extra_notes)
    letters = []
    for i in range(variants):
        letter = generate_letter(prompt, model_choice=model_choice)
        letter = redact(letter, privacy)
        letters.append(letter)
        time.sleep(0.1)
    keywords = extract_keywords(job_ad, top_k=20)
    matches = jd_match_table(keywords, letters[0] if letters else "")
    return letters, keywords, matches

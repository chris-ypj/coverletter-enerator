
from typing import List, Dict

def build_prompt(job_ad: str,
                 role_title: str,
                 skills: List[str],
                 projects: List[Dict[str,str]],
                 tone: str,
                 length_hint: str,
                 include_header: bool,
                 candidate_name: str,
                 contact_line: str,
                 city: str,
                 extra_notes: str) -> str:
    proj_lines = []
    for p in projects:
        name = p.get("name","")
        tech = p.get("tech_stack","")
        impact = p.get("impact","")
        proj_lines.append(f"- {name} — tech: {tech}; impact: {impact}")
    proj_block = "\n".join(proj_lines) if proj_lines else "- (none)"
    skills_str = ", ".join(skills) if skills else "(none)"
    header = ""
    if include_header:
        header = f"{candidate_name}\n{city}\n{contact_line}\n\n"

    prompt = f"""
You are an expert cover-letter writer. Write a tailored, ATS-friendly cover letter.
Rules:
- Tone: {tone}. Length: {length_hint} words approx.
- Use clear, specific language. Avoid clichés and empty claims. Do not invent experience.
- Respond to the job ad's must-haves using the candidate's skills/projects as evidence.
- Prefer 3–5 concise paragraphs. Start with a hook; end with a polite call-to-action.
- Company name may be inferred if present in the job text; otherwise keep it generic.
- Return only the letter body (no surrounding commentary).

JOB AD (verbatim):
\"\"\"
{job_ad}
\"\"\"

ROLE TITLE: {role_title}

CANDIDATE PROFILE
- Name: {candidate_name}
- City: {city}
- Contact: {contact_line}
- Skills: {skills_str}
- Projects:
{proj_block}

EXTRA NOTES (optional, constraints / focus): {extra_notes}

Return the final cover letter text only. If some must-haves aren't matched, emphasize rapid learning and adjacent experience.
"""
    return header + prompt.strip()

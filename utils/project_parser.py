import json
import re

def parse_projects_input(text):
    # Try list of dict
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list) and all(isinstance(p, dict) for p in parsed):
            return parsed
    except:
        pass

    # Try JSON lines
    lines = text.strip().splitlines()
    jsonl_parsed = []
    for line in lines:
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                jsonl_parsed.append(obj)
        except:
            pass
    if jsonl_parsed:
        return jsonl_parsed

    # Try natural language lines
    projects = []
    pattern = re.compile(r"^\d+\.\s*(.*?)\s*[–-]\s*(.*)")
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            title, desc = match.groups()
            projects.append({"title": title.strip(), "desc": desc.strip()})
    if projects:
        return projects

    return []
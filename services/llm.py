
import os
import textwrap

try:
    from openai import OpenAI
    HAS_NEW = True
except Exception:
    HAS_NEW = False

try:
    import openai as openai_legacy
    HAS_LEGACY = True
except Exception:
    HAS_LEGACY = False


def generate_letter(prompt: str, model_choice: str = "gpt-4o-mini") -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return textwrap.dedent("""
        Dear Hiring Team,

        I'm excited to apply for this role. I bring hands-on experience in relevant technologies and a track record of building practical tools that improve workflows. Based on the position requirements, I can contribute across development, testing, and deployment while learning any new stack quickly.

        In recent projects, I delivered automation and AI-assisted features, integrating APIs and refining user journeys end-to-end. I enjoy collaborating with cross-functional teams and translating requirements into maintainable, secure solutions.

        I would welcome the chance to learn your stack and contribute this summer. Thank you for your time and consideration.

        Sincerely,
        Candidate
        """).strip()

    if HAS_NEW:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role":"system","content":"You are a helpful, precise writing assistant."},
                {"role":"user","content":prompt},
            ],
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()

    if HAS_LEGACY:
        openai_legacy.api_key = api_key
        resp = openai_legacy.ChatCompletion.create(
            model=model_choice,
            messages=[
                {"role":"system","content":"You are a helpful, precise writing assistant."},
                {"role":"user","content":prompt},
            ],
            temperature=0.5,
        )
        return resp["choices"][0]["message"]["content"].strip()

    return "OpenAI client not installed. Please `pip install openai` or set OPENAI_API_KEY."

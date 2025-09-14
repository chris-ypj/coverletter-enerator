# ui/layout.py
import streamlit as st
from utils.project_parser import parse_projects_input

# Optional imports with graceful fallbacks
try:
    from utils.jd import clean_text
except Exception:
    def clean_text(x): return x or ""

try:
    from core.generator import generate_variants, make_email_version
    _HAS_GENERATOR = True
except Exception:
    _HAS_GENERATOR = False
    def make_email_version(text):  # simple fallback
        return text[:500] + "..." if len(text) > 500 else text

from core.prompt import build_prompt


# -------------------------------
# Sidebar Inputs
# -------------------------------
def sidebar_inputs():
    st.sidebar.header("Your Details")
    full_name = st.sidebar.text_input("Full name", placeholder="Chris Jia")
    email = st.sidebar.text_input("Email (optional for header)")
    phone = st.sidebar.text_input("Phone (optional for header)")
    location = st.sidebar.text_input("Location", placeholder="Auckland, NZ")

    st.sidebar.header("Target Role / Company")
    target_role = st.sidebar.text_input("Role", placeholder="Software Engineer Intern")
    company = st.sidebar.text_input("Company", placeholder="Harmoney")
    jd_text = st.sidebar.text_area("Job description / JD text", height=160)

    # Projects (flexible)
    st.sidebar.header("Projects")
    projects_raw = st.sidebar.text_area(
        "Projects (JSON lines / list[dict] / natural language)",
        placeholder=(
            'Example 1 (list[dict]):\n'
            '[{"title":"AI Resume Helper","tech":["Python","Streamlit"],"desc":"Cover letter tool"},'
            ' {"title":"Payment Gateway","tech":["Java"],"desc":"Stripe integration"}]\n\n'
            'Example 2 (JSON Lines):\n'
            '{"title":"AI Resume Helper","desc":"Built with Python"}\n'
            '{"title":"Payment Gateway","desc":"Java backend"}\n\n'
            'Example 3 (Natural language, one per line):\n'
            '1. AI Resume Helper – Python/Streamlit cover‑letter generator\n'
            '- Payment Gateway – Java backend with multi‑channel payments'
        ),
        height=200,
    )
    parsed_projects = parse_projects_input(projects_raw)

    with st.sidebar.expander("Preview parsed projects"):
        if parsed_projects:
            st.json(parsed_projects)
        else:
            st.caption("No projects parsed yet.")

    use_projects = st.sidebar.checkbox("Include projects in generation", value=bool(parsed_projects))

    #  Generation options (restored)
    st.sidebar.header("Generation Options")
    # target length (words)
    length_hint = st.sidebar.select_slider(
        "Target length (words)",
        options=[150, 200, 250, 300, 350, 400, 450, 500],
        value=300,
    )
    # mode: Standard / Pro / Precise
    mode = st.sidebar.radio(
        "Mode",
        ["Standard", "Pro", "Precise"],
        index=0,
        help="Pro = richer phrasing; Precise = concise, higher factual strictness.",
    )
    include_header = st.sidebar.checkbox("Include header/signature block", value=True)

    # optional: multiple variants (if your core.generator supports it)
    variants = st.sidebar.slider("Variants to generate", min_value=1, max_value=5, value=3)

    # optional: model choice passthrough (used only if your generator supports it)
    model_choice = st.sidebar.selectbox(
        "Model (passthrough)",
        ["gpt-4o-mini", "gpt-4o", "o3-mini"],
        index=0,
    )
    # privacy mode to avoid external API calls (forces fallback path)
    privacy = st.sidebar.checkbox("Privacy mode (no external API)", value=False)

    tone = st.sidebar.selectbox("Tone", ["Professional", "Warm", "Direct"], index=0)
    extra_notes = st.sidebar.text_area(
        "Extra notes / constraints (optional)",
        placeholder="Why this company, availability, constraints, etc.",
        height=100,
    )

    return {
        "full_name": (full_name or "").strip(),
        "email": (email or "").strip(),
        "phone": (phone or "").strip(),
        "location": (location or "").strip(),
        "target_role": (target_role or "").strip(),
        "company": (company or "").strip(),
        "jd_text": jd_text or "",
        "projects": parsed_projects if use_projects else [],
        "tone": tone,
        "extra_notes": (extra_notes or "").strip(),
        # restored options:
        "length_hint": int(length_hint),
        "mode": mode,
        "include_header": bool(include_header),
        "variants": int(variants),
        "model_choice": model_choice,
        "privacy": bool(privacy),
    }


# -------------------------------
# Project Conversion
# -------------------------------
def _convert_projects_for_prompt(projects):
    """ Map UI projects -> prompt.py expected schema """
    out = []
    for p in projects or []:
        out.append({
            "name": p.get("title", ""),
            "tech_stack": ", ".join(p.get("tech", [])) if isinstance(p.get("tech"), list) else (p.get("tech") or ""),
            "impact": p.get("desc", ""),
        })
    return out


# Simple fallback letter generator
def _simple_generate_letter(state):
    projects_for_prompt = _convert_projects_for_prompt(state.get("projects", []))
    contact_line = " | ".join([v for v in [state.get("email"), state.get("phone")] if v])

    # Thread the "mode" preference into extra_notes so prompt sees it
    extra = state.get("extra_notes", "").strip()
    if state.get("mode"):
        extra = (extra + f"\nMode preference: {state['mode']}").strip()

    prompt_text = build_prompt(
        job_ad=clean_text(state.get("jd_text", "")),
        role_title=state.get("target_role", ""),
        skills=[],  # extend if you add a skills UI
        projects=projects_for_prompt,
        tone=state.get("tone", "Professional"),
        length_hint=str(state.get("length_hint", 300)),  # build_prompt expects string
        include_header=bool(state.get("include_header", True)),
        candidate_name=state.get("full_name", ""),
        contact_line=contact_line,
        city=state.get("location", ""),
        extra_notes=extra,
    )
    # For now, return the prompt text as the "letter" in fallback mode.
    # If you wire OpenAI directly here, replace this with the model call.
    return prompt_text


# Main Tabs
def main_tabs(state):
    tab1, tab2, tab3, tab4 = st.tabs(["Draft", "JD Match", "Variants", "Email"])

    if st.button("Generate Letter", type="primary", use_container_width=True):
        if not (state.get("jd_text") or "").strip():
            st.error("Please provide the job ad text.")
            st.stop()

        with st.spinner("Generating..."):
            letters, keywords, matches = [], [], []

            # If privacy is ON, force simple path (no external API)
            if state.get("privacy", False):
                letters = [_simple_generate_letter(state)]
            else:
                if _HAS_GENERATOR:
                    try:
                        projects_for_prompt = _convert_projects_for_prompt(state.get("projects", []))
                        contact_line = " | ".join([v for v in [state.get("email"), state.get("phone")] if v])

                        letters, keywords, matches = generate_variants(
                            job_ad=clean_text(state["jd_text"]),
                            role_title=state["target_role"],
                            skills=[],  # optional
                            projects=projects_for_prompt,
                            tone=state["tone"],
                            length_hint=str(state["length_hint"]),
                            include_header=bool(state["include_header"]),
                            candidate_name=state["full_name"],
                            contact_line=contact_line,
                            city=state["location"],
                            extra_notes=(state["extra_notes"] + f"\nMode preference: {state['mode']}").strip(),
                            # passthrough / optional args:
                            model_choice=state["model_choice"],
                            variants=state["variants"],
                            privacy=state["privacy"],  # some generators may use this too
                        )
                    except TypeError:
                        # If signatures don't match, fall back gracefully
                        letters = [_simple_generate_letter(state)]
                    except Exception:
                        letters = [_simple_generate_letter(state)]
                else:
                    letters = [_simple_generate_letter(state)]

        with tab1:
            st.subheader("Cover Letter")
            st.write(letters[0])
            st.download_button("Download .txt", letters[0], "cover_letter.txt")
            st.download_button("Download .md", letters[0], "cover_letter.md")

        with tab2:
            st.subheader("JD Match")
            if matches:
                st.table({"keyword": [k for k, _ in matches], "present": [p for _, p in matches]})
            else:
                st.caption("No keyword matches available.")

        with tab3:
            st.subheader("Variants")
            if len(letters) > 1:
                for i, lt in enumerate(letters):
                    st.markdown(f"**Variant {i+1}**")
                    st.write(lt)
                    st.download_button(f"Download Variant {i+1}", lt, f"variant_{i+1}.txt")
            else:
                st.caption("Only one version generated.")

        with tab4:
            st.subheader("Email Version (concise)")
            email_ver = make_email_version(letters[0])
            st.code(email_ver)
            st.download_button("Download email.txt", email_ver, "email.txt")

    else:
        st.info("Fill out the sidebar, then click **Generate Letter**.")
        with st.expander("Current options"):
            st.json({
                "mode": state.get("mode"),
                "length_hint": state.get("length_hint"),
                "include_header": state.get("include_header"),
                "variants": state.get("variants"),
                "model_choice": state.get("model_choice"),
                "privacy": state.get("privacy"),
            })
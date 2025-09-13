
import json
import streamlit as st
from utils.jd import fetch_url_text, clean_text
from core.generator import generate_variants, make_email_version


def sidebar_inputs():
    st.header("Inputs")
    job_source = st.radio("Job source", ["Paste job ad text", "Fetch from URL"])
    job_ad_text = ""
    if job_source == "Paste job ad text":
        job_ad_text = st.text_area("Job Ad (paste here)", height=220, placeholder="Paste the job description...")
    else:
        url = st.text_input("Job Ad URL")
        if url and st.button("Fetch URL"):
            with st.spinner("Fetching..."):
                fetched = fetch_url_text(url)
            if fetched:
                st.success("Fetched. You can trim it below if needed.")
                job_ad_text = fetched
            else:
                st.warning("Could not fetch the page. Paste the ad text instead.")
        job_ad_text = st.text_area("Fetched/Editable Job Ad Text", value=job_ad_text, height=220)

    role_title = st.text_input("Target Role Title", value="AI & .NET Developer Intern")
    candidate_name = st.text_input("Your Name", value="Chris Jia")
    city = st.text_input("City", value="Auckland, NZ")
    email = st.text_input("Email (optional for header)", value="")
    phone = st.text_input("Phone (optional for header)", value="")
    include_header = st.checkbox("Include header (name/city/contact) in output", value=False)

    skills = st.text_input("Skills (comma-separated)", value="Python, .NET, React, SQL, AWS")
    skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    st.markdown("**Projects (JSON lines)**")
    proj_help = 'One per line, e.g.: {"name":"Onestep DevOps","tech_stack":"Python, Django, K8s","impact":"automation for 500+ apps; 90% time reduction"}'
    projects_text = st.text_area("Projects", height=120, help=proj_help, placeholder=proj_help)
    projects = []
    for line in projects_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            projects.append(json.loads(line))
        except Exception:
            st.error(f"Invalid JSON: {line}")

    tone = st.selectbox("Tone", ["professional", "confident and concise", "warm and professional", "enthusiastic but clear"])
    length_hint = st.selectbox("Length (approx words)", ["200-300","300-450","450-650"])
    variants = st.slider("Number of variants", 1, 3, 1)
    extra_notes = st.text_area("Extra notes / constraints (optional)", height=80, placeholder="e.g., emphasize agentic AI interest; align with public sector impact; highlight DevOps background")
    privacy = st.checkbox("Privacy mode (redact email/phone in outputs)", value=True)
    model_choice = st.text_input("OpenAI model (e.g., gpt-4o-mini, gpt-4o, o4-mini)", value="gpt-4o-mini")
    st.caption("Set OPENAI_API_KEY in your environment to actually call the API. Without it, a mock letter is returned for demo.")

    return {
        "job_ad_text": job_ad_text,
        "role_title": role_title,
        "candidate_name": candidate_name,
        "city": city,
        "email": email,
        "phone": phone,
        "include_header": include_header,
        "skills_list": skills_list,
        "projects": projects,
        "tone": tone,
        "length_hint": length_hint,
        "variants": variants,
        "extra_notes": extra_notes,
        "privacy": privacy,
        "model_choice": model_choice
    }


def main_tabs(state):
    tab1, tab2, tab3, tab4 = st.tabs(["Draft", "JD Match", "Variants", "Email"])

    if st.button("Generate Letter", type="primary", use_container_width=True):
        if not state["job_ad_text"].strip():
            st.error("Please provide the job ad text or fetch it from a URL.")
            st.stop()

        with st.spinner("Generating..."):
            contact_line = ", ".join([v for v in [state['email'], state['phone']] if v])
            letters, keywords, matches = generate_variants(
                job_ad=clean_text(state["job_ad_text"]),
                role_title=state["role_title"],
                skills=state["skills_list"],
                projects=state["projects"],
                tone=state["tone"],
                length_hint=state["length_hint"],
                include_header=state["include_header"],
                candidate_name=state["candidate_name"],
                contact_line=contact_line,
                city=state["city"],
                extra_notes=state["extra_notes"],
                privacy=state["privacy"],
                model_choice=state["model_choice"],
                variants=state["variants"],
            )

        with tab1:
            st.subheader("Cover Letter Draft")
            st.write(letters[0])
            st.download_button("Download as .txt", data=letters[0], file_name="cover_letter.txt")
            st.download_button("Download as .md", data=letters[0], file_name="cover_letter.md")

        with tab2:
            st.subheader("JD Keyword Match")
            st.table({"keyword": [k for k,_ in matches], "present_in_letter": [p for _,p in matches]})

        with tab3:
            st.subheader("Variants")
            for idx, lt in enumerate(letters, start=1):
                st.markdown(f"**Variant {idx}**")
                st.write(lt)
                st.download_button(f"Download Variant {idx}", data=lt, file_name=f"cover_letter_variant_{idx}.txt")

        with tab4:
            st.subheader("Email Version (concise)")
            email_ver = make_email_version(letters[0])
            st.code(email_ver)
            st.download_button("Download email.txt", data=email_ver, file_name="email.txt")

    else:
        st.info("Fill in the sidebar and click **Generate Letter**. Without an API key, a mock letter is produced for demo.")
        st.code("""
streamlit run app.py

# Set your key before running (macOS/Linux):
export OPENAI_API_KEY="sk-..."

# Windows PowerShell:
$Env:OPENAI_API_KEY="sk-..."
""")

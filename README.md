
# AI Cover Letter Builder (Modular Streamlit App)

This is a modular version of the Streamlit-based cover letter generator.
It splits logic across multiple files for better maintainability and future extension.

## Folder Structure
```
coverletter_app/
├─ app.py                # Streamlit entry point
├─ requirements.txt
├─ core/
│  ├─ generator.py       # Orchestration and business logic
│  └─ prompt.py          # Prompt construction
├─ services/
│  └─ llm.py             # LLM (OpenAI) client abstraction and mock
├─ utils/
│  ├─ jd.py              # Fetch/Clean job ad text
│  └─ keywords.py        # Keyword extraction & matching
└─ ui/
   └─ layout.py          # Streamlit UI helpers (sidebar, tabs)
```

## Quickstart
```bash
cd cover-letter-app
python -m venv venv && source venv/bin/activate      
pip install -r requirements.txt

# (Optional) set your OpenAI API key to get real model output
export OPENAI_API_KEY="sk-..."                      

streamlit run app.py
```

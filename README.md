# Critic Minds 🧠
> **From Textbook Knowledge to Critical Thinking**

Critic Minds is a GenAI-powered EdTech platform that transforms textbook and lesson content into evidence-grounded critical thinking challenges and evaluates the quality of student reasoning using explicit rubrics.

Built for the 2-Day Hackathon, Critic Minds solves a fundamental classroom problem: instruction and assessments overemphasize rote memorization. Critic Minds converts passive curriculum documents into authentic inquiry situations where students analyze evidence, expose assumptions, and justify conclusions.

---

## 🌟 Key Features

1. **Multi-Format Ingestion**: Ingests **PDF, DOCX, TXT, and PPTX** documents with automatic extraction of page numbers, slide numbers, and section titles.
2. **Pedagogical RAG Pipeline**: In-memory vector database with sentence-aware chunking and semantic retrieval tailored to educational intent.
3. **Traceable Citations**: Every challenge links directly back to specific pages and slides in the uploaded documents.
4. **Three Critical-Thinking Challenge Formats**:
   - **Evidence Analysis**: Evaluate conflicting observations and determine which explanation is best supported.
   - **What-If Challenge**: Predict systemic consequences when a key variable changes.
   - **Case Analysis**: Diagnose an applied problem, weigh alternatives, and defend a decision.
5. **Lightweight AI Quality Assurance**: Pre-review validation checking curriculum alignment, answerability, and rubric consistency.
6. **Teacher Studio**: Full editorial control—teachers can review, modify, regenerate, and approve challenges before students see them.
7. **Rubric-Based Student Reasoning Evaluation**: Assesses *how* students think across multi-dimensional criteria (Evidence use, Logical consistency, Consideration of alternatives) rather than demanding a single fixed answer string.
8. **Flexible Credentials**: Supports both platform-level integrated default AI credentials and user-provided API keys (with password-masked input).

---

## 🏗️ Architecture & Workflow

```text
Teacher Uploads (PDF / DOCX / TXT / PPTX)
        ↓
Unified Extraction & Chunking (Page/Slide/Section Metadata)
        ↓
Vector Indexing & Embeddings (Local Sentence-Transformers / MiniLM)
        ↓
Pedagogical Retrieval Query (Subject + Grade + Topic + Challenge Type)
        ↓
AI Challenge Generator (Gemini Flash / Groq)
        ↓
Lightweight AI Quality Assurance (QA) Audit
        ↓
Teacher Studio (Review, Edit Fields, Regenerate, Approve & Publish)
        ↓
Student Challenge Arena (Scenario, Evidence Citations, Reasoning Question)
        ↓
Student Submits Written Argumentation
        ↓
AI Evaluator (Scores against Rubric Dimensions, Strengths & Improvements)
```

---

## 💻 Local Setup & Installation

Critic Minds requires **Python 3.10+** and runs inside a Python virtual environment.

### 1. Clone & Navigate to Project
```bash
cd Critic_Minds
```

### 2. Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure API Keys (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your API keys (optional, as you can also enter your key directly in the Streamlit UI):
```env
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deployment on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a **New app**.
3. Select your repository, branch, and set the **Main file path** to `app.py`.
4. In **Advanced Settings -> Secrets**, paste your default API keys:
   ```toml
   DEFAULT_LLM_PROVIDER = "gemini"
   GEMINI_API_KEY = "your_gemini_api_key"
   GROQ_API_KEY = "your_groq_api_key"
   ```
5. Click **Deploy!** The application will build and run on free-tier Streamlit Community Cloud with zero server maintenance.

---

## 📂 Project Structure

```text
Critic_Minds/
│
├── app.py                         # Streamlit entry point
├── requirements.txt               # Pinned dependencies
├── requirements.md                # V1 Product & Engineering Specification
├── README.md                      # Documentation
├── .env.example                   # Safe template for environment variables
├── .gitignore                     # Git ignore rules
│
├── app/
│   ├── config.py                  # Secrets and provider configuration
│   │
│   ├── ingestion/                 # Multi-format document ingestion
│   │   ├── pdf.py                 # PyMuPDF/pypdf page extractor
│   │   ├── docx.py                # python-docx section extractor
│   │   ├── txt.py                 # Plain text & markdown decoder
│   │   ├── pptx.py                # python-pptx slide extractor
│   │   └── unified.py             # Standardized chunking with citations
│   │
│   ├── rag/                       # Educational RAG Pipeline
│   │   ├── embeddings.py          # Sentence-transformers embedding generator
│   │   ├── vectorstore.py         # In-memory vector store with cosine similarity
│   │   └── retrieval.py           # Pedagogical query builder & citation formatter
│   │
│   ├── ai/                        # AI Intelligence Layer
│   │   ├── schemas.py             # Pydantic models for Challenge & Rubrics
│   │   ├── providers.py           # Gemini & Groq provider abstraction
│   │   ├── prompts.py             # Grounded prompt templates
│   │   ├── generation.py          # Structured challenge generator
│   │   ├── qa.py                  # AI quality assurance auditor
│   │   └── evaluation.py          # Student reasoning evaluator
│   │
│   └── ui/                        # Streamlit UI Components
│       ├── styles.py              # Custom CSS design system
│       ├── teacher.py             # Teacher Studio (Upload, Config, Review)
│       ├── student.py             # Student Challenge Arena
│       └── settings.py            # AI Provider & API Key management
│
├── data/
│   └── sample_demo.py             # Grade 8 Biology Photosynthesis demo dataset
│
└── tests/
    ├── test_ingestion.py          # Parser unit tests
    ├── test_rag.py                # Vector store & retrieval tests
    └── test_ai.py                 # AI schemas & provider fallback tests
```

---

## 🔬 Testing

Run the automated test suite locally:
```bash
python -m unittest discover tests
```

---

## 🤝 Codebase Reuse & Acknowledgments

This project builds upon and adapts proven components from the `DocuMind-AI` repository (specifically in-memory vector storage, document extraction patterns, and Groq client integration). The team has explicit permission to reuse the DocuMind-AI codebase for the hackathon.

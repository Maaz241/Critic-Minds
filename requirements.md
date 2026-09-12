# Critic Minds — V1 Product & Engineering Requirements

## Document Status

- Product: **Critic Minds**
- Version: **V1 Hackathon MVP**
- Delivery constraint: **2-day hackathon**
- Primary deployment target: **Streamlit Community Cloud / free-tier Streamlit deployment**
- Primary implementation language: **Python**
- Existing reusable codebase: **DocuMind-AI** folder located in the same parent directory as this project when implementation starts
- Source-of-truth documents supplied by the product owner:
  - `Critic Minds.pdf`
  - `Naeem Zafar - From Opportunity to Solution - The AI Startup Recipe[64].pdf`
- Important: the team has permission to reuse the DocuMind-AI codebase.

---

# 1. Agent Instruction

This document is the implementation source of truth for the V1 build.

When this file is provided to an agentic coding platform (for example, Antigravity), the agent MUST:

1. Read this entire file before making implementation changes.
2. Inspect the existing `DocuMind-AI` folder in the same parent directory before designing replacement components.
3. Reuse working DocuMind-AI functionality wherever it already satisfies a requirement.
4. Preserve useful existing functionality instead of rewriting it unnecessarily.
5. Build V1 only. Do not implement deferred V2/V3 features.
6. Create and use a Python virtual environment before installing project dependencies or running the application.
7. Keep all API keys/secrets out of source code and Git.
8. Build the application so it can run locally first and then deploy on free Streamlit hosting.
9. Prefer reliable, simple, hackathon-ready implementations over complicated production architecture.
10. Do not invent unsupported educational content when generating challenges. Ground challenge generation in retrieved document content and clearly show source/page information where available.
11. If an existing DocuMind-AI component conflicts with these requirements, adapt the component rather than silently violating the V1 requirements.
12. Do not introduce paid infrastructure as a required dependency for V1.

---

# 2. Product Definition

## 2.1 Product Name

**Critic Minds**

## 2.2 Tagline

**From Textbook Knowledge to Critical Thinking**

## 2.3 Short Description

Critic Minds is a GenAI-powered EdTech platform that transforms textbook and lesson content into evidence-grounded critical-thinking challenges and evaluates the quality of student reasoning rather than simply checking factual recall.

## 2.4 Core Product Promise

> Critic Minds does not simply generate questions. It converts educational content into structured situations that require students to analyse evidence, question assumptions, consider alternatives, make decisions, and justify conclusions.

## 2.5 Core V1 Loop

```text
Teacher uploads learning material
        ↓
Document ingestion and parsing
        ↓
Chunk + metadata + embeddings
        ↓
RAG retrieval
        ↓
Teacher selects challenge configuration
        ↓
AI generates challenge + evidence + rubric
        ↓
AI quality check
        ↓
Teacher reviews/edits/approves
        ↓
Student sees challenge
        ↓
Student submits reasoning
        ↓
AI evaluates reasoning against rubric
        ↓
Student receives feedback
```

This is the single end-to-end flow that MUST work reliably in V1.

---

# 3. Problem Statement

Classroom instruction and assessment often overemphasize memorization and factual recall. Students may perform well on recall-based examinations while struggling to interpret evidence, defend an argument, consider alternative explanations, apply knowledge in unfamiliar contexts, or reach reasoned conclusions.

Teachers generally understand the importance of critical thinking, but creating high-quality, curriculum-aligned critical-thinking activities for every lesson takes time, subject knowledge, creativity, and assessment expertise.

Critic Minds addresses this by converting existing educational content into curriculum-grounded critical-thinking challenges and by giving teachers an AI-assisted mechanism for evaluating the quality of student reasoning.

---

# 4. V1 Goals

The V1 MVP MUST prove the following hypothesis:

> A teacher can provide existing educational material and quickly receive an editable, curriculum-grounded critical-thinking challenge that can then be attempted by a student and evaluated using an explicit reasoning rubric.

## V1 Goals

1. Support educational content ingestion from **PDF, DOCX/text documents, PPTX/PowerPoint**.
2. Build a working RAG pipeline over uploaded content.
3. Generate critical-thinking challenges rather than ordinary recall questions.
4. Keep generated factual content grounded in retrieved source material.
5. Show teachers which source material was used.
6. Allow teacher review/edit/regeneration before publishing.
7. Let a student submit a written reasoning response.
8. Evaluate reasoning against a generated rubric.
9. Provide actionable feedback to the student.
10. Deploy the entire V1 as a Streamlit application using free/low-cost external AI APIs.
11. Allow the user to supply their own AI API key from the frontend or use a configured default key.
12. Keep implementation simple enough to complete and demonstrate within a 2-day hackathon.

---

# 5. V1 Non-Goals

The following are explicitly OUT OF SCOPE for V1:

- Full LMS functionality.
- School-wide multi-tenant administration.
- Enterprise authentication/SSO.
- Mobile native apps.
- Real-time classroom collaboration.
- Voice/oral-answer assessment.
- Live debate or group discussion tools.
- Advanced learner analytics across semesters.
- Adaptive curriculum generation across many sessions.
- Fine-tuning a foundation model.
- Self-hosting an LLM.
- Building a custom vector database.
- Complex distributed backend services.
- Production-scale infrastructure.
- Full accessibility certification.
- Full localization into many languages.
- Complex role/permission systems.
- All challenge types listed in the long-term concept.

Only the V1 challenge types specified in this document are required.

---

# 6. Target Users

## 6.1 Teacher

The teacher is the primary user in V1.

Teacher needs:

- Fast conversion of teaching content into reasoning activities.
- Control over grade/subject/difficulty/challenge type.
- Source-grounded output.
- Ability to edit before students see the activity.
- Visibility into how the AI used the supplied material.

## 6.2 Student

The student is the secondary user in V1.

Student needs:

- Clear challenge scenario.
- Relevant evidence.
- A structured question requiring reasoning.
- Space to submit a written answer.
- Useful feedback on reasoning quality.

---

# 7. V1 Challenge Types

Implement exactly these three as first-class challenge types:

## 7.1 Evidence Analysis

Student must evaluate evidence and determine which interpretation/claim is best supported.

Must encourage:

- evidence selection;
- evidence relevance;
- interpretation;
- uncertainty;
- alternative explanations;
- justification.

## 7.2 What-If Challenge

Student is presented with a baseline situation and one changed condition, then predicts consequences and justifies them.

Must encourage:

- causal reasoning;
- prediction;
- assumptions;
- consequences;
- alternative outcomes.

## 7.3 Case Analysis

Student examines a realistic case, identifies the main problem, weighs evidence/alternatives, and proposes or justifies a response.

Must encourage:

- problem identification;
- evidence analysis;
- alternatives;
- decision/solution;
- justification.

---

# 8. Supported Input Formats

V1 MUST support:

1. **PDF**
2. **DOCX**
3. **TXT / plain text**
4. **PPTX / PowerPoint**

The frontend upload control should allow these formats.

## 8.1 Unified Content Representation

All formats MUST be converted into a common internal representation before chunking and embedding.

Each content unit/chunk should preserve, where available:

- source filename;
- document type;
- page number for PDF/DOCX where meaningful;
- slide number for PPTX;
- section/title information if available;
- source document ID;
- extracted text;
- chunk index.

Example metadata:

```json
{
  "document_id": "doc_123",
  "filename": "biology_chapter_4.pdf",
  "file_type": "pdf",
  "page": 42,
  "section": "Photosynthesis",
  "chunk_index": 7
}
```

For PPTX:

```json
{
  "document_id": "doc_123",
  "filename": "biology_lesson.pptx",
  "file_type": "pptx",
  "slide": 12,
  "section": "Factors Affecting Photosynthesis",
  "chunk_index": 3
}
```

---

# 9. Document Ingestion Requirements

## 9.1 General Pipeline

```text
Uploaded File
   ↓
File Type Detection
   ↓
Format-specific Extraction
   ↓
Cleaning / Normalization
   ↓
Metadata Attachment
   ↓
Semantic/Text Chunking
   ↓
Embedding Generation
   ↓
Vector Store
```

## 9.2 PDF

Primary extraction:

- PyMuPDF (`fitz`) or the working DocuMind-AI PDF extraction implementation.

For image-heavy/scanned pages:

- detect pages with little/no extractable text;
- optionally render those pages to images;
- use OCR as a fallback.

V1 OCR implementation may use:

- Tesseract/pytesseract, or
- EasyOCR, or
- Gemini vision when available and appropriate.

Do not run OCR unnecessarily on normal text-layer pages.

## 9.3 DOCX

Extract:

- paragraphs;
- headings when available;
- basic table text where practical.

V1 does not require preservation of exact document formatting.

## 9.4 TXT

Read as UTF-8 text where possible. Normalize whitespace and preserve source filename.

## 9.5 PPTX

Extract:

- slide number;
- slide title;
- text boxes;
- bullet points;
- speaker notes if available and easy to access;
- basic table text where practical.

V1 does not require exact recreation of PowerPoint visual layout.

Images/diagrams inside PPTX may be ignored unless a reliable extraction/vision path already exists. Do not block the complete V1 because image interpretation in slides is not perfect.

---

# 10. DocuMind-AI Reuse Requirement

The `DocuMind-AI` folder is provided alongside this project and the team has explicit permission to reuse its code.

The implementation agent MUST inspect the repository first and identify reusable modules.

Likely reusable areas include:

- document extraction;
- chunking;
- embeddings;
- vector storage;
- retrieval/RAG;
- LLM integration;
- FastAPI or application utilities if useful.

The agent MUST NOT duplicate code unnecessarily.

The agent SHOULD adapt working components into Critic Minds rather than rebuild equivalent functionality from scratch.

The product-specific layer that must be added is the educational reasoning workflow:

```text
Generic document RAG
        +
Critical-thinking configuration
        +
Challenge generation
        +
Rubric generation
        +
Teacher review
        +
Student reasoning evaluation
        =
Critic Minds
```

The final application must remain clearly organized as a Critic Minds product rather than a generic document chatbot.

---

# 11. RAG Requirements

## 11.1 Purpose of RAG

RAG is mandatory in V1.

RAG exists to:

- ground generated challenges in teacher-provided curriculum content;
- reduce unsupported factual invention;
- retrieve relevant evidence for challenge construction;
- provide traceable source/page/slide references to the teacher.

RAG MUST NOT be implemented merely as a decorative feature.

## 11.2 Recommended V1 Stack

Preferred stack, subject to compatibility with reused DocuMind code:

- Orchestration: **LlamaIndex**
- Embeddings: **`sentence-transformers/all-MiniLM-L6-v2`**
- Alternative embedding model: **`BAAI/bge-small-en-v1.5`**
- Vector store: **ChromaDB**
- LLM: **Gemini Flash** or **Groq-hosted model**
- PDF extraction: **PyMuPDF**

The agent may retain equivalent DocuMind components if they work correctly and satisfy the functional requirements. Do not change libraries merely for cosmetic reasons.

## 11.3 Chunking

Default target:

- approximately 500–800 tokens per chunk;
- approximately 50–100 tokens overlap.

Preserve source metadata on every chunk.

Use LlamaIndex `SentenceSplitter` or an equivalent reliable splitter already used by DocuMind.

## 11.4 Retrieval

On challenge generation:

1. create retrieval query from the teacher's topic/configuration;
2. retrieve top-k relevant chunks;
3. use metadata filters where possible;
4. construct an evidence context for the LLM;
5. generate the challenge only from the retrieved context plus explicit teacher configuration.

The V1 implementation may use simple semantic top-k retrieval. A reranker is OPTIONAL and should only be added if time remains after the core workflow works.

## 11.5 Source Grounding UI

Generated challenges MUST expose source references.

Example:

```text
Sources used
• Biology Textbook — Page 42
• Biology Textbook — Page 43
• Biology Textbook — Page 44
```

For PPTX:

```text
Sources used
• Biology Lesson.pptx — Slide 12
• Biology Lesson.pptx — Slide 13
```

For DOCX/TXT, show source filename and section/chunk information when page/section is unavailable.

---

# 12. Optional Pedagogy Knowledge Base

V1 SHOULD use simple internal challenge templates/rules rather than building a large external pedagogy RAG database.

Create a lightweight local template/configuration layer for:

- Evidence Analysis;
- What-If;
- Case Analysis;
- reasoning rubric dimensions.

A future version may add a dedicated pedagogy knowledge base.

Do NOT let the pedagogy layer overshadow the curriculum RAG in the 2-day build.

---

# 13. Teacher Configuration UI

The teacher MUST be able to specify:

### Required

- Subject
- Grade/age level
- Topic
- Challenge type
- Difficulty
- Expected completion time

### Optional but desirable

- Language
- Local/international context
- Individual/group mode
- Additional teacher instructions

Suggested UI:

```text
Subject:              [ Biology            ]
Grade:                [ 8                  ]
Topic:                [ Photosynthesis     ]
Challenge Type:       [ Evidence Analysis ▼]
Difficulty:            [ Medium ▼           ]
Time:                 [ 15 minutes         ]
Language:              [ English ▼          ]
Additional direction: [___________________]

                     [ Generate Challenge ]
```

---

# 14. Challenge Generation Requirements

The LLM must receive:

1. retrieved curriculum content;
2. source metadata;
3. grade/age;
4. subject;
5. topic;
6. challenge type;
7. difficulty;
8. expected completion time;
9. teacher instructions.

The model MUST return structured output.

## 14.1 Required Challenge Schema

```json
{
  "title": "string",
  "challenge_type": "evidence_analysis | what_if | case_analysis",
  "grade": "string",
  "difficulty": "easy | medium | hard",
  "estimated_time_minutes": 15,
  "learning_focus": "string",
  "scenario": "string",
  "student_role": "string",
  "central_question": "string",
  "evidence": [
    {
      "text": "string",
      "source": "string",
      "page_or_slide": "string"
    }
  ],
  "task_instructions": ["string"],
  "response_requirements": ["string"],
  "hints": ["string"],
  "extension_question": "string",
  "possible_interpretations": ["string"],
  "rubric": [
    {
      "criterion": "string",
      "description": "string",
      "max_score": 4,
      "weight": 0.25
    }
  ]
}
```

The exact internal schema may be implemented using Pydantic/dataclasses, but the generated output must be validated before display.

---

# 15. Challenge Quality Rules

Every generated challenge SHOULD satisfy all of the following:

1. Grounded in supplied material.
2. Suitable for selected grade/age.
3. Requires reasoning beyond simple recall.
4. Has a clear central question.
5. Includes enough information to be answerable.
6. Does not depend on irrelevant knowledge that was not supplied unless explicitly intended by the teacher.
7. Includes evidence or information students can reason from.
8. Allows a reasoned response rather than requiring one hidden phrase.
9. Does not unnecessarily force one opinion in ethical/case scenarios.
10. Has a coherent rubric.
11. Has source attribution.
12. Avoids unsupported factual claims.

---

# 16. AI Quality Assurance

A post-generation QA step is REQUIRED in V1, but it must remain lightweight.

The QA process should check:

- source grounding;
- curriculum alignment;
- age appropriateness;
- challenge-type correctness;
- clarity;
- answerability;
- reasoning requirement;
- obvious bias/problematic assumptions;
- rubric consistency.

Possible output:

```json
{
  "status": "pass",
  "score": 91,
  "issues": [],
  "regenerate": false
}
```

If QA detects a critical problem:

```text
Generate → QA → Fail → Regenerate once
```

If regeneration still fails, show a clear error and preserve the last valid result rather than looping indefinitely.

---

# 17. Teacher Review Workflow

Teacher MUST be the final decision-maker before publication.

Review screen should contain:

- generated title;
- scenario;
- central question;
- evidence;
- student tasks;
- hints;
- rubric;
- source references;
- QA status/score.

Teacher actions:

- Edit text.
- Approve.
- Regenerate entire challenge.
- Regenerate selected AI-generated text if feasible.
- Cancel.

Minimum V1 requirement: **edit + approve + regenerate entire challenge**.

---

# 18. Student Experience

V1 student flow:

```text
Open Published Challenge
        ↓
Read Scenario
        ↓
Read Evidence
        ↓
Read Central Question / Tasks
        ↓
Write Reasoning
        ↓
Submit
```

Student should be asked to explain reasoning, not merely provide a one-word answer.

Example response prompt:

> Explain your conclusion using the evidence. Mention any alternative explanation you considered and why you accepted or rejected it.

---

# 19. Student Evaluation Requirements

The evaluator receives:

- challenge;
- evidence;
- rubric;
- student response.

The evaluator returns structured scoring and feedback.

## 19.1 Required Evaluation Dimensions

Use the following dimensions where relevant:

1. Problem identification
2. Evidence use/relevance
3. Interpretation/reasoning
4. Consideration of alternatives
5. Logical consistency
6. Conclusion/justification

Not every challenge must show all six if a subset is more appropriate, but V1 SHOULD use a consistent core rubric for predictable evaluation.

## 19.2 Evaluation Schema

```json
{
  "total_score": 14,
  "max_score": 20,
  "criteria": [
    {
      "criterion": "Evidence use",
      "score": 3,
      "max_score": 4,
      "feedback": "string"
    }
  ],
  "strengths": ["string"],
  "improvements": ["string"],
  "overall_feedback": "string"
}
```

## 19.3 Evaluation Philosophy

The system must evaluate reasoning quality, not simple agreement with one preferred opinion.

For example, if a case permits multiple defensible decisions, a well-supported alternative conclusion should still receive credit when the reasoning is strong.

The evaluator must reference evidence and rubric criteria when explaining deductions.

---

# 20. API Key / AI Provider Requirements

This requirement is mandatory.

The Streamlit frontend MUST provide an explicit AI configuration section where the user can either:

### Option A — Use Default Integrated AI

```text
● Use Critic Minds default AI configuration
○ Use my own API key
```

When the default is selected:

- use the configured application-level key/provider from Streamlit Secrets/environment variables;
- never expose that key in the UI or source code;
- if no default key is configured, show a clear configuration error.

### Option B — Enter Own API Key

The user can enter their own API key in the frontend.

Requirements:

- use `st.text_input(..., type="password")` or equivalent secure input;
- never print the key;
- never display the key back to the user;
- never save it to Git;
- do not write it to a persistent file;
- use it only for the current application session where practical;
- clearly indicate which provider the key belongs to.

Supported providers for V1 should be limited to the configured providers actually implemented by the application.

Recommended V1 provider strategy:

1. **Gemini** as the primary default provider.
2. **Groq** as an optional supported provider/fallback if the existing DocuMind integration is already working well.

Do not build multiple complex provider abstractions if they threaten the 2-day delivery. Create a small provider interface so the application can switch providers cleanly.

Example configuration concept:

```python
provider = "gemini"  # or "groq"
api_key = user_key or default_key
```

The actual implementation must validate that a selected provider has a usable key before making a request.

---

# 21. Secrets Management

Never place real keys in:

- Python source code;
- `requirements.md`;
- README;
- Git history;
- committed `.env` files.

Local development should support `.env` or environment variables.

Streamlit deployment should support `.streamlit/secrets.toml` / platform secret configuration.

The repository MUST include a safe template such as:

```text
.env.example
```

containing variable names only.

Example:

```text
GEMINI_API_KEY=
GROQ_API_KEY=
DEFAULT_LLM_PROVIDER=gemini
```

Do not commit actual values.

---

# 22. Virtual Environment Requirement

A Python virtual environment MUST be created and used before dependency installation or execution.

Preferred local setup on Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell equivalent:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Then:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The agent MUST NOT install project packages globally when building the project.

The repository should contain:

```text
.venv/                  # local only, DO NOT commit
requirements.txt
.env.example
.gitignore
```

`.gitignore` MUST include:

```text
.venv/
.env
.streamlit/secrets.toml
__pycache__/
*.pyc
```

---

# 23. Suggested Project Structure

The agent may adapt this based on the existing DocuMind-AI structure, but the final project SHOULD be organized approximately as follows:

```text
critic-minds/
│
├── app.py                         # Streamlit entry point
├── requirements.txt
├── requirements.md
├── README.md
├── .env.example
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── app/
│   ├── ui/
│   │   ├── teacher.py
│   │   ├── student.py
│   │   └── components.py
│   │
│   ├── ingestion/
│   │   ├── pdf.py
│   │   ├── docx.py
│   │   ├── txt.py
│   │   ├── pptx.py
│   │   └── unified.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   ├── retrieval.py
│   │   └── pipeline.py
│   │
│   ├── ai/
│   │   ├── providers.py
│   │   ├── generation.py
│   │   ├── evaluation.py
│   │   ├── qa.py
│   │   └── schemas.py
│   │
│   ├── prompts/
│   │   ├── challenge_generation.txt
│   │   ├── challenge_qa.txt
│   │   └── response_evaluation.txt
│   │
│   └── config.py
│
├── data/
│   └── templates/
│       ├── evidence_analysis.json
│       ├── what_if.json
│       └── case_analysis.json
│
└── tests/
    ├── test_ingestion.py
    ├── test_rag.py
    ├── test_generation.py
    └── test_evaluation.py
```

Do not force this exact tree if DocuMind-AI already has better working modules. Preserve good existing organization where practical.

---

# 24. Streamlit UI Requirements

## 24.1 Application Navigation

Use a simple sidebar or tabs.

Recommended V1 sections:

1. **Home**
2. **Teacher Studio**
3. **Student Challenge**
4. **AI Settings**

Avoid complex navigation.

## 24.2 Home

Display:

- Critic Minds logo/name;
- tagline;
- one-sentence product explanation;
- buttons/links to Teacher Studio and Student Challenge.

## 24.3 Teacher Studio

Contains the full teacher flow:

```text
Upload Material
→ Configure
→ Generate
→ Review
→ Approve/Publish
```

## 24.4 AI Settings

Provide:

- provider selection;
- default vs user-supplied key selection;
- user API key input;
- connection/test button;
- clear status indicator.

Do not expose the default secret value.

## 24.5 Student Challenge

Display:

- title;
- scenario;
- student role;
- evidence;
- source references;
- question;
- tasks;
- hints where appropriate;
- text area for answer;
- submit button;
- feedback after evaluation.

---

# 25. Session State

Because V1 uses Streamlit, use `st.session_state` for the active demo workflow.

The app should be able to hold:

- active document;
- parsed chunks;
- retrieval results;
- generated challenge;
- approved challenge;
- active student response;
- evaluation result;
- active user/provider settings where appropriate.

Do not rely on Streamlit local filesystem persistence for critical long-term data in V1.

---

# 26. Storage Strategy for V1

V1 should prioritize simplicity.

### Vector storage

Use ChromaDB if compatible with the existing DocuMind implementation.

### Runtime state

Use Streamlit session state.

### Permanent application database

NOT REQUIRED for the hackathon MVP.

If a small local persistence mechanism is useful for the demo, it must not be a prerequisite for the app's core workflow.

Do not require Supabase, PostgreSQL, Redis, or another remote database for V1 unless the existing DocuMind code already requires it and it cannot reasonably be removed.

---

# 27. Default AI Configuration

The deployed application MUST have a documented mechanism for configuring a default provider/key through environment variables or Streamlit Secrets.

Example:

```text
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=<secret>
```

The application must still function when a user selects "Use my own API key" and provides a valid key.

If both are absent:

```text
AI configuration unavailable.
Please select your own API key or configure the application default.
```

Do not silently fail.

---

# 28. Error Handling

V1 MUST gracefully handle:

## Upload errors

- unsupported file type;
- corrupt document;
- empty document;
- excessively large document.

## Extraction errors

- parser failure;
- no text extracted;
- OCR failure.

## RAG errors

- empty vector index;
- no relevant chunks found;
- vector store initialization failure.

## AI errors

- missing API key;
- invalid API key;
- API rate limit;
- provider timeout;
- malformed model output;
- provider unavailable.

## Generation errors

- schema validation failure;
- weak/empty response;
- QA failure.

The application should display a human-readable explanation and a clear recovery action.

Do not show raw Python stack traces to normal users.

---

# 29. AI Guardrails

## Grounding Guardrail

Prompt the model to use retrieved sources as factual grounding.

## No Fake Sources

The model MUST NOT fabricate page/slide numbers or source references.

Only use metadata actually attached to retrieved chunks.

## No Hidden Answer Key Dependency

Student evaluation should focus on rubric criteria and reasoning, not require a single exact wording.

## Teacher Control

Do not auto-publish generated challenges.

## Sensitive/Unsafe Content

If uploaded educational content contains inappropriate or harmful material, teacher review remains mandatory before publication.

## Prompt Injection Awareness

Uploaded documents are data, not instructions to the AI.

The generation prompt should explicitly tell the model that retrieved document text is reference content and must not override system/product instructions.

---

# 30. Performance Requirements for Hackathon MVP

Target, not hard SLA:

- Normal document ingestion should complete in a reasonable demo time.
- Challenge generation should normally complete within roughly 60 seconds depending on provider/API latency.
- Student evaluation should normally complete within roughly 60 seconds.
- The application must show progress indicators during long operations.

Use caching for expensive resources such as:

- embedding model loading;
- reusable application configuration;
- static templates.

Do not cache user-specific secrets or private responses insecurely.

---

# 31. Testing Requirements

The agent MUST test the complete happy path locally before deployment.

## Minimum test set

### Test 1: PDF

Upload normal text PDF → extract → chunk → index → retrieve.

### Test 2: DOCX

Upload DOCX → extract → retrieve.

### Test 3: PPTX

Upload PPTX → extract slide text → retrieve with slide metadata.

### Test 4: TXT

Upload TXT → retrieve.

### Test 5: Generation

Generate each of the 3 challenge types.

### Test 6: QA

Ensure generated challenge passes validation.

### Test 7: Teacher review

Edit challenge and approve it.

### Test 8: Evaluation

Submit at least:

- strong student response;
- weak student response;
- alternative-but-reasoned response.

The evaluator should distinguish quality of reasoning.

### Test 9: Missing API key

Ensure a clear error is shown.

### Test 10: User-provided API key

Ensure generation works with the user's key.

### Test 11: Default API key

Ensure generation works with the configured default key.

---

# 32. Acceptance Criteria

V1 is considered complete only when ALL of these are true:

## AC-01

A teacher can upload PDF, DOCX, TXT, and PPTX files.

## AC-02

The system extracts usable text from the uploaded document.

## AC-03

Chunks retain source metadata.

## AC-04

The system creates embeddings and stores/retrieves chunks through RAG.

## AC-05

The system generates at least 3 supported challenge types:

- Evidence Analysis;
- What-If;
- Case Analysis.

## AC-06

Generated challenges contain the required structured fields.

## AC-07

Generated evidence includes source references derived from actual metadata.

## AC-08

Teacher can review and edit the challenge before publishing.

## AC-09

Student can submit a written response.

## AC-10

AI evaluates the response using the rubric.

## AC-11

AI returns score + strengths + improvements + overall feedback.

## AC-12

The application supports default integrated AI credentials through platform secrets/environment variables.

## AC-13

The user can provide their own API key in the Streamlit frontend.

## AC-14

Secrets are not printed, committed, or stored in source files.

## AC-15

The project runs inside a Python virtual environment.

## AC-16

The application runs locally.

## AC-17

The application can be deployed as a Streamlit app on free/community hosting.

## AC-18

The full demo flow works end-to-end without manual backend intervention.

---

# 33. Two-Day Implementation Priority

Because this is a 2-day hackathon, priorities are strict.

## Priority P0 — Must Work

1. Virtual environment.
2. DocuMind-AI inspection/reuse.
3. Streamlit application boot.
4. PDF ingestion.
5. DOCX/TXT/PPTX ingestion.
6. Chunking + metadata.
7. Embeddings.
8. Chroma/RAG retrieval.
9. Gemini/Groq generation.
10. 3 challenge types.
11. Structured challenge output.
12. Teacher review/edit.
13. Student answer.
14. Rubric evaluation.
15. Default/custom API-key selection.
16. Deployment.

## Priority P1 — Add if Stable

1. QA score.
2. Regenerate button.
3. Better source cards.
4. Progress indicators.
5. Cleaner visual design.
6. More robust PPTX extraction.
7. Better OCR fallback.
8. Simple session persistence within one run.

## Priority P2 — Do Not Risk Core Delivery

1. Fancy analytics.
2. Advanced reranker.
3. Long-term student profiles.
4. Authentication.
5. Persistent database.
6. Multi-user collaboration.
7. Complex pedagogy RAG.

If time runs short, P2 features MUST be dropped before any P0 item.

---

# 34. Suggested Demo Dataset

For the hackathon, use one polished educational example rather than many subjects.

Recommended demo:

```text
Subject: Biology
Grade: 8
Topic: Photosynthesis
```

Provide a clean PDF/DOCX/PPTX source document containing enough content to demonstrate retrieval and evidence grounding.

The demo should deliberately show:

- source retrieval;
- a critical-thinking challenge;
- teacher editing;
- a strong student response;
- a weak student response;
- rubric-based evaluation.

---

# 35. UX Principles

The interface should communicate that AI is an assistant, not the final authority.

Use labels such as:

- "AI Generated — Review Required"
- "Sources Used"
- "Teacher Approval Required"
- "Reasoning Feedback"

Avoid language implying that the AI's judgment is infallible.

The teacher should always understand:

```text
What content was retrieved?
What challenge was generated?
Why was it generated?
What sources support it?
What rubric will evaluate it?
```

---

# 36. Optional Transparency Panel

If time permits, add a compact expandable panel:

### Why this challenge?

```text
Learning topic: Photosynthesis
Challenge type: Evidence Analysis
Retrieved sources: 3
Critical-thinking focus: Evidence evaluation
Difficulty: Medium
```

This is valuable for the hackathon demonstration because it visibly connects RAG + pedagogy + generation.

---

# 37. Deployment Requirements

Primary deployment model:

**Streamlit Community Cloud / free Streamlit hosting**

The app should be deployed from GitHub.

Deployment requirements:

- working `app.py` entry point;
- `requirements.txt` complete and reproducible;
- Streamlit secrets documentation;
- no hard-coded secrets;
- no dependency on local absolute paths;
- no dependency on a locally running database service;
- no dependency on a GPU;
- no self-hosted LLM requirement.

The application should be able to start on a clean deployment environment after installing `requirements.txt`.

---

# 38. Reproducibility Requirements

The agent MUST create/update:

## `requirements.txt`

Pin versions sufficiently to make the hackathon deployment stable.

## `.env.example`

Only variable names, no secrets.

## `.gitignore`

Include environment files, virtual environment, caches, secrets, local vector-store artifacts where appropriate.

## `README.md`

Include:

1. Project overview.
2. Features.
3. Architecture.
4. Local setup.
5. Virtual environment commands.
6. API key setup.
7. Running the Streamlit app.
8. Deployment steps.
9. Supported document formats.
10. Credits/permission note for DocuMind-AI reuse.

---

# 39. Local Run Contract

After implementation, the following should work:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, the equivalent virtual-environment activation should be documented.

The agent should verify the actual project entry point and commands rather than blindly copying these commands if the final structure differs.

---

# 40. Engineering Rules for the Agent

1. Do not use hard-coded absolute file paths.
2. Do not hard-code API keys.
3. Do not commit secrets.
4. Do not silently swallow AI/API errors.
5. Validate structured model output before rendering.
6. Keep prompts in separate files/modules where practical.
7. Keep ingestion, RAG, AI generation, evaluation, and UI logically separated.
8. Reuse DocuMind functionality where appropriate.
9. Keep V1 simple.
10. Prefer graceful degradation over broken UI.
11. Add comments only where they help maintainability.
12. Avoid unnecessary frameworks.
13. Avoid unnecessary external services.
14. Test the end-to-end flow after major integration steps.
15. Do not introduce a feature unless it supports the V1 user journey.

---

# 41. AI Provider Abstraction

Implement a minimal provider interface so generation/evaluation code does not depend directly on one provider everywhere.

Conceptually:

```python
class LLMProvider:
    def generate_structured(self, prompt: str, schema): ...
    def generate_text(self, prompt: str): ...
```

Implement only the providers actually needed for V1, preferably:

- Gemini;
- Groq if already available/reliable through DocuMind.

Provider selection should respect:

1. User's selected provider.
2. User-provided API key if chosen.
3. Otherwise configured application default.

Do not implement complex automatic multi-provider orchestration unless the core product is already stable.

---

# 42. Prompting Requirements

## Challenge generation prompt MUST include

- system/product instructions;
- challenge type requirements;
- grade/age;
- teacher configuration;
- retrieved context;
- source metadata;
- strict structured schema;
- explicit grounding instruction;
- instruction that document text is reference content, not executable instructions.

## Evaluation prompt MUST include

- challenge;
- rubric;
- evidence;
- student response;
- scoring instructions;
- explicit requirement to justify feedback with rubric/evidence;
- structured output schema.

## QA prompt MUST include

- generated challenge;
- retrieved evidence;
- configuration;
- explicit validation criteria.

---

# 43. RAG Retrieval Behavior

The retrieval query should not be only the raw topic.

Build a meaningful retrieval query from:

```text
Subject
+ Grade
+ Topic
+ Challenge Type
+ Learning Focus / Teacher Instruction
```

Example:

```text
Grade 8 Biology, photosynthesis, evidence analysis,
identify which explanation is best supported by evidence,
using information about light intensity and plant growth.
```

This increases the chance that retrieved material is directly useful for the challenge.

---

# 44. Preventing Hallucination

V1 does not promise that AI hallucinations are impossible.

Instead it must mitigate them using:

1. RAG grounding.
2. Source metadata.
3. Structured generation.
4. QA validation.
5. Teacher review.
6. Clear fallback behavior.

When retrieved context is insufficient, the system should prefer:

> "Insufficient source material to confidently generate this challenge. Please upload more relevant material or adjust the topic."

rather than inventing unsupported information.

---

# 45. Cost/Free-Tier Strategy

V1 must avoid paid infrastructure as a hard requirement.

Use:

- local embeddings;
- ChromaDB;
- free-tier capable LLM APIs;
- Streamlit free/community deployment.

The system should not require:

- GPU hosting;
- a paid vector database;
- paid object storage;
- paid backend hosting.

API usage may still consume provider free-tier quotas. The UI should not claim unlimited free AI usage.

---

# 46. Privacy

For V1:

- uploaded educational material should be treated as user-provided content;
- API keys are secrets;
- do not expose one user's API key to another session;
- do not log raw API keys;
- avoid unnecessary storage of student personally identifiable information;
- use anonymous/session-based demo student identity if persistent identity is not required.

A production privacy policy is outside V1 scope.

---

# 47. Hackathon Presentation Narrative

The final demo should communicate the following story:

### Problem

Teachers have content but limited time to create high-quality critical-thinking activities.

### Solution

Critic Minds turns existing educational material into evidence-grounded reasoning challenges.

### RAG

The AI retrieves relevant textbook/lesson evidence instead of generating blindly from general model knowledge.

### Teacher Control

The teacher reviews and approves the AI-generated challenge.

### Student Thinking

Students solve a scenario using evidence and justification.

### Assessment

AI evaluates the quality of reasoning against a transparent rubric.

### Differentiator

> **Critic Minds evaluates how students think, not only whether their final answer matches an expected answer.**

---

# 48. Definition of Done

The V1 implementation is DONE only when:

- [ ] Virtual environment created and used.
- [ ] DocuMind-AI inspected and reused where appropriate.
- [ ] PDF ingestion works.
- [ ] DOCX ingestion works.
- [ ] TXT ingestion works.
- [ ] PPTX ingestion works.
- [ ] Metadata is attached to chunks.
- [ ] Embeddings work.
- [ ] Chroma/RAG retrieval works.
- [ ] Challenge generation works.
- [ ] Evidence Analysis works.
- [ ] What-If works.
- [ ] Case Analysis works.
- [ ] Rubric generation works.
- [ ] QA check works.
- [ ] Teacher can edit/approve/regenerate.
- [ ] Student can submit response.
- [ ] Student response evaluation works.
- [ ] Source references appear.
- [ ] Default AI configuration works.
- [ ] User-provided API key works.
- [ ] Secrets are protected.
- [ ] Missing/invalid API keys produce clear errors.
- [ ] App runs locally.
- [ ] App deploys on Streamlit community/free hosting.
- [ ] End-to-end demonstration completes successfully.

---

# 49. Final Implementation Principle

Build **one excellent loop** rather than a large unfinished platform.

The V1 product is:

```text
UPLOAD
  ↓
UNDERSTAND
  ↓
RETRIEVE
  ↓
CHALLENGE
  ↓
REVIEW
  ↓
THINK
  ↓
EVALUATE
  ↓
FEEDBACK
```

Everything that does not strengthen this loop is secondary for the 2-day hackathon.

**End of requirements.md**

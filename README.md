# LAWASSIST
# Indian Legal AI Assistant

AI-powered legal assistant that answers legal questions using Indian law with citations.

Built using Retrieval-Augmented Generation (RAG).

## Features

- Semantic search over Indian laws
- Answers with legal citations
- Chat interface
- Privacy-conscious design

## Tech Stack

Frontend: React  
Backend: Python ,Node.js  
Vector DB: FAISS  
Embeddings: OpenAI / BGE  
LLM: GPT-4 / Ollama

> **Bilingual AI Legal Assistant for Indian Law**  
> RAG-powered legal Q&A and document drafting in Hindi and English

---

## What It Does

LAWASSIST is an AI-powered legal assistant built specifically for the Indian legal system. It does two things:

1. **Legal Q&A** — Ask any question about Indian law and get an answer grounded in actual legal text, with Act and Section citations
2. **Document Drafting** — Generate formal legal documents (bail applications, FIRs) in Hindi or English, with automatic language detection

All answers are grounded in the three new criminal codes that replaced the IPC/CrPC/IEA in 2023.

---

## Legal Data

The system is built on India's three new criminal laws:

| Law | Full Name | Language |
|-----|-----------|----------|
| BNS 2023 | Bharatiya Nyaya Sanhita | English + Hindi |
| BNSS 2023 | Bharatiya Nagarik Suraksha Sanhita | English + Hindi |
| BSA 2023 | Bharatiya Sakshya Adhiniyam | English + Hindi |

Both English and Hindi versions are indexed separately for accurate bilingual retrieval.

---

## Architecture

```
User Query (Hindi or English)
        │
        ▼
Language Detection (langdetect)
        │
        ▼
Bilingual RAG Retrieval
  ├── English: FAISS + bge-small-en
  └── Hindi:   FAISS + multilingual embeddings
        │
        ▼
Context Builder (Act → Chapter → Section)
        │
        ▼
LLM Generation with Retry Pipeline
  ├── Attempt 1: Primary model (aya / mixtral)
  ├── Attempt 2: Fallback model
  └── Attempt 3: Best-of scoring
        │
        ▼
Output Validation & Scoring
  ├── Confession detection (hard fail)
  ├── First-person check
  ├── Repetition check
  ├── Structure validation
  └── Length check
        │
        ▼
Post-Processing (dedup, placeholder removal)
        │
        ▼
Final Legal Document
```

---

## Project Structure

```
LAWASSIST/
│
├── data/
│   ├── raw/              # Raw English legal texts (PDF extracted)
│   ├── clean/            # Cleaned English legal texts
│   ├── raw_hi/           # Raw Hindi legal texts
│   └── clean_hi/         # Cleaned Hindi legal texts
│
├── ingest/               # English data pipeline
│   ├── parse_pdf.py      # PDF → raw text
│   ├── clean_text.py     # Text cleaning
│   ├── chunk_law.py      # Section-aware chunking
│   ├── extract_structure.py
│   └── structure_law.py
│
├── ingest_hi/            # Hindi data pipeline
│   ├── pdf_to_raw_hi.py
│   ├── clean_hi.py
│   └── extract_sections_hi.py
│
├── indexing/
│   ├── build_index.py    # Build English FAISS index
│   └── build_index_hi.py # Build Hindi FAISS index
│
├── retriever/
│   ├── search_law.py     # Core vector search
│   └── retriever_v2.py   # Improved retrieval logic
│
├── rag/
│   ├── retriever.py      # RAG pipeline
│   └── rag_chain.py      # LangChain RAG chain
│
├── llm/
│   ├── ask_law.py        # Legal Q&A with citations
│   └── input_handler.py  # User input collection
│
├── drafting/
│   └── generate_draft.py # Bail application & FIR drafting
│
└── main.py               # Entry point
```

---

## Key Engineering Decisions

### Retry Pipeline with Scoring
Legal documents cannot afford hallucinations. Rather than accepting the first LLM output, the system runs up to 3 attempts and scores each output on:
- Absence of confessional language
- Correct document structure
- No first-person pronouns
- No placeholder text
- Adequate length

The highest-scoring output is returned. If any attempt scores ≥85 with no issues, it returns immediately.

### Model Routing by Language
```python
if lang == "hi":
    primary = "aya"       # Hindi-first model
    fallback = "mixtral"
else:
    primary = "mixtral"   # Strong English model
    fallback = "aya"
```

### Hard Fail on Confession Detection
A legal document that contains confessional language (`स्वीकार`, `गलती`, `पश्चाताप`) is immediately rejected regardless of other scores — simulating the real-world constraint that a bail application must never admit guilt.

### Section-Aware Chunking
Legal text is chunked by Section boundaries, not by token count. Each chunk preserves its `Act → Chapter → Section` metadata, enabling precise citations in answers.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Embeddings | `BAAI/bge-small-en`, multilingual models |
| Vector Store | FAISS |
| LLM (local) | Ollama — DeepSeek-R1, Mixtral, Aya |
| RAG Framework | LangChain |
| Language Detection | langdetect |
| PDF Parsing | Custom pipeline |

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/utkarsh0z0n3/LAWASSIST.git
cd LAWASSIST

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Ollama and pull models
ollama pull deepseek-r1
ollama pull mixtral
ollama pull aya

# 4. Build the indexes (first time only)
python indexing/build_index.py
python indexing/build_index_hi.py

# 5. Run
python main.py
```

---

## Usage

```
Indian Law Assistant

1. Ask a legal question
2. Generate a legal document

> 1
Ask a legal question: What are the bail provisions under BNSS 2023?

Searching law database...
Generating answer...

========== LEGAL ANSWER ==========
Under Section 478 of the Bharatiya Nagarik Suraksha Sanhita, 2023...
===================================
```

---

## Current Status & Roadmap

**Working:**
- [x] English legal Q&A with citations
- [x] Hindi legal Q&A
- [x] Bilingual bail application drafting
- [x] Retry + scoring pipeline
- [x] BNS / BNSS / BSA 2023 indexed in both languages

**In Progress:**
- [ ] Upgrade to multilingual embedding model (`bge-m3`) for better Hindi retrieval
- [ ] Streamlit web UI
- [ ] FIR drafting module
- [ ] OpenAI/Gemini API support for higher quality output

---

## Why This Project

India replaced the IPC, CrPC, and Indian Evidence Act with three new laws in 2023. Most legal AI tools still reference the old codes. LAWASSIST was built specifically on the new legislation — and with bilingual support, since a large proportion of courts and litigants in India operate in Hindi.

---

## Disclaimer

This tool is for informational and educational purposes only. It does not constitute legal advice. Always consult a qualified lawyer for legal matters.

---

## Author

**Utkarsh Saxena** — Full Stack Developer & AI Engineer  
[LinkedIn](https://www.linkedin.com/in/utkarsh-saxena-674459140) · [GitHub](https://github.com/utkarsh0z0n3)

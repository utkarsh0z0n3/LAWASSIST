# Legal AI Assistant – Tech Stack

## Overview
This project builds an AI-powered legal assistant for Indian law using Retrieval-Augmented Generation (RAG).

The system retrieves relevant legal sections from an indexed corpus and uses an LLM to generate answers with citations.

---

# System Architecture

User Query
   ↓
Embedding
   ↓
Vector Database Search
   ↓
Retrieve Relevant Law Sections
   ↓
LLM Prompt
   ↓
Answer with Legal Citations

---

# Frontend

Framework: React / Next.js

Responsibilities:
- Chat interface
- Display answers
- Show legal citations
- Show disclaimers

Libraries:
- React
- Tailwind CSS
- Axios / Fetch API

---

# Backend

Runtime: Node.js

Framework:
- Express.js

Responsibilities:
- Query processing
- Embedding generation
- Retrieval pipeline
- LLM interaction

Libraries:
- LangChain JS
- FAISS
- OpenAI / Ollama SDK

---

# Vector Database

Option 1: FAISS (local)

Advantages:
- Fast
- Free
- Works locally

Stored Data:
- Chunk text
- Embeddings
- Metadata

Metadata includes:
- Act Name
- Section Number
- Section Title

---

# Embeddings

Option 1:
OpenAI text-embedding-3-small

Option 2:
BGE-small (local)

Embedding Dimensions:
1536

Purpose:
Convert legal text into vector representations for semantic search.

---

# Document Processing

Source:
IndiaCode legal PDFs

Tools:
- PyMuPDF
- Regex parsing

Steps:
1. Extract text from PDF
2. Identify section headers
3. Chunk text (~512 tokens)
4. Attach metadata
5. Generate embeddings
6. Store in vector DB

---

# LLM

Options:

OpenAI GPT-4 / GPT-4o

or

Local LLM via Ollama

Responsibilities:
- Read retrieved law chunks
- Generate answer
- Cite relevant sections

---

# RAG Pipeline

Steps:

1. User query received
2. Query converted to embedding
3. Vector search retrieves top K chunks
4. Context assembled
5. LLM prompt constructed
6. LLM generates answer with citations

---

# Security & Privacy

DPDP Compliance (Initial)

Measures:
- HTTPS encryption
- No storage of personal data
- Consent checkbox in UI
- Secure API endpoints

---

# Future Stack (Phase 2)

- Hybrid search (BM25 + Vector)
- Graph database for case relationships
- Case-law corpus
- Fine-tuned legal LLM

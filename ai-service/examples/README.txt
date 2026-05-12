examples/
  rag_qa_samples.json   — sample questions and placeholder answers for POST /ask (RAG).
  bail_draft_samples.json — sample JSON bodies for POST /draft/bail (deterministic templates).

Answers in rag_qa_samples.json are not verified legal advice; replace placeholders after capturing real model output if you use them for regression.

API examples (API on http://127.0.0.1:8000):

  curl -s -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"q":"What does BNSS 2023 say about bail?"}'

For POST /draft/bail, send one JSON object matching BailDraftInput (see bail_draft_samples.json "request" field).

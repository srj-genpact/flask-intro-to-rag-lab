# Lab: Build a Context-Aware RAG Endpoint with Flask

## Overview

You will complete a simplified Retrieval-Augmented Generation, or RAG, endpoint in a Flask API. The endpoint will accept a user question, retrieve relevant context from approved company documents, build a structured prompt, call a local AI model through a provided client function, and return an answer with source information.

You’ll get:

- Starter Flask application files
- A provided document dataset
- TODOs in the files you need to complete
- A pytest test suite that checks the required behavior

Rules:

- Complete the lab individually.
- Use the provided starter files and function names.
- Do not use embeddings, semantic search, vector databases, LangChain, authentication, databases, or deployment tooling.
- Your work is graded by the automated tests.
- The tests should run without requiring Ollama because the model call is mocked in the test suite.

You will be able to:

- Implement simple keyword-based retrieval using RAG concepts.
- Build structured prompts with instructions, context, a user question, and response requirements.
- Coordinate retrieval, prompt construction, generation, and source attribution inside a Flask route.
- Return safe API responses for invalid input, missing context, and model-service errors.

You’ll show it by:

- Completing `rag_service.py` and `app.py` so all tests pass.

How you’ll work:

- Use the Identify → Assemble → Execute → Verify process.
- Start from the API goal, map each file to its responsibility, implement the TODOs, and verify behavior with pytest.

To meet the standard, your work must:

- Pass the provided pytest suite.
- Validate incoming JSON requests.
- Select relevant context based on the user query.
- Build a structured prompt using only retrieved context.
- Return a generated answer with source IDs and titles.
- Return a safe fallback when no relevant context is found.
- Return a helpful service error if the model client fails.

## Scenario

You are a junior backend developer on an internal platform team. Several departments want a small AI-powered assistant that can answer common employee questions using approved company documentation.

Employees ask questions about travel reimbursement, parental leave, API authentication, security incident reporting, software access, and data retention. A standalone model might answer confidently, but it may not know the company’s approved policies or internal technical procedures.

Your task is to complete a simplified RAG endpoint. The endpoint should:

1. Accept an employee or developer question.
2. Retrieve relevant company documentation from `COMPANY_DOCUMENTS`.
3. Build a structured prompt using the selected context.
4. Send the prompt to the provided AI client function.
5. Return the generated answer with source information.

This is an introductory RAG workflow. You are not building production search, embeddings, or a vector database. You are practicing the core flow: query → retrieval → context → prompt → model response → source-backed JSON response.

## Tools and Resources

You need:

- Python
- Pipenv
- Flask
- requests
- pytest
- Ollama with `llama3.2`
- curl, Postman, Insomnia, or another API testing tool

## Setup

Install dependencies:

```bash
pipenv install
pipenv shell
```

Run tests:

```bash
pytest
```

Run the Flask app manually:

```bash
flask --app app run --debug
```

Check the health route:

```bash
curl -i http://127.0.0.1:5000/api/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Your Task

Complete the TODOs in:

- `lib/rag_service.py`
- `lib/app.py`

You should not need to change:

- `lib/company_documents.py`
- `lib/ai_client.py`
- the tests

## Required Endpoint

Create a POST endpoint:

```text
/api/ask
```

It should accept JSON like:

```json
{
  "query": "How do I request software access?"
}
```

For a successful context-backed response, return status code `200` and JSON with this structure:

```json
{
  "query": "How do I request software access?",
  "answer": "...generated answer...",
  "sources": [
    {
      "id": "ops_software_access",
      "title": "Software Access Request Process"
    }
  ]
}
```

For a missing or blank query, return status code `400` and JSON with an `error` message.

For a query that does not match approved documents, return status code `200` and JSON like:

```json
{
  "query": "What is served in the cafeteria today?",
  "answer": "The approved company documents do not contain enough information to answer that question.",
  "sources": []
}
```

For a model-service error, return status code `503` and JSON with an `error` message.

## Implementation Checklist

### Identify

Understand the goal: the endpoint should not send a question directly to the model before retrieving context.

### Assemble

Use the project files by responsibility:

| File | Responsibility |
| --- | --- |
| `company_documents.py` | Stores approved company documents |
| `rag_service.py` | Handles tokenizing, retrieval, prompt construction, and source metadata |
| `ai_client.py` | Sends a prompt to Ollama |
| `app.py` | Coordinates the Flask route and JSON response |
| `tests/` | Verifies required behavior |

### Execute

Complete these functions:

- `tokenize()`
- `document_search_text()`
- `score_document()`
- `retrieve_context()`
- `format_context()`
- `build_prompt()`
- `source_metadata()`
- `/api/ask` route logic in `app.py`

### Verify

Run:

```bash
pytest
```

All tests should pass.

## Notes

The tests mock the AI model call, so you do not need Ollama for automated grading. Ollama is only needed if you want to manually test the full model call locally.

from __future__ import annotations

import re
from typing import Any

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "get",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "me",
    "my",
    "need",
    "of",
    "on",
    "or",
    "our",
    "should",
    "so",
    "the",
    "their",
    "to",
    "use",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
    "you",
    "your",
}


def tokenize(text: str) -> set[str]:
    """Convert text into a set of searchable lowercase tokens.

    TODO:
    - Lowercase the text.
    - Extract word-like values.
    - Remove leading/trailing apostrophes.
    - Remove tokens with length <= 1.
    - Remove tokens in STOPWORDS.
    - Return a set of searchable terms.
    """
    text_lower = text.lower()
    raw_tokens = re.findall(r"[a-z0-9']+", text_lower)
    
    result = set()
    for token in raw_tokens:
        clean_token = token.strip("'")
        if len(clean_token) > 1 and clean_token not in STOPWORDS:
            result.add(clean_token)
            
    return result


def document_search_text(document: dict[str, Any]) -> str:
    """Combine searchable document fields into one text value.

    TODO:
    Include title, category, tags, and text.
    """
    title = document.get("title", "")
    category = document.get("category", "")
    tags = " ".join(document.get("tags", []))
    text = document.get("text", "")
    return f"{title} {category} {tags} {text}"


def score_document(query: str, document: dict[str, Any]) -> dict[str, Any]:
    """Score a document using keyword overlap.

    TODO:
    - Tokenize the query.
    - Tokenize the combined searchable document text.
    - Tokenize the document title.
    - Find matched terms between query tokens and document tokens.
    - Add a small title boost: 0.5 for each query token found in the title.
    - Return a dictionary with keys: document, score, matched_terms.
    """
    query_tokens = tokenize(query)
    doc_text = document_search_text(document)
    doc_tokens = tokenize(doc_text)
    title_tokens = tokenize(document.get("title", ""))
    
    matched_terms = query_tokens.intersection(doc_tokens)
    title_boost_tokens = query_tokens.intersection(title_tokens)
    
    score = float(len(matched_terms)) + 0.5 * len(title_boost_tokens)
    
    return {
        "document": document,
        "score": score,
        "matched_terms": list(matched_terms),
    }


def retrieve_context(
    query: str,
    documents: list[dict[str, Any]],
    limit: int = 2,
    minimum_score: float = 1.0,
) -> list[dict[str, Any]]:
    """Select the most relevant documents for the query.

    TODO:
    - Score all documents.
    - Keep only matches with score >= minimum_score.
    - Sort by score from highest to lowest.
    - Return only the top `limit` matches.

    The selected context must depend on the user's query. Do not return the same
    hardcoded document for every request.
    """
    scored_docs = [score_document(query, doc) for doc in documents]
    filtered_docs = [sd for sd in scored_docs if sd["score"] >= minimum_score]
    filtered_docs.sort(key=lambda x: x["score"], reverse=True)
    return filtered_docs[:limit]


def format_context(context_matches: list[dict[str, Any]]) -> str:
    """Format retrieved documents into a context block for the prompt.

    TODO:
    - If no matches exist, return a short no-context message.
    - For each match, include Source ID, Title, Category, and Content.
    - Separate document blocks clearly.
    """
    if not context_matches:
        return "No relevant context found."
        
    blocks = []
    for match in context_matches:
        doc = match["document"]
        block = (
            f"Source ID: {doc.get('id', '')}\n"
            f"Title: {doc.get('title', '')}\n"
            f"Category: {doc.get('category', '')}\n"
            f"Content: {doc.get('text', '')}"
        )
        blocks.append(block)
        
    return "\n\n---\n\n".join(blocks)


def build_prompt(query: str, context_matches: list[dict[str, Any]]) -> str:
    """Build a structured prompt with instructions, context, question, and requirements.

    TODO:
    The prompt should include these sections:
    - Instructions
    - Context
    - Question
    - Response requirements

    The prompt should tell the model to use only the provided context and avoid
    inventing unsupported details.
    """
    formatted_ctx = format_context(context_matches)
    
    prompt = (
        "Instructions:\n"
        "You are an internal documentation assistant. Use only the provided context to answer the question. "
        "Do not invent or extrapolate any details that are not directly supported by the context.\n\n"
        "Context:\n"
        f"{formatted_ctx}\n\n"
        "Question:\n"
        f"{query}\n\n"
        "Response requirements:\n"
        "- Provide a concise, clear, and direct answer.\n"
        "- Ground your response completely in the provided context.\n"
        "- If the context does not contain enough information to answer the question, state that clearly."
    )
    return prompt


def source_metadata(match: dict[str, Any]) -> dict[str, str]:
    """Return source information that is safe to expose in the API response.

    TODO:
    Return only the document id and title.
    """
    doc = match["document"]
    return {
        "id": doc.get("id", ""),
        "title": doc.get("title", ""),
    }

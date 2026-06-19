from __future__ import annotations

from flask import Flask, jsonify, request

from lib.ai_client import generate_response
from lib.company_documents import COMPANY_DOCUMENTS
from lib.rag_service import build_prompt, retrieve_context, source_metadata


def create_app():
    app = Flask(__name__)

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.post("/api/ask")
    def ask_question():
        """Accept a query and return a source-backed generated answer.

        TODO:
        1. Read JSON request data safely.
        2. Validate that `query` is a non-empty string.
        3. Retrieve relevant context from COMPANY_DOCUMENTS.
        4. If no context is found, return a safe fallback with an empty sources list.
        5. Build a structured prompt from the selected context.
        6. Call generate_response(prompt).
        7. Return query, answer, and sources as JSON.
        8. If generate_response raises RuntimeError, return a 503 service error.
        """
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid or missing JSON data"}), 400

        if "query" not in data:
            return jsonify({"error": "Missing 'query' field in request"}), 400

        query = data["query"]
        if not isinstance(query, str):
            return jsonify({"error": "Field 'query' must be a string"}), 400

        if not query.strip():
            return jsonify({"error": "Field 'query' cannot be blank"}), 400

        context_matches = retrieve_context(query, COMPANY_DOCUMENTS)

        if not context_matches:
            return jsonify({
                "query": query,
                "answer": "I am sorry, but the approved company documents do not contain enough information to answer your question.",
                "sources": []
            }), 200

        prompt = build_prompt(query, context_matches)

        try:
            answer = generate_response(prompt)
        except RuntimeError as e:
            return jsonify({"error": f"Model service error: {str(e)}"}), 503

        sources = [source_metadata(match) for match in context_matches]
        return jsonify({
            "query": query,
            "answer": answer,
            "sources": sources
        }), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

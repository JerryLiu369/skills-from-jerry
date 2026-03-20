#!/usr/bin/env python3
"""
Gemini Search Grounding - performs a single web search via Gemini API.

Usage:
    python3 search.py "your natural language query"
    echo "your query" | python3 search.py

Requires env var: GEMINI_SEARCH_KEY
Optional env var: GEMINI_SEARCH_MODEL (default: gemini-2.5-flash)
"""

import json
import os
import sys
import urllib.error
import urllib.request


def search(query: str) -> None:
    api_key = os.environ.get("GEMINI_SEARCH_KEY", "")
    if not api_key:
        print("Error: GEMINI_SEARCH_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    model = os.environ.get("GEMINI_SEARCH_MODEL", "gemini-2.5-flash")
    base_url = os.environ.get(
        "GEMINI_SEARCH_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta",
    ).rstrip("/")
    url = f"{base_url}/models/{model}:generateContent"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": query}]}],
        "tools": [{"google_search": {}}],
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

    candidates = result.get("candidates", [])
    if not candidates:
        print("No response from Gemini API", file=sys.stderr)
        sys.exit(1)

    candidate = candidates[0]
    parts = candidate.get("content", {}).get("parts", [])
    answer = "".join(p.get("text", "") for p in parts).strip()

    grounding = candidate.get("groundingMetadata", {})
    queries_used = grounding.get("webSearchQueries", [])
    chunks = grounding.get("groundingChunks", [])

    print(answer)

    if queries_used:
        print(f"\n[Search queries: {', '.join(repr(q) for q in queries_used)}]")

    if chunks:
        print("\nSources:")
        seen = set()
        for chunk in chunks:
            web = chunk.get("web", {})
            title = web.get("title", "")
            uri = web.get("uri", "")
            if uri and uri not in seen:
                seen.add(uri)
                label = title if title else uri
                print(f"- [{label}]({uri})")


def main() -> None:
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        query = sys.stdin.read().strip()
    else:
        print("Usage: python3 search.py \"your query\"", file=sys.stderr)
        sys.exit(1)

    if not query:
        print("Error: empty query", file=sys.stderr)
        sys.exit(1)

    search(query)


if __name__ == "__main__":
    main()

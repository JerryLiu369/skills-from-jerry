---
name: gemini-search
description: Real-time web search via Google Search Grounding in the Gemini API. Use when you need up-to-date information from the web. Requires GEMINI_SEARCH_KEY environment variable.
---

# Gemini Web Search

Perform real-time web searches using Google Search Grounding built into the Gemini API. No extra dependencies — stdlib only.

## Usage

```bash
python3 scripts/search.py "your natural language query"
```

Or pipe a query:

```bash
echo "latest Python 3.14 release notes" | python3 scripts/search.py
```

## Environment Variables

| Variable                | Required | Default                        | Description                       |
| ----------------------- | -------- | ------------------------------ | --------------------------------- |
| `GEMINI_SEARCH_KEY`     | Yes      | —                              | Gemini API key                    |
| `GEMINI_SEARCH_BASE_URL`| No       | `https://generativelanguage.googleapis.com/v1beta` | API base URL (proxy or official)  |
| `GEMINI_SEARCH_MODEL`   | No       | `gemini-2.5-flash`             | Model to use for search grounding |

## How it Works

The script calls `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` with `tools: [{ google_search: {} }]`. Gemini autonomously decides when to invoke Google Search, synthesizes the results, and returns a grounded answer with inline citations.

Output format:
```
<synthesized answer from Gemini with grounded facts>

[Search queries: "actual query used by Gemini"]

Sources:
- [Page Title](https://example.com/url)
- [Another Source](https://other.com/url)
```

## Agent Instructions

When using this skill as a coding agent (Claude Code, Codex, etc.):

1. **Locate the script path** — the script is at `scripts/search.py` relative to this SKILL.md.
2. **Check for the API key** — verify `GEMINI_SEARCH_KEY` is set in the environment before running.
3. **Run directly with Bash** — no install step needed, uses Python stdlib only.
4. **Read the output** — the answer text comes first, sources at the end.

### Example invocation

```bash
GEMINI_SEARCH_KEY="$GEMINI_SEARCH_KEY" python3 scripts/search.py "React 19 new hooks"
```

### Error handling

- Missing API key → exits with `Error: GEMINI_SEARCH_KEY environment variable not set`
- HTTP errors → exits with HTTP status and response body
- Empty query → exits with usage message

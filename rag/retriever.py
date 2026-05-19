"""
rag/retriever.py — Lightweight TF-IDF FAQ retriever for VoxCart.

No external dependencies — uses Python stdlib only.
Loads faq.txt once at import time; all retrieval is in-process.
"""

import math
import os
import re
from collections import Counter
from typing import List, Tuple

# ── Load & parse FAQ ──────────────────────────────────────────────────────────

_FAQ_PATH = os.path.join(os.path.dirname(__file__), "faq.txt")


def _parse_faq(path: str) -> List[dict]:
    """Parse faq.txt into a list of {'question': str, 'answer': str, 'text': str} dicts."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    chunks = []
    for block in raw.split("---"):
        block = block.strip()
        if not block:
            continue
        q_match = re.search(r"Q:\s*(.+)", block)
        a_match = re.search(r"A:\s*([\s\S]+)", block)
        if q_match and a_match:
            question = q_match.group(1).strip()
            answer   = a_match.group(1).strip()
            chunks.append({
                "question": question,
                "answer":   answer,
                "text":     f"{question} {answer}".lower(),
            })
    return chunks


_CHUNKS: List[dict] = _parse_faq(_FAQ_PATH)


# ── TF-IDF helpers ────────────────────────────────────────────────────────────

def _tokenise(text: str) -> List[str]:
    """Lowercase, strip punctuation, split on whitespace. Drop tokens < 2 chars."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if len(t) > 1]


def _tf(tokens: List[str]) -> Counter:
    return Counter(tokens)


# Pre-compute IDF once at import time
_N = len(_CHUNKS)
_doc_tokens: List[List[str]] = [_tokenise(c["text"]) for c in _CHUNKS]
_doc_freqs:  List[Counter]   = [_tf(t) for t in _doc_tokens]

# document frequency per term
_df: Counter = Counter()
for tok_list in _doc_tokens:
    for term in set(tok_list):
        _df[term] += 1


def _idf(term: str) -> float:
    df = _df.get(term, 0)
    if df == 0:
        return 0.0
    return math.log((_N + 1) / (df + 1)) + 1.0  # smoothed IDF


def _tfidf_score(query_tokens: List[str], doc_tf: Counter, doc_len: int) -> float:
    """Cosine-style TF-IDF score between query and a document."""
    score = 0.0
    for term in set(query_tokens):
        tf   = doc_tf.get(term, 0) / max(doc_len, 1)
        score += tf * _idf(term)
    return score


# ── Public API ────────────────────────────────────────────────────────────────

def retrieve(query: str, top_k: int = 2) -> List[Tuple[str, str, float]]:
    """
    Return the top_k most relevant FAQ entries for *query*.

    Returns a list of (question, answer, score) tuples, sorted by descending score.
    Entries with score == 0 are excluded.
    """
    q_tokens = _tokenise(query)
    if not q_tokens:
        return []

    scored = []
    for i, chunk in enumerate(_CHUNKS):
        doc_len = len(_doc_tokens[i])
        score   = _tfidf_score(q_tokens, _doc_freqs[i], doc_len)
        if score > 0:
            scored.append((chunk["question"], chunk["answer"], score))

    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]


def retrieve_as_context(query: str, top_k: int = 2) -> str:
    """
    Convenience wrapper: returns retrieved FAQ chunks as a formatted string
    ready to be injected into an LLM prompt or returned as a tool response.
    Returns an empty string if nothing relevant is found.
    """
    results = retrieve(query, top_k=top_k)
    if not results:
        return ""

    lines = []
    for q, a, _ in results:
        lines.append(f"Q: {q}\nA: {a}")
    return "\n\n".join(lines)

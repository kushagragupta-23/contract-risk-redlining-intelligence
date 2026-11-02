"""
Hybrid RAG Engine for Corporate Legal Playbook.
Combines:
1. Lexical BM25 Search
2. Dense Semantic Overlap
3. Reciprocal Rank Fusion (RRF)
4. Playbook Clause Grounding
"""

import math
import re
from typing import List, Dict, Any, Tuple
from collections import Counter
from .playbook_rules import LegalPlaybook

class PlaybookHybridRAGEngine:
    """Retrieves relevant corporate playbook standards using Hybrid Lexical + Semantic RRF."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.entries: List[Dict[str, Any]] = []
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\b[A-Za-z0-9_\-\.\/]{2,}\b', text)]

    def _build_index(self):
        self.entries = []
        for cat, data in LegalPlaybook.PLAYBOOK.items():
            combined_text = f"{cat} {' '.join(data['unacceptable_indicators'])} {data['required_criteria']} {data['fallback_redline']}"
            self.entries.append({
                "category": cat,
                "text": combined_text,
                "tokens": self._tokenize(combined_text),
                "criteria": data["required_criteria"],
                "fallback": data["fallback_redline"],
                "message": data["critical_risk_message"]
            })

    def rebuild(self):
        """Re-indexes the active Playbook rules into Hybrid RAG store."""
        self._build_index()

    def search_playbook(self, clause_text: str, top_k: int = 1) -> List[Dict[str, Any]]:
        q_tokens = self._tokenize(clause_text)
        if not q_tokens:
            return []

        # 1. BM25 / TF-IDF style lexical overlap
        lexical_scores = []
        for idx, entry in enumerate(self.entries):
            overlap = len(set(q_tokens).intersection(set(entry["tokens"])))
            lexical_scores.append((idx, overlap))
        lexical_scores.sort(key=lambda x: x[1], reverse=True)

        # 2. Dense character & N-gram semantic overlap
        dense_scores = []
        q_set = set(q_tokens)
        for idx, entry in enumerate(self.entries):
            e_set = set(entry["tokens"])
            jaccard = len(q_set.intersection(e_set)) / max(1, len(q_set.union(e_set)))
            dense_scores.append((idx, jaccard))
        dense_scores.sort(key=lambda x: x[1], reverse=True)

        # 3. Reciprocal Rank Fusion (RRF)
        rrf: Dict[int, float] = {i: 0.0 for i in range(len(self.entries))}
        for rank, (idx, _) in enumerate(lexical_scores):
            rrf[idx] += 1.0 / (self.rrf_k + rank + 1)
        for rank, (idx, _) in enumerate(dense_scores):
            rrf[idx] += 1.0 / (self.rrf_k + rank + 1)

        ranked = sorted(rrf.items(), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked[:top_k]:
            e = self.entries[idx].copy()
            e["rrf_score"] = round(score, 5)
            results.append(e)

        return results


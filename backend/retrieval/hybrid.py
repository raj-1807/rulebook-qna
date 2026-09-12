"""Hybrid retrieval combining BM25 lexical search and semantic embedding similarity."""
import os
import math
import numpy as np
from typing import Optional
from rank_bm25 import BM25Okapi
from backend.ingestion.ingest import ChunkMetadata
from backend.schemas import EvidenceItem


class HybridRetriever:
    """
    Hybrid retrieval system combining:
    - BM25 (lexical/keyword matching)
    - Sentence-transformer embeddings (semantic similarity)

    Final score = alpha * bm25_normalized + (1-alpha) * semantic_score

    Alpha=0.4 gives slightly more weight to semantic similarity,
    which handles paraphrased questions better while BM25 catches
    exact terminology matches.
    """

    def __init__(self, chunks: list[ChunkMetadata], alpha: float = None, top_k: int = None):
        self.chunks = chunks
        self.alpha = alpha or float(os.getenv("HYBRID_ALPHA", "0.4"))
        self.top_k = top_k or int(os.getenv("RETRIEVAL_TOP_K", "5"))

        # Build BM25 index
        self.tokenized_corpus = [self._tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus) if chunks else None

        # Build embedding index
        self.embeddings = None
        self.model = None
        self._build_embedding_index()

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace + lowercase tokenization for BM25."""
        return text.lower().split()

    def _build_embedding_index(self):
        """Load sentence-transformer model and compute embeddings for all chunks."""
        if not self.chunks:
            return

        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        device = os.getenv("EMBEDDING_DEVICE", "cpu")

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, device=device)
            texts = [c.text for c in self.chunks]
            self.embeddings = self.model.encode(texts, convert_to_numpy=True,
                                                 show_progress_bar=False)
            # Normalize for cosine similarity
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1  # avoid division by zero
            self.embeddings = self.embeddings / norms
            print(f"✓ Embedded {len(texts)} chunks with {model_name}")
        except Exception as e:
            print(f"⚠ Embedding initialization failed: {e}")
            self.embeddings = None

    def retrieve(self, question: str) -> list[EvidenceItem]:
        """Retrieve top-k evidence using hybrid scoring."""
        if not self.chunks:
            return []

        # BM25 scores
        bm25_scores = self._bm25_score(question)

        # Semantic scores
        semantic_scores = self._semantic_score(question)

        # Combine
        hybrid_scores = self._combine_scores(bm25_scores, semantic_scores)

        # Get top-k indices
        top_indices = np.argsort(hybrid_scores)[::-1][:self.top_k]

        # Build evidence items
        evidence = []
        for rank, idx in enumerate(top_indices):
            chunk = self.chunks[idx]
            score = float(hybrid_scores[idx])
            if score <= 0:
                continue
            evidence.append(EvidenceItem(
                evidence_id=f"EV-{rank + 1:03d}",
                chunk_id=chunk.chunk_id,
                document=chunk.filename,
                page=chunk.page,
                section=chunk.section,
                text=chunk.text,
                score=round(score, 4),
            ))

        return evidence

    def _bm25_score(self, question: str) -> np.ndarray:
        """Get BM25 scores for all chunks."""
        if self.bm25 is None:
            return np.zeros(len(self.chunks))

        tokens = self._tokenize(question)
        scores = self.bm25.get_scores(tokens)
        return np.array(scores)

    def _semantic_score(self, question: str) -> np.ndarray:
        """Get semantic similarity scores for all chunks."""
        if self.model is None or self.embeddings is None:
            return np.zeros(len(self.chunks))

        q_emb = self.model.encode([question], convert_to_numpy=True)
        q_norm = np.linalg.norm(q_emb)
        if q_norm > 0:
            q_emb = q_emb / q_norm

        # Cosine similarity (already normalized)
        scores = np.dot(self.embeddings, q_emb.T).flatten()
        return scores

    def _combine_scores(self, bm25_scores: np.ndarray, semantic_scores: np.ndarray) -> np.ndarray:
        """Combine BM25 and semantic scores using min-max normalization."""
        # Normalize BM25 to [0, 1]
        bm25_norm = self._min_max_normalize(bm25_scores)

        # Semantic scores are already cosine similarity in roughly [0, 1]
        # but let's normalize to be safe
        sem_norm = self._min_max_normalize(semantic_scores)

        hybrid = self.alpha * bm25_norm + (1 - self.alpha) * sem_norm
        return hybrid

    def _min_max_normalize(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to [0, 1] range."""
        min_s = scores.min()
        max_s = scores.max()
        if max_s - min_s < 1e-9:
            return np.zeros_like(scores)
        return (scores - min_s) / (max_s - min_s)

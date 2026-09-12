"""Tests for retrieval system."""
import os
import pytest
from backend.ingestion.ingest import CorpusIngestor
from backend.retrieval.hybrid import HybridRetriever


CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")


@pytest.fixture(scope="module")
def retriever():
    """Create a retriever with the full corpus."""
    ingestor = CorpusIngestor(CORPUS_DIR)
    chunks = ingestor.ingest_all()
    return HybridRetriever(chunks)


class TestBM25Retrieval:
    """Test BM25 lexical retrieval."""

    def test_bm25_returns_scores(self, retriever):
        """BM25 should return non-zero scores for relevant queries."""
        import numpy as np
        scores = retriever._bm25_score("attendance requirement")
        assert np.any(scores > 0), "BM25 returned all zero scores"

    def test_bm25_relevant_results(self, retriever):
        """BM25 should rank attendance-related chunks high for attendance queries."""
        import numpy as np
        scores = retriever._bm25_score("minimum attendance percentage")
        top_idx = np.argmax(scores)
        top_chunk = retriever.chunks[top_idx]
        assert "attendance" in top_chunk.text.lower() or "75%" in top_chunk.text


class TestSemanticRetrieval:
    """Test semantic embedding retrieval."""

    def test_semantic_returns_scores(self, retriever):
        """Semantic search should return scores."""
        import numpy as np
        scores = retriever._semantic_score("What is the attendance policy?")
        assert scores is not None
        assert len(scores) > 0

    def test_semantic_relevant_results(self, retriever):
        """Semantic search should find relevant content."""
        import numpy as np
        if retriever.embeddings is None:
            pytest.skip("Embeddings not available")
        scores = retriever._semantic_score("tuition fee amount and deadline")
        top_idx = np.argmax(scores)
        top_chunk = retriever.chunks[top_idx]
        text_lower = top_chunk.text.lower()
        assert any(w in text_lower for w in ["fee", "tuition", "deadline", "payment"])


class TestHybridRetrieval:
    """Test the combined hybrid retrieval."""

    def test_retrieve_returns_evidence(self, retriever):
        """Retrieve should return EvidenceItem objects."""
        evidence = retriever.retrieve("What is the minimum attendance?")
        assert len(evidence) > 0
        assert all(hasattr(e, 'evidence_id') for e in evidence)

    def test_evidence_has_provenance(self, retriever):
        """Evidence items should have full provenance."""
        evidence = retriever.retrieve("hostel gate closing time")
        for e in evidence:
            assert e.document, "Missing document"
            assert e.section, "Missing section"
            assert e.text, "Missing text"
            assert e.score > 0, "Score should be positive"

    def test_evidence_limited_to_top_k(self, retriever):
        """Should return at most top_k results."""
        evidence = retriever.retrieve("examination rules")
        assert len(evidence) <= retriever.top_k

    def test_evidence_sorted_by_score(self, retriever):
        """Evidence should be sorted by descending score."""
        evidence = retriever.retrieve("scholarship eligibility")
        if len(evidence) > 1:
            for i in range(len(evidence) - 1):
                assert evidence[i].score >= evidence[i+1].score

    def test_evidence_ids_format(self, retriever):
        """Evidence IDs should follow EV-XXX format."""
        evidence = retriever.retrieve("fee deadline")
        for e in evidence:
            assert e.evidence_id.startswith("EV-"), f"Invalid evidence ID format: {e.evidence_id}"

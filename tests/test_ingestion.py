"""Tests for document ingestion."""
import os
import pytest
from backend.ingestion.ingest import CorpusIngestor, ChunkMetadata


CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")


class TestCorpusIngestor:
    """Test the corpus ingestion pipeline."""

    def test_corpus_directory_exists(self):
        """The corpus directory should exist."""
        assert os.path.isdir(CORPUS_DIR), f"Corpus directory not found: {CORPUS_DIR}"

    def test_ingest_all_returns_chunks(self):
        """Ingesting the corpus should produce chunks."""
        ingestor = CorpusIngestor(CORPUS_DIR)
        chunks = ingestor.ingest_all()
        assert len(chunks) > 0, "No chunks produced from ingestion"

    def test_chunks_have_provenance(self):
        """Every chunk must have full provenance metadata."""
        ingestor = CorpusIngestor(CORPUS_DIR)
        chunks = ingestor.ingest_all()
        for chunk in chunks:
            assert chunk.document_id, f"Missing document_id in chunk {chunk.chunk_id}"
            assert chunk.filename, f"Missing filename in chunk {chunk.chunk_id}"
            assert chunk.document_type in ("markdown", "pdf", "text"), f"Invalid type: {chunk.document_type}"
            assert chunk.section, f"Missing section in chunk {chunk.chunk_id}"
            assert chunk.chunk_id, f"Missing chunk_id"
            assert chunk.text.strip(), f"Empty text in chunk {chunk.chunk_id}"

    def test_markdown_files_ingested(self):
        """All .md files in corpus should be ingested."""
        ingestor = CorpusIngestor(CORPUS_DIR)
        chunks = ingestor.ingest_all()
        md_files = {f for f in os.listdir(CORPUS_DIR) if f.endswith(".md")}
        ingested_files = {c.filename for c in chunks if c.document_type == "markdown"}
        for md in md_files:
            assert md in ingested_files, f"Markdown file {md} was not ingested"

    def test_pdf_files_ingested(self):
        """PDF files should be ingested with page numbers."""
        ingestor = CorpusIngestor(CORPUS_DIR)
        chunks = ingestor.ingest_all()
        pdf_chunks = [c for c in chunks if c.document_type == "pdf"]
        if not any(f.endswith(".pdf") for f in os.listdir(CORPUS_DIR)):
            pytest.skip("No PDF files in corpus")
        assert len(pdf_chunks) > 0, "No PDF chunks produced"

    def test_pdf_page_metadata(self):
        """PDF chunks must have page numbers."""
        ingestor = CorpusIngestor(CORPUS_DIR)
        chunks = ingestor.ingest_all()
        pdf_chunks = [c for c in chunks if c.document_type == "pdf"]
        for chunk in pdf_chunks:
            assert chunk.page is not None, f"PDF chunk {chunk.chunk_id} missing page number"
            assert chunk.page >= 1, f"Invalid page number {chunk.page}"

    def test_chunk_ids_unique(self):
        """All chunk IDs should be unique."""
        ingestor = CorpusIngestor(CORPUS_DIR)
        chunks = ingestor.ingest_all()
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids)), "Duplicate chunk IDs found"

    def test_chunking_reasonable_size(self):
        """Chunks should not be excessively large or tiny."""
        ingestor = CorpusIngestor(CORPUS_DIR)
        chunks = ingestor.ingest_all()
        for chunk in chunks:
            word_count = len(chunk.text.split())
            assert word_count >= 5, f"Chunk {chunk.chunk_id} too small: {word_count} words"
            assert word_count <= 500, f"Chunk {chunk.chunk_id} too large: {word_count} words"

    def test_to_dict(self):
        """ChunkMetadata.to_dict() should return all fields."""
        chunk = ChunkMetadata(
            document_id="TEST",
            filename="test.md",
            document_type="markdown",
            section="Test Section",
            page=None,
            chunk_id="TEST-C001",
            text="Some test text.",
        )
        d = chunk.to_dict()
        assert d["document_id"] == "TEST"
        assert d["filename"] == "test.md"
        assert d["chunk_id"] == "TEST-C001"

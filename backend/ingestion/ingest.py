"""Document ingestion module - processes corpus files into chunks with provenance."""
import os
import re
import json
from typing import Optional


class ChunkMetadata:
    """Metadata for a single chunk of text."""

    def __init__(self, document_id: str, filename: str, document_type: str,
                 section: str, page: Optional[int], chunk_id: str, text: str):
        self.document_id = document_id
        self.filename = filename
        self.document_type = document_type
        self.section = section
        self.page = page
        self.chunk_id = chunk_id
        self.text = text

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "document_type": self.document_type,
            "section": self.section,
            "page": self.page,
            "chunk_id": self.chunk_id,
            "text": self.text,
        }


class CorpusIngestor:
    """
    Ingests corpus documents (Markdown, PDF, text) into chunks with full provenance.

    Chunking strategy:
    - Section-aware: splits on markdown headers (##, ###) to preserve section boundaries
    - Target chunk size: ~300 words with 50-word overlap
    - Each chunk retains: document_id, filename, type, section, page, chunk_id
    """

    CHUNK_SIZE = 300  # target words per chunk
    CHUNK_OVERLAP = 50  # overlap in words

    def __init__(self, corpus_dir: str):
        self.corpus_dir = corpus_dir
        self.chunks: list[ChunkMetadata] = []

    def ingest_all(self) -> list[ChunkMetadata]:
        """Ingest all files in the corpus directory."""
        self.chunks = []
        if not os.path.isdir(self.corpus_dir):
            raise FileNotFoundError(f"Corpus directory not found: {self.corpus_dir}")

        for filename in sorted(os.listdir(self.corpus_dir)):
            filepath = os.path.join(self.corpus_dir, filename)
            if not os.path.isfile(filepath):
                continue

            if filename.endswith(".md"):
                self._ingest_markdown(filepath, filename)
            elif filename.endswith(".pdf"):
                self._ingest_pdf(filepath, filename)
            elif filename.endswith(".txt"):
                self._ingest_text(filepath, filename)

        return self.chunks

    def _make_document_id(self, filename: str) -> str:
        """Create a stable document ID from filename."""
        name = os.path.splitext(filename)[0]
        return name.upper().replace(" ", "_").replace("-", "_")

    def _ingest_markdown(self, filepath: str, filename: str):
        """Ingest a Markdown file, splitting on headers."""
        doc_id = self._make_document_id(filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        sections = self._split_markdown_sections(content)
        chunk_counter = 0

        for section_title, section_text in sections:
            if not section_text.strip():
                continue
            sub_chunks = self._split_into_chunks(section_text)
            for chunk_text in sub_chunks:
                chunk_counter += 1
                chunk_id = f"{doc_id}-C{chunk_counter:03d}"
                self.chunks.append(ChunkMetadata(
                    document_id=doc_id,
                    filename=filename,
                    document_type="markdown",
                    section=section_title,
                    page=None,
                    chunk_id=chunk_id,
                    text=chunk_text.strip(),
                ))

    def _ingest_pdf(self, filepath: str, filename: str):
        """Ingest a PDF file, preserving page numbers."""
        doc_id = self._make_document_id(filename)
        try:
            from pypdf import PdfReader
        except ImportError:
            print(f"[WARN] pypdf not installed, skipping {filename}")
            return

        try:
            reader = PdfReader(filepath)
        except Exception as e:
            print(f"[WARN] Failed to open PDF {filename}: {e}")
            return

        chunk_counter = 0
        current_section = "General"

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if not text.strip():
                continue

            # Try to detect section headers (lines in bold or ALL CAPS)
            lines = text.split("\n")
            page_sections = self._detect_pdf_sections(lines, current_section)

            for section_title, section_text in page_sections:
                current_section = section_title
                if not section_text.strip():
                    continue
                sub_chunks = self._split_into_chunks(section_text)
                for chunk_text in sub_chunks:
                    chunk_counter += 1
                    chunk_id = f"{doc_id}-P{page_num + 1}-C{chunk_counter:03d}"
                    self.chunks.append(ChunkMetadata(
                        document_id=doc_id,
                        filename=filename,
                        document_type="pdf",
                        section=section_title,
                        page=page_num + 1,
                        chunk_id=chunk_id,
                        text=chunk_text.strip(),
                    ))

    def _ingest_text(self, filepath: str, filename: str):
        """Ingest a plain text file."""
        doc_id = self._make_document_id(filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        chunk_counter = 0
        sub_chunks = self._split_into_chunks(content)
        for chunk_text in sub_chunks:
            chunk_counter += 1
            chunk_id = f"{doc_id}-C{chunk_counter:03d}"
            self.chunks.append(ChunkMetadata(
                document_id=doc_id,
                filename=filename,
                document_type="text",
                section="General",
                page=None,
                chunk_id=chunk_id,
                text=chunk_text.strip(),
            ))

    def _split_markdown_sections(self, content: str) -> list[tuple[str, str]]:
        """Split markdown content into (section_title, section_text) pairs."""
        # Split on ## or ### headers
        pattern = r'^(#{1,3})\s+(.+)$'
        sections = []
        current_title = "General"
        current_text = []

        for line in content.split("\n"):
            match = re.match(pattern, line)
            if match:
                # Save previous section
                if current_text:
                    sections.append((current_title, "\n".join(current_text)))
                current_title = match.group(2).strip()
                current_text = []
            else:
                current_text.append(line)

        # Save last section
        if current_text:
            sections.append((current_title, "\n".join(current_text)))

        return sections

    def _detect_pdf_sections(self, lines: list[str], default_section: str) -> list[tuple[str, str]]:
        """Detect section headers in PDF text lines."""
        sections = []
        current_title = default_section
        current_text = []

        for line in lines:
            stripped = line.strip()
            # Heuristic: lines that are short, upper-case or title-case, and don't end with period
            if (stripped and len(stripped) < 80 and
                (stripped.isupper() or stripped.istitle()) and
                not stripped.endswith(".") and
                    len(stripped.split()) <= 8):
                if current_text:
                    sections.append((current_title, "\n".join(current_text)))
                current_title = stripped.title()
                current_text = []
            else:
                current_text.append(line)

        if current_text:
            sections.append((current_title, "\n".join(current_text)))

        return sections if sections else [(default_section, "\n".join(lines))]

    def _split_into_chunks(self, text: str) -> list[str]:
        """Split text into chunks of approximately CHUNK_SIZE words with overlap."""
        words = text.split()
        if len(words) <= self.CHUNK_SIZE:
            return [text]

        chunks = []
        start = 0
        while start < len(words):
            end = start + self.CHUNK_SIZE
            chunk_words = words[start:end]
            chunks.append(" ".join(chunk_words))
            start = end - self.CHUNK_OVERLAP

        return chunks

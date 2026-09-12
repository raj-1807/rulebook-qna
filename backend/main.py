"""FastAPI application entry point for Rulebook QnA."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Global state
pipeline = None
app_state = {"corpus_loaded": False, "chunks_count": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the pipeline on startup."""
    global pipeline, app_state
    try:
        from backend.ingestion.ingest import CorpusIngestor
        from backend.retrieval.hybrid import HybridRetriever
        from backend.reasoning.classifier import StateClassifier
        from backend.generation.generator import GroundedGenerator
        from backend.pipeline import QnAPipeline

        corpus_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "corpus")
        ingestor = CorpusIngestor(corpus_dir)
        chunks = ingestor.ingest_all()

        retriever = HybridRetriever(chunks)
        classifier = StateClassifier()
        generator = GroundedGenerator()

        pipeline = QnAPipeline(retriever, classifier, generator)
        app_state["corpus_loaded"] = True
        app_state["chunks_count"] = len(chunks)
        print(f"✓ Pipeline initialized with {len(chunks)} chunks")
    except Exception as e:
        print(f"⚠ Pipeline initialization failed: {e}")
        print("  Server running in degraded mode. POST /api/ask will return 503.")

    yield

    pipeline = None
    print("Pipeline shutdown complete.")


app = FastAPI(
    title="Rulebook QnA",
    description="Evidence-grounded university regulations Q&A with three-state reasoning",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.routes import router
app.include_router(router)

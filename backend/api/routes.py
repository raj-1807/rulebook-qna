"""API routes for the Rulebook QnA system."""
from fastapi import APIRouter, HTTPException
from backend.schemas import AskRequest, AskResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from backend.main import app_state
    return HealthResponse(
        status="ok",
        service="rulebook-qna",
        corpus_loaded=app_state.get("corpus_loaded", False),
        chunks_count=app_state.get("chunks_count", 0),
    )


@router.post("/api/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a question about the university regulations.
    Returns one of three states: ANSWERABLE, NOT_FOUND, or CONTRADICTORY.
    """
    from backend.main import pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="System not initialized. Please wait for startup.")

    try:
        result = pipeline.process_question(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

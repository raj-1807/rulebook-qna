"""Pipeline orchestrator that connects retrieval → reasoning → generation."""
from backend.schemas import AskResponse, QuestionState
from backend.retrieval.hybrid import HybridRetriever
from backend.reasoning.classifier import StateClassifier
from backend.generation.generator import GroundedGenerator


class QnAPipeline:
    """
    Main pipeline: Question → Retrieval → Evidence → Reasoning → Generation → Response.
    """

    def __init__(self, retriever: HybridRetriever, classifier: StateClassifier, generator: GroundedGenerator):
        self.retriever = retriever
        self.classifier = classifier
        self.generator = generator

    def process_question(self, question: str) -> AskResponse:
        """Process a question through the full pipeline."""
        # Step 1: Hybrid retrieval
        evidence_items = self.retriever.retrieve(question)

        # Step 2: State classification (ANSWERABLE / NOT_FOUND / CONTRADICTORY)
        classification = self.classifier.classify(question, evidence_items)

        # Step 3: Grounded generation
        response = self.generator.generate(
            question=question,
            state=classification["state"],
            confidence=classification["confidence"],
            evidence=classification["evidence"],
            conflicts=classification.get("conflicts", []),
        )

        return response

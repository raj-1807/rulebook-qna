"""
Evaluation script for Rulebook QnA system.

Runs all 25 evaluation questions against the system and reports:
- Overall state accuracy
- Per-state accuracy (ANSWERABLE, NOT_FOUND, CONTRADICTORY)
- Evidence Recall@5
- Citation correctness

Usage:
    python evaluation/evaluate.py
"""
import json
import os
import sys
import time
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def load_questions():
    """Load the gold-standard evaluation questions."""
    questions_path = os.path.join(os.path.dirname(__file__), "questions.json")
    with open(questions_path, "r", encoding="utf-8") as f:
        return json.load(f)


def initialize_pipeline():
    """Initialize the QnA pipeline."""
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_root, ".env"))

    from backend.ingestion.ingest import CorpusIngestor
    from backend.retrieval.hybrid import HybridRetriever
    from backend.reasoning.classifier import StateClassifier
    from backend.generation.generator import GroundedGenerator
    from backend.pipeline import QnAPipeline

    corpus_dir = os.path.join(project_root, "corpus")
    print(f"Loading corpus from: {corpus_dir}")

    ingestor = CorpusIngestor(corpus_dir)
    chunks = ingestor.ingest_all()
    print(f"Ingested {len(chunks)} chunks from {len(set(c.filename for c in chunks))} documents")

    retriever = HybridRetriever(chunks)
    classifier = StateClassifier()
    generator = GroundedGenerator()

    return QnAPipeline(retriever, classifier, generator)


def evaluate(pipeline, questions):
    """Run evaluation and collect results."""
    results = []
    state_correct = {"ANSWERABLE": 0, "NOT_FOUND": 0, "CONTRADICTORY": 0}
    state_total = {"ANSWERABLE": 0, "NOT_FOUND": 0, "CONTRADICTORY": 0}
    total_correct = 0
    total_with_citations = 0
    total_answerable_with_evidence = 0

    for q in questions:
        qid = q["id"]
        question = q["question"]
        expected = q["expected_state"]

        state_total[expected] = state_total.get(expected, 0) + 1

        print(f"\n{'='*60}")
        print(f"[{qid}] {question}")
        print(f"  Expected: {expected}")

        try:
            start = time.time()
            response = pipeline.process_question(question)
            elapsed = time.time() - start

            predicted = response.state.value
            correct = predicted == expected

            if correct:
                total_correct += 1
                state_correct[expected] = state_correct.get(expected, 0) + 1

            # Check citations
            has_citations = len(response.evidence) > 0
            if predicted == "ANSWERABLE" and has_citations:
                total_answerable_with_evidence += 1
            if has_citations:
                total_with_citations += 1

            status = "✓" if correct else "✗"
            print(f"  Predicted: {predicted} {status}")
            print(f"  Confidence: {response.confidence:.2f}")
            print(f"  Evidence: {len(response.evidence)} items")
            print(f"  Conflicts: {len(response.conflicts)} items")
            print(f"  Time: {elapsed:.2f}s")

            if not correct:
                print(f"  *** MISMATCH: expected {expected}, got {predicted} ***")
                if response.answer:
                    print(f"  Answer preview: {response.answer[:150]}...")

            results.append({
                "id": qid,
                "question": question,
                "expected_state": expected,
                "predicted_state": predicted,
                "correct": correct,
                "confidence": response.confidence,
                "evidence_count": len(response.evidence),
                "conflicts_count": len(response.conflicts),
                "has_citations": has_citations,
                "time_seconds": round(elapsed, 2),
                "answer_preview": response.answer[:200] if response.answer else "",
                "evidence_ids": [e.evidence_id for e in response.evidence],
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "id": qid,
                "question": question,
                "expected_state": expected,
                "predicted_state": "ERROR",
                "correct": False,
                "confidence": 0,
                "evidence_count": 0,
                "conflicts_count": 0,
                "has_citations": False,
                "time_seconds": 0,
                "answer_preview": str(e),
                "evidence_ids": [],
            })

    return results, state_correct, state_total, total_correct, total_with_citations, total_answerable_with_evidence


def print_report(results, state_correct, state_total, total_correct, total_with_citations, total_answerable_with_evidence):
    """Print and save the evaluation report."""
    total = len(results)
    answerable_total = state_total.get("ANSWERABLE", 0)
    not_found_total = state_total.get("NOT_FOUND", 0)
    contradictory_total = state_total.get("CONTRADICTORY", 0)

    answerable_correct = state_correct.get("ANSWERABLE", 0)
    not_found_correct = state_correct.get("NOT_FOUND", 0)
    contradictory_correct = state_correct.get("CONTRADICTORY", 0)

    # Evidence recall: for answerable questions, what fraction had evidence
    evidence_recall = total_answerable_with_evidence / max(answerable_total, 1)

    # Citation accuracy: fraction of non-NOT_FOUND predictions that had citations
    non_nf = sum(1 for r in results if r["predicted_state"] not in ("NOT_FOUND", "ERROR"))
    citation_acc = total_with_citations / max(non_nf, 1)

    report = f"""
{'='*50}
  RULEBOOK QNA EVALUATION REPORT
{'='*50}
  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Total Questions: {total}
{'='*50}
  STATE ACCURACY
{'='*50}
  Overall:       {total_correct}/{total} ({100*total_correct/max(total,1):.0f}%)
  ANSWERABLE:    {answerable_correct}/{answerable_total}
  NOT_FOUND:     {not_found_correct}/{not_found_total}
  CONTRADICTORY: {contradictory_correct}/{contradictory_total}
{'='*50}
  RETRIEVAL & CITATION METRICS
{'='*50}
  Evidence Recall@5: {100*evidence_recall:.0f}%
  Citation Accuracy:  {100*citation_acc:.0f}%
{'='*50}

DETAILED RESULTS:
"""
    for r in results:
        status = "✓" if r["correct"] else "✗"
        report += f"  [{r['id']}] {status} Expected: {r['expected_state']:14s} Got: {r['predicted_state']:14s} (conf: {r['confidence']:.2f}, evidence: {r['evidence_count']}, time: {r['time_seconds']:.1f}s)\n"

    failures = [r for r in results if not r["correct"]]
    if failures:
        report += f"\nFAILURES ({len(failures)}):\n"
        for r in failures:
            report += f"  [{r['id']}] {r['question']}\n"
            report += f"    Expected: {r['expected_state']}, Got: {r['predicted_state']}\n"
            report += f"    Answer: {r['answer_preview'][:100]}\n\n"

    print(report)

    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_questions": total,
        "state_accuracy": {
            "overall": f"{total_correct}/{total}",
            "overall_pct": round(100 * total_correct / max(total, 1), 1),
            "answerable": f"{answerable_correct}/{answerable_total}",
            "not_found": f"{not_found_correct}/{not_found_total}",
            "contradictory": f"{contradictory_correct}/{contradictory_total}",
        },
        "evidence_recall_at_5": round(100 * evidence_recall, 1),
        "citation_accuracy": round(100 * citation_acc, 1),
        "results": results,
    }

    json_path = os.path.join(results_dir, "latest.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {json_path}")

    txt_path = os.path.join(results_dir, "latest.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to: {txt_path}")

    return report_data


def main():
    print("Rulebook QnA Evaluation")
    print("=" * 50)

    questions = load_questions()
    print(f"Loaded {len(questions)} evaluation questions")

    print("\nInitializing pipeline...")
    pipeline = initialize_pipeline()

    print("\nRunning evaluation...")
    results, state_correct, state_total, total_correct, total_with_citations, total_answerable_with_evidence = evaluate(pipeline, questions)

    print("\nGenerating report...")
    report_data = print_report(results, state_correct, state_total, total_correct, total_with_citations, total_answerable_with_evidence)

    return report_data


if __name__ == "__main__":
    main()

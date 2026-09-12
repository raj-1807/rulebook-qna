"""Tests for evidence, citations, and state classification."""
import os
import pytest
from backend.schemas import EvidenceItem, QuestionState, ConflictDetail, AskResponse


class TestEvidenceObjects:
    """Test evidence object structure."""

    def test_evidence_item_creation(self):
        """EvidenceItem should be constructable with all fields."""
        ev = EvidenceItem(
            evidence_id="EV-001",
            chunk_id="REG-C001",
            document="regulations.md",
            page=None,
            section="Attendance Requirements",
            text="Students require 75% attendance.",
            score=0.91,
        )
        assert ev.evidence_id == "EV-001"
        assert ev.score == 0.91
        assert ev.document == "regulations.md"

    def test_evidence_item_with_page(self):
        """PDF evidence should include page number."""
        ev = EvidenceItem(
            evidence_id="EV-002",
            chunk_id="ACAD-P3-C005",
            document="academic_regulations.pdf",
            page=3,
            section="Supplementary Examinations",
            text="Maximum grade is B.",
            score=0.85,
        )
        assert ev.page == 3

    def test_conflict_detail_creation(self):
        """ConflictDetail should hold two evidence items and explanation."""
        rule_a = EvidenceItem(
            evidence_id="EV-001",
            chunk_id="MED-C005",
            document="medical_exemptions.md",
            page=None,
            section="Limitations",
            text="Attendance may not be waived below 60%.",
            score=0.90,
        )
        rule_b = EvidenceItem(
            evidence_id="EV-002",
            chunk_id="REG-C042",
            document="regulations.md",
            page=None,
            section="Academic Committee Powers",
            text="The committee may waive any academic requirement.",
            score=0.88,
        )
        conflict = ConflictDetail(
            rule_a=rule_a,
            rule_b=rule_b,
            explanation="60% floor contradicts committee waiver power.",
        )
        assert conflict.rule_a.evidence_id == "EV-001"
        assert conflict.rule_b.evidence_id == "EV-002"
        assert "contradicts" in conflict.explanation.lower()


class TestAskResponse:
    """Test the ask response model."""

    def test_answerable_response(self):
        """ANSWERABLE response should have state and evidence."""
        resp = AskResponse(
            state=QuestionState.ANSWERABLE,
            confidence=0.91,
            answer="The minimum attendance is 75%.",
            evidence=[
                EvidenceItem(
                    evidence_id="EV-001",
                    chunk_id="REG-C010",
                    document="regulations.md",
                    section="Attendance",
                    text="75% minimum.",
                    score=0.91,
                )
            ],
            conflicts=[],
        )
        assert resp.state == QuestionState.ANSWERABLE
        assert len(resp.evidence) == 1

    def test_not_found_response(self):
        """NOT_FOUND response should have empty evidence."""
        resp = AskResponse(
            state=QuestionState.NOT_FOUND,
            confidence=0.85,
            answer="The regulations do not specify this.",
            evidence=[],
            conflicts=[],
        )
        assert resp.state == QuestionState.NOT_FOUND
        assert len(resp.evidence) == 0

    def test_contradictory_response(self):
        """CONTRADICTORY response should have conflicts."""
        rule_a = EvidenceItem(
            evidence_id="EV-001",
            chunk_id="A",
            document="a.md",
            section="S1",
            text="Rule A text",
            score=0.9,
        )
        rule_b = EvidenceItem(
            evidence_id="EV-002",
            chunk_id="B",
            document="b.md",
            section="S2",
            text="Rule B text",
            score=0.88,
        )
        resp = AskResponse(
            state=QuestionState.CONTRADICTORY,
            confidence=0.9,
            answer="Contradiction found.",
            evidence=[rule_a, rule_b],
            conflicts=[ConflictDetail(rule_a=rule_a, rule_b=rule_b, explanation="Conflict")],
        )
        assert resp.state == QuestionState.CONTRADICTORY
        assert len(resp.conflicts) == 1


class TestCitationFormatting:
    """Test that citations contain required information."""

    def test_evidence_contains_document(self):
        ev = EvidenceItem(
            evidence_id="EV-001",
            chunk_id="C001",
            document="regulations.md",
            section="Attendance",
            text="Some text",
            score=0.9,
        )
        assert ev.document != ""

    def test_evidence_contains_section(self):
        ev = EvidenceItem(
            evidence_id="EV-001",
            chunk_id="C001",
            document="regulations.md",
            section="Attendance Requirements",
            text="Some text",
            score=0.9,
        )
        assert ev.section != ""

    def test_evidence_contains_text(self):
        ev = EvidenceItem(
            evidence_id="EV-001",
            chunk_id="C001",
            document="regulations.md",
            section="Attendance",
            text="Students require 75% attendance.",
            score=0.9,
        )
        assert len(ev.text) > 0

"""Grounded answer generation - only uses supplied evidence, never invents."""
import os
from backend.schemas import AskResponse, EvidenceItem, ConflictDetail, QuestionState


class GroundedGenerator:
    """
    Generates answers ONLY from supplied evidence.

    Rules:
    - ANSWERABLE: answer from evidence, cite sources
    - NOT_FOUND: explicitly refuse, state what's missing
    - CONTRADICTORY: present both rules, explain conflict
    """

    def __init__(self):
        self.llm_client = None
        self._init_llm()

    def _init_llm(self):
        """Initialize the LLM client."""
        provider = os.getenv("LLM_PROVIDER", "google")
        api_key = os.getenv("LLM_API_KEY", "")

        if not api_key:
            print("⚠ No LLM_API_KEY. Generator will use template-based responses.")
            return

        try:
            if provider == "google":
                from google import genai
                self.llm_client = genai.Client(api_key=api_key)
            elif provider == "openai":
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"⚠ LLM init failed for generator: {e}")

    def generate(self, question: str, state: QuestionState,
                 confidence: float, evidence: list[EvidenceItem],
                 conflicts: list[ConflictDetail]) -> AskResponse:
        """Generate a grounded response based on state and evidence."""

        if state == QuestionState.NOT_FOUND:
            answer = self._generate_not_found(question, evidence)
        elif state == QuestionState.CONTRADICTORY:
            answer = self._generate_contradictory(question, evidence, conflicts)
        else:
            answer = self._generate_answerable(question, evidence)

        return AskResponse(
            state=state,
            confidence=confidence,
            answer=answer,
            evidence=evidence,
            conflicts=conflicts,
        )

    def _generate_answerable(self, question: str, evidence: list[EvidenceItem]) -> str:
        """Generate answer from evidence."""
        if self.llm_client is None:
            return self._template_answerable(question, evidence)

        evidence_text = "\n\n".join([
            f"[{e.evidence_id}] From {e.document}, Section: {e.section}" +
            (f", Page: {e.page}" if e.page else "") +
            f"\n\"{e.text}\""
            for e in evidence
        ])

        prompt = f"""You are answering a question about university regulations.
You must ONLY use the evidence provided below. Do NOT use any outside knowledge.
Do NOT invent any rules or citations. If the evidence is unclear, say so.

Question: {question}

Evidence:
{evidence_text}

Provide a clear, direct answer based ONLY on the evidence above.
Reference the source documents and sections in your answer.
Keep the answer concise and factual."""

        try:
            return self._call_llm(prompt)
        except Exception as e:
            return self._template_answerable(question, evidence)

    def _generate_not_found(self, question: str, evidence: list[EvidenceItem]) -> str:
        """Generate a NOT_FOUND response."""
        base = f"The provided university regulations do not contain specific information to answer this question: \"{question}\""

        if evidence:
            related = ", ".join(set(e.section for e in evidence[:2]))
            base += f"\n\nThe closest related sections found were about {related}, but they do not directly address this specific query."

        base += "\n\nPlease consult the university administration for clarification on this matter."
        return base

    def _generate_contradictory(self, question: str, evidence: list[EvidenceItem],
                                 conflicts: list[ConflictDetail]) -> str:
        """Generate a CONTRADICTORY response showing both rules."""
        if self.llm_client is None:
            return self._template_contradictory(question, conflicts)

        conflict_text = ""
        for i, c in enumerate(conflicts):
            conflict_text += f"\nConflict {i+1}:\n"
            conflict_text += f"Rule A [{c.rule_a.evidence_id}] from {c.rule_a.document}, "
            conflict_text += f"Section: {c.rule_a.section}"
            if c.rule_a.page:
                conflict_text += f", Page {c.rule_a.page}"
            conflict_text += f":\n\"{c.rule_a.text}\"\n\n"
            conflict_text += f"Rule B [{c.rule_b.evidence_id}] from {c.rule_b.document}, "
            conflict_text += f"Section: {c.rule_b.section}"
            if c.rule_b.page:
                conflict_text += f", Page {c.rule_b.page}"
            conflict_text += f":\n\"{c.rule_b.text}\"\n"

        prompt = f"""You are reporting a CONTRADICTION found in university regulations.
Two or more rules conflict with each other regarding this question.
Do NOT pick a side. Present BOTH rules and explain the conflict clearly.

Question: {question}

Conflicts found:
{conflict_text}

Explain the contradiction clearly. State both rules and why they conflict.
Advise the student to seek clarification from the relevant university authority."""

        try:
            return self._call_llm(prompt)
        except Exception as e:
            return self._template_contradictory(question, conflicts)

    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM."""
        provider = os.getenv("LLM_PROVIDER", "google")
        model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))

        if provider == "google":
            from google.genai import types
            response = self.llm_client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature, max_output_tokens=800),
            )
            return response.text
        elif provider == "openai":
            response = self.llm_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=800,
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    def _template_answerable(self, question: str, evidence: list[EvidenceItem]) -> str:
        """Template-based answer when LLM is unavailable."""
        parts = [f"Based on the university regulations:\n"]
        for e in evidence[:3]:
            parts.append(f"• According to {e.document} ({e.section}): \"{e.text[:200]}...\"")
        return "\n".join(parts)

    def _template_contradictory(self, question: str, conflicts: list[ConflictDetail]) -> str:
        """Template-based contradiction response."""
        parts = ["⚠ CONTRADICTORY REGULATIONS DETECTED\n"]
        for c in conflicts:
            parts.append(f"Rule A ({c.rule_a.document}, {c.rule_a.section}):")
            parts.append(f'  "{c.rule_a.text[:200]}"')
            parts.append(f"\nRule B ({c.rule_b.document}, {c.rule_b.section}):")
            parts.append(f'  "{c.rule_b.text[:200]}"')
            parts.append(f"\nConflict: {c.explanation}")
        parts.append("\nPlease consult the relevant university committee for clarification.")
        return "\n".join(parts)

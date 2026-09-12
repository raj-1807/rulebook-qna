"""Three-state classifier: ANSWERABLE, NOT_FOUND, CONTRADICTORY."""
import os
import re
from backend.schemas import EvidenceItem, QuestionState, ConflictDetail


class StateClassifier:
    """
    Classifies a question into one of three states based on retrieved evidence.

    Strategy (hybrid rule-based + LLM-assisted):
    1. If top evidence scores are all below a threshold → NOT_FOUND
    2. Use LLM to check if evidence actually answers the question → ANSWERABLE or NOT_FOUND
    3. Use LLM to detect contradictions among evidence → CONTRADICTORY

    The LLM is used as an ASSISTANT for classification, not as the sole decision-maker.
    The structured logic (thresholds, evidence presence) gates the LLM's output.
    """

    NOT_FOUND_THRESHOLD = 0.25  # minimum hybrid score to consider evidence relevant
    CONTRADICTION_MIN_EVIDENCE = 2  # minimum evidence pieces to check for contradictions

    def __init__(self):
        self.llm_client = None
        self._init_llm()

    def _init_llm(self):
        """Initialize the LLM client based on environment config."""
        provider = os.getenv("LLM_PROVIDER", "google")
        api_key = os.getenv("LLM_API_KEY", "")

        if not api_key:
            print("⚠ No LLM_API_KEY set. Classifier will use rule-based fallback only.")
            return

        try:
            if provider == "google":
                from google import genai
                self.llm_client = genai.Client(api_key=api_key)
            elif provider == "openai":
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"⚠ LLM init failed: {e}")

    def classify(self, question: str, evidence: list[EvidenceItem]) -> dict:
        """
        Classify the question state based on evidence.

        Returns dict with: state, confidence, evidence, conflicts
        """
        # Gate 1: No evidence or very low scores → NOT_FOUND
        if not evidence or evidence[0].score < self.NOT_FOUND_THRESHOLD:
            return {
                "state": QuestionState.NOT_FOUND,
                "confidence": 0.9,
                "evidence": [],
                "conflicts": [],
            }

        # Filter to relevant evidence (above threshold)
        relevant = [e for e in evidence if e.score >= self.NOT_FOUND_THRESHOLD]

        if not relevant:
            return {
                "state": QuestionState.NOT_FOUND,
                "confidence": 0.85,
                "evidence": [],
                "conflicts": [],
            }

        # Gate 2: Check for contradictions first (if enough evidence)
        if len(relevant) >= self.CONTRADICTION_MIN_EVIDENCE:
            conflicts = self._detect_contradictions(question, relevant)
            if conflicts:
                return {
                    "state": QuestionState.CONTRADICTORY,
                    "confidence": 0.9,
                    "evidence": relevant,
                    "conflicts": conflicts,
                }

        # Gate 3: Check if evidence actually answers the question
        is_answerable = self._check_answerable(question, relevant)

        if is_answerable:
            return {
                "state": QuestionState.ANSWERABLE,
                "confidence": round(relevant[0].score, 2),
                "evidence": relevant,
                "conflicts": [],
            }
        else:
            return {
                "state": QuestionState.NOT_FOUND,
                "confidence": 0.8,
                "evidence": relevant[:2],  # show what was found but insufficient
                "conflicts": [],
            }

    def _detect_contradictions(self, question: str, evidence: list[EvidenceItem]) -> list[ConflictDetail]:
        """Detect contradictions among evidence pieces using LLM assistance."""
        if self.llm_client is None:
            return self._rule_based_contradiction_check(question, evidence)

        evidence_text = "\n\n".join([
            f"[{e.evidence_id}] From {e.document}, Section: {e.section}" +
            (f", Page: {e.page}" if e.page else "") +
            f"\n\"{e.text}\""
            for e in evidence
        ])

        prompt = f"""You are analyzing university regulations for contradictions.

Question: {question}

Evidence passages:
{evidence_text}

Do any of these passages CONTRADICT each other regarding the question asked?
A contradiction means two rules that cannot both be true when applied to the same situation.

Respond in EXACTLY this format:
CONTRADICTION: YES or NO
If YES, specify:
RULE_A_ID: <evidence_id>
RULE_B_ID: <evidence_id>
EXPLANATION: <one sentence explaining the conflict>

If NO contradictions, just respond:
CONTRADICTION: NO"""

        try:
            response_text = self._call_llm(prompt)
            return self._parse_contradiction_response(response_text, evidence)
        except Exception as e:
            print(f"⚠ LLM contradiction check failed: {e}")
            return self._rule_based_contradiction_check(question, evidence)

    def _check_answerable(self, question: str, evidence: list[EvidenceItem]) -> bool:
        """Check if the evidence actually answers the question."""
        if self.llm_client is None:
            # Rule-based fallback: if top score is high enough, consider answerable
            return evidence[0].score >= 0.35

        evidence_text = "\n\n".join([
            f"[{e.evidence_id}] \"{e.text}\""
            for e in evidence[:3]
        ])

        prompt = f"""You are checking if university regulations contain enough information to answer a question.

Question: {question}

Available evidence from the regulations:
{evidence_text}

Does the evidence contain SPECIFIC information that DIRECTLY answers the question?
Do NOT use general knowledge. Only consider what the evidence explicitly states.

Respond with EXACTLY one word: ANSWERABLE or NOT_FOUND"""

        try:
            response_text = self._call_llm(prompt)
            return "ANSWERABLE" in response_text.upper()
        except Exception as e:
            print(f"⚠ LLM answerable check failed: {e}")
            return evidence[0].score >= 0.35

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
                config=types.GenerateContentConfig(temperature=temperature, max_output_tokens=500),
            )
            return response.text
        elif provider == "openai":
            response = self.llm_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=500,
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    def _parse_contradiction_response(self, response: str, evidence: list[EvidenceItem]) -> list[ConflictDetail]:
        """Parse LLM contradiction detection response."""
        if "CONTRADICTION: NO" in response.upper() or "CONTRADICTION:NO" in response.upper():
            return []

        if "CONTRADICTION: YES" not in response.upper() and "CONTRADICTION:YES" not in response.upper():
            return []

        conflicts = []
        try:
            rule_a_match = re.search(r'RULE_A_ID:\s*(EV-\d+)', response)
            rule_b_match = re.search(r'RULE_B_ID:\s*(EV-\d+)', response)
            explanation_match = re.search(r'EXPLANATION:\s*(.+)', response)

            if rule_a_match and rule_b_match:
                rule_a_id = rule_a_match.group(1)
                rule_b_id = rule_b_match.group(1)
                explanation = explanation_match.group(1).strip() if explanation_match else "Conflicting rules detected."

                rule_a = next((e for e in evidence if e.evidence_id == rule_a_id), None)
                rule_b = next((e for e in evidence if e.evidence_id == rule_b_id), None)

                if rule_a and rule_b:
                    conflicts.append(ConflictDetail(
                        rule_a=rule_a,
                        rule_b=rule_b,
                        explanation=explanation,
                    ))
        except Exception:
            pass

        return conflicts

    def _rule_based_contradiction_check(self, question: str, evidence: list[EvidenceItem]) -> list[ConflictDetail]:
        """Simple rule-based contradiction detection as fallback."""
        # Check if evidence comes from different sections/documents and contains
        # opposing numerical values or keywords
        conflicts = []
        question_lower = question.lower()

        for i in range(len(evidence)):
            for j in range(i + 1, len(evidence)):
                a = evidence[i]
                b = evidence[j]
                # Different sections or documents are candidates
                if a.section != b.section or a.document != b.document:
                    # Look for numerical disagreements about percentages
                    a_percents = re.findall(r'(\d+)%', a.text)
                    b_percents = re.findall(r'(\d+)%', b.text)
                    if a_percents and b_percents:
                        # Check if they reference similar topics but different values
                        a_text_lower = a.text.lower()
                        b_text_lower = b.text.lower()
                        common_keywords = set(question_lower.split()) & set(a_text_lower.split()) & set(b_text_lower.split())
                        if len(common_keywords) >= 2 and set(a_percents) != set(b_percents):
                            conflicts.append(ConflictDetail(
                                rule_a=a,
                                rule_b=b,
                                explanation=f"Different percentage values found: {a_percents} vs {b_percents}",
                            ))
                            return conflicts[:1]  # Return first conflict found

        return conflicts

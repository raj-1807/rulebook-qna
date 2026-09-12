# Rulebook QnA — Demo Script

This document provides three demo questions to showcase the three states of the Rulebook QnA system.

---

## Demo 1: ANSWERABLE

**Question:**
```
What is the minimum attendance requirement for regular students?
```

**Expected State:** ANSWERABLE

**Expected Evidence:**
- From `regulations.md`, Section 3.1 — Minimum Attendance
- Passage: "Students are required to maintain a minimum of 75% attendance in each course."

**What to Point Out:**
1. The system retrieves the exact passage from the regulations.
2. The source document, section, and text are clearly cited.
3. The answer is grounded entirely in the evidence — no hallucination.

---

## Demo 2: NOT_FOUND

**Question:**
```
Can a student miss an exam because of a family wedding?
```

**Expected State:** NOT_FOUND

**Expected Evidence:**
- The system may retrieve related content about exam absence (Section 4.3, 4.4) but these only cover unapproved absence and medical absence.
- No policy covers family events as grounds for exam absence.

**What to Point Out:**
1. The system does NOT make up an answer about family events.
2. It correctly identifies that the regulations only discuss medical absence, not family events.
3. The response clearly states that the regulations do not address this specific situation.
4. It recommends consulting the university administration.

---

## Demo 3: CONTRADICTORY ⭐ (Most Important)

**Question:**
```
Can the Academic Committee waive the 60% minimum attendance requirement for a student with a severe medical condition?
```

**Expected State:** CONTRADICTORY

**Expected Evidence:**
- **Rule A:** From `medical_exemptions.md`, Section 2.4: "attendance may not be waived below 60% under any circumstances"
- **Rule B:** From `regulations.md`, Section 11.2: The Academic Committee can "waive any academic requirement" in cases of manifest injustice

**What to Point Out:**
1. The system detects that two rules **directly conflict** on this question.
2. Both rules are displayed side-by-side with full source citations.
3. The conflict explanation clearly articulates why these rules are incompatible.
4. The system does NOT silently pick one rule over the other.
5. This is the core differentiator — a normal chatbot would just give one answer and ignore the contradiction.

---

## Additional Demo Questions (Optional)

### Contradiction Demo 2:
```
Can a student with an approved medical exemption who has 70% attendance retain their merit scholarship?
```
Shows the scholarship attendance (85%) vs medical exemption attendance (60%) conflict.

### Contradiction Demo 3:
```
If a student appeals a registration suspension due to non-payment of fees, can they continue attending classes while the appeal is pending?
```
Shows the fee suspension (no classes) vs appeal interim measures (enrollment preserved) conflict.

---

## Running the Demo

```bash
# Start backend
cd rulebook-qna
uvicorn backend.main:app --reload

# Start frontend (in another terminal)
cd rulebook-qna/frontend
npm run dev

# Open browser to http://localhost:5173
```

For each demo question, copy the exact question text, paste it into the interface, and click "Ask." Wait for the response and point out the relevant features described above.

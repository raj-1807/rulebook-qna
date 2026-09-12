# Deliberate Contradictions in the Greenfield University Corpus

This document records the three (3) intentional contradictions planted in the corpus for testing the system's contradiction detection capability.

---

## Contradiction 1: Attendance Floor vs. Committee Waiver Authority

**ID:** CONTRA-001

**Document A:** `medical_exemptions.md`
**Section A:** Section 2.4 — Limitations on Medical Attendance Exemption
**Exact Passage A:**
> "The reduced attendance requirement of 60% is the absolute minimum; attendance may not be waived below 60% under any circumstances."

**Document B:** `regulations.md`
**Section B:** Section 11.2 — Powers of the Academic Committee
**Exact Passage B:**
> "The Academic Committee has the authority to: ... Waive any academic requirement when the committee determines that strict application would result in manifest injustice, provided that a two-thirds majority of the committee members present approve the waiver."

**Explanation:** The medical exemptions policy establishes 60% as an absolute floor that cannot be waived "under any circumstances." However, the general academic regulations grant the Academic Committee the power to "waive any academic requirement" in cases of manifest injustice. These two provisions directly conflict: can the Academic Committee waive the 60% minimum, or is it truly absolute?

**Related Evaluation Question:** "Can the Academic Committee waive the 60% minimum attendance requirement for a student with a severe medical condition?"

---

## Contradiction 2: Scholarship Attendance Requirement vs. Medical Exemption Attendance

**ID:** CONTRA-002

**Document A:** `fee_schedule.md`
**Section A:** Section 4.2 — Scholarship Eligibility
**Exact Passage A:**
> "To be eligible for a merit scholarship, a student must: ... Maintain a minimum attendance of 85% across all courses."

**Document B:** `medical_exemptions.md`
**Section B:** Section 2.1 — Medical Attendance Exemption
**Exact Passage B:**
> "Upon approval, the minimum attendance threshold shall be reduced to 60% for the affected courses during the period of the medical condition."

**Explanation:** A student with an approved medical exemption has their minimum attendance reduced to 60%. However, scholarship eligibility requires 85% attendance. The regulations do not specify whether the scholarship attendance requirement is also adjusted for students with medical exemptions, nor whether the medical exemption policy supersedes the scholarship requirement. A student with a medical condition who attends 70% of classes meets the medical exemption threshold but not the scholarship requirement — and the regulations are silent on which rule prevails.

**Related Evaluation Question:** "Can a student with an approved medical exemption who has 70% attendance retain their merit scholarship?"

---

## Contradiction 3: Late Fee Deadline Consequences vs. Exam Eligibility

**ID:** CONTRA-003

**Document A:** `fee_schedule.md`
**Section A:** Section 2.2 — Non-Payment
**Exact Passage A:**
> "Students who fail to pay all required fees by the late deadline shall have their registration suspended. A suspended student: May not attend classes. May not access laboratory facilities. May not appear in examinations. Will not receive grades for the semester."

**Document B:** `regulations.md`
**Section B:** Section 12.4 — Interim Measures (Appeals)
**Exact Passage B:**
> "During the pendency of an appeal, the student's enrollment status shall not be altered unless there are safety concerns. The student may continue attending classes pending the outcome of the appeal."

**Explanation:** If a student's registration is suspended for non-payment and the student appeals the suspension, the appeals regulation (Section 12.4) states that enrollment status "shall not be altered" and the student "may continue attending classes" during the appeal. However, the fee schedule explicitly states the student "may not attend classes" while registration is suspended. These provisions conflict on whether a student with a fee-related suspension can continue attending classes while their appeal is being processed.

**Related Evaluation Question:** "If a student appeals a registration suspension due to non-payment of fees, can they continue attending classes while the appeal is pending?"

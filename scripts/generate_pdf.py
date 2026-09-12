"""Script to generate the academic_regulations.pdf corpus file using fpdf2."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_pdf():
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    def nl(h=8):
        pdf.cell(0, h, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_title_page():
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 24)
        nl(40)
        pdf.cell(0, 15, "GREENFIELD UNIVERSITY", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "Academic Regulations", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.cell(0, 12, "Supplementary Provisions", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.set_font("Helvetica", "", 12)
        nl(20)
        pdf.cell(0, 8, "Academic Year 2025-2026", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.cell(0, 8, "Approved by the Academic Council", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.cell(0, 8, "Resolution AC-2025-031", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.cell(0, 8, "Effective: August 1, 2025", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    def add_section(title, content_lines):
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 12, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 10)
        for line in content_lines:
            if line.startswith("SUBSECTION:"):
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 8, line.replace("SUBSECTION:", "").strip(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Helvetica", "", 10)
            elif line == "---":
                nl(4)
            else:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(w=pdf.epw, h=6, text=line)
        nl(4)

    add_title_page()

    # Page 2
    pdf.add_page()
    add_section("SUPPLEMENTARY EXAMINATION REGULATIONS", [
        "These supplementary provisions extend and clarify the examination regulations set forth in the General Academic Regulations document.",
        "---",
        "SUBSECTION: S1. Examination Scheduling",
        "End-semester examinations shall be scheduled by the Controller of Examinations at least thirty (30) days before the examination period begins. The examination timetable shall be published on the University Portal and displayed on departmental notice boards.",
        "---",
        "No student shall be required to sit for more than two (2) examinations on the same day. If a scheduling conflict arises, the student must notify the Controller of Examinations at least fifteen (15) days before the examination, and an alternative date shall be arranged.",
        "---",
        "SUBSECTION: S2. Examination Hall Conduct",
        "Students must arrive at the examination hall at least fifteen (15) minutes before the scheduled start time. Late arrival up to thirty (30) minutes after the start time is permitted, but no additional time shall be granted. Students arriving more than thirty minutes late shall not be permitted to sit for the examination.",
        "---",
        "The following items are prohibited in the examination hall: mobile phones, smart watches, electronic devices (except approved calculators), notes, textbooks (unless the examination is designated as open-book), and any unauthorized material.",
        "---",
        "SUBSECTION: S3. Examination Malpractice",
        "Any student found engaging in examination malpractice shall be immediately expelled from the examination hall. The invigilator shall prepare a written report and submit it to the Controller of Examinations within twenty-four (24) hours.",
    ])

    add_section("GRADE IMPROVEMENT POLICY", [
        "SUBSECTION: S4. Grade Improvement Examinations",
        "Students who have passed a course with a grade of C or below may apply for a grade improvement examination.",
        "---",
        "Conditions: (a) Application must be submitted within the first four weeks of the semester following the original examination.",
        "(b) A grade improvement fee of Rs. 2,000 per course shall be payable.",
        "(c) A maximum of two courses may be attempted for grade improvement in any semester.",
        "(d) The higher of the original grade and the improvement examination grade shall be recorded.",
        "(e) Grade improvement examinations are available only for courses taken within the preceding two semesters.",
        "---",
        "SUBSECTION: S5. Supplementary Examinations",
        "Supplementary examinations are available for students who have failed a course (grade F or FA). The supplementary examination covers the same syllabus as the original end-semester examination.",
        "---",
        "To be eligible for a supplementary examination, the student must: (a) Have attended a minimum of 75% of classes in the original course offering. (b) Have completed all continuous assessment components. (c) Apply within two weeks of the publication of results. (d) Pay the supplementary examination fee of Rs. 1,500 per course.",
        "---",
        "The maximum grade achievable through a supplementary examination is B (6 grade points). Students who fail the supplementary examination must re-register for the course.",
    ])

    # Page 3
    pdf.add_page()
    add_section("RESEARCH AND PROJECT WORK REGULATIONS", [
        "SUBSECTION: S6. Final Year Project",
        "All undergraduate students in their final year must complete a capstone project or thesis as part of their degree requirements. The project carries a minimum of 6 credit hours and a maximum of 12 credit hours.",
        "---",
        "Each student shall be assigned a faculty supervisor by the Head of Department. The supervisor-to-student ratio shall not exceed 1:5 for project supervision.",
        "---",
        "SUBSECTION: S7. Project Evaluation",
        "Final year projects are evaluated through: (a) Interim review presentation with 20% weightage, conducted midway through the project duration. (b) Final project report with 40% weightage, submitted at least two weeks before the end-semester examination. (c) Final presentation and viva voce with 40% weightage, conducted by a panel of at least three faculty members.",
        "---",
        "SUBSECTION: S8. Plagiarism in Projects",
        "All final year project reports must be submitted through a plagiarism detection system. A similarity index exceeding 20% (excluding bibliography and properly cited quotations) shall require the student to revise and resubmit. A similarity index exceeding 40% shall be treated as academic dishonesty.",
    ])

    add_section("INTERNSHIP AND INDUSTRY COLLABORATION", [
        "SUBSECTION: S9. Mandatory Internship",
        "Students in programs requiring a mandatory internship must complete a minimum of eight weeks of full-time internship at an approved organization, between the third year and the final year.",
        "---",
        "The internship is evaluated based on: (a) Supervisor evaluation from the host organization at 30%. (b) Internship report submitted by the student at 40%. (c) Presentation to the departmental internship committee at 30%.",
        "---",
        "SUBSECTION: S10. Internship Attendance",
        "The attendance requirement during internship is governed by the host organization's policies. However, the student must complete at least 90% of the scheduled internship duration.",
        "---",
        "SUBSECTION: S11. Industry-Sponsored Projects",
        "Students may undertake industry-sponsored projects as part of their final year project with approval from the Head of Department. A faculty supervisor must be assigned. Intellectual property agreements must be executed before the project begins.",
    ])

    # Page 4
    pdf.add_page()
    add_section("CONTINUING EDUCATION AND CERTIFICATE PROGRAMS", [
        "SUBSECTION: S12. Certificate Programs",
        "Greenfield University offers certificate programs in various disciplines. Certificate programs consist of a minimum of 12 credit hours of coursework designed to complement the student's primary degree program.",
        "---",
        "Credits earned in certificate programs may count toward the degree requirements if the courses are relevant to the student's program of study.",
        "---",
        "SUBSECTION: S13. Online and Hybrid Courses",
        "Select courses may be offered in online or hybrid format. For online courses, attendance is measured through: (a) Completion of weekly online modules with a minimum 80% completion rate required. (b) Participation in scheduled synchronous sessions with minimum 75% attendance required. (c) Timely submission of online assessments.",
        "---",
        "SUBSECTION: S14. Summer and Winter Sessions",
        "Intensive courses may be offered during summer (June-July) and winter (December-January) sessions. Each session consists of four weeks of instruction. The attendance requirement for summer and winter courses is 85% due to the compressed format.",
        "---",
        "A maximum of two courses may be taken per summer or winter session. Fees for summer and winter courses are charged separately at Rs. 5,000 per credit hour.",
    ])

    add_section("CONVOCATION AND DEGREE AWARD", [
        "SUBSECTION: S15. Degree Requirements",
        "To be eligible for the award of a degree, a student must have: (a) Completed all required credits. (b) Achieved a CGPA of 4.0 or above. (c) Completed the mandatory internship if required. (d) Cleared all financial dues. (e) No pending disciplinary actions.",
        "---",
        "SUBSECTION: S16. Degree Classification",
        "Degrees are classified as: First Class with Distinction for CGPA 8.0 and above. First Class for CGPA 6.5 to 7.99. Second Class for CGPA 5.0 to 6.49. Pass for CGPA 4.0 to 4.99.",
        "---",
        "SUBSECTION: S17. Convocation Ceremony",
        "The annual convocation ceremony is held in November. Students who have completed all degree requirements by September 30 are eligible to participate. In absentia degree conferral is available with an application submitted at least fifteen days before the ceremony.",
    ])

    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "corpus", "academic_regulations.pdf")
    pdf.output(output_path)
    print(f"Generated: {output_path}")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    generate_pdf()

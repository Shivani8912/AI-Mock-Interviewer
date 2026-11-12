"""
Automated unit and integration test suite for AI Mock Interviewer.
"""

import sys
from utils.resume_parser import parse_resume, extract_text_from_pdf, extract_text_from_docx
from utils.ai_client import get_ai_client
from utils.interview_engine import InterviewEngine
from utils.audio_utils import get_speech_html


def test_resume_parser():
    print("Testing Resume Parser...")
    sample_text = """
    Jane Doe
    Software Engineer | jane@example.com | 123-456-7890 | github.com/janedoe
    SKILLS:
    Languages: Python, JavaScript, TypeScript, SQL
    Frameworks: React, Node.js, FastAPI, Django
    Databases: PostgreSQL, Redis, MongoDB
    Cloud & Tools: AWS, Docker, Kubernetes, Git, CI/CD
    EXPERIENCE:
    Senior Developer - Built scalable microservices using FastAPI and PostgreSQL.
    Architected React frontend with Redux.
    """
    res = parse_resume(sample_text, "test_resume.txt")
    assert res["success"] is True, "Parsing failed"
    assert res["candidate_name"] == "Jane Doe", f"Expected Jane Doe, got {res['candidate_name']}"
    assert res["contact_info"]["email"] == "jane@example.com"
    assert len(res["top_skills"]) > 5, "Skills extraction should find multiple skills"
    assert len(res["recommended_roles"]) > 0, "Should generate role recommendations"
    top_role = res["recommended_roles"][0]
    print(f"  ✓ Top recommended role: {top_role['role']} ({top_role['match_score']}% match)")
    print("  ✓ Resume Parser passed successfully!\n")


def test_ai_client_and_engine():
    print("Testing AI Client & Interview Engine...")
    engine = InterviewEngine()

    # 1. Opening Question
    q1 = engine.generate_opening_question(
        candidate_name="Jane Doe",
        role="Full Stack Developer",
        level="Mid-Level",
        interview_type="Technical",
        skills=["Python", "React", "PostgreSQL", "AWS"]
    )
    assert "question" in q1, "Opening question missing"
    assert "ideal_answer" in q1, "Ideal answer missing"
    print(f"  ✓ Opening Question generated: {q1['question'][:60]}...")

    # 2. Next Question
    qa_history = [{
        "question": q1["question"],
        "answer": "In my previous project, I used React with Redux for state management and built the backend with FastAPI and PostgreSQL.",
        "ideal_answer": q1["ideal_answer"]
    }]

    q2 = engine.generate_next_question(
        role="Full Stack Developer",
        level="Mid-Level",
        interview_type="Technical",
        question_index=1,
        total_questions=5,
        skills=["Python", "React", "PostgreSQL"],
        previous_qa=qa_history
    )
    assert "question" in q2, "Next question missing"
    print(f"  ✓ Adaptive Next Question generated: {q2['question'][:60]}...")

    # 3. Session Evaluation
    qa_history.append({
        "question": q2["question"],
        "answer": "We mitigated race conditions by using database row-level locking and Redis distributed locks.",
        "ideal_answer": q2.get("ideal_answer", "")
    })

    evaluation = engine.evaluate_interview_session(
        candidate_name="Jane Doe",
        role="Full Stack Developer",
        level="Mid-Level",
        interview_type="Technical",
        qa_history=qa_history
    )
    assert 0 <= evaluation["overall_score"] <= 100, "Overall score out of bounds"
    assert len(evaluation["question_evaluations"]) == 2, "Should have 2 question evaluations"
    assert len(evaluation["strengths"]) > 0, "Strengths should not be empty"
    assert len(evaluation["growth_areas"]) > 0, "Growth areas should not be empty"
    print(f"  ✓ Session evaluated! Overall score: {evaluation['overall_score']}/100")
    print("  ✓ Interview Engine passed successfully!\n")


def test_audio_utils():
    print("Testing Audio Utils...")
    html_code = get_speech_html("What is your experience with Docker?")
    assert "speechSynthesis" in html_code, "Speech synthesis JS missing"
    assert "Docker" in html_code, "Text missing from speech widget"
    print("  ✓ Audio Utils passed successfully!\n")


if __name__ == "__main__":
    test_resume_parser()
    test_ai_client_and_engine()
    test_audio_utils()
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")

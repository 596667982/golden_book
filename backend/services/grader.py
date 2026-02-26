"""Auto-grading logic for objective question types."""
from __future__ import annotations
from datetime import datetime
from models import Question, SessionAnswer


def grade_answer(question: Question, student_answer: str | None) -> tuple[bool | None, float]:
    """Returns (is_correct, score_awarded). Subjective returns (None, 0)."""
    if question.question_type == "subjective":
        return None, 0.0

    if not student_answer:
        return False, 0.0

    correct = (question.correct_answer or "").strip().upper()
    student = student_answer.strip().upper()

    if question.question_type in ("single", "fill"):
        is_correct = correct == student
    elif question.question_type == "multi":
        # Order-insensitive comparison
        is_correct = set(correct.replace(" ", "")) == set(student.replace(" ", ""))
    else:
        is_correct = correct == student

    return is_correct, question.score if is_correct else 0.0


def grade_session(questions: list[Question], answers: list[SessionAnswer]) -> tuple[float, float]:
    """Returns (total_score, max_score) excluding subjective questions."""
    answer_map = {a.question_id: a for a in answers}
    total = 0.0
    max_score = 0.0

    for q in questions:
        if q.question_type == "subjective":
            continue
        max_score += q.score
        ans = answer_map.get(q.id)
        if ans and ans.score_awarded:
            total += ans.score_awarded

    return total, max_score

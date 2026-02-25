from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from database import get_db
from models import Exam, Question, ExamSession, SessionAnswer
from schemas import SessionCreate, SessionSubmitAll, AnswerSubmit, SessionOut, PreviewGradeResult, PreviewAnswerResult
from services.grader import grade_answer, grade_session

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionOut])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExamSession)
        .options(selectinload(ExamSession.answers))
        .order_by(ExamSession.started_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=SessionOut)
async def start_session(data: SessionCreate, db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, data.exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    session = ExamSession(exam_id=data.exam_id)
    db.add(session)
    await db.commit()
    # Reload with answers (will be empty for new session)
    result = await db.execute(
        select(ExamSession)
        .where(ExamSession.id == session.id)
        .options(selectinload(ExamSession.answers))
    )
    return result.scalar_one()


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExamSession)
        .where(ExamSession.id == session_id)
        .options(selectinload(ExamSession.answers))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Not found")
    return session


@router.post("/{session_id}/answers", response_model=SessionOut)
async def submit_answer(session_id: int, data: AnswerSubmit, db: AsyncSession = Depends(get_db)):
    session = await db.get(ExamSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status == "completed":
        raise HTTPException(400, "Session already completed")

    # Upsert answer
    existing = await db.execute(
        select(SessionAnswer).where(
            SessionAnswer.session_id == session_id,
            SessionAnswer.question_id == data.question_id
        )
    )
    answer = existing.scalar_one_or_none()
    if answer:
        answer.student_answer = data.student_answer
    else:
        answer = SessionAnswer(session_id=session_id, question_id=data.question_id, student_answer=data.student_answer)
        db.add(answer)

    await db.commit()
    # Reload session with answers
    result = await db.execute(
        select(ExamSession)
        .where(ExamSession.id == session_id)
        .options(selectinload(ExamSession.answers))
    )
    return result.scalar_one()


@router.post("/{session_id}/submit", response_model=SessionOut)
async def submit_session(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await db.get(ExamSession, session_id)
    if not session:
        raise HTTPException(404, "Not found")

    # Load questions
    q_result = await db.execute(select(Question).where(Question.exam_id == session.exam_id))
    questions = {q.id: q for q in q_result.scalars().all()}

    # Load answers
    ans_result = await db.execute(select(SessionAnswer).where(SessionAnswer.session_id == session_id))
    answers = ans_result.scalars().all()

    # Grade each answer
    for ans in answers:
        q = questions.get(ans.question_id)
        if q:
            is_correct, score = grade_answer(q, ans.student_answer)
            ans.is_correct = is_correct
            ans.score_awarded = score
            ans.graded_at = datetime.utcnow()

    # Compute totals
    total, max_score = grade_session(list(questions.values()), answers)
    session.total_score = total
    session.max_score = max_score
    session.status = "completed"
    session.finished_at = datetime.utcnow()

    await db.commit()
    # Reload session with answers
    result = await db.execute(
        select(ExamSession)
        .where(ExamSession.id == session_id)
        .options(selectinload(ExamSession.answers))
    )
    return result.scalar_one()


@router.get("/{session_id}/results", response_model=SessionOut)
async def get_results(session_id: int, db: AsyncSession = Depends(get_db)):
    return await get_session(session_id, db)

@router.post("/preview-grade", response_model=PreviewGradeResult)
async def preview_grade(data: SessionSubmitAll, db: AsyncSession = Depends(get_db)):
    """Preview grading results without saving to database"""
    exam = await db.get(Exam, data.exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")

    # Load questions
    q_result = await db.execute(select(Question).where(Question.exam_id == data.exam_id))
    questions = {q.id: q for q in q_result.scalars().all()}

    # Grade all questions (including unanswered)
    results = []
    total_score = 0.0
    max_score = 0.0

    for question_id, q in questions.items():
        student_answer = data.answers.get(question_id, "")
        is_correct, score = grade_answer(q, student_answer)

        results.append(PreviewAnswerResult(
            question_id=question_id,
            order_num=q.order_num,
            content=q.content,
            question_type=q.question_type,
            student_answer=student_answer,
            is_correct=is_correct,
            score_awarded=score,
            max_score=q.score
        ))

        total_score += score
        max_score += q.score

    # Sort by order_num
    results.sort(key=lambda x: x.order_num)

    return PreviewGradeResult(
        total_score=total_score,
        max_score=max_score,
        results=results
    )

@router.post("/submit-all", response_model=SessionOut)
async def submit_all_answers(data: SessionSubmitAll, db: AsyncSession = Depends(get_db)):
    """Create session, save all answers, and grade in one call"""
    exam = await db.get(Exam, data.exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    
    # Create session
    session = ExamSession(exam_id=data.exam_id, status="completed", finished_at=datetime.utcnow())
    db.add(session)
    await db.flush()  # Get session.id
    
    # Load questions
    q_result = await db.execute(select(Question).where(Question.exam_id == data.exam_id))
    questions = {q.id: q for q in q_result.scalars().all()}
    
    # Save and grade answers for ALL questions
    answers = []
    for question_id, q in questions.items():
        student_answer = data.answers.get(question_id, "")
        is_correct, score = grade_answer(q, student_answer)
        ans = SessionAnswer(
            session_id=session.id,
            question_id=question_id,
            student_answer=student_answer,
            is_correct=is_correct,
            score_awarded=score,
            graded_at=datetime.utcnow()
        )
        db.add(ans)
        answers.append(ans)
    
    # Compute totals
    total, max_score = grade_session(list(questions.values()), answers)
    session.total_score = total
    session.max_score = max_score
    
    await db.commit()
    
    # Reload with answers
    result = await db.execute(
        select(ExamSession)
        .where(ExamSession.id == session.id)
        .options(selectinload(ExamSession.answers))
    )
    return result.scalar_one()


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await db.get(ExamSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    await db.execute(delete(SessionAnswer).where(SessionAnswer.session_id == session_id))
    await db.delete(session)
    await db.commit()

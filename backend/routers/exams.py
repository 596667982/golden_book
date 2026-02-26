from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from sqlalchemy.orm import selectinload
from database import get_db
from models import Exam, Question
from schemas import ExamCreate, ExamUpdate, ExamOut, ExamSimpleOut, ExamListOut, QuestionCreate, QuestionUpdate, QuestionOut

router = APIRouter(prefix="/api/exams", tags=["exams"])


@router.get("", response_model=list[ExamListOut])
async def list_exams(
    category: Optional[str] = Query(None),
    grade: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Exam)
    if category:
        stmt = stmt.where(Exam.category == category)
    if grade is not None:
        stmt = stmt.where(Exam.grade == grade)
    stmt = stmt.order_by(Exam.created_at.desc())
    result = await db.execute(stmt)
    exams = result.scalars().all()
    out = []
    for exam in exams:
        count_result = await db.execute(select(func.count()).where(Question.exam_id == exam.id))
        count = count_result.scalar_one()
        img_count = len(exam.exercise_image_paths) if exam.exercise_image_paths else 0
        out.append(ExamListOut(
            id=exam.id, title=exam.title, description=exam.description,
            category=exam.category, grade=exam.grade,
            status=exam.status, created_at=exam.created_at, question_count=count,
            exercise_image_count=img_count
        ))
    return out


@router.post("", response_model=ExamSimpleOut)
async def create_exam(data: ExamCreate, db: AsyncSession = Depends(get_db)):
    exam = Exam(**data.model_dump())
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


@router.get("/{exam_id}", response_model=ExamOut)
async def get_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Exam)
        .where(Exam.id == exam_id)
        .options(selectinload(Exam.questions))
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(404, "Not found")
    return exam


@router.put("/{exam_id}", response_model=ExamSimpleOut)
async def update_exam(exam_id: int, data: ExamUpdate, db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(exam, k, v)
    await db.commit()
    await db.refresh(exam)
    return exam


@router.delete("/{exam_id}")
async def delete_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Not found")
    await db.delete(exam)
    await db.commit()
    return {"ok": True}


# Questions sub-resource
@router.get("/{exam_id}/questions", response_model=list[QuestionOut])
async def list_questions(exam_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.exam_id == exam_id).order_by(Question.order_num))
    return result.scalars().all()


@router.post("/{exam_id}/questions", response_model=QuestionOut)
async def create_question(exam_id: int, data: QuestionCreate, db: AsyncSession = Depends(get_db)):
    q = Question(exam_id=exam_id, **data.model_dump())
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q


@router.put("/questions/{question_id}", response_model=QuestionOut)
async def update_question(question_id: int, data: QuestionUpdate, db: AsyncSession = Depends(get_db)):
    q = await db.get(Question, question_id)
    if not q:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(q, k, v)
    await db.commit()
    await db.refresh(q)
    return q


@router.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.get(Question, question_id)
    if not q:
        raise HTTPException(404, "Not found")
    await db.delete(q)
    await db.commit()
    return {"ok": True}

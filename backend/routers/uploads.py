from __future__ import annotations
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import attributes
from database import get_db
from models import Exam, Question
from config import settings
from services import ai_service

router = APIRouter(prefix="/api/upload", tags=["upload"])


def _save_file(file_bytes: bytes, original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[-1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    os.makedirs(settings.upload_dir, exist_ok=True)
    path = os.path.join(settings.upload_dir, filename)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return filename


@router.post("/exercise")
async def upload_exercise(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    data = await file.read()
    filename = _save_file(data, file.filename or "image.jpg")
    exam = Exam(title="新练习册", exercise_image_paths=[filename])
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return {"exam_id": exam.id, "filename": filename}


@router.post("/exercise/{exam_id}")
async def add_exercise_image(exam_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Add another exercise image to existing exam"""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    data = await file.read()
    filename = _save_file(data, file.filename or "image.jpg")
    if not exam.exercise_image_paths:
        exam.exercise_image_paths = []
    exam.exercise_image_paths.append(filename)
    # Mark JSON field as modified for SQLAlchemy to detect change
    attributes.flag_modified(exam, "exercise_image_paths")
    await db.commit()
    await db.refresh(exam)
    print(f"[DEBUG] Added image {filename} to exam {exam_id}, total: {len(exam.exercise_image_paths)}")
    return {"exam_id": exam_id, "filename": filename, "total_images": len(exam.exercise_image_paths)}


@router.post("/answer/{exam_id}")
async def upload_answer(exam_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    data = await file.read()
    filename = _save_file(data, file.filename or "image.jpg")
    exam.answer_image_path = filename
    await db.commit()
    return {"exam_id": exam_id, "filename": filename}


@router.post("/parse/{exam_id}")
async def parse_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    if not exam.exercise_image_paths or len(exam.exercise_image_paths) == 0:
        raise HTTPException(400, "请先上传练习题图片")

    # Parse all exercise images and merge results
    all_questions_data = []
    for img_path in exam.exercise_image_paths:
        ex_path = os.path.join(settings.upload_dir, img_path)
        with open(ex_path, "rb") as f:
            ex_bytes = f.read()
        questions_data = await ai_service.parse_exercise_image(ex_bytes, db)
        all_questions_data.extend(questions_data)

    # Parse answers if available
    answers_map: dict[int, str] = {}
    if exam.answer_image_path:
        ans_path = os.path.join(settings.upload_dir, exam.answer_image_path)
        with open(ans_path, "rb") as f:
            ans_bytes = f.read()
        answers_data = await ai_service.parse_answer_image(ans_bytes, db)
        answers_map = {a["order_num"]: a.get("correct_answer") for a in answers_data}

    # Delete existing questions
    existing = await db.execute(select(Question).where(Question.exam_id == exam_id))
    for q in existing.scalars().all():
        await db.delete(q)

    # Save new questions
    for qd in all_questions_data:
        q = Question(
            exam_id=exam_id,
            order_num=qd.get("order_num", 0),
            content=qd.get("content", ""),
            question_type=qd.get("question_type", "fill"),
            options=qd.get("options"),
            correct_answer=answers_map.get(qd.get("order_num", 0)) or qd.get("correct_answer"),
            score=qd.get("score", 1.0),
        )
        db.add(q)

    exam.status = "ready"
    await db.commit()

    result = await db.execute(select(Question).where(Question.exam_id == exam_id).order_by(Question.order_num))
    return {"questions": [{"id": q.id, "order_num": q.order_num, "content": q.content, "question_type": q.question_type} for q in result.scalars().all()]}

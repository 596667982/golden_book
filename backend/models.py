from datetime import datetime
from sqlalchemy import Integer, String, Text, Boolean, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class AIConfig(Base):
    __tablename__ = "ai_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(50))  # openai | qwen | claude | custom
    api_key: Mapped[str] = mapped_column(String(500))
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    model_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exercise_image_paths: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)  # List of image filenames
    answer_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft | ready
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions: Mapped[list["Question"]] = relationship("Question", back_populates="exam", cascade="all, delete-orphan", order_by="Question.order_num")
    sessions: Mapped[list["ExamSession"]] = relationship("ExamSession", back_populates="exam")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"))
    order_num: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text)
    question_type: Mapped[str] = mapped_column(String(20), default="fill")  # single | multi | fill | subjective
    options: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {"A": "...", "B": "..."}
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=1.0)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exam: Mapped["Exam"] = relationship("Exam", back_populates="questions")


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer, ForeignKey("exams.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")  # in_progress | completed

    exam: Mapped["Exam"] = relationship("Exam", back_populates="sessions")
    answers: Mapped[list["SessionAnswer"]] = relationship("SessionAnswer", back_populates="session", cascade="all, delete-orphan")


class SessionAnswer(Base):
    __tablename__ = "session_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam_sessions.id"))
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"))
    student_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    score_awarded: Mapped[float | None] = mapped_column(Float, nullable=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    session: Mapped["ExamSession"] = relationship("ExamSession", back_populates="answers")

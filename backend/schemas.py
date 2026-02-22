from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Any


# AI Config
class AIConfigCreate(BaseModel):
    name: str
    provider: str
    api_key: str
    base_url: Optional[str] = None
    model_name: str
    is_active: bool = False

class AIConfigUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    is_active: Optional[bool] = None

class AIConfigOut(BaseModel):
    id: int
    name: str
    provider: str
    api_key: str
    base_url: Optional[str]
    model_name: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# Question
class QuestionCreate(BaseModel):
    content: str
    question_type: str = "fill"
    options: Optional[dict] = None
    correct_answer: Optional[str] = None
    score: float = 1.0
    order_num: int = 0

class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    question_type: Optional[str] = None
    options: Optional[dict] = None
    correct_answer: Optional[str] = None
    score: Optional[float] = None
    order_num: Optional[int] = None

class QuestionOut(BaseModel):
    id: int
    exam_id: int
    order_num: int
    content: str
    question_type: str
    options: Optional[dict]
    correct_answer: Optional[str]
    score: float
    image_path: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


# Exam
class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ExamOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    exercise_image_paths: Optional[list[str]]
    answer_image_path: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    questions: list[QuestionOut] = []
    model_config = {"from_attributes": True}

class ExamSimpleOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    exercise_image_paths: Optional[list[str]]
    answer_image_path: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class ExamListOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    question_count: int = 0
    exercise_image_count: int = 0
    model_config = {"from_attributes": True}


# Session
class SessionCreate(BaseModel):
    exam_id: int

class SessionSubmitAll(BaseModel):
    exam_id: int
    answers: dict[int, str]  # question_id -> student_answer

class AnswerSubmit(BaseModel):
    question_id: int
    student_answer: Optional[str] = None

class SessionAnswerOut(BaseModel):
    id: int
    question_id: int
    student_answer: Optional[str]
    is_correct: Optional[bool]
    score_awarded: Optional[float]
    graded_at: Optional[datetime]
    model_config = {"from_attributes": True}

class SessionOut(BaseModel):
    id: int
    exam_id: int
    started_at: datetime
    finished_at: Optional[datetime]
    total_score: Optional[float]
    max_score: Optional[float]
    status: str
    answers: list[SessionAnswerOut] = []
    model_config = {"from_attributes": True}

class PreviewAnswerResult(BaseModel):
    question_id: int
    order_num: int
    content: str
    question_type: str
    student_answer: str
    is_correct: Optional[bool]  # None for subjective questions
    score_awarded: float
    max_score: float

class PreviewGradeResult(BaseModel):
    total_score: float
    max_score: float
    results: list[PreviewAnswerResult]

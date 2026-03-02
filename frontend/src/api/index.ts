import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export interface AIConfig {
  id: number; name: string; provider: string; api_key: string
  base_url?: string; model_name: string; is_active: boolean; created_at: string
}
export interface Exam {
  id: number; title: string; description?: string; status: string
  category?: string; grade?: number
  created_at: string; question_count?: number; exercise_image_count?: number
  exercise_image_paths?: string[]; answer_image_path?: string; questions?: Question[]
}
export interface Question {
  id: number; exam_id: number; order_num: number; content: string
  question_type: string; options?: Record<string, string>
  correct_answer?: string; score: number; image_path?: string; created_at: string
}
export interface Session {
  id: number; exam_id: number; started_at: string; finished_at?: string
  total_score?: number; max_score?: number; status: string; answers: SessionAnswer[]
}
export interface SessionAnswer {
  id: number; question_id: number; student_answer?: string
  is_correct?: boolean; score_awarded?: number; graded_at?: string
}
export interface PreviewAnswerResult {
  question_id: number; order_num: number; content: string
  question_type: string; student_answer: string; is_correct: boolean | null
  score_awarded: number; max_score: number
}
export interface PreviewGradeResult {
  total_score: number; max_score: number; results: PreviewAnswerResult[]
}

// AI Configs
export const aiConfigApi = {
  list: () => http.get<AIConfig[]>('/ai-configs').then(r => r.data),
  create: (d: Omit<AIConfig, 'id'|'created_at'>) => http.post<AIConfig>('/ai-configs', d).then(r => r.data),
  update: (id: number, d: Partial<AIConfig>) => http.put<AIConfig>(`/ai-configs/${id}`, d).then(r => r.data),
  delete: (id: number) => http.delete(`/ai-configs/${id}`),
  activate: (id: number) => http.post(`/ai-configs/${id}/activate`),
  test: (id: number) => http.post<{ok: boolean}>(`/ai-configs/${id}/test`).then(r => r.data),
}

// Exams
export const examApi = {
  list: (params?: { category?: string; grade?: number }) => http.get<Exam[]>('/exams', { params }).then(r => r.data),
  get: (id: number) => http.get<Exam>(`/exams/${id}`).then(r => r.data),
  create: (d: {title: string; description?: string}) => http.post<Exam>('/exams', d).then(r => r.data),
  update: (id: number, d: Partial<Exam>) => http.put<Exam>(`/exams/${id}`, d).then(r => r.data),
  delete: (id: number) => http.delete(`/exams/${id}`),
  updateQuestion: (qid: number, d: Partial<Question>) => http.put<Question>(`/exams/questions/${qid}`, d).then(r => r.data),
  deleteQuestion: (qid: number) => http.delete(`/exams/questions/${qid}`),
}

// Upload
export const uploadApi = {
  exercise: (file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return http.post<{exam_id: number; filename: string}>('/upload/exercise', fd).then(r => r.data)
  },
  addExercise: (examId: number, file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return http.post<{exam_id: number; filename: string; total_images: number}>(`/upload/exercise/${examId}`, fd).then(r => r.data)
  },
  answer: (examId: number, file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return http.post(`/upload/answer/${examId}`, fd)
  },
  parse: (examId: number) => http.post(`/upload/parse/${examId}`).then(r => r.data),
}

// Sessions
export const sessionApi = {
  list: () => http.get<Session[]>('/sessions').then(r => r.data),
  getInProgress: (examId: number) => http.get<Session | null>(`/sessions/exam/${examId}/in-progress`).then(r => r.data),
  start: (examId: number) => http.post<Session>('/sessions', { exam_id: examId }).then(r => r.data),
  get: (id: number) => http.get<Session>(`/sessions/${id}`).then(r => r.data),
  submitAnswer: (sessionId: number, questionId: number, answer: string) =>
    http.post<Session>(`/sessions/${sessionId}/answers`, { question_id: questionId, student_answer: answer }).then(r => r.data),
  submit: (id: number) => http.post<Session>(`/sessions/${id}/submit`).then(r => r.data),
  previewGrade: (examId: number, answers: Record<number, string>) =>
    http.post<PreviewGradeResult>('/sessions/preview-grade', { exam_id: examId, answers }).then(r => r.data),
  submitAll: (examId: number, answers: Record<number, string>) =>
    http.post<Session>('/sessions/submit-all', { exam_id: examId, answers }).then(r => r.data),
  results: (id: number) => http.get<Session>(`/sessions/${id}/results`).then(r => r.data),
  delete: (id: number) => http.delete(`/sessions/${id}`),
}

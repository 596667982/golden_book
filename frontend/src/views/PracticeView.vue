<template>
  <div v-if="exam">
    <el-page-header @back="$router.push('/exams')" :content="`答题 - ${exam.title}`" style="margin-bottom:16px" />
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card v-if="currentQ">
          <template #header>
            <span>第 {{ currentIndex + 1 }} 题 / 共 {{ questions.length }} 题</span>
            <el-tag style="margin-left:8px" size="small">{{ typeLabel(currentQ.question_type) }}</el-tag>
            <span style="float:right;color:#999">{{ currentQ.score }} 分</span>
          </template>
          <div v-math="currentQ.content" style="font-size:16px;margin-bottom:16px"></div>

          <!-- Single choice -->
          <el-radio-group v-if="currentQ.question_type === 'single'" v-model="answers[currentQ.id]">
            <el-radio v-for="(v, k) in currentQ.options" :key="k" :value="k" style="display:block;margin:8px 0">
              <span>{{ k }}. </span><span v-math="v"></span>
            </el-radio>
          </el-radio-group>

          <!-- Multi choice -->
          <el-checkbox-group v-else-if="currentQ.question_type === 'multi'" v-model="multiAnswers[currentQ.id]">
            <el-checkbox v-for="(v, k) in currentQ.options" :key="k" :value="k" style="display:block;margin:8px 0">
              <span>{{ k }}. </span><span v-math="v"></span>
            </el-checkbox>
          </el-checkbox-group>

          <!-- Fill / Subjective -->
          <el-input v-else v-model="answers[currentQ.id]" :type="currentQ.question_type === 'subjective' ? 'textarea' : 'text'" :rows="4" placeholder="请输入答案" />

          <div style="margin-top:24px;display:flex;gap:8px">
            <el-button :disabled="currentIndex === 0" @click="currentIndex--">上一题</el-button>
            <el-button v-if="currentIndex < questions.length - 1" type="primary" @click="currentIndex++">下一题</el-button>
            <el-button v-else type="success" :loading="submitting" @click="previewSubmit">提交答卷</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card title="答题卡">
          <template #header>答题卡</template>
          <div class="answer-card-grid">
            <el-button
              v-for="(q, i) in questions" :key="q.id"
              :type="hasAnswer(q) ? 'primary' : 'default'"
              size="small" circle
              @click="currentIndex = i"
            >{{ i + 1 }}</el-button>
          </div>
          <el-divider />
          <div style="color:#999;font-size:12px">已答 {{ answeredCount }} / {{ questions.length }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Preview Dialog -->
    <el-dialog v-model="showPreview" title="评分预览" width="800px" :close-on-click-modal="false">
      <div v-if="previewResult" style="margin-bottom:16px">
        <el-alert type="info" :closable="false">
          <template #title>
            <span style="font-size:18px">总分：{{ previewResult.total_score }} / {{ previewResult.max_score }}</span>
            <span style="margin-left:16px;font-size:14px;color:#999">
              正确率：{{ Math.round(previewResult.total_score / previewResult.max_score * 100) }}%
            </span>
          </template>
        </el-alert>
      </div>
      <el-table v-if="previewResult" :data="previewResult.results" max-height="400">
        <el-table-column prop="order_num" label="序号" width="70" />
        <el-table-column label="题目" min-width="200">
          <template #default="{row}">
            <div v-math="row.content" style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"></div>
          </template>
        </el-table-column>
        <el-table-column label="你的答案" width="120">
          <template #default="{row}">
            {{ row.student_answer || '未作答' }}
          </template>
        </el-table-column>
        <el-table-column label="结果" width="80">
          <template #default="{row}">
            <el-tag v-if="row.is_correct === null" type="info">主观题</el-tag>
            <el-tag v-else :type="row.is_correct ? 'success' : 'danger'">{{ row.is_correct ? '正确' : '错误' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="得分" width="100">
          <template #default="{row}">
            {{ row.score_awarded }} / {{ row.max_score }}
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showPreview = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="confirmSubmit">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { examApi, sessionApi, type Exam, type Question, type PreviewGradeResult } from '@/api'

const route = useRoute()
const router = useRouter()
const exam = ref<Exam | null>(null)
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const answers = ref<Record<number, string>>({})
const multiAnswers = ref<Record<number, string[]>>({})
const submitting = ref(false)
const showPreview = ref(false)
const previewResult = ref<PreviewGradeResult | null>(null)

const currentQ = computed(() => questions.value[currentIndex.value])
const typeLabel = (t: string) => ({ single: '单选', multi: '多选', fill: '填空', subjective: '主观' }[t] ?? t)
const hasAnswer = (q: Question) => !!(answers.value[q.id] || (multiAnswers.value[q.id]?.length))
const answeredCount = computed(() => questions.value.filter(hasAnswer).length)

function getAnswer(q: Question): string {
  if (q.question_type === 'multi') return (multiAnswers.value[q.id] ?? []).sort().join(',')
  return answers.value[q.id] ?? ''
}

async function previewSubmit() {
  submitting.value = true
  try {
    // Collect all answers
    const allAnswers: Record<number, string> = {}
    for (const q of questions.value) {
      const ans = getAnswer(q)
      if (ans) allAnswers[q.id] = ans
    }
    // Get preview results
    previewResult.value = await sessionApi.previewGrade(exam.value!.id, allAnswers)
    showPreview.value = true
  } catch (e: any) {
    ElMessage.error('预览失败')
  } finally {
    submitting.value = false
  }
}

async function confirmSubmit() {
  submitting.value = true
  try {
    // Collect all answers
    const allAnswers: Record<number, string> = {}
    for (const q of questions.value) {
      const ans = getAnswer(q)
      if (ans) allAnswers[q.id] = ans
    }
    // Submit all at once
    const result = await sessionApi.submitAll(exam.value!.id, allAnswers)
    router.push(`/sessions/${result.id}/results`)
  } catch (e: any) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const id = Number(route.params.id)
  exam.value = await examApi.get(id)
  questions.value = exam.value.questions ?? []
})
</script>

<style scoped>
.answer-card-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  align-items: center;
  justify-items: center;
}

.answer-card-grid :deep(.el-button) {
  width: 32px !important;
  height: 32px !important;
  padding: 0 !important;
  min-width: 32px !important;
  margin: 0 !important;
}
</style>

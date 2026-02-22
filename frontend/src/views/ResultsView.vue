<template>
  <div v-if="session">
    <el-page-header @back="$router.push('/sessions')" content="答题结果" style="margin-bottom:16px" />
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="8">
        <el-card>
          <el-statistic title="得分" :value="session.total_score ?? 0" suffix="`/ ${session.max_score ?? 0}`" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic title="正确率" :value="correctRate" suffix="%" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic title="答题时间" :value="duration" suffix="秒" />
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>题目详情</template>
      <el-table :data="answerDetails">
        <el-table-column prop="order_num" label="序号" width="70" />
        <el-table-column label="题目">
          <template #default="{row}">
            <div v-math="row.content"></div>
          </template>
        </el-table-column>
        <el-table-column label="你的答案" width="120">
          <template #default="{row}">
            {{ row.student_answer || '未作答' }}
          </template>
        </el-table-column>
        <el-table-column label="参考答案" width="120">
          <template #default="{row}">
            {{ row.correct_answer }}
          </template>
        </el-table-column>
        <el-table-column label="结果" width="80">
          <template #default="{row}">
            <el-tag :type="row.is_correct ? 'success' : 'danger'">{{ row.is_correct ? '正确' : '错误' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score_awarded" label="得分" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { sessionApi, examApi, type Session, type Question } from '@/api'

const route = useRoute()
const session = ref<Session | null>(null)
const questions = ref<Question[]>([])

const correctRate = computed(() => {
  if (!questions.value.length) return 0
  const correct = session.value?.answers.filter(a => a.is_correct).length ?? 0
  return Math.round(correct / questions.value.length * 100)
})

const duration = computed(() => {
  if (!session.value?.started_at || !session.value?.finished_at) return 0
  return Math.round((new Date(session.value.finished_at).getTime() - new Date(session.value.started_at).getTime()) / 1000)
})

const answerDetails = computed(() => {
  if (!session.value || !questions.value.length) return []
  // Map all questions to include answer data
  return questions.value.map(q => {
    const answer = session.value!.answers.find(a => a.question_id === q.id)
    return {
      question_id: q.id,
      order_num: q.order_num,
      content: q.content,
      correct_answer: q.correct_answer,
      student_answer: answer?.student_answer ?? '',
      is_correct: answer?.is_correct ?? false,
      score_awarded: answer?.score_awarded ?? 0
    }
  }).sort((a, b) => (a.order_num ?? 0) - (b.order_num ?? 0))
})

onMounted(async () => {
  const id = Number(route.params.id)
  session.value = await sessionApi.results(id)
  if (session.value) {
    const exam = await examApi.get(session.value.exam_id)
    questions.value = exam.questions ?? []
  }
})
</script>

<template>
  <div v-if="exam">
    <el-page-header @back="$router.push('/exams')" :content="exam.title" style="margin-bottom:16px" />
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>题目列表</span>
          <el-button type="primary" :disabled="exam.status !== 'ready'" @click="$router.push(`/exams/${exam.id}/practice`)">开始答题</el-button>
        </div>
      </template>
      <el-table :data="exam.questions" v-loading="loading">
        <el-table-column prop="order_num" label="序号" width="70" />
        <el-table-column label="题目内容">
          <template #default="{row}">
            <div v-math="row.content"></div>
          </template>
        </el-table-column>
        <el-table-column prop="question_type" label="类型" width="100">
          <template #default="{row}">
            <el-tag size="small">{{ typeLabel(row.question_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="correct_answer" label="参考答案" width="120" />
        <el-table-column prop="score" label="分值" width="80" />
        <el-table-column label="操作" width="120">
          <template #default="{row}">
            <el-button size="small" @click="editQuestion(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="delQuestion(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="editDialog" title="编辑题目" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="题目内容"><el-input v-model="editForm.content" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="题型">
          <el-select v-model="editForm.question_type">
            <el-option label="单选" value="single" />
            <el-option label="多选" value="multi" />
            <el-option label="填空" value="fill" />
            <el-option label="主观" value="subjective" />
          </el-select>
        </el-form-item>
        <el-form-item label="参考答案"><el-input v-model="editForm.correct_answer" /></el-form-item>
        <el-form-item label="分值"><el-input-number v-model="editForm.score" :min="0.5" :step="0.5" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" @click="saveQuestion">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { examApi, type Exam, type Question } from '@/api'

const route = useRoute()
const exam = ref<Exam | null>(null)
const loading = ref(false)
const editDialog = ref(false)
const editForm = ref<Partial<Question>>({})

const typeLabel = (t: string) => ({ single: '单选', multi: '多选', fill: '填空', subjective: '主观' }[t] ?? t)

async function load() {
  loading.value = true
  exam.value = await examApi.get(Number(route.params.id)).finally(() => loading.value = false)
}

function editQuestion(q: Question) {
  editForm.value = { ...q }
  editDialog.value = true
}

async function saveQuestion() {
  await examApi.updateQuestion(editForm.value.id!, editForm.value)
  editDialog.value = false
  await load()
}

async function delQuestion(id: number) {
  await examApi.deleteQuestion(id)
  await load()
}

onMounted(load)
</script>

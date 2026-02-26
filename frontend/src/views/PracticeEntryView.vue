<template>
  <div style="max-width:800px;margin:40px auto;padding:0 16px">
    <el-card>
      <template #header>
        <span style="font-size:18px;font-weight:600">选择练习册</span>
      </template>

      <div style="margin-bottom:16px;display:flex;gap:12px">
        <el-select v-model="filterCategory" placeholder="科目" clearable style="width:120px" @change="load">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="filterGrade" placeholder="年级" clearable style="width:120px" @change="load">
          <el-option v-for="g in grades" :key="g.value" :label="g.label" :value="g.value" />
        </el-select>
      </div>

      <el-table :data="exams" v-loading="loading">
        <el-table-column prop="title" label="练习册" />
        <el-table-column prop="category" label="科目" width="80" />
        <el-table-column prop="grade" label="年级" width="80">
          <template #default="{row}">{{ row.grade ? `${row.grade}年级` : '-' }}</template>
        </el-table-column>
        <el-table-column prop="question_count" label="题目数" width="80" />
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button
              type="primary"
              :disabled="row.status !== 'ready'"
              @click="$router.push(`/exams/${row.id}/practice?from=practice`)"
            >开始答题</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { examApi, type Exam } from '@/api'

const categories = ['语文', '数学', '英语']
const grades = [
  { value: 6, label: '六年级' },
  { value: 7, label: '初一' }, { value: 8, label: '初二' }, { value: 9, label: '初三' },
  { value: 10, label: '高一' }, { value: 11, label: '高二' }, { value: 12, label: '高三' },
]

const exams = ref<Exam[]>([])
const loading = ref(false)
const filterCategory = ref<string | undefined>(undefined)
const filterGrade = ref<number | undefined>(undefined)

async function load() {
  loading.value = true
  exams.value = await examApi.list({
    category: filterCategory.value,
    grade: filterGrade.value,
  }).finally(() => loading.value = false)
}

onMounted(load)
</script>

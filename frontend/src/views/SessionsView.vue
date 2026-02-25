<template>
  <div>
    <el-card>
      <template #header>答题记录</template>
      <el-table :data="sessions" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="练习册" min-width="140">
          <template #default="{row}">
            {{ examTitles[row.exam_id] ?? `练习册 #${row.exam_id}` }}
          </template>
        </el-table-column>
        <el-table-column label="得分" width="120">
          <template #default="{row}">
            <span v-if="row.status === 'completed'">
              {{ row.total_score ?? '-' }} / {{ row.max_score ?? '-' }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="正确率" width="100">
          <template #default="{row}">
            <span v-if="row.status === 'completed' && row.max_score">
              {{ Math.round((row.total_score / row.max_score) * 100) }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{row}">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
              {{ row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="170">
          <template #default="{row}">{{ new Date(row.started_at).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" :disabled="row.status !== 'completed'" @click="$router.push(`/sessions/${row.id}/results`)">查看结果</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { sessionApi, examApi, type Session } from '@/api'

const sessions = ref<Session[]>([])
const loading = ref(false)
const examTitles = ref<Record<number, string>>({})

async function load() {
  loading.value = true
  try {
    sessions.value = await sessionApi.list()
    const ids = [...new Set(sessions.value.map(s => s.exam_id))]
    const exams = await Promise.all(ids.map(id => examApi.get(id).catch(() => null)))
    exams.forEach(e => { if (e) examTitles.value[e.id] = e.title })
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除该答题记录吗？', '提示', { type: 'warning' })
  await sessionApi.delete(id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>

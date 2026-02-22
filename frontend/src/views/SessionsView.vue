<template>
  <div>
    <el-card>
      <template #header>答题记录</template>
      <el-table :data="sessions" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="exam_id" label="练习册ID" width="100" />
        <el-table-column label="得分" width="120">
          <template #default="{row}">
            {{ row.total_score ?? '-' }} / {{ row.max_score ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="180">
          <template #default="{row}">{{ new Date(row.started_at).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button size="small" :disabled="row.status !== 'completed'" @click="$router.push(`/sessions/${row.id}/results`)">查看结果</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { sessionApi, type Session } from '@/api'

const sessions = ref<Session[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  sessions.value = await sessionApi.list().finally(() => loading.value = false)
})
</script>

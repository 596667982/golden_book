<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>AI 配置</span>
          <el-button type="primary" @click="openAdd">添加配置</el-button>
        </div>
      </template>
      <el-table :data="configs" v-loading="loading">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="provider" label="提供商" width="120" />
        <el-table-column prop="model_name" label="模型" width="160" />
        <el-table-column label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '激活' : '未激活' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{row}">
            <el-button size="small" @click="testConfig(row.id)" :loading="testing === row.id">测试</el-button>
            <el-button size="small" type="primary" :disabled="row.is_active" @click="activate(row.id)">激活</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="del(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="editId ? '编辑 AI 配置' : '添加 AI 配置'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="提供商">
          <el-select v-model="form.provider">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="API Key"><el-input v-model="form.api_key" show-password /></el-form-item>
        <el-form-item label="Base URL"><el-input v-model="form.base_url" placeholder="可选，自定义端点" /></el-form-item>
        <el-form-item label="模型名称"><el-input v-model="form.model_name" placeholder="如 gpt-4o" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { aiConfigApi, type AIConfig } from '@/api'

const configs = ref<AIConfig[]>([])
const loading = ref(false)
const dialog = ref(false)
const saving = ref(false)
const testing = ref<number | null>(null)
const editId = ref<number | null>(null)
const form = ref({ name: '', provider: 'openai', api_key: '', base_url: '', model_name: 'gpt-4o' })

async function load() {
  loading.value = true
  configs.value = await aiConfigApi.list().finally(() => loading.value = false)
}

function openAdd() {
  editId.value = null
  form.value = { name: '', provider: 'openai', api_key: '', base_url: '', model_name: 'gpt-4o' }
  dialog.value = true
}

function openEdit(row: AIConfig) {
  editId.value = row.id
  form.value = { name: row.name, provider: row.provider, api_key: row.api_key, base_url: row.base_url ?? '', model_name: row.model_name }
  dialog.value = true
}

async function save() {
  saving.value = true
  try {
    if (editId.value) {
      await aiConfigApi.update(editId.value, { ...form.value })
    } else {
      await aiConfigApi.create({ ...form.value, is_active: false })
    }
    dialog.value = false
    await load()
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

async function activate(id: number) {
  await aiConfigApi.activate(id)
  await load()
}

async function testConfig(id: number) {
  testing.value = id
  try {
    const res = await aiConfigApi.test(id)
    ElMessage[res.ok ? 'success' : 'error'](res.ok ? '连接成功' : '连接失败')
  } catch { ElMessage.error('测试失败') }
  finally { testing.value = null }
}

async function del(id: number) {
  await aiConfigApi.delete(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>练习册列表</span>
          <el-button type="primary" @click="showUpload = true">上传练习册</el-button>
        </div>
      </template>
      <el-table :data="exams" v-loading="loading">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="exercise_image_count" label="图片数" width="80" />
        <el-table-column prop="question_count" label="题目数" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.status === 'ready' ? 'success' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{row}">{{ new Date(row.created_at).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{row}">
            <el-button size="small" @click="$router.push(`/exams/${row.id}`)">查看</el-button>
            <el-button size="small" type="primary" :disabled="row.status !== 'ready'" @click="$router.push(`/exams/${row.id}/practice`)">答题</el-button>
            <el-button size="small" type="danger" @click="deleteExam(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Upload Dialog -->
    <el-dialog v-model="showUpload" title="上传练习册" width="500px">
      <el-steps :active="step" finish-status="success" style="margin-bottom:24px">
        <el-step title="上传题目" />
        <el-step title="上传答案" />
        <el-step title="AI 解析" />
      </el-steps>

      <div v-if="step === 0">
        <el-input v-model="examTitle" placeholder="练习册名称" style="margin-bottom:12px" />
        <el-upload
          drag
          :auto-upload="false"
          :file-list="fileList"
          :on-change="onExerciseChange"
          :on-remove="onExerciseRemove"
          accept="image/*"
          multiple
          list-type="picture">
          <el-icon style="font-size:48px"><UploadFilled /></el-icon>
          <div>拖拽或点击上传练习题图片（可多选）</div>
        </el-upload>
      </div>

      <div v-if="step === 1">
        <el-upload drag :auto-upload="false" :on-change="onAnswerChange" accept="image/*">
          <el-icon style="font-size:48px"><UploadFilled /></el-icon>
          <div>拖拽或点击上传答案图片（可选）</div>
        </el-upload>
      </div>

      <div v-if="step === 2">
        <el-result v-if="parseResult" icon="success" title="解析完成" :sub-title="`共识别 ${parseResult.questions?.length ?? 0} 道题目`" />
        <div v-else style="text-align:center;padding:24px">
          <el-icon class="is-loading" style="font-size:32px"><Loading /></el-icon>
          <div style="margin-top:8px">AI 正在解析中...</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button v-if="step === 1" @click="step = 0">上一步</el-button>
        <el-button type="primary" :loading="uploading" @click="nextStep">
          {{ step === 2 ? '完成' : step === 1 ? '开始解析' : '下一步' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { examApi, uploadApi, type Exam } from '@/api'

const exams = ref<Exam[]>([])
const loading = ref(false)
const showUpload = ref(false)
const step = ref(0)
const uploading = ref(false)
const examTitle = ref('新练习册')
const fileList = ref<any[]>([])
const answerFile = ref<File | null>(null)
const currentExamId = ref<number | null>(null)
const parseResult = ref<any>(null)

async function load() {
  loading.value = true
  exams.value = await examApi.list().finally(() => loading.value = false)
}

function onExerciseChange(file: any, files: any[]) {
  console.log('[DEBUG] onExerciseChange, file:', file, 'files count:', files.length)
  fileList.value = files
}

function onExerciseRemove(file: any, files: any[]) {
  fileList.value = files
}

function onAnswerChange(f: any) { answerFile.value = f.raw }

async function nextStep() {
  if (step.value === 0) {
    if (fileList.value.length === 0) return ElMessage.warning('请选择练习题图片')
    console.log('[DEBUG] Uploading', fileList.value.length, 'images')
    uploading.value = true
    try {
      // Upload first image to create exam
      console.log('[DEBUG] Uploading image 1:', fileList.value[0].name)
      const res = await uploadApi.exercise(fileList.value[0].raw)
      currentExamId.value = res.exam_id
      await examApi.update(res.exam_id, { title: examTitle.value })
      // Upload remaining images
      for (let i = 1; i < fileList.value.length; i++) {
        console.log('[DEBUG] Uploading image', i + 1, ':', fileList.value[i].name)
        const addRes = await uploadApi.addExercise(res.exam_id, fileList.value[i].raw)
        console.log('[DEBUG] Added, total images:', addRes.total_images)
      }
      step.value = 1
    } catch (e) {
      console.error('[DEBUG] Upload error:', e)
      ElMessage.error('上传失败')
    }
    finally { uploading.value = false }
  } else if (step.value === 1) {
    if (answerFile.value && currentExamId.value) {
      await uploadApi.answer(currentExamId.value, answerFile.value)
    }
    step.value = 2
    parseResult.value = null
    try {
      parseResult.value = await uploadApi.parse(currentExamId.value!)
    } catch { ElMessage.error('解析失败') }
  } else {
    showUpload.value = false
    step.value = 0
    fileList.value = []
    answerFile.value = null
    parseResult.value = null
    await load()
  }
}

async function deleteExam(id: number) {
  await examApi.delete(id)
  await load()
}

onMounted(load)
</script>

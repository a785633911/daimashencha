<template>
  <div class="ai-config">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>AI配置管理</span>
          <el-button type="primary" @click="openAddDialog">添加配置</el-button>
        </div>
      </template>

      <el-table :data="configs" style="width: 100%" row-key="id" ref="tableRef">
        <el-table-column width="50" align="center">
          <template #default>
            <el-icon class="drag-handle" style="cursor: move; color: var(--el-color-primary)">
              <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" width="16" height="16">
                <path d="M384 192m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="currentColor"/>
                <path d="M640 192m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="currentColor"/>
                <path d="M384 512m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="currentColor"/>
                <path d="M640 512m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="currentColor"/>
                <path d="M384 832m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="currentColor"/>
                <path d="M640 832m-64 0a64 64 0 1 0 128 0 64 64 0 1 0-128 0Z" fill="currentColor"/>
              </svg>
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="api_url" label="API地址" width="200" />
        <el-table-column prop="review_model" label="审查模型" width="150" />
        <el-table-column prop="recheck_model" label="复查模型" width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '已激活' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="editConfig(row)">编辑</el-button>
            <el-button size="small" type="success" @click="activateConfig(row.id)" :disabled="row.is_active">激活</el-button>
            <el-button size="small" type="danger" @click="deleteConfig(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑配置' : '添加配置'" width="600px" @close="resetForm">
      <el-form :model="form" label-width="120px">
        <el-form-item label="配置名称">
          <el-input v-model="form.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="API地址">
          <el-input v-model="form.api_url" placeholder="例如: https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="API密钥">
          <el-input v-model="form.api_key" type="password" show-password placeholder="请输入API密钥" />
        </el-form-item>
        <el-form-item label="审查模型">
          <el-select
            v-model="form.review_model"
            filterable
            allow-create
            default-first-option
            placeholder="输入API地址和密钥后点击加载模型"
            style="width: 100%"
            :loading="modelsLoading"
          >
            <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
          </el-select>
          <el-button size="small" style="margin-top: 4px" @click="fetchModels" :loading="modelsLoading" :disabled="!form.api_url || !form.api_key">
            加载模型列表
          </el-button>
        </el-form-item>
        <el-form-item label="复查模型">
          <el-select
            v-model="form.recheck_model"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入复查模型"
            style="width: 100%"
            :loading="modelsLoading"
          >
            <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="流式输出">
          <el-switch v-model="form.stream_enabled" />
        </el-form-item>
        <el-form-item label="参考资料路径">
          <el-select v-model="form.reference_paths" multiple filterable allow-create default-first-option placeholder="输入文件/文件夹路径后回车添加" style="width: 100%" />
          <div style="margin-top: 4px; font-size: 12px; color: var(--text-light)">支持多个文件或文件夹路径</div>
        </el-form-item>
        <el-form-item label="回答格式规范">
          <el-select v-model="form.format_paths" multiple filterable allow-create default-first-option placeholder="输入文件/文件夹路径后回车添加" style="width: 100%" />
          <div style="margin-top: 4px; font-size: 12px; color: var(--text-light)">支持多个文件或文件夹路径</div>
        </el-form-item>
        <el-form-item label="工作流程路径">
          <el-select v-model="form.workflow_paths" multiple filterable allow-create default-first-option placeholder="输入文件/文件夹路径后回车添加" style="width: 100%" />
          <div style="margin-top: 4px; font-size: 12px; color: var(--text-light)">支持多个文件或文件夹路径</div>
        </el-form-item>
        <el-form-item label="审核标准路径">
          <el-select v-model="form.standard_paths" multiple filterable allow-create default-first-option placeholder="输入文件/文件夹路径后回车添加" style="width: 100%" />
          <div style="margin-top: 4px; font-size: 12px; color: var(--text-light)">支持多个文件或文件夹路径</div>
        </el-form-item>
        <el-form-item label="配置标签">
          <el-select v-model="form.tags" multiple filterable allow-create default-first-option placeholder="输入标签后回车添加" style="width: 100%">
            <el-option v-for="t in allTags" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { aiConfigAPI } from '@/api'
import api from '@/api'
import Sortable from 'sortablejs'

const configs = ref([])
const showDialog = ref(false)
const editingId = ref(null)
const modelOptions = ref([])
const modelsLoading = ref(false)
const allTags = ref([])
const tableRef = ref(null)

const defaultForm = () => ({
  name: '', api_url: '', api_key: '', review_model: '', recheck_model: '', stream_enabled: false,
  reference_paths: ['./docs/references'], format_paths: ['./docs/format'], workflow_paths: ['./docs/workflow'], standard_paths: ['./docs/standards'], tags: []
})
const form = ref(defaultForm())

const loadConfigs = async () => {
  try {
    const { data } = await aiConfigAPI.getAll()
    configs.value = data
    await nextTick()
    initSortable()
  } catch (error) {
    ElMessage.error('加载配置失败')
  }
}

const initSortable = () => {
  if (!tableRef.value) return
  const tbody = tableRef.value.$el.querySelector('.el-table__body-wrapper tbody')
  if (!tbody) return

  Sortable.create(tbody, {
    handle: '.drag-handle',
    animation: 150,
    ghostClass: 'sortable-ghost',
    onEnd: async (evt) => {
      const oldIndex = evt.oldIndex
      const newIndex = evt.newIndex

      if (oldIndex === newIndex) return

      const movedItem = configs.value.splice(oldIndex, 1)[0]
      configs.value.splice(newIndex, 0, movedItem)

      const order = configs.value.map(c => c.id)
      try {
        await api.put('/ai-configs/reorder', order)
        ElMessage.success('排序已保存')
      } catch (error) {
        ElMessage.error('保存排序失败')
        loadConfigs()
      }
    }
  })
}

const loadAllTags = async () => {
  try {
    const { data } = await api.get('/tags')
    allTags.value = data.tags || []
  } catch (error) { /* ignore */ }
}

const fetchModels = async () => {
  if (!form.value.api_url || !form.value.api_key) {
    ElMessage.warning('请先填写API地址和API密钥')
    return
  }
  modelsLoading.value = true
  try {
    if (editingId.value) {
      const { data } = await aiConfigAPI.getModels(editingId.value)
      modelOptions.value = data.models || []
    } else {
      const { data } = await api.post('/ai-configs/fetch-models', {
        api_url: form.value.api_url, api_key: form.value.api_key
      })
      modelOptions.value = data.models || []
    }
    if (modelOptions.value.length > 0) {
      ElMessage.success(`已加载 ${modelOptions.value.length} 个模型`)
    } else {
      ElMessage.warning('未获取到模型列表')
    }
  } catch (error) {
    ElMessage.error('加载模型失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    modelsLoading.value = false
  }
}
const openAddDialog = () => {
  editingId.value = null
  form.value = defaultForm()
  modelOptions.value = []
  showDialog.value = true
}

const editConfig = (config) => {
  editingId.value = config.id
  form.value = {
    ...config,
    reference_paths: config.reference_paths || [],
    format_paths: config.format_paths || [],
    workflow_paths: config.workflow_paths || [],
    standard_paths: config.standard_paths || [],
    tags: config.tags || []
  }
  modelOptions.value = []
  showDialog.value = true
}

const resetForm = () => {
  editingId.value = null
  form.value = defaultForm()
  modelOptions.value = []
}

const saveConfig = async () => {
  try {
    if (editingId.value) {
      await aiConfigAPI.update(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await aiConfigAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    resetForm()
    loadConfigs()
    loadAllTags()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const activateConfig = async (id) => {
  try {
    await aiConfigAPI.activate(id)
    ElMessage.success('激活成功')
    loadConfigs()
  } catch (error) {
    ElMessage.error('激活失败')
  }
}

const deleteConfig = async (id) => {
  try {
    await aiConfigAPI.delete(id)
    ElMessage.success('删除成功')
    loadConfigs()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadConfigs()
  loadAllTags()
})
</script>

<style scoped>
.ai-config {
  padding: 20px;
}

.sortable-ghost {
  opacity: 0.4;
  background: #f5f7fa;
}

.drag-handle {
  transition: all 0.3s ease;
}

.drag-handle:hover {
  transform: scale(1.2);
}
</style>

<template>
  <div class="projects">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>项目管理</span>
          <el-button type="primary" @click="openAddDialog">添加项目</el-button>
        </div>
      </template>

      <el-table :data="projects" style="width: 100%" row-key="id" ref="tableRef">
        <el-table-column width="50" align="center">
          <template #default>
            <el-icon class="drag-handle" style="cursor: move; color: #ff8c42">
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
        <el-table-column prop="name" label="项目名称" width="150" />
        <el-table-column prop="path" label="项目路径" width="250" />
        <el-table-column prop="default_branch" label="当前分支" width="100" />
        <el-table-column prop="base_branch" label="基准分支" width="100" />
        <el-table-column label="统计信息" width="350">
          <template #default="{ row }">
            <div class="stats-container">
              <el-tooltip content="审查次数" placement="top">
                <el-tag size="small" type="info" class="stat-tag">
                  <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ row.stats?.total_reviews || 0 }}
                </el-tag>
              </el-tooltip>
              <el-tooltip content="当前问题数" placement="top">
                <el-tag size="small" type="warning" class="stat-tag">
                  <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 5H7.2C6.0799 5 5.51984 5 5.09202 5.21799C4.71569 5.40973 4.40973 5.71569 4.21799 6.09202C4 6.51984 4 7.0799 4 8.2V20L8.5 17.5L12 20L15.5 17.5L20 20V8.2C20 7.0799 20 6.51984 19.782 6.09202C19.5903 5.71569 19.2843 5.40973 18.908 5.21799C18.4802 5 17.9201 5 16.8 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5M12 12H16M12 16H16M8 12H8.01M8 16H8.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ row.stats?.total_issues || 0 }}
                </el-tag>
              </el-tooltip>
              <el-tooltip content="已解决" placement="top">
                <el-tag size="small" type="success" class="stat-tag">
                  <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ row.stats?.resolved || 0 }}
                </el-tag>
              </el-tooltip>
              <el-tooltip content="已忽略" placement="top">
                <el-tag size="small" class="stat-tag">
                  <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ row.stats?.ignored || 0 }}
                </el-tag>
              </el-tooltip>
              <el-tooltip content="待解决" placement="top">
                <el-tag size="small" type="danger" class="stat-tag">
                  <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 8V12M12 16H12.01M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ row.stats?.pending || 0 }}
                </el-tag>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="标签" width="150">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag" size="small" style="margin-right: 5px">{{ tag }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="editProject(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProject(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑项目' : '添加项目'" width="600px" @close="resetForm">
      <el-form :model="form" label-width="120px">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目路径">
          <el-input v-model="form.path" placeholder="请输入项目本地路径" />
          <el-button size="small" style="margin-top: 4px" @click="loadBranches" :loading="branchesLoading" :disabled="!form.path">
            加载分支列表
          </el-button>
        </el-form-item>
        <el-form-item label="当前分支">
          <el-input v-model="form.default_branch" readonly placeholder="自动获取当前分支" style="width: 100%" />
        </el-form-item>
        <el-form-item label="基准分支">
          <el-select v-model="form.base_branch" filterable allow-create default-first-option placeholder="选择或输入基准分支" style="width: 100%" :loading="branchesLoading">
            <el-option v-for="b in branchOptions" :key="b" :label="b" :value="b">
              <span>{{ b }}</span>
              <el-tag v-if="remoteBranches.includes(b)" size="small" type="success" style="margin-left: 8px">远程</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="子路径">
          <el-select v-model="form.sub_paths" multiple filterable allow-create default-first-option placeholder="输入子路径后回车添加" style="width: 100%" />
        </el-form-item>
        <el-form-item label="项目标签">
          <el-select v-model="form.tags" multiple filterable allow-create default-first-option placeholder="输入标签后回车添加" style="width: 100%">
            <el-option v-for="t in allTags" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目图标">
          <el-input v-model="form.icon" placeholder="可选，输入图标标识" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="项目备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProject">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { projectAPI } from '@/api'
import api from '@/api'
import Sortable from 'sortablejs'

const projects = ref([])
const showDialog = ref(false)
const editingId = ref(null)
const branchOptions = ref([])
const remoteBranches = ref([])
const branchesLoading = ref(false)
const allTags = ref([])
const tableRef = ref(null)

const defaultForm = () => ({
  name: '', path: '', default_branch: '', base_branch: 'main', sub_paths: [], tags: [], icon: '', notes: ''
})
const form = ref(defaultForm())

const loadProjects = async () => {
  try {
    const { data } = await projectAPI.getAll()

    // Load stats for each project
    for (const project of data) {
      try {
        const statsRes = await projectAPI.getStats(project.id)
        project.stats = statsRes.data
      } catch (error) {
        project.stats = { total_reviews: 0, total_issues: 0, resolved: 0, ignored: 0, pending: 0 }
      }
    }

    projects.value = data
    await nextTick()
    initSortable()
  } catch (error) {
    ElMessage.error('加载项目失败')
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

      const movedItem = projects.value.splice(oldIndex, 1)[0]
      projects.value.splice(newIndex, 0, movedItem)

      const order = projects.value.map(p => p.id)
      try {
        await api.put('/projects/reorder', order)
        ElMessage.success('排序已保存')
      } catch (error) {
        ElMessage.error('保存排序失败')
        loadProjects()
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

const loadBranches = async () => {
  if (!form.value.path) {
    ElMessage.warning('请先填写项目路径')
    return
  }
  branchesLoading.value = true
  try {
    if (editingId.value) {
      const { data } = await projectAPI.getBranches(editingId.value)
      branchOptions.value = data.branches || []
      if (data.current) {
        form.value.default_branch = data.current
      }
      const remoteResp = await api.post('/projects/fetch-remote-branches', { project_id: editingId.value })
      remoteBranches.value = remoteResp.data.branches || []
      branchOptions.value = [...new Set([...branchOptions.value, ...remoteBranches.value])]
    } else {
      const { data } = await api.post('/projects/fetch-branches', { path: form.value.path })
      branchOptions.value = data.branches || []
      if (data.current) {
        form.value.default_branch = data.current
      }
      remoteBranches.value = []
    }
    if (branchOptions.value.length > 0) {
      ElMessage.success(`已加载 ${branchOptions.value.length} 个分支`)
    } else {
      ElMessage.warning('未获取到分支列表')
    }
  } catch (error) {
    ElMessage.error('加载分支失败: ' + (error.response?.data?.detail || error.message))
    branchOptions.value = []
  } finally {
    branchesLoading.value = false
  }
}

const openAddDialog = () => {
  editingId.value = null
  form.value = defaultForm()
  branchOptions.value = []
  showDialog.value = true
}

const editProject = (project) => {
  editingId.value = project.id
  form.value = { ...project, tags: project.tags || [], sub_paths: project.sub_paths || [] }
  branchOptions.value = []
  showDialog.value = true
}

const resetForm = () => {
  editingId.value = null
  form.value = defaultForm()
  branchOptions.value = []
}

const saveProject = async () => {
  try {
    if (editingId.value) {
      await projectAPI.update(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await projectAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    resetForm()
    loadProjects()
    loadAllTags()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteProject = async (id) => {
  try {
    await projectAPI.delete(id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadProjects()
  loadAllTags()
})
</script>

<style scoped>
.projects {
  padding: 20px;
}

.sortable-ghost {
  opacity: 0.4;
  background: #fff5f0;
}

.drag-handle {
  transition: all 0.2s ease;
  cursor: move;
}

.drag-handle:hover {
  transform: scale(1.2);
}

.stats-container {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.stat-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.stat-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.stat-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(255, 140, 66, 0.3);
}
</style>
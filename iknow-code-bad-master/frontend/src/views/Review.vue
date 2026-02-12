<template>
  <div class="review">
    <el-container style="height: calc(100vh - 60px)">
      <!-- 左侧项目列表 -->
      <el-aside width="280px" class="project-sidebar">
        <div class="sidebar-header">
          <h3>项目列表</h3>
          <el-input
            v-model="projectSearch"
            placeholder="搜索项目"
            clearable
            size="small"
            style="margin-top: 12px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div class="project-list">
          <div
            v-for="project in filteredProjects"
            :key="project.id"
            class="project-item"
            :class="{ active: selectedProjectId === project.id }"
            @click="selectProject(project.id)"
          >
            <svg class="project-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 7L11.8845 4.76892C11.5634 4.1268 11.4029 3.80573 11.1634 3.57116C10.9516 3.36373 10.6963 3.20597 10.4161 3.10931C10.0992 3 9.74021 3 9.02229 3H5.2C4.0799 3 3.51984 3 3.09202 3.21799C2.71569 3.40973 2.40973 3.71569 2.21799 4.09202C2 4.51984 2 5.0799 2 6.2V7M2 7H17.2C18.8802 7 19.7202 7 20.362 7.32698C20.9265 7.6146 21.3854 8.07354 21.673 8.63803C22 9.27976 22 10.1198 22 11.8V16.2C22 17.8802 22 18.7202 21.673 19.362C21.3854 19.9265 20.9265 20.3854 20.362 20.673C19.7202 21 18.8802 21 17.2 21H6.8C5.11984 21 4.27976 21 3.63803 20.673C3.07354 20.3854 2.6146 19.9265 2.32698 19.362C2 18.7202 2 17.8802 2 16.2V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="project-info">
              <div class="project-name">{{ project.name }}</div>
              <div class="project-stats">
                <el-tag size="small" type="warning">{{ project.stats?.total_issues || 0 }}</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-if="filteredProjects.length === 0" description="暂无项目" :image-size="80" />
        </div>
      </el-aside>

      <!-- 右侧主内容区 -->
      <el-main class="main-content">
        <div v-if="selectedProject">
          <!-- 上部分：分支信息、文件统计、数据统计 -->
          <el-card class="info-card" style="margin-bottom: 20px">
            <el-row :gutter="20">
              <!-- 分支信息 -->
              <el-col :span="8">
                <div class="info-section">
                  <div class="section-header">
                    <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6 3V15M18 9V21M6 15C4.34315 15 3 16.3431 3 18C3 19.6569 4.34315 21 6 21C7.65685 21 9 19.6569 9 18C9 16.3431 7.65685 15 6 15ZM18 9C16.3431 9 15 7.65685 15 6C15 4.34315 16.3431 3 18 3C19.6569 3 21 4.34315 21 6C21 7.65685 19.6569 9 18 9ZM18 9C16.3431 9 15 10.3431 15 12C15 13.6569 16.3431 15 18 15C19.6569 15 21 13.6569 21 12C21 10.3431 19.6569 9 18 9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h4>分支信息</h4>
                  </div>
                  <div class="info-content">
                    <div class="info-row">
                      <span class="info-label">当前分支</span>
                      <el-tag type="success" size="small">{{ currentBranch || '未知' }}</el-tag>
                    </div>
                    <div class="info-row">
                      <span class="info-label">基准分支</span>
                      <el-select
                        v-model="baseBranch"
                        filterable
                        placeholder="选择"
                        size="small"
                        @change="onBaseBranchChange"
                      >
                        <el-option
                          v-for="branch in branches"
                          :key="branch"
                          :label="branch"
                          :value="branch"
                        />
                      </el-select>
                    </div>
                  </div>
                  <el-button
                    type="primary"
                    size="small"
                    style="margin-top: 12px; width: 100%; border-radius: 8px"
                    @click="goToBranchReview"
                  >
                    前往分支审查
                  </el-button>
                </div>
              </el-col>

              <!-- 文件统计 -->
              <el-col :span="8">
                <div class="info-section">
                  <div class="section-header">
                    <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 19V6L3 12L9 19ZM9 19H21M15 5V18L21 12L15 5ZM15 5H3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h4>文件统计</h4>
                  </div>
                  <div class="stats-grid">
                    <div class="stat-card">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 12H15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <div class="stat-info">
                        <div class="stat-label">修改</div>
                        <div class="stat-value">{{ gitStatus.modified_files || 0 }}</div>
                      </div>
                    </div>
                    <div class="stat-card">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <div class="stat-info">
                        <div class="stat-label">新增</div>
                        <div class="stat-value">{{ gitStatus.added_files || 0 }}</div>
                      </div>
                    </div>
                    <div class="stat-card">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 6H21M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <div class="stat-info">
                        <div class="stat-label">删除</div>
                        <div class="stat-value">{{ gitStatus.deleted_files || 0 }}</div>
                      </div>
                    </div>
                    <div class="stat-card">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <div class="stat-info">
                        <div class="stat-label">提交</div>
                        <div class="stat-value">{{ gitStatus.staged_commits || 0 }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </el-col>

              <!-- 问题统计 -->
              <el-col :span="8">
                <div class="info-section">
                  <div class="section-header">
                    <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 5H7.2C6.0799 5 5.51984 5 5.09202 5.21799C4.71569 5.40973 4.40973 5.71569 4.21799 6.09202C4 6.51984 4 7.0799 4 8.2V20L8.5 17.5L12 20L15.5 17.5L20 20V8.2C20 7.0799 20 6.51984 19.782 6.09202C19.5903 5.71569 19.2843 5.40973 18.908 5.21799C18.4802 5 17.9201 5 16.8 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5M12 12H16M12 16H16M8 12H8.01M8 16H8.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h4>问题统计</h4>
                  </div>
                  <div class="stats-grid">
                    <div class="stat-card">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 6V12L16 14M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <div class="stat-info">
                        <div class="stat-label">待解决</div>
                        <div class="stat-value">{{ stats.pending || 0 }}</div>
                      </div>
                    </div>
                    <div class="stat-card">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <div class="stat-info">
                        <div class="stat-label">已解决</div>
                        <div class="stat-value">{{ stats.resolved || 0 }}</div>
                      </div>
                    </div>
                    <div class="stat-card">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <div class="stat-info">
                        <div class="stat-label">已忽略</div>
                        <div class="stat-value">{{ stats.ignored || 0 }}</div>
                      </div>
                    </div>
                    <div class="stat-card">
                      <svg class="stat-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 19V6L3 12L9 19ZM9 19H21M15 5V18L21 12L15 5ZM15 5H3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <div class="stat-info">
                        <div class="stat-label">总计</div>
                        <div class="stat-value">{{ stats.total || 0 }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>

          <!-- 下部分：问题列表 -->
          <el-card class="issues-card">
            <template #header>
              <div class="issues-header">
                <span>问题列表</span>
                <div class="filter-controls">
                  <el-select
                    v-model="statusFilter"
                    placeholder="筛选状态"
                    clearable
                    size="small"
                    style="width: 120px"
                    @change="handleFilterChange"
                  >
                    <el-option label="全部" value="" />
                    <el-option label="待审核" value="待审核" />
                    <el-option label="待排期" value="待排期" />
                    <el-option label="待解决" value="待解决" />
                    <el-option label="修改中" value="修改中" />
                    <el-option label="待复查" value="待复查" />
                    <el-option label="已解决" value="已解决" />
                    <el-option label="已忽略" value="已忽略" />
                  </el-select>
                  <el-select
                    v-model="severityFilter"
                    placeholder="重要程度"
                    clearable
                    size="small"
                    style="width: 120px"
                    @change="handleFilterChange"
                  >
                    <el-option label="致命" value="致命" />
                    <el-option label="高" value="高" />
                    <el-option label="中" value="中" />
                    <el-option label="低" value="低" />
                    <el-option label="建议" value="建议" />
                  </el-select>
                  <el-select
                    v-model="sortBy"
                    placeholder="排序方式"
                    size="small"
                    style="width: 140px"
                    @change="handleSortChange"
                  >
                    <el-option label="创建时间 ↓" value="created_at_desc" />
                    <el-option label="创建时间 ↑" value="created_at_asc" />
                    <el-option label="严重程度 ↓" value="severity_desc" />
                    <el-option label="严重程度 ↑" value="severity_asc" />
                    <el-option label="状态" value="status" />
                  </el-select>
                </div>
              </div>
            </template>

            <div v-if="issues.length === 0" class="empty-state">
              <el-empty description="暂无问题" />
            </div>

            <el-row :gutter="20" v-else>
              <el-col :xs="24" :sm="12" :lg="8" v-for="issue in issues" :key="issue.id" style="margin-bottom: 20px">
                <el-card shadow="hover" class="issue-card">
                  <div class="issue-header">
                    <el-tag :type="getStatusType(displayStatus(issue))" size="small">{{ displayStatus(issue) || '待审核' }}</el-tag>
                    <el-tag v-if="issue.severity" :type="getSeverityTagType(issue.severity)" size="small" style="margin-left: 8px">
                      {{ issue.severity }}
                    </el-tag>
                  </div>
                  <div class="issue-title">{{ issue.issue_type }}</div>
                  <div class="issue-description">{{ issue.description }}</div>
                  <div class="issue-file">{{ issue.file_path }}:{{ issue.line_start }}</div>

                  <!-- 主要操作 -->
                  <div class="issue-actions-primary">
                    <el-button size="small" type="primary" @click="viewDetail(issue.id)">查看详细</el-button>
                    <el-button size="small" @click="recheckIssue(issue.id)" :loading="recheckingId === issue.id">复查代码</el-button>
                  </div>

                  <!-- 状态管理 -->
                  <div class="issue-actions-status">
                    <el-dropdown @command="(cmd) => handleStatusChange(issue.id, cmd)" style="width: 100%">
                      <el-button size="small" style="width: 100%">
                        修改状态 <el-icon class="el-icon--right"><arrow-down /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="待审核">待审核</el-dropdown-item>
                          <el-dropdown-item command="待排期">待排期</el-dropdown-item>
                          <el-dropdown-item command="待解决">待解决</el-dropdown-item>
                          <el-dropdown-item command="修改中">修改中</el-dropdown-item>
                          <el-dropdown-item command="待复查">待复查</el-dropdown-item>
                          <el-dropdown-item command="已解决">已解决</el-dropdown-item>
                          <el-dropdown-item command="已忽略">已忽略</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                    <el-button
                      size="small"
                      type="success"
                      @click="resolveIssue(issue.id)"
                      :disabled="issue.is_ignored || displayStatus(issue) === '已忽略'"
                      style="flex: 1"
                    >标记已解决</el-button>
                  </div>

                  <!-- 次要操作 -->
                  <div class="issue-actions-secondary">
                    <el-button size="small" plain @click="ignoreIssue(issue.id)">忽略</el-button>
                    <el-button size="small" plain @click="ignoreSimilar(issue)">忽略同类</el-button>
                    <el-button size="small" type="danger" plain @click="deleteIssue(issue.id)">删除</el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-pagination
              v-if="total > 0"
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              style="margin-top: 20px; justify-content: center"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </el-card>
        </div>

        <el-empty v-else description="请选择项目" :image-size="120" />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowDown } from '@element-plus/icons-vue'
import { projectAPI, issueAPI } from '@/api'
import api from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const projects = ref([])
const projectSearch = ref('')
const selectedProjectId = ref(null)
const selectedProject = computed(() => projects.value.find(p => p.id === selectedProjectId.value))
const filteredProjects = computed(() => {
  if (!projectSearch.value) return projects.value
  return projects.value.filter(p => p.name.toLowerCase().includes(projectSearch.value.toLowerCase()))
})

const issues = ref([])
const statusFilter = ref('待解决')
const severityFilter = ref('')
const sortBy = ref('created_at_desc')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const recheckingId = ref(null)

const currentBranch = ref('')
const baseBranch = ref('main')
const branches = ref([])
const gitStatus = ref({
  modified_files: 0,
  added_files: 0,
  deleted_files: 0,
  staged_commits: 0
})

const stats = ref({
  pending: 0,
  resolved: 0,
  ignored: 0,
  total: 0
})

const STORAGE_KEY = 'review_page_config'
const statusFilterNormalizeMap = { '待审批': '待审核', '已完成': '已解决' }
const normalizeStatusFilter = (value) => statusFilterNormalizeMap[value] || value

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

    // Restore selected project
    const saved = loadConfig()
    if (saved && saved.selectedProjectId) {
      const project = data.find(p => p.id === saved.selectedProjectId)
      if (project) {
        selectedProjectId.value = project.id
        baseBranch.value = saved.baseBranch || 'main'
        currentPage.value = saved.currentPage || 1
        pageSize.value = saved.pageSize || 20
        sortBy.value = saved.sortBy || 'created_at_desc'
        statusFilter.value = normalizeStatusFilter(saved.statusFilter ?? statusFilter.value)
        severityFilter.value = saved.severityFilter ?? severityFilter.value
        await loadProjectData()
      }
    } else if (data.length > 0) {
      selectedProjectId.value = data[0].id
      await loadProjectData()
    }
  } catch (error) {
    ElMessage.error('加载项目失败')
  }
}

const loadConfig = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? JSON.parse(saved) : null
  } catch (e) {
    return null
  }
}

const saveConfig = () => {
  const config = {
    selectedProjectId: selectedProjectId.value,
    baseBranch: baseBranch.value,
    currentPage: currentPage.value,
    pageSize: pageSize.value,
    sortBy: sortBy.value,
    statusFilter: statusFilter.value,
    severityFilter: severityFilter.value
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
}

const selectProject = async (projectId) => {
  selectedProjectId.value = projectId
  currentPage.value = 1
  await loadProjectData()
  saveConfig()
}

const loadProjectData = async () => {
  if (!selectedProject.value) return
  await Promise.all([
    loadBranches(),
    loadFullStats(),
    loadIssues()
  ])
}

const loadBranches = async () => {
  if (!selectedProject.value) return
  try {
    const { data } = await projectAPI.getBranches(selectedProject.value.id)
    branches.value = data.branches || []
    currentBranch.value = data.current || 'main'
    if (!baseBranch.value || !branches.value.includes(baseBranch.value)) {
      baseBranch.value = selectedProject.value.base_branch || 'main'
    }
  } catch (error) {
    branches.value = []
    currentBranch.value = 'main'
  }
}

const loadFullStats = async () => {
  if (!selectedProject.value) return
  try {
    const { data } = await api.post(`/projects/${selectedProject.value.id}/full-stats`, {
      base_branch: baseBranch.value
    })

    // 更新当前分支
    currentBranch.value = data.current_branch || 'main'

    // 更新git状态
    gitStatus.value = data.git_status || {
      modified_files: 0,
      added_files: 0,
      deleted_files: 0,
      staged_commits: 0
    }

    // 更新问题统计
    stats.value = data.issue_stats || {
      pending: 0,
      resolved: 0,
      ignored: 0,
      total: 0
    }
  } catch (error) {
    gitStatus.value = {
      modified_files: 0,
      added_files: 0,
      deleted_files: 0,
      staged_commits: 0
    }
    stats.value = { pending: 0, resolved: 0, ignored: 0, total: 0 }
  }
}

const onBaseBranchChange = () => {
  loadFullStats()
  saveConfig()
}

const loadIssues = async () => {
  if (!selectedProject.value) return
  try {
    const params = {
      project_id: selectedProject.value.id,
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (statusFilter.value) params.status = statusFilter.value
    if (severityFilter.value) params.severity = severityFilter.value

    const { data, headers } = await issueAPI.getAll(params)

    // Apply client-side sorting
    let sortedData = [...data]
    if (sortBy.value === 'created_at_desc') {
      sortedData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    } else if (sortBy.value === 'created_at_asc') {
      sortedData.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    } else if (sortBy.value === 'severity_desc') {
      const severityOrder = { '致命': 4, '高': 3, '中': 2, '低': 1, '建议': 0 }
      sortedData.sort((a, b) => (severityOrder[b.severity] ?? -1) - (severityOrder[a.severity] ?? -1))
    } else if (sortBy.value === 'severity_asc') {
      const severityOrder = { '致命': 4, '高': 3, '中': 2, '低': 1, '建议': 0 }
      sortedData.sort((a, b) => (severityOrder[a.severity] ?? -1) - (severityOrder[b.severity] ?? -1))
    } else if (sortBy.value === 'status') {
      sortedData.sort((a, b) => (displayStatus(a) || '').localeCompare(displayStatus(b) || ''))
    }

    issues.value = sortedData
    total.value = parseInt(headers['x-total-count'] || data.length)
  } catch (error) {
    ElMessage.error('加载问题失败')
  }
}

const handleSortChange = () => {
  currentPage.value = 1
  loadIssues()
  saveConfig()
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadIssues()
  saveConfig()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadIssues()
  saveConfig()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadIssues()
  saveConfig()
}

const handleStatusChange = async (issueId, status) => {
  try {
    if (status === '已忽略') {
      await issueAPI.updateStatus(issueId, { is_ignored: true })
    } else {
      await issueAPI.updateStatus(issueId, { status, is_ignored: false })
    }
    ElMessage.success('状态已更新')
    loadIssues()
    loadFullStats()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const resolveIssue = async (id) => {
  const target = issues.value.find(i => i.id === id)
  if (target && (target.is_ignored || displayStatus(target) === '已忽略')) {
    ElMessage.warning('已忽略的问题不能标记为已解决')
    return
  }
  try {
    await issueAPI.resolve(id)
    ElMessage.success('已标记为已解决')
    loadIssues()
    loadFullStats()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const ignoreIssue = async (id) => {
  try {
    await issueAPI.updateStatus(id, { is_ignored: true })
    ElMessage.success('已忽略')
    loadIssues()
    loadFullStats()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteIssue = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此问题吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await issueAPI.delete(id)
    ElMessage.success('已删除')
    loadIssues()
    loadFullStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const statusAliasMap = {
  pending_review: '待审核',
  scheduled: '待排期',
  in_progress: '修改中',
  pending_recheck: '待复查',
  resolved: '已解决',
  pending: '待解决',
  '待审批': '待审核',
  '已完成': '已解决'
}

const normalizeStatus = (status) => statusAliasMap[status] || status

const displayStatus = (issue) => {
  if (!issue) return ''
  if (issue.is_ignored) return '已忽略'
  return normalizeStatus(issue.status)
}

const getStatusType = (status) => {
  const types = {
    '待审核': 'info',
    '待排期': 'warning',
    '待解决': 'warning',
    '修改中': 'primary',
    '待复查': 'warning',
    '已解决': 'success',
    '已忽略': 'info'
  }
  return types[status] || 'info'
}

const getSeverityTagType = (severity) => {
  const types = { '致命': 'danger', '高': 'danger', '中': 'warning', '低': 'info', '建议': '' }
  return types[severity] || 'info'
}

const viewDetail = (id) => {
  router.push(`/issue/${id}`)
}

const recheckIssue = async (id) => {
  try {
    recheckingId.value = id
    await ElMessageBox.confirm('确定要对此问题进行复查吗？', '复查确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    await issueAPI.chat(id, '请重新审查这个问题，给出详细的分析和建议。')
    ElMessage.success('复查请求已提交，请在详情页查看结果')
    viewDetail(id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('复查失败')
    }
  } finally {
    recheckingId.value = null
  }
}

const ignoreSimilar = async (issue) => {
  try {
    await ElMessageBox.confirm(
      `确定要忽略所有类型为"${issue.issue_type}"的问题吗？`,
      '忽略同类问题',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await issueAPI.ignoreSimilar(issue.issue_type, selectedProject.value.id)
    ElMessage.success('已忽略同类问题')
    loadIssues()
    loadFullStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const goToBranchReview = () => {
  router.push('/branch-review')
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.review {
  height: 100%;
  background: #f5f7fa;
}

/* 左侧项目列表 */
.project-sidebar {
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h3 {
  margin: 0;
  color: var(--text-dark);
  font-size: 16px;
  font-weight: 600;
}

.project-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: #f5f7fa;
}

.project-item:hover {
  background: #fff5f0;
  transform: translateX(4px);
}

.project-item.active {
  background: linear-gradient(135deg, #ff8c42 0%, #ff6b35 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(255, 140, 66, 0.3);
}

.project-icon {
  width: 24px;
  height: 24px;
  color: currentColor;
  flex-shrink: 0;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-item.active .project-name {
  color: white;
}

.project-stats {
  margin-top: 4px;
}

/* 右侧主内容区 */
.main-content {
  padding: 20px;
  overflow-y: auto;
}

.info-card {
  border-radius: 12px;
}

.info-card :deep(.el-card__body) {
  border-radius: 12px;
}

.info-section h4 {
  margin: 0;
  color: var(--text-dark);
  font-size: 14px;
  font-weight: 600;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: var(--primary-orange);
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.info-label {
  font-size: 13px;
  color: var(--text-medium);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-light);
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-card:hover {
  background: var(--primary-orange-lighter);
  transform: translateY(-2px);
}

.stat-icon {
  width: 24px;
  height: 24px;
  color: var(--primary-orange);
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--text-medium);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-orange);
}

/* 问题列表 */
.issues-card {
  border-radius: 12px;
}

.issues-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-controls {
  display: flex;
  gap: 12px;
}

.empty-state {
  padding: 40px 0;
}

.issue-card {
  height: 100%;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.issue-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(255, 140, 66, 0.2);
}

.issue-header {
  margin-bottom: 12px;
}

.issue-title {
  font-weight: 600;
  font-size: 15px;
  color: var(--text-dark);
  margin-bottom: 8px;
}

.issue-description {
  color: var(--text-medium);
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.issue-file {
  font-size: 12px;
  color: var(--text-light);
  font-family: 'Courier New', monospace;
  margin-bottom: 16px;
}

.issue-actions-primary {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.issue-actions-primary .el-button {
  flex: 1;
  border-radius: 8px;
}

.issue-actions-status {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.issue-actions-status .el-button {
  border-radius: 8px;
}

.issue-actions-secondary {
  display: flex;
  gap: 8px;
}

.issue-actions-secondary .el-button {
  flex: 1;
  border-radius: 8px;
}
</style>

<template>
  <div class="issue-detail">
    <!-- Back Button -->
    <div class="back-bar">
      <el-button :icon="ArrowLeft" @click="$router.push('/review')" class="back-btn">
        返回问题列表
      </el-button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <template v-else-if="issue">
      <!-- Issue Info Card -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="info-card-header">
            <h2 class="info-title">{{ issue.issue_type }}</h2>
            <div class="info-header-actions">
              <el-select
                v-model="statusValue"
                placeholder="更新状态"
                class="status-select"
                @change="handleStatusChange"
              >
                <el-option
                  v-for="opt in statusOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <el-button
                type="success"
                @click="handleResolve"
                :loading="resolving"
                :disabled="resolving || issue?.is_ignored || displayStatus === '已忽略'"
              >
                标记已解决
              </el-button>
            </div>
          </div>
        </template>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="问题类型">
            <el-select v-model="issue.issue_type" placeholder="选择问题类型" size="small" @change="handleIssueTypeChange" filterable allow-create>
              <el-option v-for="type in issueTypeOptions" :key="type" :label="type" :value="type" />
            </el-select>
          </el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-select v-model="issue.severity" placeholder="选择严重程度" size="small" @change="handleSeverityChange">
              <el-option label="致命" value="致命" />
              <el-option label="高" value="高" />
              <el-option label="中" value="中" />
              <el-option label="低" value="低" />
              <el-option label="建议" value="建议" />
            </el-select>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTagType">{{ statusLabel }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="文件路径" :span="2">
            <span class="file-path-text">{{ issue.file_path }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="行号">
            <span v-if="issue.line_start && issue.line_end">
              第 {{ issue.line_start }} - {{ issue.line_end }} 行
            </span>
            <span v-else-if="issue.line_start">第 {{ issue.line_start }} 行</span>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="3">
            <div class="issue-description">{{ issue.description }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Code Display Area with File Tree -->
      <el-card class="code-card" shadow="hover">
        <template #header>
          <h3 class="section-title">相关代码</h3>
        </template>
        <div class="code-layout">
          <!-- Left: File Tree -->
          <div class="file-tree">
            <div
              v-for="file in fileList"
              :key="file.path"
              class="file-item"
              :class="{ active: selectedFile === file.path }"
              @click="selectFile(file.path)"
            >
              <svg class="file-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12H15M12 9V15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="file-name">{{ file.name }}</span>
            </div>
            <el-empty v-if="fileList.length === 0" description="暂无文件" :image-size="60" />
          </div>

          <!-- Right: Code Viewer -->
          <div class="code-viewer">
            <div v-if="currentCode" class="code-container">
              <div class="code-header">
                <span class="code-file-path">{{ selectedFile }}</span>
              </div>
              <div class="code-block">
                <pre class="code-pre"><code>{{ currentCode }}</code></pre>
              </div>
            </div>
            <el-empty v-else description="请选择文件查看代码" :image-size="80" />
          </div>
        </div>
      </el-card>

      <!-- AI Chat Area -->
      <el-card class="chat-card" shadow="hover">
        <template #header>
          <h3 class="section-title">AI 对话</h3>
        </template>
        <div class="chat-messages" ref="chatMessagesRef">
          <div v-if="chatHistory.length === 0 && !chatLoading" class="chat-empty">
            <p>暂无对话记录，发送消息开始与 AI 讨论此问题。</p>
          </div>
          <div
            v-for="(msg, index) in chatHistory"
            :key="index"
            class="chat-message"
            :class="msg.role === 'user' ? 'chat-message-user' : 'chat-message-ai'"
          >
            <div class="chat-bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-ai'">
              <div class="bubble-content">{{ msg.content }}</div>
              <div class="bubble-time" v-if="msg.created_at">
                {{ formatTime(msg.created_at) }}
              </div>
            </div>
          </div>
          <div v-if="chatLoading" class="chat-message chat-message-ai">
            <div class="chat-bubble bubble-ai">
              <div class="bubble-content typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <el-input
            v-model="chatInput"
            type="textarea"
            :rows="2"
            placeholder="输入你的问题，与 AI 讨论此问题..."
            resize="none"
            @keydown.enter.ctrl="sendMessage"
            class="chat-input"
          />
          <el-button
            type="primary"
            :icon="Promotion"
            :loading="chatLoading"
            :disabled="!chatInput.trim()"
            @click="sendMessage"
            class="send-btn"
          >
            发送
          </el-button>
        </div>
      </el-card>
    </template>

    <!-- Error State -->
    <el-empty v-else description="未找到该问题" :image-size="120">
      <el-button type="primary" @click="$router.push('/review')">返回列表</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Promotion } from '@element-plus/icons-vue'
import { issueAPI } from '@/api'

const route = useRoute()
const router = useRouter()
const issueId = route.params.id

// State
const loading = ref(true)
const resolving = ref(false)
const chatLoading = ref(false)
const issue = ref(null)
const codeData = ref({ code: '', file_path: '' })
const chatHistory = ref([])
const chatInput = ref('')
const chatMessagesRef = ref(null)
const isFirstMessage = ref(true)

// File tree state
const fileList = ref([])
const selectedFile = ref('')
const currentCode = ref('')

// Issue type options
const issueTypeOptions = ref([
  '代码规范问题',
  '潜在Bug',
  '性能问题',
  '安全漏洞',
  '逻辑错误',
  '代码重复',
  '命名不规范',
  '注释缺失',
  '其他'
])

// Status options
const statusOptions = [
  { value: '待审核', label: '待审核' },
  { value: '待排期', label: '待排期' },
  { value: '待解决', label: '待解决' },
  { value: '修改中', label: '修改中' },
  { value: '待复查', label: '待复查' },
  { value: '已解决', label: '已解决' },
  { value: '已忽略', label: '已忽略' }
]

const statusAliasMap = {
  pending_review: '待审核',
  scheduled: '待排期',
  pending: '待解决',
  in_progress: '修改中',
  pending_recheck: '待复查',
  resolved: '已解决',
  '待审批': '待审核',
  '已完成': '已解决'
}

const normalizeStatus = (status) => statusAliasMap[status] || status
const statusValue = ref('')
const displayStatus = computed(() => {
  if (!issue.value) return ''
  if (issue.value.is_ignored) return '已忽略'
  return normalizeStatus(issue.value.status)
})

// Computed
const severityTagType = computed(() => {
  if (!issue.value) return 'info'
  const map = { '致命': 'danger', '高': 'danger', '中': 'warning', '低': 'info', '建议': '' }
  return map[issue.value.severity] || 'info'
})

const statusTagType = computed(() => {
  if (!issue.value) return 'info'
  const map = {
    '待审核': 'info',
    '待排期': 'warning',
    '待解决': 'warning',
    '修改中': 'primary',
    '待复查': 'warning',
    '已解决': 'success',
    '已忽略': 'info'
  }
  return map[displayStatus.value] || 'info'
})

const statusLabel = computed(() => {
  if (!issue.value) return ''
  const opt = statusOptions.find(o => o.value === displayStatus.value)
  return opt ? opt.label : displayStatus.value
})

// Methods
const loadIssue = async () => {
  try {
    const { data } = await issueAPI.getOne(issueId)
    issue.value = data
    if (issue.value) {
      issue.value.status = normalizeStatus(issue.value.status)
      statusValue.value = issue.value.is_ignored ? '已忽略' : issue.value.status
    }
  } catch (error) {
    ElMessage.error('加载问题详情失败')
    issue.value = null
  }
}

const loadCode = async () => {
  try {
    const { data } = await issueAPI.getCode(issueId)
    codeData.value = { code: data.code || '', file_path: data.file_path || '' }

    // Initialize file list
    if (data.file_path) {
      fileList.value = [{ path: data.file_path, name: data.file_path.split('/').pop() }]
      selectedFile.value = data.file_path
      currentCode.value = data.code || ''
    }
  } catch (error) {
    codeData.value = { code: '', file_path: '' }
  }
}

const selectFile = (filePath) => {
  selectedFile.value = filePath
  if (filePath === codeData.value.file_path) {
    currentCode.value = codeData.value.code
  }
}

const handleIssueTypeChange = async () => {
  try {
    await issueAPI.update(issueId, { issue_type: issue.value.issue_type })
    ElMessage.success('问题类型已更新')
  } catch (error) {
    ElMessage.error('更新失败')
    await loadIssue()
  }
}

const handleSeverityChange = async () => {
  try {
    await issueAPI.update(issueId, { severity: issue.value.severity })
    ElMessage.success('严重程度已更新')
  } catch (error) {
    ElMessage.error('更新失败')
    await loadIssue()
  }
}

const loadChatHistory = async () => {
  try {
    const { data } = await issueAPI.getChatHistory(issueId)
    chatHistory.value = Array.isArray(data) ? data : []
    if (chatHistory.value.length > 0) {
      isFirstMessage.value = false
    }
    await nextTick()
    scrollToBottom()
  } catch (error) {
    chatHistory.value = []
  }
}

const scrollToBottom = () => {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

const sendMessage = async () => {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return

  let messageContent = text
  // For the first message, prepend code context so AI understands the code
  if (isFirstMessage.value && codeData.value.code) {
    messageContent = `以下是相关代码（文件：${codeData.value.file_path}）：\n\`\`\`\n${codeData.value.code}\n\`\`\`\n\n问题描述：${issue.value?.description || ''}\n\n我的问题：${text}`
    isFirstMessage.value = false
  }

  // Add user message to chat display (show only the user's typed text)
  chatHistory.value.push({ role: 'user', content: text, created_at: new Date().toISOString() })
  chatInput.value = ''
  chatLoading.value = true
  await nextTick()
  scrollToBottom()

  try {
    const { data } = await issueAPI.chat(issueId, messageContent)
    chatHistory.value.push({ role: 'assistant', content: data.reply, created_at: new Date().toISOString() })
  } catch (error) {
    chatHistory.value.push({ role: 'assistant', content: '抱歉，AI 回复失败，请稍后重试。', created_at: new Date().toISOString() })
    ElMessage.error('发送消息失败')
  } finally {
    chatLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const handleStatusChange = async (newStatus) => {
  try {
    if (newStatus === '已忽略') {
      await issueAPI.updateStatus(issueId, { is_ignored: true })
      if (issue.value) {
        issue.value.is_ignored = true
        issue.value.status = '已忽略'
      }
    } else {
      await issueAPI.updateStatus(issueId, { status: newStatus, is_ignored: false })
      if (issue.value) {
        issue.value.status = newStatus
        issue.value.is_ignored = false
      }
    }
    ElMessage.success('状态已更新')
  } catch (error) {
    ElMessage.error('更新状态失败')
    await loadIssue()
  } finally {
    statusValue.value = displayStatus.value
  }
}

const handleResolve = async () => {
  if (!issue.value || issue.value.is_ignored || displayStatus.value === '已忽略') {
    ElMessage.warning('已忽略的问题不能标记为已解决')
    return
  }
  resolving.value = true
  try {
    await issueAPI.resolve(issueId)
    issue.value.status = '已解决'
    issue.value.is_ignored = false
    statusValue.value = '已解决'
    ElMessage.success('已标记为已解决')
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    resolving.value = false
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  await Promise.all([loadIssue(), loadCode(), loadChatHistory()])
  loading.value = false
})
</script>

<style scoped>
.issue-detail {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px;
  font-family: 'Open Sans', sans-serif;
  color: #1E293B;
}

.back-bar {
  margin-bottom: 12px;
}

.back-btn {
  color: #2563EB;
  border-color: #2563EB;
  font-family: 'Open Sans', sans-serif;
  border-radius: 8px;
}

.back-btn:hover {
  background: #2563EB;
  color: #fff;
}

.loading-container {
  padding: 40px 0;
}

/* Info Card */
.info-card {
  margin-bottom: 12px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

.info-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.info-title {
  font-family: 'Poppins', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.info-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-select {
  width: 140px;
}

.file-path-text {
  font-family: 'Courier New', Consolas, monospace;
  font-size: 13px;
  color: #64748B;
  word-break: break-all;
}

.issue-description {
  line-height: 1.7;
  color: #475569;
  white-space: pre-wrap;
}

/* Code Card with File Tree */
.code-card {
  margin-bottom: 12px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

.section-title {
  font-family: 'Poppins', sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.code-layout {
  display: flex;
  gap: 12px;
  height: 500px;
}

.file-tree {
  width: 250px;
  border-right: 1px solid #E2E8F0;
  overflow-y: auto;
  padding-right: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
}

.file-item:hover {
  background: #F1F5F9;
}

.file-item.active {
  background: #EFF6FF;
  color: #2563EB;
  font-weight: 500;
}

.file-icon {
  width: 16px;
  height: 16px;
  color: var(--text-medium);
  flex-shrink: 0;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.code-viewer {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.code-header {
  padding: 8px 12px;
  background: #F8FAFC;
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid #E2E8F0;
}

.code-file-path {
  font-family: 'Courier New', Consolas, monospace;
  font-size: 12px;
  color: #64748B;
}

.code-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.code-block {
  flex: 1;
  background: #1E293B;
  border-radius: 0 0 8px 8px;
  overflow: auto;
}

.code-pre {
  margin: 0;
  padding: 16px;
  font-family: 'Courier New', Consolas, 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #E2E8F0;
  white-space: pre;
  tab-size: 4;
}

/* Chat Card */
.chat-card {
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

.chat-messages {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: #F8FAFC;
  border-radius: 8px;
  margin-bottom: 16px;
  scroll-behavior: smooth;
}

.chat-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #64748B;
  font-size: 14px;
}

.chat-message {
  display: flex;
  margin-bottom: 16px;
}

.chat-message-user {
  justify-content: flex-end;
}

.chat-message-ai {
  justify-content: flex-start;
}

.chat-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.bubble-user {
  background: #2563EB;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.bubble-ai {
  background: #E2E8F0;
  color: #1E293B;
  border-bottom-left-radius: 4px;
}

.bubble-content {
  white-space: pre-wrap;
}

.bubble-time {
  font-size: 11px;
  margin-top: 6px;
  opacity: 0.7;
  text-align: right;
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #64748B;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* Chat Input */
.chat-input-area {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
}

.chat-input :deep(.el-textarea__inner) {
  font-family: 'Open Sans', sans-serif;
  font-size: 14px;
  border-radius: 8px;
  border-color: #E2E8F0;
}

.chat-input :deep(.el-textarea__inner:focus) {
  border-color: #2563EB;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.send-btn {
  background: #2563EB;
  border-color: #2563EB;
  border-radius: 8px;
  height: 54px;
  padding: 0 24px;
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
}

.send-btn:hover {
  background: #1D4ED8;
  border-color: #1D4ED8;
}

/* Scrollbar styling */
.chat-messages::-webkit-scrollbar,
.file-tree::-webkit-scrollbar,
.code-block::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.chat-messages::-webkit-scrollbar-track,
.file-tree::-webkit-scrollbar-track,
.code-block::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb,
.file-tree::-webkit-scrollbar-thumb,
.code-block::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.file-tree::-webkit-scrollbar-thumb:hover,
.code-block::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}
</style>

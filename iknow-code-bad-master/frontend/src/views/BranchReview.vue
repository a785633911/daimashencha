<template>
  <div class="branch-review">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px">
      <svg style="width: 32px; height: 32px; color: var(--primary-orange)" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 3V15M18 9V21M6 15C4.34315 15 3 16.3431 3 18C3 19.6569 4.34315 21 6 21C7.65685 21 9 19.6569 9 18C9 16.3431 7.65685 15 6 15ZM18 9C16.3431 9 15 7.65685 15 6C15 4.34315 16.3431 3 18 3C19.6569 3 21 4.34315 21 6C21 7.65685 19.6569 9 18 9ZM18 9C16.3431 9 15 10.3431 15 12C15 13.6569 16.3431 15 18 15C19.6569 15 21 13.6569 21 12C21 10.3431 19.6569 9 18 9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <h1 style="margin: 0; color: var(--text-dark); font-family: 'Poppins', sans-serif">分支审查</h1>
    </div>

    <!-- 搜索配置板块 -->
    <el-card style="margin-bottom: 20px" class="search-card">
      <el-row :gutter="20" style="margin-bottom: 16px">
        <el-col :span="6">
          <div class="field-label">项目</div>
          <el-select v-model="selectedProject" placeholder="选择项目" style="width: 100%" filterable @change="onProjectChange">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <div class="field-label">当前分支 <el-tag size="small" type="info">只读</el-tag></div>
          <el-input v-model="currentBranch" placeholder="当前分支" readonly style="width: 100%" />
        </el-col>
        <el-col :span="5">
          <div class="field-label">基准分支</div>
          <el-select v-model="baseBranch" placeholder="选择基准分支" style="width: 100%" filterable @change="onBaseBranchChange">
            <el-option v-for="branch in allBranches" :key="branch" :label="branch" :value="branch">
              <span>{{ branch }}</span>
              <el-tag v-if="remoteBranches.includes(branch)" size="small" type="success" style="margin-left: 8px">远程</el-tag>
            </el-option>
          </el-select>
        </el-col>
        <el-col :span="5">
          <div class="field-label">审查范围</div>
          <el-select v-model="reviewScope" placeholder="审查范围" style="width: 100%" @change="saveSearchConfig">
            <el-option label="已提交" value="committed" />
            <el-option label="暂存" value="staged" />
            <el-option label="未提交" value="unstaged" />
            <el-option label="已提交+暂存" value="committed+staged" />
            <el-option label="暂存+未提交" value="staged+unstaged" />
            <el-option label="全部" value="all" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <div class="field-label">&nbsp;</div>
          <el-button type="primary" style="width: 100%" @click="startReview" :loading="reviewing" :disabled="!selectedProject || !currentBranch || !baseBranch">
            执行审查
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Git状态信息 -->
    <el-card v-if="selectedProject && currentBranch" style="margin-bottom: 20px" class="git-status-card" v-loading="gitStatusLoading">
      <div class="git-status-header">
        <div style="display: flex; align-items: center; gap: 8px">
          <svg style="width: 20px; height: 20px; color: var(--primary-orange)" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 19V6L3 12L9 19ZM9 19H21M15 5V18L21 12L15 5ZM15 5H3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <h3 style="margin: 0; color: var(--text-dark)">Git 状态</h3>
        </div>
        <el-button size="small" @click="refreshAll" :loading="gitStatusLoading || filesLoading">刷新</el-button>
      </div>
      <el-row :gutter="16" style="margin-top: 16px" v-if="gitStatus">
        <el-col :span="6">
          <div class="status-item">
            <svg class="status-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12H15M12 9V15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="status-content">
              <div class="status-label">领先提交数</div>
              <div class="status-value">{{ gitStatus.staged_commits || 0 }}</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <svg class="status-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12H15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="status-content">
              <div class="status-label">修改的文件</div>
              <div class="status-value">{{ gitStatus.modified_files || 0 }}</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <svg class="status-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="status-content">
              <div class="status-label">新增的文件</div>
              <div class="status-value">{{ gitStatus.added_files || 0 }}</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <svg class="status-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 6H21M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="status-content">
              <div class="status-label">删除的文件</div>
              <div class="status-value">{{ gitStatus.deleted_files || 0 }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 变更文件列表 -->
    <el-card v-if="selectedProject && currentBranch" style="margin-bottom: 20px" class="changed-files-card" v-loading="filesLoading">
      <template #header>
        <div class="changed-files-header">
          <div style="display: flex; align-items: center; gap: 8px">
            <svg style="width: 20px; height: 20px; color: var(--primary-orange)" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 7L11.8845 4.76892C11.5634 4.1268 11.4029 3.80573 11.1634 3.57116C10.9516 3.36373 10.6963 3.20597 10.4161 3.10931C10.0992 3 9.74021 3 9.02229 3H5.2C4.0799 3 3.51984 3 3.09202 3.21799C2.71569 3.40973 2.40973 3.71569 2.21799 4.09202C2 4.51984 2 5.0799 2 6.2V7M2 7H17.2C18.8802 7 19.7202 7 20.362 7.32698C20.9265 7.6146 21.3854 8.07354 21.673 8.63803C22 9.27976 22 10.1198 22 11.8V16.2C22 17.8802 22 18.7202 21.673 19.362C21.3854 19.9265 20.9265 20.3854 20.362 20.673C19.7202 21 18.8802 21 17.2 21H6.8C5.11984 21 4.27976 21 3.63803 20.673C3.07354 20.3854 2.6146 19.9265 2.32698 19.362C2 18.7202 2 17.8802 2 16.2V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h3 style="margin: 0; color: var(--text-dark)">变更文件列表</h3>
          </div>
          <el-tag type="info" effect="plain">共 {{ changedFiles.length }} 个文件</el-tag>
        </div>
      </template>
      <div class="files-layout" v-if="changedFiles.length > 0">
        <!-- Left: File Tree -->
        <div class="files-tree">
          <div
            v-for="(file, index) in changedFiles"
            :key="index"
            class="file-tree-item"
            :class="{ active: selectedFileIndex === index }"
          >
            <div class="file-item-content" @click="selectFileToView(index)">
              <svg class="file-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12H15M12 9V15M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <div class="file-info">
                <div class="file-name">{{ file.path.split('/').pop() }}</div>
                <el-tag size="small" :type="getFileStatusType(file.status)">{{ file.status }}</el-tag>
              </div>
            </div>
            <el-button
              size="small"
              type="primary"
              :loading="reviewingSingleFile === index"
              @click.stop="reviewSingleFile(file, index)"
              class="review-file-btn"
            >
              审查
            </el-button>
          </div>
        </div>

        <!-- Right: Code Viewer -->
        <div class="files-code-viewer">
          <div v-if="selectedFileCode" class="code-view-container">
            <div class="code-view-header">
              <span class="code-view-path">{{ changedFiles[selectedFileIndex]?.path }}</span>
            </div>
            <div class="code-view-block">
              <pre class="code-view-pre"><code>{{ selectedFileCode }}</code></pre>
            </div>
          </div>
          <el-empty v-else description="请选择文件查看代码" :image-size="80" />
        </div>
      </div>
      <el-empty v-else description="暂无变更文件" :image-size="80" />
    </el-card>

    <!-- 审查进度 -->
    <el-card v-if="progressSteps.length > 0" style="margin-bottom: 20px" class="progress-card">
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px">
        <svg style="width: 20px; height: 20px; color: var(--primary-orange)" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 6V12L16 14M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h3 style="margin: 0; color: var(--text-dark)">审查进度</h3>
      </div>
      <el-progress :percentage="progress" :status="progressStatus" :stroke-width="12" />
      <div style="margin-top: 12px; color: var(--text-medium); font-size: 14px">{{ progressText }}</div>

      <!-- 详细进度信息 -->
      <el-collapse v-model="progressDetailOpen" style="margin-top: 16px">
        <el-collapse-item title="查看详细进度" name="1">
          <div class="progress-details-container">
            <div class="progress-details">
              <div v-for="(step, index) in progressSteps" :key="index" class="progress-step">
                <div class="step-icon" :class="{ active: step.status === 'active', completed: step.status === 'completed', error: step.status === 'error' }">
                  <span v-if="step.status === 'completed'">✓</span>
                  <span v-else-if="step.status === 'active'">⏳</span>
                  <span v-else-if="step.status === 'error'">✗</span>
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="step-content">
                  <div class="step-title">{{ step.title }}</div>
                  <div v-if="step.detail" class="step-detail" :class="{ error: step.status === 'error' }">{{ step.detail }}</div>
                  <!-- 初始化详情 -->
                  <div v-if="step.initDetails" class="step-extra-details">
                    <div class="detail-item">
                      <span class="detail-label">项目:</span>
                      <span class="detail-value">{{ step.initDetails.project_name }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">AI配置:</span>
                      <span class="detail-value">{{ step.initDetails.ai_config }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">审查模型:</span>
                      <span class="detail-value">{{ step.initDetails.review_model }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">工作流程文档:</span>
                      <span class="detail-value" :class="{ success: step.initDetails.workflow_loaded, warning: !step.initDetails.workflow_loaded }">
                        {{ step.initDetails.workflow_loaded ? '已加载' : '未加载' }}
                        <span v-if="step.initDetails.workflow_docs.length > 0" class="doc-paths">
                          ({{ step.initDetails.workflow_docs.join(', ') }})
                        </span>
                      </span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">格式规范文档:</span>
                      <span class="detail-value" :class="{ success: step.initDetails.format_loaded, warning: !step.initDetails.format_loaded }">
                        {{ step.initDetails.format_loaded ? '已加载' : '未加载' }}
                        <span v-if="step.initDetails.format_docs.length > 0" class="doc-paths">
                          ({{ step.initDetails.format_docs.join(', ') }})
                        </span>
                      </span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">审核标准文档:</span>
                      <span class="detail-value" :class="{ success: step.initDetails.standards_loaded, warning: !step.initDetails.standards_loaded }">
                        {{ step.initDetails.standards_loaded ? '已加载' : '未加载' }}
                        <span v-if="step.initDetails.standard_docs.length > 0" class="doc-paths">
                          ({{ step.initDetails.standard_docs.join(', ') }})
                        </span>
                      </span>
                    </div>
                  </div>
                  <!-- 文件列表详情 -->
                  <div v-if="step.fileDetails" class="step-extra-details">
                    <div class="detail-item">
                      <span class="detail-label">文件总数:</span>
                      <span class="detail-value">{{ step.fileDetails.total_files }}</span>
                    </div>
                    <div v-if="step.fileDetails.files.length > 0" class="file-list">
                      <div class="detail-label">文件列表:</div>
                      <div class="file-list-scroll">
                        <div v-for="(file, idx) in step.fileDetails.files" :key="idx" class="file-list-item">
                          <span class="file-path">{{ file.path }}</span>
                          <el-tag size="small" :type="getFileStatusType(file.status)">{{ file.status }}</el-tag>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- AI分析详情 -->
                  <div v-if="step.analysisDetails" class="step-extra-details">
                    <div class="analysis-list-scroll">
                      <div v-for="(analysis, idx) in step.analysisDetails" :key="idx" class="analysis-item">
                        <div class="analysis-header">
                          <span class="analysis-file">{{ analysis.file }}</span>
                          <el-tag size="small" :type="analysis.status === 'success' ? 'success' : analysis.status === 'error' ? 'danger' : 'info'">
                            {{ analysis.status }}
                          </el-tag>
                        </div>
                        <div class="analysis-message" :class="{ error: analysis.status === 'error' }">
                          {{ analysis.message }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 实时日志和并行状态 -->
    <el-card v-if="wsLogs.length > 0 || wsCurrentFiles.length > 0" style="margin-bottom: 20px" class="logs-card">
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px">
        <svg style="width: 20px; height: 20px; color: var(--primary-orange)" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 5H7.2C6.0799 5 5.51984 5 5.09202 5.21799C4.71569 5.40973 4.40973 5.71569 4.21799 6.09202C4 6.51984 4 7.0799 4 8.2V20L8.5 17.5L12 20L15.5 17.5L20 20V8.2C20 7.0799 20 6.51984 19.782 6.09202C19.5903 5.71569 19.2843 5.40973 18.908 5.21799C18.4802 5 17.9201 5 16.8 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5M12 12H16M12 16H16M8 12H8.01M8 16H8.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h3 style="margin: 0; color: var(--text-dark)">实时日志</h3>
      </div>

      <!-- 当前处理的文件 -->
      <div v-if="wsCurrentFiles.length > 0" class="current-files-section">
        <div class="section-title">
          <svg style="width: 16px; height: 16px; display: inline-block; vertical-align: middle; margin-right: 4px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          正在并行处理 ({{ wsCurrentFiles.length }}/3)
        </div>
        <div class="current-files-list">
          <div v-for="file in wsCurrentFiles" :key="file" class="current-file-item">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span class="file-name">{{ file }}</span>
          </div>
        </div>
      </div>

      <!-- 日志列表 -->
      <div class="logs-container">
        <div v-for="(log, index) in wsLogs.slice(-50)" :key="index" class="log-item" :class="`log-${log.level}`">
          <span class="log-time">{{ formatLogTime(log.timestamp) }}</span>
          <span class="log-icon">{{ getLogIcon(log.level) }}</span>
          <span class="log-file" v-if="log.file">{{ log.file }}</span>
          <span class="log-round" v-if="log.round">[第{{ log.round }}轮]</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </el-card>

    <!-- 审查结果 -->
    <el-card v-if="reviewResults.length > 0" class="results-card">
      <div class="results-header">
        <div style="display: flex; align-items: center; gap: 8px">
          <svg style="width: 20px; height: 20px; color: var(--primary-orange)" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <h3 style="margin: 0; color: var(--text-dark)">审查结果</h3>
        </div>
        <div class="results-meta">
          <el-tag type="info" effect="plain" style="margin-right: 8px">
            文件数: {{ fileCount }}
          </el-tag>
          <el-tag type="warning" effect="plain">
            问题数: {{ reviewResults.length }}
          </el-tag>
        </div>
      </div>
      <div v-for="(result, index) in reviewResults" :key="index" class="result-item">
        <div class="result-header">
          <el-select v-model="result.severity" placeholder="选择严重程度" size="small" style="width: 100px" @change="updateResultField(result, index, 'severity')">
            <el-option label="致命" value="致命" />
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
            <el-option label="建议" value="建议" />
          </el-select>
          <el-select v-model="result.issue_type" placeholder="选择问题类型" size="small" filterable allow-create style="width: 180px; margin-left: 12px" @change="updateResultField(result, index, 'issue_type')">
            <el-option label="代码规范问题" value="代码规范问题" />
            <el-option label="潜在Bug" value="潜在Bug" />
            <el-option label="性能问题" value="性能问题" />
            <el-option label="安全漏洞" value="安全漏洞" />
            <el-option label="逻辑错误" value="逻辑错误" />
            <el-option label="代码重复" value="代码重复" />
            <el-option label="命名不规范" value="命名不规范" />
            <el-option label="注释缺失" value="注释缺失" />
            <el-option label="其他" value="其他" />
          </el-select>
        </div>
        <div class="result-description">{{ result.description || '暂无描述' }}</div>
        <div class="result-file">
          <span v-if="result.file_path">{{ result.file_path }}</span>
          <span v-if="result.line_start">:{{ result.line_start }}</span>
          <span v-if="result.line_end && result.line_end !== result.line_start">-{{ result.line_end }}</span>
        </div>
        <div class="result-actions">
          <el-button size="small" type="primary" @click="addToIssues(result, index)">添加到问题</el-button>
          <el-button size="small" type="success" @click="addAndMarkResolved(result, index)">添加并标记已解决</el-button>
          <el-button size="small" type="warning" @click="addAndMarkPending(result, index)">添加并标记待解决</el-button>
          <el-button size="small" @click="ignoreResult(index)">忽略</el-button>
          <el-button size="small" type="info" @click="openChat(result, index)">对话</el-button>
        </div>
      </div>
    </el-card>

    <!-- Chat Dialog -->
    <el-dialog v-model="chatDialogVisible" title="与AI对话" width="700px" @close="closeChatDialog">
      <div class="chat-container">
        <div class="chat-context" v-if="currentChatResult">
          <div class="context-header">当前问题上下文</div>
          <div class="context-item">
            <strong>问题类型:</strong> {{ currentChatResult.issue_type }}
          </div>
          <div class="context-item">
            <strong>严重程度:</strong> <el-tag :type="getSeverityType(currentChatResult.severity)" size="small">{{ currentChatResult.severity }}</el-tag>
          </div>
          <div class="context-item">
            <strong>描述:</strong> {{ currentChatResult.description }}
          </div>
          <div class="context-item">
            <strong>文件:</strong> {{ currentChatResult.file_path }}:{{ currentChatResult.line_start }}
          </div>
        </div>

        <div class="chat-messages" ref="chatMessagesRef">
          <div v-for="(msg, idx) in chatMessages" :key="idx" class="chat-message" :class="msg.role">
            <div class="message-avatar">
              <svg v-if="msg.role === 'user'" style="width: 20px; height: 20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else style="width: 20px; height: 20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12L11 14L15 10M7.835 4.697C8.791 3.602 9.269 3.055 9.866 2.715C10.392 2.416 10.977 2.25 11.575 2.228C12.257 2.203 12.977 2.448 14.417 2.938L16.3 3.617C17.74 4.107 18.46 4.352 19.005 4.807C19.487 5.208 19.872 5.717 20.13 6.292C20.423 6.948 20.5 7.722 20.654 9.27L20.808 10.818C20.962 12.366 21.039 13.14 20.866 13.838C20.715 14.451 20.424 15.021 20.018 15.502C19.556 16.046 18.866 16.391 17.486 17.081L15.7 17.97C14.32 18.66 13.63 19.005 12.898 19.127C12.248 19.236 11.582 19.236 10.932 19.127C10.2 19.005 9.51 18.66 8.13 17.97L6.344 17.081C4.964 16.391 4.274 16.046 3.812 15.502C3.406 15.021 3.115 14.451 2.964 13.838C2.791 13.14 2.868 12.366 3.022 10.818L3.176 9.27C3.33 7.722 3.407 6.948 3.7 6.292C3.958 5.717 4.343 5.208 4.825 4.807C5.37 4.352 6.09 4.107 7.53 3.617L9.413 2.938C10.853 2.448 11.573 2.203 12.255 2.228C12.853 2.25 13.438 2.416 13.964 2.715C14.561 3.055 15.039 3.602 15.995 4.697L7.835 4.697Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>
          <div v-if="chatLoading" class="chat-message assistant">
            <div class="message-avatar">
              <svg style="width: 20px; height: 20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12L11 14L15 10M7.835 4.697C8.791 3.602 9.269 3.055 9.866 2.715C10.392 2.416 10.977 2.25 11.575 2.228C12.257 2.203 12.977 2.448 14.417 2.938L16.3 3.617C17.74 4.107 18.46 4.352 19.005 4.807C19.487 5.208 19.872 5.717 20.13 6.292C20.423 6.948 20.5 7.722 20.654 9.27L20.808 10.818C20.962 12.366 21.039 13.14 20.866 13.838C20.715 14.451 20.424 15.021 20.018 15.502C19.556 16.046 18.866 16.391 17.486 17.081L15.7 17.97C14.32 18.66 13.63 19.005 12.898 19.127C12.248 19.236 11.582 19.236 10.932 19.127C10.2 19.005 9.51 18.66 8.13 17.97L6.344 17.081C4.964 16.391 4.274 16.046 3.812 15.502C3.406 15.021 3.115 14.451 2.964 13.838C2.791 13.14 2.868 12.366 3.022 10.818L3.176 9.27C3.33 7.722 3.407 6.948 3.7 6.292C3.958 5.717 4.343 5.208 4.825 4.807C5.37 4.352 6.09 4.107 7.53 3.617L9.413 2.938C10.853 2.448 11.573 2.203 12.255 2.228C12.853 2.25 13.438 2.416 13.964 2.715C14.561 3.055 15.039 3.602 15.995 4.697L7.835 4.697Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="message-content">
              <div class="message-text">
                <el-icon class="is-loading"><Loading /></el-icon> AI正在思考...
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <el-input
            v-model="chatInput"
            type="textarea"
            :rows="3"
            placeholder="输入您的问题..."
            @keydown.ctrl.enter="sendChatMessage"
          />
          <div class="chat-input-actions">
            <span class="input-hint">Ctrl + Enter 发送</span>
            <el-button type="primary" @click="sendChatMessage" :loading="chatLoading" :disabled="!chatInput.trim()">
              发送
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { projectAPI, reviewAPI, issueAPI } from '@/api'
import api from '@/api'
import { useWebSocketReview } from '@/composables/useWebSocketReview'

// WebSocket审查
const {
  connected: wsConnected,
  phase: wsPhase,
  progress: wsProgress,
  progressText: wsProgressText,
  progressStatus: wsProgressStatus,
  fileGroups: wsFileGroups,
  totalFiles: wsTotalFiles,
  processedFiles: wsProcessedFiles,
  currentFiles: wsCurrentFiles,
  progressSteps: wsProgressSteps,
  reviewResults: wsReviewResults,
  errors: wsErrors,
  logs: wsLogs,
  connect: wsConnect,
  startReview: wsStartReview,
  cancelReview: wsCancelReview,
  startHeartbeat: wsStartHeartbeat
} = useWebSocketReview()

const projects = ref([])
const selectedProject = ref(null)
const branches = ref([])
const remoteBranches = ref([])
const allBranches = ref([])
const currentBranch = ref('')
const baseBranch = ref('main')
const reviewScope = ref('all')
const reviewing = ref(false)
const progressDetailOpen = ref([])
const gitStatus = ref(null)
const gitStatusLoading = ref(false)
const changedFiles = ref([])
const filesLoading = ref(false)
const selectedFileIndex = ref(null)
const selectedFileCode = ref('')
const reviewingSingleFile = ref(null)
const chatDialogVisible = ref(false)
const currentChatResult = ref(null)
const currentChatIndex = ref(null)
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatMessagesRef = ref(null)

// 使用WebSocket的响应式数据
const progress = wsProgress
const progressText = wsProgressText
const progressStatus = wsProgressStatus
const progressSteps = wsProgressSteps
const reviewResults = wsReviewResults
const fileCount = wsTotalFiles

const STORAGE_KEY = 'branch_review_config'

const loadProjects = async () => {
  try {
    const { data } = await projectAPI.getAll()
    projects.value = data
  } catch (error) {
    ElMessage.error('加载项目失败')
  }
}

const loadBranches = async () => {
  if (!selectedProject.value) return
  try {
    const { data } = await projectAPI.getBranches(selectedProject.value)
    branches.value = data.branches || []
    currentBranch.value = data.current || 'main'

    // 获取远程分支
    try {
      const remoteResp = await api.post('/projects/fetch-remote-branches', {
        project_id: selectedProject.value
      })
      remoteBranches.value = remoteResp.data.branches || []
    } catch (e) {
      remoteBranches.value = []
    }

    // 合并本地和远程分支
    allBranches.value = [...new Set([...branches.value, ...remoteBranches.value])]

    // 加载git状态
    loadGitStatus()
  } catch (error) {
    branches.value = ['main', 'develop']
    currentBranch.value = 'main'
    allBranches.value = ['main', 'develop']
  }
}

const loadGitStatus = async () => {
  if (!selectedProject.value || !currentBranch.value) return
  gitStatusLoading.value = true
  try {
    const { data } = await api.post('/projects/git-status', {
      project_id: selectedProject.value,
      branch: currentBranch.value,
      base_branch: baseBranch.value
    })
    gitStatus.value = data
  } catch (error) {
    gitStatus.value = null
  } finally {
    gitStatusLoading.value = false
  }
}

const loadChangedFiles = async () => {
  if (!selectedProject.value || !currentBranch.value || !baseBranch.value) return
  filesLoading.value = true
  try {
    const project = projects.value.find(p => p.id === selectedProject.value)
    if (!project) return

    const { data } = await api.post('/projects/get-changed-files', {
      repo_path: project.path,
      base_branch: baseBranch.value,
      target_branch: currentBranch.value,
      scope: reviewScope.value
    })
    changedFiles.value = data.files || []
    ElMessage.success(`已加载 ${changedFiles.value.length} 个变更文件`)
  } catch (error) {
    changedFiles.value = []
    ElMessage.error('加载文件列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    filesLoading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadGitStatus(), loadChangedFiles()])
}

const getFileStatusType = (status) => {
  const types = {
    'modified': 'warning',
    'added': 'success',
    'deleted': 'danger',
    'renamed': 'info'
  }
  return types[status] || 'info'
}

const selectFileToView = async (index) => {
  selectedFileIndex.value = index
  const file = changedFiles.value[index]
  if (!file) return

  try {
    const project = projects.value.find(p => p.id === selectedProject.value)
    if (!project) return

    const { data } = await api.post('/projects/get-file-content', {
      repo_path: project.path,
      file_path: file.path,
      branch: currentBranch.value
    })
    selectedFileCode.value = data.content || ''
  } catch (error) {
    selectedFileCode.value = ''
    ElMessage.error('加载文件内容失败')
  }
}

const onProjectChange = () => {
  loadBranches()
  saveSearchConfig()
}

const onBaseBranchChange = () => {
  saveSearchConfig()
}

const saveSearchConfig = () => {
  const config = {
    selectedProject: selectedProject.value,
    baseBranch: baseBranch.value,
    reviewScope: reviewScope.value
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
  // 当基准分支或审查范围改变时，重新加载文件列表
  if (selectedProject.value && currentBranch.value && baseBranch.value) {
    loadGitStatus()
    loadChangedFiles()
  }
}

const loadSearchConfig = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const config = JSON.parse(saved)
      selectedProject.value = config.selectedProject
      baseBranch.value = config.baseBranch || 'main'
      reviewScope.value = config.reviewScope || 'all'
      if (selectedProject.value) {
        loadBranches()
      }
    }
  } catch (e) {
    // ignore
  }
}

const startReview = async () => {
  if (!selectedProject.value) {
    ElMessage.warning('请选择项目')
    return
  }

  reviewing.value = true
  progressDetailOpen.value = ['1'] // 自动展开详情

  try {
    // 连接WebSocket（如果未连接）
    if (!wsConnected.value) {
      await wsConnect()
      wsStartHeartbeat()
    }

    // 启动WebSocket审查
    await wsStartReview(
      selectedProject.value,
      baseBranch.value,
      currentBranch.value,
      reviewScope.value
    )

    ElMessage.success('审查已启动，正在实时处理...')
  } catch (error) {
    progressStatus.value = 'exception'
    progressText.value = '审查失败'
    ElMessage.error('启动审查失败：' + (error.message || '未知错误'))
  } finally {
    reviewing.value = false
  }
}

const addToIssues = async (result, index) => {
  try {
    await issueAPI.create({
      project_id: selectedProject.value,
      branch: currentBranch.value,
      status: '待审核',
      ...result
    })
    reviewResults.value.splice(index, 1)
    ElMessage.success('已添加到问题列表')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const updateResultField = (result, index, field) => {
  // 实时更新结果对象，无需额外操作
  ElMessage.success(`已更新${field === 'severity' ? '严重程度' : '问题类型'}`)
}

const reviewSingleFile = async (file, index) => {
  if (!selectedProject.value) {
    ElMessage.warning('请选择项目')
    return
  }

  reviewingSingleFile.value = index
  progressDetailOpen.value = ['1']

  try {
    if (!wsConnected.value) {
      await wsConnect()
      wsStartHeartbeat()
    }

    await wsStartReview(
      selectedProject.value,
      baseBranch.value,
      currentBranch.value,
      reviewScope.value,
      [file.path]
    )

    ElMessage.success(`正在审查文件: ${file.path}`)
  } catch (error) {
    ElMessage.error('启动审查失败：' + (error.message || '未知错误'))
  } finally {
    reviewingSingleFile.value = null
  }
}

const addAndMarkResolved = async (result, index) => {
  try {
    await issueAPI.create({
      project_id: selectedProject.value,
      branch: currentBranch.value,
      status: '已解决',
      ...result
    })
    reviewResults.value.splice(index, 1)
    ElMessage.success('已添加并标记为已解决')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const addAndMarkPending = async (result, index) => {
  try {
    await issueAPI.create({
      project_id: selectedProject.value,
      branch: currentBranch.value,
      status: '待解决',
      ...result
    })
    reviewResults.value.splice(index, 1)
    ElMessage.success('已添加并标记为待解决')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const ignoreResult = (index) => {
  reviewResults.value.splice(index, 1)
  ElMessage.info('已忽略')
}

const getSeverityType = (severity) => {
  const types = { '致命': 'danger', '高': 'danger', '中': 'warning', '低': 'info', '建议': '' }
  return types[severity] || 'info'
}

const openChat = (result, index) => {
  currentChatResult.value = result
  currentChatIndex.value = index
  chatMessages.value = []
  chatInput.value = ''
  chatDialogVisible.value = true

  // Load chat history if this result was already added as an issue
  // For now, start fresh conversation
}

const closeChatDialog = () => {
  chatDialogVisible.value = false
  currentChatResult.value = null
  currentChatIndex.value = null
  chatMessages.value = []
  chatInput.value = ''
}

const sendChatMessage = async () => {
  if (!chatInput.value.trim() || chatLoading.value) return

  const userMessage = chatInput.value.trim()
  chatMessages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  chatInput.value = ''
  chatLoading.value = true

  // Scroll to bottom
  await nextTick()
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }

  try {
    // Create a temporary issue to use the chat API
    const tempIssue = await issueAPI.create({
      project_id: selectedProject.value,
      branch: currentBranch.value,
      ...currentChatResult.value
    })

    // Send chat message
    const { data } = await api.post(`/issues/${tempIssue.data.id}/chat`, {
      content: userMessage
    })

    chatMessages.value.push({
      role: 'assistant',
      content: data.reply,
      timestamp: new Date()
    })

    // Scroll to bottom
    await nextTick()
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  } catch (error) {
    ElMessage.error('发送消息失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    chatLoading.value = false
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatLogTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const getLogIcon = (level) => {
  return ''
}

onMounted(() => {
  loadProjects()
  loadSearchConfig()
})
</script>

<style scoped>
.branch-review {
  max-width: 1400px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-medium);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.search-card, .git-status-card, .progress-card, .results-card {
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.git-status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-light);
  border-radius: 12px;
  transition: all 0.3s;
}

.status-item:hover {
  background: var(--primary-orange-lighter);
  transform: translateY(-2px);
}

.status-icon {
  width: 32px;
  height: 32px;
  color: var(--primary-orange);
  flex-shrink: 0;
}

.status-content {
  flex: 1;
}

.status-label {
  font-size: 12px;
  color: var(--text-medium);
  margin-bottom: 4px;
}

.status-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-orange);
  font-family: 'Poppins', sans-serif;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-meta {
  display: flex;
  align-items: center;
}

.result-item {
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  margin-bottom: 12px;
  background: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.result-item:hover {
  border-color: var(--primary-orange);
  box-shadow: 0 4px 16px var(--shadow-medium);
  transform: translateY(-2px);
}

.result-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.result-description {
  color: var(--text-medium);
  margin-bottom: 8px;
  line-height: 1.6;
}

.result-file {
  font-size: 12px;
  color: var(--text-light);
  font-family: 'Courier New', monospace;
  margin-bottom: 12px;
}

.result-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.progress-details-container {
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 12px;
}

.progress-details {
  padding: 12px 0 12px 20px;
}

.progress-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-left: 2px solid #e4e7ed;
  padding-left: 24px;
  position: relative;
}

.progress-step:last-child {
  border-left-color: transparent;
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f5f7fa;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
  position: absolute;
  left: -17px;
  border: 2px solid #e4e7ed;
  transition: all 0.3s ease;
}

.step-icon.active {
  background: #ff8c42;
  color: white;
  border-color: #ff8c42;
  animation: pulse 1.5s ease-in-out infinite;
}

.step-icon.completed {
  background: #67c23a;
  color: white;
  border-color: #67c23a;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 140, 66, 0.7);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 8px rgba(255, 140, 66, 0);
  }
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  color: var(--text-dark);
  margin-bottom: 4px;
}

.step-detail {
  font-size: 12px;
  color: var(--text-light);
}

.step-detail.error {
  color: #f56c6c;
  font-weight: 500;
}

.step-icon.error {
  background: #f56c6c;
  color: white;
  border-color: #f56c6c;
}

.step-extra-details {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 3px solid #ff8c42;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-weight: 600;
  color: var(--text-medium);
  min-width: 100px;
  flex-shrink: 0;
}

.detail-value {
  color: var(--text-dark);
  flex: 1;
}

.detail-value.success {
  color: #67c23a;
  font-weight: 500;
}

.detail-value.warning {
  color: #e6a23c;
  font-weight: 500;
}

.doc-paths {
  font-size: 12px;
  color: var(--text-light);
  word-break: break-all;
  display: block;
  margin-top: 4px;
}

.file-list {
  margin-top: 8px;
}

.file-list-scroll {
  max-height: 200px;
  overflow-y: auto;
  overflow-x: hidden;
}

.file-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  margin-top: 4px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
}

.file-path {
  font-family: 'Courier New', monospace;
  color: var(--text-dark);
  flex: 1;
  margin-right: 8px;
  word-break: break-all;
  overflow-wrap: break-word;
}

.analysis-list-scroll {
  max-height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
}

.analysis-item {
  padding: 8px;
  margin-top: 8px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.analysis-item:first-child {
  margin-top: 0;
}

.analysis-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.analysis-file {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: var(--text-dark);
  font-weight: 500;
  flex: 1;
  margin-right: 8px;
  word-break: break-all;
}

.analysis-message {
  font-size: 12px;
  color: var(--text-medium);
}

.analysis-message.error {
  color: #f56c6c;
  font-weight: 500;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.chat-context {
  background: #fff5f0;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid #ff8c42;
}

.context-header {
  font-weight: 600;
  color: #ff8c42;
  margin-bottom: 8px;
}

.context-item {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: var(--primary-orange);
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.chat-message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-text {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-wrap: break-word;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.chat-message.user .message-text {
  background: #ff8c42;
  color: white;
}

.message-time {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

.chat-input-area {
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
}

.chat-input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.input-hint {
  font-size: 12px;
  color: #909399;
}

.changed-files-card {
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.changed-files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.files-layout {
  display: flex;
  gap: 12px;
  height: 400px;
}

.files-tree {
  width: 280px;
  border-right: 1px solid #E2E8F0;
  overflow-y: auto;
  padding-right: 12px;
}

.file-tree-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  transition: all 0.2s;
}

.file-item-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.file-tree-item:hover {
  background: #F1F5F9;
}

.file-tree-item.active {
  background: #FFF5F0;
  border-left: 3px solid #ff8c42;
}

.review-file-btn {
  flex-shrink: 0;
  padding: 4px 8px;
  font-size: 12px;
}

.file-icon {
  width: 18px;
  height: 18px;
  color: var(--text-medium);
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 13px;
  color: var(--text-dark);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.files-code-viewer {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.code-view-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.code-view-header {
  padding: 8px 12px;
  background: #F8FAFC;
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid #E2E8F0;
}

.code-view-path {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #64748B;
}

.code-view-block {
  flex: 1;
  background: #1E293B;
  border-radius: 0 0 8px 8px;
  overflow: auto;
}

.code-view-pre {
  margin: 0;
  padding: 16px;
  font-family: 'Courier New', Consolas, 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #E2E8F0;
  white-space: pre;
  tab-size: 4;
}

/* 实时日志样式 */
.logs-card {
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.current-files-section {
  margin-bottom: 20px;
  padding: 12px;
  background: #fff5f0;
  border-radius: 8px;
  border-left: 4px solid #ff8c42;
}

.section-title {
  font-weight: 600;
  color: #ff8c42;
  margin-bottom: 12px;
  font-size: 14px;
}

.current-files-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.current-file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: var(--text-dark);
}

.current-file-item .el-icon {
  color: #ff8c42;
  font-size: 16px;
}

.file-name {
  flex: 1;
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
}

.log-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 8px;
  margin-bottom: 4px;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
  transition: background 0.2s;
}

.log-item:hover {
  background: rgba(255, 255, 255, 0.5);
}

.log-time {
  color: #909399;
  font-size: 11px;
  min-width: 70px;
  flex-shrink: 0;
}

.log-icon {
  display: none;
}

.log-file {
  font-family: 'Courier New', monospace;
  color: #606266;
  font-size: 12px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 0;
}

.log-round {
  color: #ff8c42;
  font-weight: 600;
  font-size: 11px;
  flex-shrink: 0;
}

.log-message {
  color: #606266;
  flex: 1;
  word-break: break-word;
}

.log-info .log-message {
  color: #606266;
}

.log-success {
  background: rgba(103, 194, 58, 0.1);
}

.log-success .log-message {
  color: #67c23a;
  font-weight: 500;
}

.log-warning {
  background: rgba(230, 162, 60, 0.1);
}

.log-warning .log-message {
  color: #e6a23c;
}

.log-error {
  background: rgba(245, 108, 108, 0.1);
}

.log-error .log-message {
  color: #f56c6c;
  font-weight: 500;
}

.log-phase {
  background: rgba(64, 158, 255, 0.1);
}

.log-phase .log-message {
  color: #409eff;
  font-weight: 600;
}

.log-ai_stream .log-message,
.log-ai_thinking .log-message {
  color: #909399;
  font-style: italic;
}

.log-multi_round {
  background: rgba(255, 140, 66, 0.1);
}

.log-multi_round .log-message {
  color: #ff8c42;
  font-weight: 500;
}

</style>

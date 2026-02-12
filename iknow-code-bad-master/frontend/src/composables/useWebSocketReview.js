import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

export function useWebSocketReview() {
  const ws = ref(null)
  const connected = ref(false)
  const taskId = ref(null)
  const connectionId = ref(null)

  // 进度状态
  const phase = ref('init')
  const progress = ref(0)
  const progressText = ref('')
  const progressStatus = ref(undefined)

  // 文件分组
  const fileGroups = ref({})
  const totalFiles = ref(0)
  const processedFiles = ref(0)
  const currentFiles = ref([])

  // 详细进度步骤
  const progressSteps = ref([])

  // 审查结果
  const reviewResults = ref([])
  const errors = ref([])

  // 实时日志
  const logs = ref([])

  const connect = () => {
    return new Promise((resolve, reject) => {
      connectionId.value = `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const wsUrl = `ws://localhost:8000/ws/review/${connectionId.value}`

      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = () => {
        connected.value = true
        console.log('WebSocket connected')
        resolve()
      }

      ws.value.onerror = (error) => {
        console.error('WebSocket error:', error)
        ElMessage.error('WebSocket连接失败')
        reject(error)
      }

      ws.value.onclose = () => {
        connected.value = false
        console.log('WebSocket disconnected')
      }

      ws.value.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          handleMessage(message)
        } catch (e) {
          console.error('Failed to parse message:', e)
        }
      }
    })
  }

  const handleMessage = (message) => {
    const { type } = message

    switch (type) {
      case 'task_created':
        taskId.value = message.task_id
        addLog('info', `任务已创建: ${message.task_id}`)
        break

      case 'phase_change':
        phase.value = message.phase
        progressText.value = message.message
        addLog('phase', message.message)
        updateProgressSteps(message)
        break

      case 'progress':
        handleProgressUpdate(message)
        break

      case 'file_grouping':
        fileGroups.value = message.groups
        totalFiles.value = message.total_files
        addLog('info', `文件分组完成，共 ${message.total_files} 个文件`)
        break

      case 'file_start':
        currentFiles.value.push(message.file)
        addLog('file_start', `开始分析: ${message.file} (${message.index}/${message.total})`)
        break

      case 'ai_stream':
        // 实时AI输出
        addLog('ai_stream', message.content, message.file, message.round)
        break

      case 'ai_thinking':
        // AI深度思考
        addLog('ai_thinking', message.thought, message.file, message.round)
        break

      case 'file_complete':
        handleFileComplete(message)
        break

      case 'file_error':
        errors.value.push({ file: message.file, error: message.error })
        addLog('error', `文件分析失败: ${message.file} - ${message.error}`)
        break

      case 'context_loading':
        addLog('context', `加载关联文件: ${message.loading_files.join(', ')}`, message.current_file)
        break

      case 'multi_round_start':
        addLog('multi_round', `开始第${message.round}轮深度分析`, message.file)
        break

      case 'deep_analysis_complete':
        addLog('success', `深度分析完成，新发现 ${message.new_issues_found} 个问题`, message.file)
        if (message.issues && message.issues.length > 0) {
          reviewResults.value.push(...message.issues)
        }
        break

      case 'progress_update':
        processedFiles.value = message.processed
        progress.value = message.percentage
        break

      case 'complete':
        progressStatus.value = 'success'
        progressText.value = '审查完成！'
        progress.value = 100
        addLog('success', `审查完成！共审查 ${message.summary.total_files} 个文件，发现 ${message.summary.total_issues} 个问题`)
        ElMessage.success('审查完成！')
        break

      case 'error':
        progressStatus.value = 'exception'
        progressText.value = '审查失败'
        addLog('error', message.message)
        ElMessage.error(message.message)
        break

      case 'cancelled':
        progressStatus.value = 'exception'
        progressText.value = '审查已取消'
        addLog('warning', '审查已取消')
        ElMessage.warning('审查已取消')
        break

      case 'pong':
        // 心跳响应
        break

      default:
        console.log('Unknown message type:', type, message)
    }
  }

  const handleProgressUpdate = (message) => {
    const step = message.step
    const details = message.details

    if (step === 'init' && details) {
      // 初始化详情
      const stepIndex = progressSteps.value.findIndex(s => s.title === '初始化审查环境')
      if (stepIndex >= 0) {
        progressSteps.value[stepIndex].status = 'completed'
        progressSteps.value[stepIndex].detail = message.message
        progressSteps.value[stepIndex].initDetails = details
      }
    }

    addLog('progress', message.message)
  }

  const handleFileComplete = (message) => {
    // 从当前处理列表中移除
    const index = currentFiles.value.indexOf(message.file)
    if (index > -1) {
      currentFiles.value.splice(index, 1)
    }

    if (message.status === 'success') {
      addLog('success', `分析完成: ${message.file} - 发现 ${message.issues_found} 个问题 (耗时 ${message.duration?.toFixed(2)}s)`)

      // 添加问题到结果列表
      if (message.issues && message.issues.length > 0) {
        reviewResults.value.push(...message.issues)
      }
    } else if (message.status === 'skipped') {
      addLog('warning', `跳过: ${message.file} - ${message.message}`)
    }
  }

  const updateProgressSteps = (message) => {
    const phaseMap = {
      'init': '初始化审查环境',
      'file_grouping': '加载文件列表',
      'quick_scan': 'AI快速扫描',
      'deep_analysis': 'AI深度分析',
      'generating_report': '生成审查报告',
      'complete': '完成'
    }

    const stepTitle = phaseMap[message.phase]
    if (!stepTitle) return

    const stepIndex = progressSteps.value.findIndex(s => s.title === stepTitle)
    if (stepIndex >= 0) {
      progressSteps.value[stepIndex].status = 'active'
      progressSteps.value[stepIndex].detail = message.message
    }
  }

  const addLog = (level, message, file = null, round = null) => {
    logs.value.push({
      level,
      message,
      file,
      round,
      timestamp: new Date()
    })

    // 限制日志数量
    if (logs.value.length > 1000) {
      logs.value.shift()
    }
  }

  const startReview = async (projectId, baseBranch, targetBranch, scope, specificFiles = null) => {
    if (!connected.value) {
      await connect()
    }

    // 重置状态
    phase.value = 'init'
    progress.value = 0
    progressText.value = ''
    progressStatus.value = undefined
    fileGroups.value = {}
    totalFiles.value = 0
    processedFiles.value = 0
    currentFiles.value = []
    reviewResults.value = []
    errors.value = []
    logs.value = []

    // 初始化进度步骤
    progressSteps.value = [
      { title: '初始化审查环境', status: 'pending', detail: '', initDetails: null },
      { title: '加载文件列表', status: 'pending', detail: '', fileDetails: null },
      { title: 'AI快速扫描', status: 'pending', detail: '', analysisDetails: [] },
      { title: 'AI深度分析', status: 'pending', detail: '', deepAnalysisDetails: [] },
      { title: '生成审查报告', status: 'pending', detail: '' },
      { title: '完成', status: 'pending', detail: '' }
    ]

    // 发送开始审查消息
    const message = {
      type: 'start_review',
      project_id: projectId,
      base_branch: baseBranch,
      target_branch: targetBranch,
      scope: scope
    }

    // 如果指定了特定文件，添加到消息中
    if (specificFiles && specificFiles.length > 0) {
      message.specific_files = specificFiles
    }

    ws.value.send(JSON.stringify(message))
  }

  const cancelReview = () => {
    if (ws.value && taskId.value) {
      ws.value.send(JSON.stringify({
        type: 'cancel_review',
        task_id: taskId.value
      }))
    }
  }

  const disconnect = () => {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    connected.value = false
  }

  // 心跳保持连接
  let heartbeatInterval = null
  const startHeartbeat = () => {
    heartbeatInterval = setInterval(() => {
      if (connected.value && ws.value) {
        ws.value.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // 每30秒发送一次心跳
  }

  const stopHeartbeat = () => {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }

  // 组件卸载时清理
  onUnmounted(() => {
    stopHeartbeat()
    disconnect()
  })

  return {
    // 状态
    connected,
    taskId,
    phase,
    progress,
    progressText,
    progressStatus,
    fileGroups,
    totalFiles,
    processedFiles,
    currentFiles,
    progressSteps,
    reviewResults,
    errors,
    logs,

    // 方法
    connect,
    disconnect,
    startReview,
    cancelReview,
    startHeartbeat,
    stopHeartbeat
  }
}

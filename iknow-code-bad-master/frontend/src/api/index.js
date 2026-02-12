import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 120000  // 增加到120秒，AI审查可能需要较长时间
})

export const aiConfigAPI = {
  getAll: () => api.get('/ai-configs'),
  getOne: (id) => api.get(`/ai-configs/${id}`),
  create: (data) => api.post('/ai-configs', data),
  update: (id, data) => api.put(`/ai-configs/${id}`, data),
  delete: (id) => api.delete(`/ai-configs/${id}`),
  activate: (id) => api.put(`/ai-configs/${id}/activate`),
  getModels: (id) => api.get(`/ai-configs/${id}/models`)
}

export const projectAPI = {
  getAll: () => api.get('/projects'),
  getOne: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
  getBranches: (id) => api.get(`/projects/${id}/branches`),
  getStats: (id) => api.get(`/projects/${id}/stats`)
}

export const issueAPI = {
  getAll: (params) => api.get('/issues', { params }),
  getOne: (id) => api.get(`/issues/${id}`),
  create: (data) => api.post('/issues', data),
  update: (id, data) => api.put(`/issues/${id}`, data),
  updateStatus: (id, data) => api.put(`/issues/${id}/status`, data),
  resolve: (id) => api.put(`/issues/${id}/resolve`),
  delete: (id) => api.delete(`/issues/${id}`),
  ignore: (id) => api.put(`/issues/${id}/ignore`),
  ignoreSimilar: (issueType, projectId) => api.post('/issues/ignore-similar', null, { params: { issue_type: issueType, project_id: projectId } }),
  getCode: (id) => api.get(`/issues/${id}/code`),
  chat: (id, content) => api.post(`/issues/${id}/chat`, { content }),
  getChatHistory: (id) => api.get(`/issues/${id}/chat-history`)
}

export const reviewAPI = {
  execute: (data) => api.post('/reviews/execute', null, { params: data })
}

export default api

<template>
  <div class="logs-container">
    <header class="logs-header">
      <h1>操作日志</h1>
      <p class="subtitle">查看您的系统操作历史</p>
    </header>

    <!-- 筛选器 -->
    <div class="filters">
      <select v-model="days" @change="loadLogs">
        <option :value="7">最近 7 天</option>
        <option :value="14">最近 14 天</option>
        <option :value="30">最近 30 天</option>
      </select>
      <button class="refresh-btn" @click="loadLogs">刷新</button>
    </div>

    <!-- 日志列表 -->
    <div class="logs-list">
      <div v-if="logs.length === 0" class="empty-state">
        <p>暂无日志记录</p>
      </div>
      
      <div v-else class="log-item" v-for="log in logs" :key="log.id">
        <div class="log-icon" :class="getActionClass(log.action)">
          {{ getActionIcon(log.action) }}
        </div>
        <div class="log-content">
          <div class="log-action">{{ formatAction(log.action) }}</div>
          <div class="log-details" v-if="log.details">{{ log.details }}</div>
          <div class="log-meta">
            <span class="log-time">{{ formatTime(log.created_at) }}</span>
            <span class="log-status" :class="log.status">{{ log.status }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const logs = ref([])
const days = ref(7)

const loadLogs = async () => {
  try {
    const res = await axios.get('/api/v1/logs/my', {
      params: { days: days.value, limit: 50 }
    })
    logs.value = res.data
  } catch (error) {
    console.error('Failed to load logs:', error)
  }
}

const formatAction = (action) => {
  const map = {
    login: '系统登录 (Sign In)',
    logout: '系统登出 (Sign Out)',
    query: 'AI 对话 (AI Query)',
    upload: '数据上传 (Upload)',
    export: '数据导出 (Export)',
    predict: '营销预测 (Prediction)',
    analysis: '数据分析 (Analysis)'
  }
  return map[action] || action
}

const getActionIcon = (action) => {
  const map = {
    login: '🔑',
    logout: '🚪',
    query: '💬',
    upload: '📤',
    export: '📥',
    predict: '🎯',
    analysis: '📊'
  }
  return map[action] || '📝'
}

const getActionClass = (action) => {
  const map = {
    login: 'green',
    logout: 'gray',
    query: 'blue',
    upload: 'purple',
    export: 'orange',
    predict: 'pink',
    analysis: 'teal'
  }
  return map[action] || ''
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs-container {
  padding: 32px 40px;
  background: #F5F5F7;
  min-height: 100vh;
}

.logs-header h1 {
  font-size: 34px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.subtitle {
  color: #86868B;
  margin-top: 4px;
}

.filters {
  display: flex;
  gap: 12px;
  margin: 24px 0;
}

.filters select {
  padding: 10px 16px;
  border: 1px solid #D2D2D7;
  border-radius: 8px;
  background: white;
  font-size: 14px;
}

.refresh-btn {
  padding: 10px 20px;
  background: #0071E3;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.logs-list {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.empty-state {
  padding: 60px;
  text-align: center;
  color: #86868B;
}

.log-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 24px;
  border-bottom: 1px solid #F2F2F7;
}

.log-item:last-child { border-bottom: none; }

.log-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: #F5F5F7;
}

.log-icon.green { background: #D1FAE5; }
.log-icon.blue { background: #DBEAFE; }
.log-icon.purple { background: #EDE9FE; }
.log-icon.orange { background: #FEF3C7; }
.log-icon.pink { background: #FCE7F3; }
.log-icon.teal { background: #CCFBF1; }
.log-icon.gray { background: #F3F4F6; }

.log-content {
  flex: 1;
}

.log-action {
  font-size: 16px;
  font-weight: 600;
  color: #1D1D1F;
}

.log-details {
  font-size: 14px;
  color: #86868B;
  margin-top: 4px;
}

.log-meta {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  font-size: 13px;
}

.log-time { color: #86868B; }

.log-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.log-status.success { background: #D1FAE5; color: #059669; }
.log-status.failed { background: #FEE2E2; color: #DC2626; }
</style>

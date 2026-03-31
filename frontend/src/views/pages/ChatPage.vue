<template>
  <div class="gemini-layout">
    <!-- 左侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- 顶部操作 -->
      <div class="sidebar-top">
        <button class="icon-btn menu-btn" @click="sidebarCollapsed = !sidebarCollapsed" title="折叠侧栏">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" fill="currentColor"/></svg>
        </button>
        <button class="new-chat-btn icon-btn" @click="createNewSession" title="新建对话" v-if="!sidebarCollapsed">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor"/></svg>
        </button>
      </div>

      <!-- 返回主页 -->
      <router-link to="/dashboard" class="sidebar-nav-item back-link" v-if="!sidebarCollapsed">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" fill="currentColor"/></svg>
        <span>返回主页</span>
      </router-link>

      <!-- 历史对话 -->
      <div class="sessions-section" v-if="!sidebarCollapsed">
        <div class="sessions-label">最近对话</div>
        <div class="sessions-list">
          <div
            v-for="session in sessions"
            :key="session.id"
            :class="['session-item', { active: session.id === currentSessionId }]"
            @click="switchSession(session.id)"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" fill="currentColor"/></svg>
            <span class="session-name">{{ session.title || '新对话' }}</span>
            <button class="delete-btn" @click.stop="deleteSession(session.id)" title="删除">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/></svg>
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部工具栏 -->
      <header class="top-bar">
        <div class="mode-tabs">
          <button :class="['tab-btn', { active: chatMode === 'data' }]" @click="chatMode = 'data'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z" fill="currentColor"/></svg>
            数据查询
          </button>
          <button :class="['tab-btn', { active: chatMode === 'knowledge' }]" @click="chatMode = 'knowledge'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z" fill="currentColor"/></svg>
            知识库
          </button>
        </div>
      </header>

      <!-- 消息区域（独立滚动） -->
      <div class="messages-scroll-area" ref="messagesRef">
        <!-- 欢迎状态 -->
        <div v-if="messages.length === 0" class="welcome-view">
          <div class="welcome-avatar">🎀</div>
          <h1 class="welcome-title">你好，我是小贝壳</h1>
          <p class="welcome-subtitle">你的银行数据智能分析助手</p>
          <div class="suggestion-chips">
            <button class="chip" @click="sendSuggestion('查询30岁以下的客户有哪些？')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="currentColor"/></svg>
              查询30岁以下客户
            </button>
            <button class="chip" @click="sendSuggestion('各职业的转化率是多少？')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z" fill="currentColor"/></svg>
              各职业转化率统计
            </button>
            <button class="chip" @click="sendSuggestion('用柱状图展示各学历人数分布')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm7 13H5v-.23c0-.62.28-1.2.76-1.58C7.47 15.82 9.64 15 12 15s4.53.82 6.24 2.19c.48.38.76.97.76 1.58V19z" fill="currentColor"/></svg>
              学历分布可视化
            </button>
            <button class="chip" @click="sendSuggestion('银行的定期存款产品有哪些特点？')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z" fill="currentColor"/></svg>
              定期存款产品特点
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="messages-list">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message-row', msg.role]"
          >
            <!-- 用户消息 -->
            <div v-if="msg.role === 'user'" class="user-bubble">
              <div class="bubble-text">{{ msg.content }}</div>
            </div>

            <!-- AI 消息 -->
            <div v-else class="ai-message">
              <div class="ai-avatar">🎀</div>
              <div class="ai-body">
                <!-- 打字动画 -->
                <div v-if="!msg.content && loading && index === messages.length - 1" class="typing-dots">
                  <span></span><span></span><span></span>
                </div>
                <!-- 正文 -->
                <div v-if="msg.content" class="ai-text markdown-body" v-html="renderMarkdown(msg.content)"></div>
                <!-- 图表 -->
                <div v-if="msg.chartData" class="chart-card">
                  <div :id="`chart-${index}`" class="echarts-box"></div>
                </div>
                <!-- 来源 -->
                <div v-if="msg.sources && msg.sources.length > 0" class="sources-card">
                  <div class="card-label">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" fill="currentColor"/></svg>
                    知识来源 ({{ msg.sources.length }})
                  </div>
                  <div v-for="(src, i) in msg.sources" :key="i" class="source-row">
                    <span class="source-num">{{ i + 1 }}</span>
                    <span class="source-text">{{ src.content }}</span>
                  </div>
                </div>
                <!-- SQL -->
                <div v-if="msg.sql" class="sql-card">
                  <div class="card-label">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M20 3H4v10c0 2.21 1.79 4 4 4h6c2.21 0 4-1.79 4-4v-3h2c1.11 0 2-.9 2-2V5c0-1.11-.89-2-2-2zm0 5h-2V5h2v3zM4 19h16v2H4z" fill="currentColor"/></svg>
                    执行的 SQL
                  </div>
                  <pre class="sql-code">{{ msg.sql }}</pre>
                </div>
                <div class="msg-time">{{ formatMessageTime(msg.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部占位，防止内容被输入框遮挡 -->
        <div class="scroll-spacer"></div>
      </div>

      <!-- 底部固定输入栏 -->
      <div class="input-panel">
        <div class="input-wrapper">
          <textarea
            v-model="inputMessage"
            @keydown.enter.exact.prevent="sendMessage"
            rows="1"
            placeholder="向小贝壳提问..."
            :disabled="loading"
            class="chat-textarea"
            ref="textareaRef"
            @input="autoResize"
          ></textarea>
          <div class="input-actions">
            <button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim() || loading">
              <svg v-if="!loading" width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"/></svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" class="spin"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" fill="currentColor"/></svg>
            </button>
          </div>
        </div>
        <p class="disclaimer">小贝壳可能会出错。请核查重要信息。</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import * as echarts from 'echarts'
import {
  Plus, DArrowLeft, DArrowRight, ChatDotRound, Delete, TrendCharts,
  Reading, Search, DataAnalysis, Histogram, DocumentCopy, Tickets,
  Compass, Close, Promotion, Loading, House, ArrowLeft
} from '@element-plus/icons-vue'

// 状态管理
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesRef = ref(null)
const textareaRef = ref(null)
const chatMode = ref('data')
const sidebarCollapsed = ref(false)

// 会话管理
const sessions = ref([])
const currentSessionId = ref(null)
const STORAGE_KEY = 'chat_sessions'

// ECharts 实例
const chartInstances = ref(new Map())

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const formatMessageTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// Markdown 渲染
const renderMarkdown = (content) => {
  if (!content) return ''
  return marked.parse(content)
}

// 自动调整 textarea 高度
const autoResize = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

// LocalStorage 操作
const loadSessions = () => {
  const userId = localStorage.getItem('userId') || 'default'
  const data = localStorage.getItem(`${STORAGE_KEY}_${userId}`)
  if (data) sessions.value = JSON.parse(data)
}

const saveSessions = () => {
  const userId = localStorage.getItem('userId') || 'default'
  localStorage.setItem(`${STORAGE_KEY}_${userId}`, JSON.stringify(sessions.value))
}

const loadMessages = (sessionId) => {
  const session = sessions.value.find(s => s.id === sessionId)
  if (session) messages.value = session.messages || []
}

// 会话管理
const createNewSession = () => {
  const newSession = {
    id: Date.now().toString(),
    title: '',
    messages: [],
    createdAt: Date.now(),
    updatedAt: Date.now()
  }
  sessions.value.unshift(newSession)
  currentSessionId.value = newSession.id
  messages.value = newSession.messages
  saveSessions()
}

const switchSession = (sessionId) => {
  currentSessionId.value = sessionId
  loadMessages(sessionId)
}

const deleteSession = (sessionId) => {
  sessions.value = sessions.value.filter(s => s.id !== sessionId)
  if (currentSessionId.value === sessionId) {
    if (sessions.value.length > 0) {
      switchSession(sessions.value[0].id)
    } else {
      createNewSession()
    }
  }
  saveSessions()
}

const updateSessionTitle = (sessionId, firstMessage) => {
  const session = sessions.value.find(s => s.id === sessionId)
  if (session && !session.title) {
    session.title = firstMessage.slice(0, 20) + (firstMessage.length > 20 ? '...' : '')
    saveSessions()
  }
}

const updateSessionAndSave = () => {
  const session = sessions.value.find(s => s.id === currentSessionId.value)
  if (session) {
    session.updatedAt = Date.now()
    saveSessions()
  }
}

// 渲染图表
const renderChart = (index, chartData, retryCount = 0) => {
  const chartId = `chart-${index}`
  const doRender = () => {
    const chartDom = document.getElementById(chartId)
    if (!chartDom) {
      if (retryCount < 10) setTimeout(() => renderChart(index, chartData, retryCount + 1), 100)
      return
    }
    if (chartInstances.value.has(chartId)) {
      chartInstances.value.get(chartId).dispose()
    }
    const chart = echarts.init(chartDom)
    chartInstances.value.set(chartId, chart)
    const option = {
      backgroundColor: 'transparent',
      title: { text: chartData.title || '', left: 'center', top: 10, textStyle: { fontSize: 14, color: '#2C2420', fontWeight: 600 } },
      tooltip: { trigger: chartData.chart_type === 'pie' ? 'item' : 'axis', backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#EFEBE5', textStyle: { color: '#2C2420' } },
      grid: { left: '4%', right: '4%', bottom: '15%', containLabel: true },
      xAxis: chartData.chart_type !== 'pie' ? {
        type: 'category', data: chartData.x_data,
        axisLine: { lineStyle: { color: '#EFEBE5' } },
        axisLabel: { color: '#8C827D', interval: 0, rotate: chartData.x_data?.length > 8 ? 35 : 0, formatter: (val) => val && val.length > 10 ? val.slice(0, 10) + '...' : val }
      } : undefined,
      yAxis: chartData.chart_type !== 'pie' ? {
        type: 'value', axisLine: { show: false }, axisLabel: { color: '#8C827D' },
        splitLine: { lineStyle: { color: '#F5F2ED', type: 'dashed' } }
      } : undefined,
      dataZoom: (chartData.chart_type === 'bar' || chartData.chart_type === 'line') ? [
        { type: 'inside', start: 0, end: chartData.x_data?.length > 10 ? 50 : 100 },
        { type: 'slider', show: chartData.x_data?.length > 10, height: 20, bottom: 4, borderColor: 'transparent', fillerColor: 'rgba(176,141,111,0.12)', textStyle: { color: '#8C827D' } }
      ] : undefined,
      series: [{
        name: chartData.series_name || '', type: chartData.chart_type,
        data: chartData.chart_type === 'pie'
          ? chartData.x_data.map((name, i) => ({ name, value: chartData.y_data[i], itemStyle: { color: ['#B08D6F', '#8C827D', '#D9D2C9', '#EFEBE5', '#2C2420'][i % 5] } }))
          : chartData.y_data,
        itemStyle: {
          borderRadius: chartData.chart_type === 'bar' ? [4, 4, 0, 0] : 0,
          color: chartData.chart_type === 'bar'
            ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#B08D6F' }, { offset: 1, color: '#D9D2C9' }])
            : '#B08D6F'
        },
        lineStyle: { width: 2, color: '#B08D6F' },
        areaStyle: chartData.chart_type === 'line' ? { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(176,141,111,0.2)' }, { offset: 1, color: 'rgba(176,141,111,0)' }]) } : undefined,
        smooth: true,
        radius: chartData.chart_type === 'pie' ? ['40%', '70%'] : undefined,
        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(44,36,32,0.2)' } }
      }]
    }
    chart.setOption(option)
    const resizeHandler = () => chart.resize()
    window.addEventListener('resize', resizeHandler)
    chartDom._resizeHandler = resizeHandler
  }
  if (retryCount === 0) nextTick(doRender)
  else doRender()
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return
  const userMsgText = inputMessage.value
  inputMessage.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  loading.value = true
  messages.value.push({ role: 'user', content: userMsgText, timestamp: Date.now() })
  updateSessionTitle(currentSessionId.value, userMsgText)
  updateSessionAndSave()
  await scrollToBottom()
  const assistantMsg = { role: 'assistant', content: '', chartData: null, sql: null, sources: null, timestamp: Date.now() }
  messages.value.push(assistantMsg)
  updateSessionAndSave()
  try {
    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsgText, user_id: localStorage.getItem('userId') || 'default', session_id: currentSessionId.value, history: [] })
    })
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop()
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'text') assistantMsg.content += data.content
            else if (data.type === 'answer') assistantMsg.content = data.content
            else if (data.type === 'sql') assistantMsg.sql = data.sql
            else if (data.type === 'chart_data') { assistantMsg.chartData = data; renderChart(messages.value.length - 1, data) }
            else if (data.type === 'sources') assistantMsg.sources = data.sources
            else if (data.type === 'error') assistantMsg.content = data.message
            else if (data.type === 'done') { loading.value = false; updateSessionAndSave(); await scrollToBottom(); return }
            await scrollToBottom()
          } catch (e) {}
        }
      }
    }
  } catch (error) {
    console.error('Chat error:', error)
    assistantMsg.content = '抱歉，遇到了一些问题，请稍后再试。'
  } finally {
    loading.value = false
    updateSessionAndSave()
    await scrollToBottom()
  }
}

const sendSuggestion = (text) => {
  inputMessage.value = text
  sendMessage()
}

onMounted(() => {
  loadSessions()
  if (sessions.value.length === 0) {
    createNewSession()
  } else {
    currentSessionId.value = sessions.value[0].id
    loadMessages(currentSessionId.value)
    nextTick(() => {
      messages.value.forEach((msg, index) => {
        if (msg.chartData) renderChart(index, msg.chartData)
      })
    })
  }
})

onUnmounted(() => {
  chartInstances.value.forEach(chart => chart.dispose())
  chartInstances.value.clear()
})
</script>

<style scoped>
/* ============================================================
   根布局 - Gemini 经典三列 (Sidebar + Main) - 暖白换肤版
   ============================================================ */
.gemini-layout {
  display: flex;
  height: 100vh;
  width: 100%;
  background: #FDFBF7; /* 暖白背景 */
  font-family: 'Inter', -apple-system, sans-serif;
  overflow: hidden;
  color: #2C2420; /* 暖褐文字 */
}

/* ============================================================
   左侧边栏 (暖米色调)
   ============================================================ */
.sidebar {
  width: 260px;
  min-width: 260px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #F5F2ED; /* 稍深的暖米色 */
  border-right: 1px solid #EFEBE5;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.25s;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 72px;
  min-width: 72px;
}

.sidebar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 12px;
  gap: 8px;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: #5C524D;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}

.icon-btn:hover {
  background: #EFEBE5;
  color: #B08D6F;
}

.new-chat-btn {
  margin-left: auto;
}

/* 返回主页 */
.sidebar .back-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 0 8px 8px 8px;
  border-radius: 24px;
  color: #5C524D;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s;
}

.sidebar .back-link:hover {
  background: #EFEBE5;
  color: #B08D6F;
}

/* 历史列表区 */
.sessions-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 0 8px;
}

.sessions-label {
  font-size: 11px;
  font-weight: 700;
  color: #8C827D;
  padding: 8px 12px 6px 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sessions-list::-webkit-scrollbar { width: 4px; }
.sessions-list::-webkit-scrollbar-thumb { background: #D9D2C9; border-radius: 4px; }

.session-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 24px;
  cursor: pointer;
  color: #2C2420;
  font-size: 14px;
  transition: all 0.15s;
  position: relative;
}

.session-item:hover {
  background: #EFEBE5;
}

.session-item.active {
  background: #E8E2D9;
  color: #B08D6F;
  font-weight: 600;
}

.session-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-btn {
  opacity: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #8C827D;
  padding: 2px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #E57373;
  color: white;
}

/* ============================================================
   主内容区
   ============================================================ */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #FDFBF7;
  position: relative;
}

/* 顶部模式标签 */
.top-bar {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  flex-shrink: 0;
}

.mode-tabs {
  display: flex;
  gap: 4px;
  background: #F5F2ED;
  padding: 4px;
  border-radius: 24px;
  border: 1px solid #EFEBE5;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border: none;
  border-radius: 20px;
  background: transparent;
  color: #8C827D;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #B08D6F;
}

.tab-btn.active {
  background: #fff;
  color: #B08D6F;
  box-shadow: 0 2px 8px rgba(44, 36, 32, 0.08);
}

/* 消息滚动区域 */
.messages-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
}

.messages-scroll-area::-webkit-scrollbar { width: 5px; }
.messages-scroll-area::-webkit-scrollbar-thumb { background: #EFEBE5; border-radius: 10px; }

.scroll-spacer {
  height: 180px;
  flex-shrink: 0;
}

/* 欢迎视图 */
.welcome-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  text-align: center;
  flex: 1;
}

.welcome-avatar {
  font-size: 60px;
  margin-bottom: 16px;
}

.welcome-title {
  font-size: 42px;
  font-weight: 700;
  color: #2C2420;
  margin: 0 0 12px 0;
  font-family: 'Playfair Display', serif;
}

.welcome-subtitle {
  font-size: 16px;
  color: #8C827D;
  margin: 0 0 48px 0;
  font-weight: 500;
}

/* 建议芯片 */
.suggestion-chips {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-width: 680px;
  width: 100%;
}

.chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  background: #fff;
  border: 1px solid #EFEBE5;
  border-radius: 16px;
  color: #2C2420;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(44, 36, 32, 0.04);
}

.chip:hover {
  border-color: #B08D6F;
  color: #B08D6F;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(176, 141, 111, 0.12);
}

/* 消息列表 */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
  max-width: 860px;
  margin: 0 auto;
  padding: 0 24px;
}

/* 消息行 */
.message-row {
  padding: 24px 0;
}

/* 用户气泡 */
.user-bubble {
  display: flex;
  justify-content: flex-end;
  padding-left: 80px;
}

.bubble-text {
  background: #B08D6F;
  color: #fff;
  padding: 14px 24px;
  border-radius: 24px 24px 4px 24px;
  font-size: 15px;
  line-height: 1.65;
  max-width: 100%;
  word-wrap: break-word;
  box-shadow: 0 4px 15px rgba(176, 141, 111, 0.2);
}

/* AI 消息 (无背景直排，Gemini 风格) */
.ai-message {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.ai-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #F5F2ED;
  border: 1px solid #EFEBE5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 4px;
}

.ai-body {
  flex: 1;
  min-width: 0;
}

/* 打字动画 */
.typing-dots {
  display: flex;
  gap: 6px;
  padding: 12px 0;
}

.typing-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #B08D6F;
  opacity: 0.4;
  animation: pulse 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.85); opacity: 0.4; }
  40% { transform: scale(1.1); opacity: 0.8; }
}

/* AI 文本 */
.ai-text {
  font-size: 16px;
  line-height: 1.8;
  color: #2C2420;
}

.ai-text :deep(p) { margin: 0 0 16px 0; }
.ai-text :deep(p:last-child) { margin-bottom: 0; }
.ai-text :deep(h1), .ai-text :deep(h2), .ai-text :deep(h3) { font-weight: 700; margin: 24px 0 12px 0; color: #2C2420; }
.ai-text :deep(strong) { font-weight: 700; color: #B08D6F; }
.ai-text :deep(code) { background: #F5F2ED; padding: 2px 6px; border-radius: 4px; font-size: 14px; color: #B08D6F; font-family: monospace; }
.ai-text :deep(pre) { background: #F5F2ED; border-radius: 12px; padding: 20px; overflow-x: auto; margin: 16px 0; border: 1px solid #EFEBE5; }
.ai-text :deep(ul), .ai-text :deep(ol) { padding-left: 20px; margin: 12px 0; }
.ai-text :deep(li) { margin-bottom: 8px; }

/* 时间戳 */
.msg-time {
  font-size: 11px;
  color: #BDB1A8;
  margin-top: 12px;
}

/* 图表卡片 */
.chart-card {
  margin-top: 20px;
  background: #fff;
  border: 1px solid #EFEBE5;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(44, 36, 32, 0.04);
}

.echarts-box {
  width: 100%;
  height: 360px;
}

/* 来源 & SQL 卡片 */
.sources-card, .sql-card {
  margin-top: 16px;
  background: #FDFBF7;
  border: 1px solid #EFEBE5;
  border-radius: 16px;
  padding: 20px;
}

.card-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #8C827D;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 16px;
}

.source-row {
  display: flex;
  gap: 14px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #5C524D;
  line-height: 1.6;
}

.source-num {
  width: 20px;
  height: 20px;
  background: #EFEBE5;
  color: #B08D6F;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.sql-code {
  font-family: 'Roboto Mono', monospace;
  font-size: 13px;
  color: #B08D6F;
  white-space: pre-wrap;
  margin: 0;
  line-height: 1.5;
}

/* ============================================================
   底部输入栏 - Gemini 暖白版
   ============================================================ */
.input-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0 24px 32px 24px;
  background: linear-gradient(0deg, #FDFBF7 75%, rgba(253, 251, 247, 0) 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.input-wrapper {
  width: 100%;
  max-width: 860px;
  background: #fff;
  border: 1px solid #EFEBE5;
  border-radius: 32px;
  padding: 10px 12px 10px 24px;
  display: flex;
  align-items: flex-end;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(44, 36, 32, 0.05);
}

.input-wrapper:focus-within {
  border-color: #B08D6F;
  box-shadow: 0 8px 32px rgba(176, 141, 111, 0.12);
  transform: translateY(-1px);
}

.chat-textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  font-size: 16px;
  font-family: inherit;
  color: #2C2420;
  outline: none;
  line-height: 1.6;
  max-height: 200px;
  overflow-y: auto;
  padding: 4px 0;
}

.chat-textarea::placeholder {
  color: #BDB1A8;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: #B08D6F;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #96765A;
  transform: scale(1.04);
}

.send-btn:disabled {
  background: #EFEBE5;
  color: #BDB1A8;
  cursor: not-allowed;
}

.disclaimer {
  font-size: 11px;
  color: #BDB1A8;
  margin: 10px 0 0 0;
  text-align: center;
  font-weight: 500;
}

.spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>

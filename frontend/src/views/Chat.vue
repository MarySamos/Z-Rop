<template>
  <div class="chat-page">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-title">
        <h2>智能数据助手</h2>
        <span class="subtitle">基于大语言模型的数据分析</span>
      </div>
      <el-button text @click="clearChat">
        <el-icon><Delete /></el-icon>
        <span>清空对话</span>
      </el-button>
    </div>

    <!-- 消息区域 -->
    <div class="messages-container" ref="messagesRef">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-section">
        <div class="welcome-card">
          <div class="welcome-icon">
            <el-icon :size="40"><ChatDotRound /></el-icon>
          </div>
          <h3>你好！我是 BankAgent 智能助手</h3>
          <p>我可以帮你分析银行营销数据，试试问我：</p>
          <div class="suggestion-chips">
            <span class="chip" @click="sendSuggestion('查询30岁以下的客户有哪些？')">
              <el-icon><Search /></el-icon>
              查询30岁以下客户
            </span>
            <span class="chip" @click="sendSuggestion('各职业的转化率是多少？')">
              <el-icon><DataAnalysis /></el-icon>
              职业转化率
            </span>
            <span class="chip" @click="sendSuggestion('分析客户年龄分布')">
              <el-icon><TrendCharts /></el-icon>
              年龄分布分析
            </span>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index" class="message-group" :class="msg.role">
        <!-- AI 消息 -->
        <template v-if="msg.role === 'assistant'">
          <div class="message-avatar assistant-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-bubble">
              <div class="message-text">{{ msg.content }}</div>
              <!-- 图表展示 -->
              <div v-if="msg.chart" class="chart-container" v-html="msg.chart"></div>

              <!-- SQL 展示 -->
              <div v-if="msg.sql" class="sql-card">
                <div class="sql-header">
                  <el-icon><Document /></el-icon>
                  已执行的 SQL
                </div>
                <pre class="sql-code">{{ msg.sql }}</pre>
              </div>
            </div>
          </div>
        </template>

        <!-- 用户消息 -->
        <template v-else>
          <div class="message-content user-content">
            <div class="message-bubble user-bubble">
              {{ msg.content }}
            </div>
          </div>
        </template>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="message-group assistant">
        <div class="message-avatar assistant-avatar">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-section">
      <div class="input-wrapper">
        <div class="input-box">
          <el-input
            v-model="inputMessage"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="输入问题，如：查询30岁以下的客户"
            :disabled="loading"
            size="large"
            class="chat-input"
          >
            <template #suffix>
              <el-button
                class="send-button"
                type="primary"
                @click="sendMessage"
                :disabled="!inputMessage.trim() || loading"
                :icon="Promotion"
              />
            </template>
          </el-input>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Delete, Search, DataAnalysis, TrendCharts, Document, Promotion } from '@element-plus/icons-vue'
import axios from 'axios'

const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是 BankAgent Pro 智能助手。关于银行营销数据，你有什么想问的吗？'
  }
])
const inputMessage = ref('')
const loading = ref(false)
const messagesRef = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMsg = inputMessage.value
  messages.value.push({ role: 'user', content: userMsg })
  inputMessage.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const response = await axios.post('/api/v1/chat/send', {
      message: userMsg,
      history: []
    })

    const data = response.data
    messages.value.push({
      role: 'assistant',
      content: data.answer || '处理完成',
      chart: data.chart,
      sql: data.sql
    })
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，遇到了一些问题，请检查后端服务是否正常运行。'
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

const sendSuggestion = (text) => {
  inputMessage.value = text
  sendMessage()
}

const clearChat = () => {
  messages.value = [
    {
      role: 'assistant',
      content: '你好！我是 BankAgent Pro 智能助手。关于银行营销数据，你有什么想问的吗？'
    }
  ]
  ElMessage.success('对话已清空')
}

onMounted(() => {
  // Focus input on mount
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
}

/* 聊天头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #f0f0f0;
}

.header-title h2 {
  font-size: 17px;
  font-weight: 600;
  color: #333333;
  margin: 0;
}

.header-title .subtitle {
  font-size: 12px;
  color: #999999;
  margin-left: 8px;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
  border-radius: 12px;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  padding: 20px;
}

.welcome-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  max-width: 480px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  border: 1px solid #f0f0f0;
}

.welcome-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #ff6b81 0%, #ff8fa3 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: #ffffff;
}

.welcome-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
  margin: 0 0 8px 0;
}

.welcome-card p {
  font-size: 14px;
  color: #999999;
  margin: 0 0 24px 0;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: #f8f8f8;
  border-radius: 20px;
  font-size: 13px;
  color: #666666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip:hover {
  background: #ff6b81;
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 129, 0.25);
}

/* 消息组 */
.message-group {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: messageSlide 0.3s ease;
}

.message-group.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.assistant-avatar {
  background: linear-gradient(135deg, #ff6b81 0%, #ff8fa3 100%);
  color: #ffffff;
  font-size: 16px;
}

.message-content {
  max-width: 70%;
}

.user-content {
  display: flex;
  justify-content: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.assistant-bubble {
  background: #ffffff;
  color: #333333;
  border: 1px solid #f0f0f0;
  border-bottom-left-radius: 4px;
}

.user-bubble {
  background: linear-gradient(135deg, #ff6b81 0%, #ff8fa3 100%);
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.message-text {
  white-space: pre-wrap;
}

/* SQL 卡片 */
.sql-card {
  margin-top: 10px;
  background: #f8f8f8;
  border-radius: 8px;
  overflow: hidden;
}

.sql-header {
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 500;
  color: #666666;
  background: #eeeeee;
  display: flex;
  align-items: center;
  gap: 6px;
}

.sql-code {
  padding: 10px 12px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #ff6b81;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 图表容器 */
.chart-container {
  margin-top: 12px;
  background: #ffffff;
  border-radius: 8px;
  padding: 16px;
  overflow: hidden;
}

.chart-container :deep(div) {
  width: 100% !important;
}


/* 打字动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  border-bottom-left-radius: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #ff6b81;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* 输入区域 */
.input-section {
  padding: 0;
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.input-box {
  display: flex;
  align-items: center;
  padding: 8px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
}

.chat-input {
  flex: 1;
}

.chat-input :deep(.el-input__wrapper) {
  border: none;
  box-shadow: none;
  background: transparent;
}

.send-button {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  padding: 0;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

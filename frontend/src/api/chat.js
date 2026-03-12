/**
 * Chat API
 * 智能对话相关接口
 */
import axios from 'axios'

const BASE_URL = '/api/v1'

/**
 * 发送聊天消息
 */
export const sendMessage = async (message, history = []) => {
  return axios.post(`${BASE_URL}/chat/send`, {
    message,
    history
  })
}

/**
 * 流式聊天（SSE）
 */
export const chatStream = async (message, sessionId = null, userId = 'anonymous') => {
  const response = await fetch(`${BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_id: userId
    })
  })
  return response
}

/**
 * 智能分析（带查询重写）
 */
export const smartChat = async (message, history = []) => {
  return axios.post(`${BASE_URL}/chat/smart`, {
    message,
    history
  })
}

/**
 * 分析查询
 */
export const analyzeQuery = async (message) => {
  return axios.post(`${BASE_URL}/chat/analyze`, { message })
}

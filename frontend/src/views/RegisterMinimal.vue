<template>
  <div class="register-page">
    <!-- 纯净背景层 -->
    <div class="background-glass"></div>

    <!-- 左侧：品牌区域 -->
    <div class="brand-section">
      <div class="brand-content animate-in">
        <div class="brand-mark">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="18" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
            <circle cx="20" cy="20" r="12" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
            <circle cx="20" cy="20" r="6" fill="currentColor" opacity="0.8"/>
          </svg>
        </div>
        <h1 class="brand-title">Z-Rop</h1>
        <p class="brand-tagline">开启智能数据分析之旅</p>

        <div class="brand-features">
          <div class="feature-item">
            <span class="feature-icon">—</span>
            <span>全流程数据洞察</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">—</span>
            <span>AI 驱动决策支持</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">—</span>
            <span>企业级安全保障</span>
          </div>
        </div>

        <div class="brand-footer">
          <p>已有账户？</p>
          <router-link to="/login" class="link">立即登录</router-link>
        </div>
      </div>
    </div>

    <!-- 右侧：注册表单 -->
    <div class="form-section">
      <div class="form-container animate-in">
        <div class="form-header">
          <p class="form-greeting">创建账户</p>
          <h2 class="form-title">加入 Z-Rop</h2>
          <p class="form-subtitle">请填写以下信息完成注册</p>
        </div>

        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">工号</label>
              <input
                v-model="form.employee_id"
                type="text"
                class="form-input"
                placeholder="请输入工号"
                autocomplete="username"
              />
            </div>
            <div class="form-group">
              <label class="form-label">姓名</label>
              <input
                v-model="form.name"
                type="text"
                class="form-input"
                placeholder="请输入姓名"
                autocomplete="name"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">部门</label>
            <select v-model="form.department" class="form-input" required>
              <option value="">请选择部门</option>
              <option value="营销部">营销部</option>
              <option value="风控部">风控部</option>
              <option value="数据部">数据部</option>
              <option value="技术部">技术部（管理员）</option>
              <option value="IT部">IT部（管理员）</option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">密码</label>
              <input
                v-model="form.password"
                type="password"
                class="form-input"
                placeholder="至少6位"
                autocomplete="new-password"
              />
            </div>
            <div class="form-group">
              <label class="form-label">确认密码</label>
              <input
                v-model="confirmPassword"
                type="password"
                class="form-input"
                placeholder="再次输入密码"
                autocomplete="new-password"
              />
            </div>
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="!loading">创建账户</span>
            <span v-else class="loading-text">
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
            </span>
          </button>
        </form>

        <div class="terms">
          注册即表示您同意我们的服务条款和隐私政策
        </div>
      </div>
    </div>

    <!-- 通知提示 -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()

const form = reactive({
  employee_id: '',
  name: '',
  department: '',
  password: ''
})

const confirmPassword = ref('')
const loading = ref(false)
const notification = reactive({ show: false, message: '', type: '' })

const showNotification = (message, type = 'error') => {
  notification.message = message
  notification.type = type
  notification.show = true
  setTimeout(() => { notification.show = false }, 3000)
}

const handleRegister = async () => {
  // 验证
  if (!form.employee_id.trim()) {
    showNotification('请输入工号')
    return
  }
  if (!form.name.trim()) {
    showNotification('请输入姓名')
    return
  }
  if (!form.department) {
    showNotification('请选择部门')
    return
  }
  if (form.password.length < 6) {
    showNotification('密码长度至少6位')
    return
  }
  if (form.password !== confirmPassword.value) {
    showNotification('两次密码输入不一致')
    return
  }

  loading.value = true

  try {
    const response = await api.post('/api/v1/auth/register', form)
    const data = response.data

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('userId', data.user.id)

    ElMessage.success('注册成功！')
    router.push('/chat')
  } catch (error) {
    showNotification(error.response?.data?.detail || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ============================================================
   Apple Style Layout
   ============================================================ */

.register-page {
  min-height: 100vh;
  display: flex;
  background: var(--color-bg-page);
  position: relative;
  overflow: hidden;
}

.background-glass {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 15% 50%, rgba(0, 113, 227, 0.04), transparent 40%),
              radial-gradient(circle at 85% 30%, rgba(0, 113, 227, 0.03), transparent 40%);
  pointer-events: none;
}

/* ============================================================
   左侧品牌区
   ============================================================ */

.brand-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px;
  position: relative;
  z-index: 1;
}

.brand-content {
  max-width: 440px;
}

.brand-mark {
  width: 56px;
  height: 56px;
  color: var(--color-primary);
  margin-bottom: 32px;
}

.brand-title {
  font-size: 3.5rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--color-text-primary);
  margin-bottom: 16px;
  line-height: 1.1;
}

.brand-tagline {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  margin-bottom: 56px;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 56px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-regular);
}

.feature-icon {
  font-size: 24px;
  color: var(--color-primary);
}

.brand-footer {
  padding-top: 32px;
  border-top: 1px solid var(--color-border-light);
  display: flex;
  gap: 8px;
  font-size: 15px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.brand-footer .link {
  color: var(--color-primary);
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.brand-footer .link:hover {
  opacity: 0.8;
}

/* ============================================================
   右侧表单区
   ============================================================ */

.form-section {
  flex: 0 0 540px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: var(--color-bg-container);
  border-left: 1px solid var(--color-border-light);
  box-shadow: -20px 0 40px rgba(0, 0, 0, 0.02);
  position: relative;
  z-index: 1;
  overflow-y: auto;
}

/* 自定义滚动条风格 */
.form-section::-webkit-scrollbar {
  width: 6px;
}
.form-section::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

.form-container {
  width: 100%;
  max-width: 420px;
}

.form-header {
  margin-bottom: 48px;
}

.form-greeting {
  font-size: 14px;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 12px;
  font-weight: 600;
}

.form-title {
  font-size: 2.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
  margin: 0 0 12px 0;
}

.form-subtitle {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
  font-weight: 400;
}

/* ============================================================
   表单样式
   ============================================================ */

.register-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-regular);
}

.form-input {
  width: 100%;
  padding: 16px 20px;
  font-family: inherit;
  font-size: 16px;
  color: var(--color-text-primary);
  background: var(--color-bg-page);
  border: 1px solid transparent;
  border-radius: var(--radius-base);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.form-input::placeholder {
  color: var(--color-text-placeholder);
}

.form-input:focus {
  outline: none;
  background: var(--color-bg-container);
  border-color: var(--color-primary-light);
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.15);
}

select.form-input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L6 6L11 1' stroke='%2386868b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 20px center;
  padding-right: 48px;
}

.btn-submit {
  width: 100%;
  padding: 18px;
  font-family: inherit;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  background: var(--color-text-primary);
  border: none;
  border-radius: var(--radius-large);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  margin-top: 16px;
  letter-spacing: 0.02em;
}

.btn-submit:hover:not(:disabled) {
  background: #000000;
  transform: scale(0.98);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.btn-submit:active:not(:disabled) {
  transform: scale(0.96);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载动画 */
.loading-text {
  display: flex;
  gap: 6px;
  justify-content: center;
  align-items: center;
  height: 24px;
}

.loading-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  animation: pulse 1.4s infinite;
}

.loading-dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 60%, 100% { transform: scale(0.8); opacity: 0.4; }
  30% { transform: scale(1.2); opacity: 1; }
}

/* ============================================================
   表单底部条款
   ============================================================ */

.terms {
  margin-top: 32px;
  text-align: center;
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* ============================================================
   通知提示
   ============================================================ */

.notification {
  position: fixed;
  top: 32px;
  left: 50%;
  transform: translateX(-50%) translateY(-20px);
  padding: 16px 32px;
  background: var(--color-text-primary);
  color: var(--color-bg-container);
  border-radius: var(--radius-xl);
  font-size: 15px;
  font-weight: 500;
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 1000;
  box-shadow: var(--shadow-dark);
}

.notification.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.notification.error {
  background: var(--color-danger);
}

.notification.success {
  background: var(--color-success);
}

/* ============================================================
   响应式
   ============================================================ */

@media (max-width: 1024px) {
  .register-page {
    flex-direction: column;
  }

  .brand-section {
    flex: 0 1 auto;
    padding: 60px 32px;
  }

  .brand-title {
    font-size: 2.5rem;
  }

  .form-section {
    flex: 1;
    padding: 60px 32px;
    border-left: none;
    border-top: 1px solid var(--color-border-light);
  }

  .form-container {
    max-width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}

/* 入场动画 */
.animate-in {
  animation: fadeUpIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateY(20px);
}

.form-container.animate-in {
  animation-delay: 0.2s;
}

@keyframes fadeUpIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 左侧介绍区域 -->
      <div class="login-intro">
        <div class="intro-content">
          <div class="intro-logo">
            <el-icon :size="42"><TrendCharts /></el-icon>
          </div>
          <h1 class="intro-title">BankAgent Pro</h1>
          <p class="intro-description">
            基于大语言模型的银行数据分析系统
          </p>
          <div class="intro-features">
            <div class="feature-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>智能问答</span>
            </div>
            <div class="feature-item">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据分析</span>
            </div>
            <div class="feature-item">
              <el-icon><TrendCharts /></el-icon>
              <span>可视化</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-form-section">
        <div class="login-form-card">
          <div class="form-header">
            <h2>登录系统</h2>
            <p>请使用您的工号登录</p>
          </div>

          <el-form :model="loginForm" class="login-form">
            <div class="form-item">
              <el-input
                v-model="loginForm.employee_id"
                placeholder="请输入工号"
                size="large"
                :prefix-icon="User"
              />
            </div>

            <div class="form-item">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </div>

            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>

            <div class="form-footer">
              <router-link to="/register" class="register-link">
                还没有账号？立即注册
              </router-link>
            </div>
          </el-form>
        </div>

        <div class="copyright">
          © 2026 BankAgent Pro. All rights reserved.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { User, Lock, ChatDotRound, DataAnalysis, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)

const loginForm = reactive({
  employee_id: '',
  password: ''
})

const handleLogin = async () => {
  if (!loginForm.employee_id || !loginForm.password) {
    ElMessage.warning('请输入工号和密码')
    return
  }

  loading.value = true

  try {
    const response = await axios.post('/api/v1/auth/login', {
      employee_id: loginForm.employee_id,
      password: loginForm.password
    })

    const data = response.data

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    ElMessage.success(`欢迎回来，${data.user.name}！`)
    router.push('/chat')

  } catch (error) {
    console.error('Login error:', error)

    if (error.response?.status === 401) {
      ElMessage.error('工号或密码错误')
    } else {
      ElMessage.error('登录失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8f8f8 0%, #eeeeee 100%);
  padding: 20px;
}

.login-container {
  display: flex;
  max-width: 1000px;
  width: 100%;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

/* ========== 左侧介绍区域 ========== */
.login-intro {
  flex: 1;
  padding: 60px;
  background: linear-gradient(135deg, #2d2d2d 0%, #3d3d3d 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.intro-content {
  text-align: center;
  color: #ffffff;
}

.intro-logo {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: var(--color-primary, #ff6b81);
}

.intro-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.intro-description {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.65);
  margin: 0 0 32px 0;
}

.intro-features {
  display: flex;
  justify-content: center;
  gap: 24px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
}

.feature-item .el-icon {
  font-size: 20px;
  color: var(--color-primary, #ff6b81);
}

/* ========== 右侧表单区域 ========== */
.login-form-section {
  flex: 1;
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-form-card {
  width: 100%;
  max-width: 360px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 22px;
  font-weight: 600;
  color: #333333;
  margin: 0 0 6px 0;
}

.form-header p {
  font-size: 14px;
  color: #999999;
  margin: 0;
}

.login-form .form-item {
  margin-bottom: 18px;
}

.login-btn {
  width: 100%;
  height: 46px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  margin-top: 8px;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
}

.register-link {
  color: var(--color-primary, #ff6b81);
  text-decoration: none;
  font-size: 13px;
}

.register-link:hover {
  text-decoration: underline;
}

.copyright {
  margin-top: auto;
  text-align: center;
  font-size: 12px;
  color: #cccccc;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .login-intro {
    padding: 40px 20px;
  }

  .intro-features {
    flex-direction: column;
    gap: 16px;
  }

  .login-form-section {
    padding: 40px 20px;
  }

  .intro-title {
    font-size: 22px;
  }
}
</style>

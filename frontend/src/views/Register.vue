<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="title">创建新账号</h1>
      <p class="subtitle">加入 BankAgent Pro 智能营销平台</p>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="input-group">
          <label>员工工号 (Employee ID)</label>
          <input v-model="form.employee_id" type="text" placeholder="请输入工号" required />
        </div>

        <div class="input-group">
          <label>姓名 (Full Name)</label>
          <input v-model="form.name" type="text" placeholder="请输入真实姓名" required />
        </div>

        <div class="input-group">
          <label>所属部门 (Department)</label>
          <select v-model="form.department" required>
            <option value="">请选择部门</option>
            <option value="营销部">营销部</option>
            <option value="风控部">风控部</option>
            <option value="数据部">数据部</option>
            <option value="技术部">技术部</option>
          </select>
        </div>

        <div class="input-group">
          <label>登录密码 (Password)</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" required />
        </div>

        <div class="input-group">
          <label>确认密码 (Confirm Password)</label>
          <input v-model="confirmPassword" type="password" placeholder="请再次输入密码" required />
        </div>

        <button type="submit" class="register-btn" :disabled="loading">
          {{ loading ? '正在创建...' : '立即注册' }}
        </button>
      </form>

      <p class="login-link">
        已有账号？ <a @click="goToLogin">立即登录</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const confirmPassword = ref('')

const form = reactive({
  employee_id: '',
  name: '',
  department: '',
  password: ''
})

const handleRegister = async () => {
  if (form.password !== confirmPassword.value) {
    ElMessage.error('两次密码输入不一致')
    return
  }

  if (form.password.length < 6) {
    ElMessage.error('密码长度至少6位')
    return
  }

  loading.value = true

  try {
    const response = await axios.post('/api/v1/auth/register', form)
    const data = response.data

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    ElMessage.success('注册成功！')
    router.push('/chat')

  } catch (error) {
    console.error('Register error:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  background: white;
  padding: 40px;
  border-radius: 20px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
  text-align: center;
}

.subtitle {
  color: #86868B;
  text-align: center;
  margin-bottom: 30px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1D1D1F;
  margin-bottom: 8px;
}

.input-group input,
.input-group select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #D2D2D7;
  border-radius: 10px;
  font-size: 16px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.input-group input:focus,
.input-group select:focus {
  outline: none;
  border-color: #0071E3;
}

.register-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.register-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #86868B;
  font-size: 14px;
}

.login-link a {
  color: #0071E3;
  cursor: pointer;
  font-weight: 500;
}
</style>

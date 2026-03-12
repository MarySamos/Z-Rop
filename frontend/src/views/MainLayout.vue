<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-title">BankAgent Pro</div>
        <div class="logo-subtitle">智能数据分析</div>
      </div>

      <nav class="nav-menu">
        <div class="nav-item" :class="{ active: isActive('/chat') }" @click="navigate('/chat')">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能助手</span>
        </div>
        <div class="nav-item" :class="{ active: isActive('/dashboard') }" @click="navigate('/dashboard')">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </div>
        <div class="nav-item" :class="{ active: isActive('/analysis') }" @click="navigate('/analysis')">
          <el-icon><TrendCharts /></el-icon>
          <span>深度分析</span>
        </div>
        <div class="nav-item" :class="{ active: isActive('/predict') }" @click="navigate('/predict')">
          <el-icon><DataAnalysis /></el-icon>
          <span>预测模型</span>
        </div>
        <div class="nav-item" :class="{ active: isActive('/data') }" @click="navigate('/data')">
          <el-icon><Document /></el-icon>
          <span>数据管理</span>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info" v-if="user">
          <div class="user-avatar">
            {{ user.name?.charAt(0) || 'U' }}
          </div>
          <div class="user-details">
            <div class="user-name">{{ user.name }}</div>
            <div class="user-role">{{ user.role === 'admin' ? '管理员' : '用户' }}</div>
          </div>
        </div>
        <el-button text @click="handleLogout" class="logout-btn">
          <el-icon><SwitchButton /></el-icon>
          <span>退出登录</span>
        </el-button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="content-container">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ChatDotRound, DataAnalysis, TrendCharts, Document, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const user = ref(null)

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const navigate = (path) => {
  router.push(path)
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    try {
      user.value = JSON.parse(storedUser)
    } catch (e) {
      user.value = null
    }
  }
})
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  background-color: #f8f8f8;
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e0e0e0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.02);
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.logo-title {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
}

.logo-subtitle {
  font-size: 12px;
  color: #999999;
  margin-top: 2px;
}

.nav-menu {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  margin-bottom: 4px;
  border-radius: 8px;
  color: #666666;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.nav-item .el-icon {
  font-size: 18px;
}

.nav-item:hover {
  background: #f8f8f8;
  color: #333333;
}

.nav-item.active {
  background: linear-gradient(135deg, #ff6b81 0%, #ff8fa3 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(255, 107, 129, 0.25);
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f8f8f8;
  border-radius: 8px;
  margin-bottom: 10px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b81 0%, #ff8fa3 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #333333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 11px;
  color: #999999;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-start;
  padding: 10px 14px;
  color: #999999;
  border-radius: 8px;
}

.logout-btn:hover {
  background: #f8f8f8;
  color: #ff6b81;
}

/* 主内容区 */
.main-content {
  flex: 1;
  overflow: hidden;
}

.content-container {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
}
</style>

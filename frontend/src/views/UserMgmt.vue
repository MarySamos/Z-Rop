<template>
  <div class="user-mgmt-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1>用户管理</h1>
        <p class="subtitle">管理系统用户、角色权限与账号状态</p>
      </div>
      <button class="create-btn" @click="showCreateDialog = true">
        <span class="btn-icon">+</span>
        <span>创建用户</span>
      </button>
    </header>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索姓名或工号..."
          @input="handleSearch"
        />
      </div>
      <div class="filter-group">
        <select v-model="roleFilter" @change="loadUsers">
          <option value="">全部角色</option>
          <option value="admin">管理员</option>
          <option value="analyst">分析师</option>
          <option value="user">普通用户</option>
        </select>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="user-table">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="users.length === 0" class="empty-state">
        <p>暂无用户数据</p>
      </div>

      <template v-else>
        <!-- 表头 -->
        <div class="table-header">
          <span class="col-avatar"></span>
          <span class="col-id">工号</span>
          <span class="col-name">姓名</span>
          <span class="col-dept">部门</span>
          <span class="col-role">角色</span>
          <span class="col-status">状态</span>
          <span class="col-time">注册时间</span>
          <span class="col-actions">操作</span>
        </div>

        <!-- 用户行 -->
        <div class="table-row" v-for="user in users" :key="user.id">
          <span class="col-avatar">
            <div class="avatar" :class="getRoleColor(user.role)">
              {{ user.name.substring(0, 1) }}
            </div>
          </span>
          <span class="col-id">{{ user.employee_id }}</span>
          <span class="col-name">{{ user.name }}</span>
          <span class="col-dept">{{ user.department || '—' }}</span>
          <span class="col-role">
            <span class="role-tag" :class="'role-' + user.role">
              {{ formatRole(user.role) }}
            </span>
          </span>
          <span class="col-status">
            <span class="status-dot" :class="user.is_active ? 'active' : 'inactive'"></span>
            {{ user.is_active ? '正常' : '已禁用' }}
          </span>
          <span class="col-time">{{ formatTime(user.created_at) }}</span>
          <span class="col-actions">
            <button class="action-btn" @click="openRoleDialog(user)" title="修改角色">
              🎭
            </button>
            <button
              class="action-btn"
              @click="toggleStatus(user)"
              :title="user.is_active ? '禁用' : '启用'"
            >
              {{ user.is_active ? '🔒' : '🔓' }}
            </button>
          </span>
        </div>

        <!-- 分页 -->
        <div class="pagination">
          <span class="page-info">共 {{ total }} 位用户</span>
          <div class="page-controls">
            <button
              class="page-btn"
              :disabled="currentPage <= 1"
              @click="changePage(currentPage - 1)"
            >
              ‹
            </button>
            <span class="page-num">{{ currentPage }} / {{ totalPages }}</span>
            <button
              class="page-btn"
              :disabled="currentPage >= totalPages"
              @click="changePage(currentPage + 1)"
            >
              ›
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- 创建用户弹窗 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <h2>创建用户</h2>
        <div class="form-group">
          <label>工号</label>
          <input v-model="newUser.employee_id" type="text" placeholder="请输入工号" />
        </div>
        <div class="form-group">
          <label>姓名</label>
          <input v-model="newUser.name" type="text" placeholder="请输入姓名" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="newUser.password" type="password" placeholder="请输入密码（至少6位）" />
        </div>
        <div class="form-group">
          <label>部门</label>
          <input v-model="newUser.department" type="text" placeholder="请输入部门（可选）" />
        </div>
        <div class="form-group">
          <label>角色</label>
          <select v-model="newUser.role">
            <option value="user">普通用户</option>
            <option value="analyst">分析师</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="showCreateDialog = false">取消</button>
          <button class="confirm-btn" @click="handleCreate" :disabled="creating">
            {{ creating ? '创建中...' : '确认创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 修改角色弹窗 -->
    <div v-if="showRoleDialog" class="dialog-overlay" @click.self="showRoleDialog = false">
      <div class="dialog">
        <h2>修改角色</h2>
        <p class="dialog-desc">
          修改用户 <strong>{{ editingUser?.name }}</strong> 的角色
        </p>
        <div class="form-group">
          <label>新角色</label>
          <select v-model="newRole">
            <option value="user">普通用户</option>
            <option value="analyst">分析师</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="showRoleDialog = false">取消</button>
          <button class="confirm-btn" @click="handleRoleChange">确认修改</button>
        </div>
      </div>
    </div>

    <!-- 提示消息 -->
    <transition name="toast">
      <div v-if="toast.show" class="toast" :class="toast.type">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 数据状态
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const loading = ref(false)
const keyword = ref('')
const roleFilter = ref('')

// 弹窗状态
const showCreateDialog = ref(false)
const showRoleDialog = ref(false)
const creating = ref(false)
const editingUser = ref(null)
const newRole = ref('user')

// 新建用户表单
const newUser = ref({
  employee_id: '',
  name: '',
  password: '',
  department: '',
  role: 'user'
})

// 提示消息
const toast = ref({ show: false, message: '', type: 'success' })

// 计算属性
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

// ===== 数据加载 =====

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (roleFilter.value) params.role = roleFilter.value
    if (keyword.value) params.keyword = keyword.value

    const res = await axios.get('/api/v1/admin/users', { params })
    users.value = res.data.users
    total.value = res.data.total
  } catch (error) {
    showToast('加载用户列表失败', 'error')
  } finally {
    loading.value = false
  }
}

// ===== 搜索（防抖） =====

let searchTimer = null
const handleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadUsers()
  }, 300)
}

// ===== 分页 =====

const changePage = (page) => {
  currentPage.value = page
  loadUsers()
}

// ===== 创建用户 =====

const handleCreate = async () => {
  if (!newUser.value.employee_id || !newUser.value.name || !newUser.value.password) {
    showToast('请填写必要信息', 'error')
    return
  }
  if (newUser.value.password.length < 6) {
    showToast('密码至少 6 位', 'error')
    return
  }

  creating.value = true
  try {
    await axios.post('/api/v1/admin/users', newUser.value)
    showToast(`用户 ${newUser.value.name} 创建成功`)
    showCreateDialog.value = false
    newUser.value = { employee_id: '', name: '', password: '', department: '', role: 'user' }
    loadUsers()
  } catch (error) {
    const msg = error.response?.data?.detail || '创建失败'
    showToast(msg, 'error')
  } finally {
    creating.value = false
  }
}

// ===== 修改角色 =====

const openRoleDialog = (user) => {
  editingUser.value = user
  newRole.value = user.role
  showRoleDialog.value = true
}

const handleRoleChange = async () => {
  try {
    await axios.put(`/api/v1/admin/users/${editingUser.value.id}/role`, {
      role: newRole.value
    })
    showToast(`${editingUser.value.name} 角色已修改为 ${formatRole(newRole.value)}`)
    showRoleDialog.value = false
    loadUsers()
  } catch (error) {
    const msg = error.response?.data?.detail || '修改失败'
    showToast(msg, 'error')
  }
}

// ===== 修改状态 =====

const toggleStatus = async (user) => {
  const action = user.is_active ? '禁用' : '启用'
  if (!confirm(`确定要${action}用户 "${user.name}" 吗？`)) return

  try {
    await axios.put(`/api/v1/admin/users/${user.id}/status`, {
      is_active: !user.is_active
    })
    showToast(`${user.name} 已${action}`)
    loadUsers()
  } catch (error) {
    const msg = error.response?.data?.detail || `${action}失败`
    showToast(msg, 'error')
  }
}

// ===== 工具函数 =====

const formatRole = (role) => {
  const map = { admin: '管理员', analyst: '分析师', user: '普通用户' }
  return map[role] || role
}

const getRoleColor = (role) => {
  const map = { admin: 'avatar-red', analyst: 'avatar-purple', user: 'avatar-blue' }
  return map[role] || 'avatar-blue'
}

const formatTime = (time) => {
  if (!time) return '—'
  return new Date(time).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}

// 初始化
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-mgmt-container {
  padding: 32px 40px;
  background: #F5F5F7;
  min-height: 100vh;
  position: relative;
}

/* ===== 页面头部 ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.page-header h1 {
  font-size: 34px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.subtitle {
  font-size: 17px;
  color: #86868B;
  margin-top: 4px;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #0071E3;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.create-btn:hover {
  background: #0062CC;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
}

.btn-icon {
  font-size: 20px;
  font-weight: 300;
}

/* ===== 筛选栏 ===== */
.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.search-box {
  flex: 1;
  max-width: 360px;
  display: flex;
  align-items: center;
  background: white;
  border-radius: 12px;
  padding: 0 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.search-icon {
  font-size: 16px;
  margin-right: 8px;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  padding: 12px 0;
  font-size: 15px;
  background: transparent;
  color: #1D1D1F;
}

.filter-group select {
  padding: 12px 16px;
  border: 1px solid #D2D2D7;
  border-radius: 12px;
  background: white;
  font-size: 14px;
  color: #1D1D1F;
  cursor: pointer;
  outline: none;
}

/* ===== 用户表格 ===== */
.user-table {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.table-header {
  display: grid;
  grid-template-columns: 56px 100px 120px 1fr 100px 100px 140px 80px;
  padding: 16px 24px;
  background: #FAFAFA;
  font-size: 13px;
  font-weight: 600;
  color: #86868B;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row {
  display: grid;
  grid-template-columns: 56px 100px 120px 1fr 100px 100px 140px 80px;
  padding: 16px 24px;
  align-items: center;
  border-bottom: 1px solid #F2F2F7;
  transition: background 0.15s;
}

.table-row:last-child { border-bottom: none; }
.table-row:hover { background: #FAFBFC; }

/* 头像 */
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  color: white;
}

.avatar-blue { background: linear-gradient(135deg, #0071E3, #42a1ff); }
.avatar-red { background: linear-gradient(135deg, #FF3B30, #FF6B6B); }
.avatar-purple { background: linear-gradient(135deg, #AF52DE, #C77DFF); }

/* 角色标签 */
.role-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.role-admin { background: #FFEBEE; color: #D32F2F; }
.role-analyst { background: #F3E5F5; color: #7B1FA2; }
.role-user { background: #E3F2FD; color: #1565C0; }

/* 状态指示器 */
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.status-dot.active { background: #34C759; }
.status-dot.inactive { background: #FF3B30; }

.col-status {
  font-size: 14px;
  color: #1D1D1F;
}

.col-time {
  font-size: 13px;
  color: #86868B;
}

/* 操作按钮 */
.action-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: background 0.15s;
}

.action-btn:hover {
  background: #F2F2F7;
}

/* ===== 分页 ===== */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid #F2F2F7;
}

.page-info {
  font-size: 14px;
  color: #86868B;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #D2D2D7;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.page-btn:hover:not(:disabled) {
  background: #F2F2F7;
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-num {
  font-size: 14px;
  color: #1D1D1F;
  font-weight: 500;
}

/* ===== 弹窗 ===== */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 20px;
  padding: 32px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.dialog h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 20px;
}

.dialog-desc {
  font-size: 15px;
  color: #86868B;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #86868B;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #D2D2D7;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #0071E3;
}

.dialog-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 10px 24px;
  border: 1px solid #D2D2D7;
  background: white;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.15s;
}

.cancel-btn:hover {
  background: #F5F5F7;
}

.confirm-btn {
  padding: 10px 24px;
  background: #0071E3;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover {
  background: #0062CC;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== 加载和空状态 ===== */
.loading-state, .empty-state {
  padding: 80px 40px;
  text-align: center;
  color: #86868B;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E5E5EA;
  border-top-color: #0071E3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== Toast 提示 ===== */
.toast {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  padding: 14px 28px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  z-index: 2000;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.toast.success {
  background: #1D1D1F;
  color: white;
}

.toast.error {
  background: #FF3B30;
  color: white;
}

.toast-enter-active { animation: toastIn 0.3s ease; }
.toast-leave-active { animation: toastOut 0.3s ease; }

@keyframes toastIn {
  from { opacity: 0; transform: translate(-50%, 20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

@keyframes toastOut {
  from { opacity: 1; transform: translate(-50%, 0); }
  to { opacity: 0; transform: translate(-50%, 20px); }
}
</style>

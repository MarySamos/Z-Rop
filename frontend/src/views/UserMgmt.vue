<template>
  <div class="page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">系统管理 / 用户权限</p>
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">配置系统访问级别与成员权限</p>
      </div>
      <div class="header-actions">
        <button class="btn-refresh" @click="loadUsers" :disabled="loading">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" fill="currentColor"/></svg>
          同步列表
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <section class="stats-grid">
      <div v-for="(stat, i) in statItems" :key="i" class="stat-card animate-in" :style="{ animationDelay: `${i * 0.1}s` }">
        <span class="stat-label">{{ stat.label }}</span>
        <span class="stat-value">{{ stat.value }}</span>
      </div>
    </section>

    <!-- 用户表格 -->
    <section class="table-section animate-in">
      <div class="table-container">
        <el-table :data="users" v-loading="loading" class="warm-table">
          <el-table-column prop="id" label="ID" width="70" align="center" />
          <el-table-column prop="employee_id" label="工号" width="140">
            <template #default="{ row }">
              <span class="id-text">{{ row.employee_id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="姓名" width="150" />
          <el-table-column prop="department" label="部门">
            <template #default="{ row }">
              <span class="dept-tag">{{ row.department || '未分配' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="role" label="角色" width="130">
            <template #default="{ row }">
              <span :class="['role-chip', `role-${row.role || 'user'}`]">
                {{ getRoleName(row.role) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.is_active"
                @change="toggleStatus(row)"
                active-color="#B08D6F"
                inactive-color="#EFEBE5"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="加入时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="管理" width="100" align="center" fixed="right">
            <template #default="{ row }">
              <button class="btn-delete" @click="deleteUser(row)" title="下线用户">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" /></svg>
              </button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const loading = ref(false)
const users = ref([])

const statItems = computed(() => {
  const total = users.value.length
  const active = users.value.filter(u => u.is_active).length
  const admins = users.value.filter(u => u.role === 'admin').length
  const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  const newThisWeek = users.value.filter(u => new Date(u.created_at) > oneWeekAgo).length
  return [
    { label: '用户总数', value: total },
    { label: '活跃成员', value: active },
    { label: '高级管理', value: admins },
    { label: '近期新增', value: newThisWeek }
  ]
})

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/v1/admin/users')
    users.value = Array.isArray(res.data.users) ? res.data.users : (Array.isArray(res.data) ? res.data : [])
  } catch (e) {
    ElMessage.error('无法同步用户列表')
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (user) => {
  try {
    await api.put(`/api/v1/admin/users/${user.id}/status`, { is_active: user.is_active })
    ElMessage({ message: user.is_active ? '用户已接入' : '用户已脱离', type: 'success', customClass: 'warm-msg' })
  } catch (e) {
    ElMessage.error('操作中断，请重试')
    user.is_active = !user.is_active
  }
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要将用户 "${user.name}" 置为非活动状态并清除记录吗？`,
      '权限变更确认',
      { confirmButtonText: '确定核销', cancelButtonText: '取消', type: 'warning' }
    )
    await api.delete(`/api/v1/admin/users/${user.id}`)
    ElMessage.success('操作成功完成')
    loadUsers()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('权限核销失败')
  }
}

const getRoleName = (role) => {
  const names = { admin: '首席管理', analyst: '高级分析', user: '标准成员' }
  return names[role] || role
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => loadUsers())
</script>

<style scoped>
.page { padding: 40px; background: #FDFBF7; min-height: 100vh; color: #2C2420; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 48px; }
.page-breadcrumb { font-size: 11px; font-weight: 700; color: #B08D6F; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; }
.page-title { font-size: 2.5rem; font-weight: 700; font-family: 'Playfair Display', serif; margin: 0; }
.page-subtitle { font-size: 14px; color: #8C827D; margin-top: 4px; }

.btn-refresh { padding: 10px 24px; background: #B08D6F; color: #fff; border: none; border-radius: 24px; font-weight: 600; font-size: 13px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s; box-shadow: 0 4px 12px rgba(176,141,111,0.2); }
.btn-refresh:hover { background: #96765A; transform: translateY(-1px); }

/* 统计区域 */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 48px; }
.stat-card { background: #fff; border: 1px solid #EFEBE5; border-radius: 20px; padding: 28px; text-align: center; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(44, 36, 32, 0.05); border-color: #B08D6F; }

.stat-label { display: block; font-size: 11px; font-weight: 700; color: #8C827D; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; }
.stat-value { font-size: 2rem; font-weight: 700; font-family: 'Playfair Display', serif; color: #2C2420; }

/* 表格区域 */
.table-section { background: #fff; border-radius: 24px; padding: 32px; border: 1px solid #EFEBE5; box-shadow: 0 2px 12px rgba(44, 36, 32, 0.02); }
.table-container { width: 100%; }

.id-text { font-family: monospace; color: #B08D6F; font-weight: 600; }
.dept-tag { padding: 4px 12px; background: #F5F2ED; border-radius: 12px; font-size: 13px; color: #5C524D; font-weight: 500; }

.role-chip { display: inline-block; padding: 4px 14px; border-radius: 14px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.role-admin { background: #FFF4F4; color: #E57373; border: 1px solid #FFEBEB; }
.role-analyst { background: #FFF9F2; color: #B08D6F; border: 1px solid #FDF3E9; }
.role-user { background: #F5F2ED; color: #8C827D; }

.btn-delete { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: transparent; border: none; color: #BDB1A8; border-radius: 50%; cursor: pointer; transition: all 0.2s; }
.btn-delete:hover { color: #E57373; background: #FFF4F4; }

/* Element Plus 覆盖 */
:deep(.warm-table) { background: transparent; --el-table-header-bg-color: #FDFBF7; --el-table-row-hover-bg-color: #FDFBF7; }
:deep(.warm-table th.el-table__cell) { padding: 16px 0; color: #8C827D; border-bottom: 2px solid #F5F2ED; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
:deep(.warm-table td.el-table__cell) { padding: 18px 0; border-bottom: 1px solid #F5F2ED; color: #2C2420; font-size: 14px; }
:deep(.warm-table .el-table__inner-wrapper::before) { display: none; }

@media (max-width: 1200px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .stats-grid { grid-template-columns: 1fr; } .page-header { flex-direction: column; gap: 24px; } }
</style>

<template>
  <div class="admin-dashboard">
    <!-- 页面头部 -->
    <header class="page-header">
      <h1>系统概览</h1>
      <p class="subtitle">实时监控系统状态与用户活动</p>
    </header>

    <!-- KPI 卡片 -->
    <section class="kpi-section">
      <div class="kpi-card">
        <div class="kpi-icon blue">
          <svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" fill="currentColor"/></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ dashData.user_stats.total_users }}</span>
          <span class="kpi-label">总用户数</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon green">
          <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ dashData.user_stats.active_users }}</span>
          <span class="kpi-label">活跃用户</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon orange">
          <svg viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z" fill="currentColor"/></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ dashData.today_logins }}</span>
          <span class="kpi-label">今日登录</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon purple">
          <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="currentColor"/></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ formatNumber(dashData.total_operations) }}</span>
          <span class="kpi-label">操作总数 (30天)</span>
        </div>
      </div>
    </section>

    <!-- 图表区域 -->
    <section class="charts-row">
      <!-- 操作趋势图 -->
      <div class="chart-card">
        <h3>最近 7 天操作趋势</h3>
        <div ref="activityChartRef" class="chart-area"></div>
      </div>

      <!-- 角色分布图 -->
      <div class="chart-card">
        <h3>用户角色分布</h3>
        <div ref="roleChartRef" class="chart-area"></div>
      </div>
    </section>

    <!-- 最近操作日志 -->
    <section class="recent-section">
      <div class="section-card">
        <div class="section-header">
          <h3>最近操作日志</h3>
          <router-link to="/logs" class="view-all">查看全部 →</router-link>
        </div>
        <div v-if="dashData.recent_logs.length === 0" class="empty-logs">
          <p>暂无操作记录</p>
        </div>
        <div v-else class="log-list">
          <div class="log-item" v-for="(log, index) in dashData.recent_logs" :key="index">
            <div class="log-icon" :class="getActionClass(log.action)">
              {{ getActionIcon(log.action) }}
            </div>
            <div class="log-content">
              <div class="log-main">
                <span class="log-user">{{ log.user_name }}</span>
                <span class="log-action">{{ formatAction(log.action) }}</span>
              </div>
              <div class="log-details" v-if="log.details">{{ log.details }}</div>
            </div>
            <div class="log-time">{{ formatTime(log.created_at) }}</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

// 图表引用
const activityChartRef = ref(null)
const roleChartRef = ref(null)

// Dashboard 数据
const dashData = reactive({
  user_stats: {
    total_users: 0,
    active_users: 0,
    admin_count: 0,
    analyst_count: 0,
    user_count: 0
  },
  today_logins: 0,
  total_operations: 0,
  daily_activity: [],
  role_distribution: {},
  recent_logs: []
})

// 数字格式化
const formatNumber = (num) => {
  return num?.toLocaleString() || '0'
}

// ===== 图表初始化 =====

const initActivityChart = (data) => {
  if (!activityChartRef.value) return
  const chart = echarts.init(activityChartRef.value)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#E5E5EA',
      textStyle: { color: '#1D1D1F' }
    },
    grid: { top: 20, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
      axisLine: { lineStyle: { color: '#E5E5EA' } },
      axisLabel: { color: '#86868B' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F2F2F7' } },
      axisLabel: { color: '#86868B' }
    },
    series: [{
      data: data.map(d => d.count),
      type: 'line',
      smooth: true,
      lineStyle: { color: '#0071E3', width: 3 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 113, 227, 0.2)' },
          { offset: 1, color: 'rgba(0, 113, 227, 0.02)' }
        ])
      },
      itemStyle: { color: '#0071E3' },
      symbol: 'circle',
      symbolSize: 8
    }]
  })
}

const initRoleChart = (distribution) => {
  if (!roleChartRef.value) return
  const chart = echarts.init(roleChartRef.value)

  const roleColors = {
    '管理员': '#FF3B30',
    '分析师': '#AF52DE',
    '普通用户': '#0071E3'
  }

  const data = Object.entries(distribution).map(([name, value]) => ({
    name,
    value,
    itemStyle: { color: roleColors[name] || '#86868B' }
  }))

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 人 ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['45%', '72%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 3
      },
      label: {
        show: true,
        formatter: '{b}\n{c} 人',
        fontSize: 13,
        color: '#1D1D1F'
      },
      labelLine: { length: 12, length2: 16 },
      data: data
    }]
  })
}

// ===== 日志格式化 =====

const formatAction = (action) => {
  const map = {
    login: '登录系统',
    logout: '退出系统',
    query: 'AI 对话',
    upload: '上传数据',
    export: '导出数据',
    predict: '营销预测',
    analysis: '数据分析',
    admin_create_user: '创建用户',
    admin_change_role: '修改角色',
    admin_change_status: '修改状态'
  }
  return map[action] || action
}

const getActionIcon = (action) => {
  const map = {
    login: '🔑', logout: '🚪', query: '💬',
    upload: '📤', export: '📥', predict: '🎯',
    analysis: '📊', admin_create_user: '👤',
    admin_change_role: '🎭', admin_change_status: '🔄'
  }
  return map[action] || '📝'
}

const getActionClass = (action) => {
  const map = {
    login: 'green', logout: 'gray', query: 'blue',
    upload: 'purple', export: 'orange', predict: 'pink',
    analysis: 'teal', admin_create_user: 'blue',
    admin_change_role: 'purple', admin_change_status: 'orange'
  }
  return map[action] || ''
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

// ===== 数据加载 =====

onMounted(async () => {
  try {
    const res = await axios.get('/api/v1/admin/dashboard')
    Object.assign(dashData, res.data)

    // 等待 DOM 更新后初始化图表
    await nextTick()
    initActivityChart(dashData.daily_activity)
    initRoleChart(dashData.role_distribution)
  } catch (error) {
    console.error('加载管理员 Dashboard 失败:', error)
  }
})
</script>

<style scoped>
.admin-dashboard {
  padding: 32px 40px;
  background: #F5F5F7;
  min-height: 100vh;
  overflow-y: auto;
}

/* ===== 页面头部 ===== */
.page-header {
  margin-bottom: 32px;
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

/* ===== KPI 卡片 ===== */
.kpi-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon svg { width: 24px; height: 24px; }

.kpi-icon.blue { background: #E3F2FD; color: #0071E3; }
.kpi-icon.green { background: #E8F5E9; color: #34C759; }
.kpi-icon.orange { background: #FFF3E0; color: #FF9500; }
.kpi-icon.purple { background: #F3E5F5; color: #AF52DE; }

.kpi-content {
  display: flex;
  flex-direction: column;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1D1D1F;
}

.kpi-label {
  font-size: 14px;
  color: #86868B;
}

/* ===== 图表区域 ===== */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.chart-card h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1D1D1F;
  margin: 0 0 16px;
}

.chart-area {
  height: 280px;
}

/* ===== 最近日志 ===== */
.recent-section {
  margin-top: 20px;
}

.section-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 0;
}

.section-header h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1D1D1F;
  margin: 0;
}

.view-all {
  font-size: 14px;
  color: #0071E3;
  text-decoration: none;
  font-weight: 500;
}

.view-all:hover {
  text-decoration: underline;
}

.empty-logs {
  padding: 40px;
  text-align: center;
  color: #86868B;
}

.log-list {
  padding: 16px 0;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 24px;
  transition: background 0.15s;
}

.log-item:hover {
  background: #FAFBFC;
}

.log-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: #F5F5F7;
  flex-shrink: 0;
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
  min-width: 0;
}

.log-main {
  font-size: 14px;
  color: #1D1D1F;
}

.log-user {
  font-weight: 600;
  margin-right: 6px;
}

.log-action {
  color: #86868B;
}

.log-details {
  font-size: 13px;
  color: #86868B;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.log-time {
  font-size: 13px;
  color: #86868B;
  white-space: nowrap;
  flex-shrink: 0;
}
</style>

<template>
  <div class="dashboard-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">数据概览</h1>
        <p class="page-subtitle">实时监控核心业务指标</p>
      </div>
      <el-button type="primary" @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="(stat, index) in stats" :key="index">
        <div class="stat-icon" :class="stat.colorClass">
          <el-icon :size="24">
            <component :is="stat.icon" />
          </el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-change" :class="stat.trendClass">
            <el-icon :size="12">
              <component :is="stat.trendIcon" />
            </el-icon>
            {{ stat.change }}
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-card">
        <div class="card-header">
          <h3>数据概览</h3>
          <p>系统正常运行中</p>
        </div>
        <div class="chart-placeholder">
          <el-empty description="图表数据加载中..." />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, CaretTop, CaretBottom, User, Money, Phone } from '@element-plus/icons-vue'

// 统计数据
const stats = reactive([
  {
    label: '客户总数',
    value: '41,188',
    icon: User,
    colorClass: 'rose',
    trendIcon: CaretTop,
    trendClass: 'up',
    change: '+12.5%'
  },
  {
    label: '转化率',
    value: '11.7%',
    icon: Money,
    colorClass: 'green',
    trendIcon: CaretTop,
    trendClass: 'up',
    change: '+3.2%'
  },
  {
    label: '平均余额',
    value: '€1,428',
    icon: Money,
    colorClass: 'orange',
    trendIcon: CaretBottom,
    trendClass: 'down',
    change: '-2.1%'
  },
  {
    label: '平均通话',
    value: '2.8次',
    icon: Phone,
    colorClass: 'orange',
    trendIcon: CaretTop,
    trendClass: 'up',
    change: '+8.7%'
  }
])

const refreshData = () => {
  ElMessage.success('数据已刷新')
}
</script>

<style scoped>
.dashboard-page {
  padding: 0;
}

/* ========== 页面标题 ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #333333;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #999999;
  margin: 0;
}

/* ========== 统计卡片 ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue { background: linear-gradient(135deg, #ffe5e8 0%, #ffcdd2 100%); color: #ff6b81; }
.stat-icon.green { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); color: #388e3c; }
.stat-icon.purple { background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); color: #faad14; }
.stat-icon.orange { background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); color: #f57c00; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #333333;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #999999;
  margin-top: 2px;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  margin-top: 6px;
}

.stat-change.up { color: #67c23a; }
.stat-change.down { color: #ff6b81; }

/* ========== 图表区域 ========== */
.charts-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.chart-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #f0f0f0;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333333;
  margin: 0 0 4px 0;
}

.card-header p {
  font-size: 13px;
  color: #999999;
  margin: 0;
}

.chart-placeholder {
  padding: 40px 0;
  display: flex;
  justify-content: center;
}

/* ========== 响应式 ========== */
@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>

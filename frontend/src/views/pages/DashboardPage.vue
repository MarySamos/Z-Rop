<template>
  <div class="page">
    <header class="page-header">
      <div>
        <p class="page-breadcrumb">数据概览</p>
        <h1 class="page-title">数据仪表盘</h1>
        <p class="page-subtitle">银行营销数据实时资产分析</p>
      </div>
      <div class="header-actions">
        <div class="alert-pill animate-in">
          <span class="dot"></span> 3条未处理风险预警
        </div>
        <button class="btn-refresh" @click="loadData" :disabled="loading">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" fill="currentColor"/></svg>
          同步数据
        </button>
      </div>
    </header>

    <!-- 增强版统计卡片 -->
    <section class="stats-grid">
      <div v-for="(item, i) in kpiList" :key="i" class="stat-card-enhanced animate-in" :style="{ animationDelay: `${i * 0.1}s` }">
        <div class="stat-main">
          <span class="stat-label">{{ item.label }}</span>
          <div class="stat-value-group">
            <span class="stat-value">{{ item.value }}</span>
            <span :class="['stat-trend', item.trend > 0 ? 'up' : 'down']">
              {{ item.trend > 0 ? '↑' : '↓' }} {{ Math.abs(item.trend) }}%
            </span>
          </div>
        </div>
        <div class="stat-mini-chart">
          <div :ref="el => setMiniChartRef(el, i)" class="mini-canvas"></div>
        </div>
      </div>
    </section>

    <!-- 主布局：图表 + 活动流 -->
    <div class="dashboard-layout">
      <!-- 左侧：主要分析图表 -->
      <div class="analysis-main">
        <div class="charts-grid-compact">
          <div class="chart-box animate-in">
            <div class="chart-header">
              <h3>客户画像分布</h3>
              <div class="chart-actions">
                <span class="tag">实时</span>
              </div>
            </div>
            <div class="chart-body">
              <div ref="jobChartRef" class="echarts-container"></div>
            </div>
          </div>
          <div class="chart-box animate-in">
            <div class="chart-header">
              <h3>婚姻与教育水平</h3>
              <div class="chart-actions">
                <span class="tag">全量</span>
              </div>
            </div>
            <div class="chart-body">
              <div ref="maritalChartRef" class="echarts-container"></div>
            </div>
          </div>
          <div class="chart-box animate-in">
            <div class="chart-header">
              <h3>营销成果转化趋势</h3>
              <div class="chart-actions">
                <span class="tag accent">趋势</span>
              </div>
            </div>
            <div class="chart-body">
              <div ref="outcomeChartRef" class="echarts-container-large"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：最近活动流 -->
      <aside class="activity-sidebar animate-in">
        <div class="sidebar-header">
            <h3>最近活动记录</h3>
            <span class="badge">今日 12</span>
        </div>
        <div class="activity-list">
          <div v-for="(act, idx) in activities" :key="idx" class="activity-item">
            <div class="activity-dot" :class="act.status"></div>
            <div class="activity-content">
              <p class="act-text">{{ act.text }}</p>
              <p class="act-time">{{ act.time }}</p>
            </div>
          </div>
        </div>
        <button class="btn-more">查看完整审计日志</button>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, nextTick } from 'vue'
import api from '../../api'
import * as echarts from 'echarts'

const loading = ref(false)
const stats = ref({})
const miniChartRefs = ref([])
const activities = ref([
  { text: '客户 ID 4322 完成了定期存款转化', time: '10 分钟前', status: 'success' },
  { text: '营销计划 "春季金融季" 已向 231 位客户推送', time: '25 分钟前', status: 'info' },
  { text: '检测到 5 位高风险资产变动客户', time: '1 小时前', status: 'warning' },
  { text: '系统同步了 1200 条新客户记录', time: '2 小时前', status: 'info' },
  { text: '客户 ID 2311 更新了风险偏好等级', time: '3 小时前', status: 'success' },
  { text: '营销活动 A12 数据分析报告已生成', time: '5 小时前', status: 'info' }
])

const kpiList = computed(() => [
  { label: '总客户数', value: stats.value.kpi?.total_customers ?? '-', trend: 12.5 },
  { label: '转化率', value: (stats.value.kpi?.conversion_rate ?? '-') + '%', trend: 3.2 },
  { label: '平均余额', value: '€' + (stats.value.kpi?.avg_balance ?? '-'), trend: -0.8 },
  { label: '营销频率', value: (stats.value.kpi?.avg_campaign ?? '-') + '次', trend: 0.5 }
])

const setMiniChartRef = (el, i) => { if (el) miniChartRefs.value[i] = el }

const jobChartRef = ref(null)
const maritalChartRef = ref(null)
const outcomeChartRef = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/dashboard/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  const colorPalette = ['#B08D6F', '#8A817C', '#C4A882', '#D4C5B2', '#A09284'];
  const textColor = '#8C827D';
  const gridColor = '#F5F2ED';

  const initChart = (refVal, option) => {
    if (refVal.value) {
      const chart = echarts.init(refVal.value)
      chart.setOption(option)
      window.addEventListener('resize', () => chart.resize())
      return chart
    }
  }

  // 渲染 Mini Charts (过去 7 天趋势)
  miniChartRefs.value.forEach((el, i) => {
    const chart = echarts.init(el)
    const data = [12, 14, 11, 15, 18, i % 2 === 0 ? 20 : 15, i % 2 === 0 ? 22 : 12];
    chart.setOption({
      backgroundColor: 'transparent',
      grid: { left: 0, right: 0, top: 0, bottom: 0 },
      xAxis: { type: 'category', show: false },
      yAxis: { type: 'value', show: false },
      series: [{
        type: 'line', smooth: true, data, symbol: 'none',
        lineStyle: { width: 2, color: '#B08D6F' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(176,141,111,0.3)' }, { offset: 1, color: 'transparent' }]) }
      }]
    })
  })

  initChart(jobChartRef, {
    tooltip: { trigger: 'item', backgroundColor: '#fff', borderColor: '#EFEBE5', borderWidth: 1, textStyle: { color: '#2C2420' } },
    color: colorPalette,
    series: [{
      type: 'pie', radius: ['45%', '70%'], itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: [{ value: 3480, name: '管理' }, { value: 2921, name: '教育' }, { value: 2678, name: '技术' }, { value: 1678, name: '其他' }]
    }]
  })

  initChart(maritalChartRef, {
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#EFEBE5', borderWidth: 1 },
    grid: { left: '8%', right: '8%', bottom: '15%', top: '15%' },
    xAxis: { type: 'category', data: ['已婚', '单身', '离异'], axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: textColor } },
    yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: gridColor } } },
    series: [{ type: 'bar', barWidth: 20, itemStyle: { borderRadius: 4, color: '#B08D6F' }, data: [120, 200, 150] }]
  })

  initChart(outcomeChartRef, {
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#EFEBE5' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: ['1月', '2月', '3月', '4月', '5月', '6月'], axisLine: { lineStyle: { color: gridColor } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: gridColor, type: 'dashed' } } },
    series: [{
      type: 'line', smooth: true, areaStyle: { color: 'rgba(176,141,111,0.1)' },
      lineStyle: { width: 3, color: '#B08D6F' }, itemStyle: { color: '#B08D6F' },
      data: [320, 532, 401, 734, 690, 830]
    }]
  })
}

onMounted(async () => {
  await loadData()
  await nextTick()
  renderCharts()
})
</script>

<style scoped>
.page { padding: 24px; background: #FDFBF7; min-height: 100vh; color: #2C2420; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; }
.page-breadcrumb { font-size: 11px; font-weight: 700; color: #B08D6F; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.page-title { font-size: 2.5rem; font-weight: 700; font-family: 'Playfair Display', serif; margin: 0; }
.page-subtitle { font-size: 14px; color: #8C827D; margin-top: 4px; }

.header-actions { display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
.alert-pill { background: #FFF4F4; color: #E57373; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 8px; border: 1px solid #FFEBEB; }
.alert-pill .dot { width: 6px; height: 6px; background: #E57373; border-radius: 50%; display: block; animation: pulse 2s infinite; }

.btn-refresh { padding: 10px 20px; background: #B08D6F; color: #fff; border: none; border-radius: 24px; font-weight: 600; font-size: 13px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s; box-shadow: 0 4px 12px rgba(176,141,111,0.2); }
.btn-refresh:hover { background: #96765A; transform: translateY(-1px); }

/* 增强统计卡片 */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 32px; }
.stat-card-enhanced { background: #fff; border: 1px solid #EFEBE5; border-radius: 20px; padding: 24px; display: flex; justify-content: space-between; align-items: center; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.stat-card-enhanced:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(44, 36, 32, 0.06); border-color: #B08D6F; }

.stat-label { font-size: 12px; font-weight: 700; color: #8C827D; text-transform: uppercase; margin-bottom: 8px; display: block; }
.stat-value { font-size: 2rem; font-weight: 700; font-family: 'Playfair Display', serif; }
.stat-trend { font-size: 12px; font-weight: 600; margin-left: 8px; }
.stat-trend.up { color: #34A853; }
.stat-trend.down { color: #EA4335; }

.stat-mini-chart { width: 80px; height: 40px; }
.mini-canvas { width: 100%; height: 100%; }

/* 仪表盘主布局 */
.dashboard-layout { display: grid; grid-template-columns: 1fr 300px; gap: 24px; }
.analysis-main { display: flex; flex-direction: column; }

.charts-grid-compact { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.chart-box { background: #fff; border: 1px solid #EFEBE5; border-radius: 20px; padding: 24px; }
.chart-box:nth-child(3) { grid-column: span 2; }

.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.chart-header h3 { font-size: 1rem; font-weight: 700; color: #2C2420; margin: 0; }
.tag { font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 12px; background: #F5F2ED; color: #8C827D; text-transform: uppercase; }
.tag.accent { background: #FFF9F2; color: #B08D6F; }

.echarts-container { height: 200px; }
.echarts-container-large { height: 260px; }

/* 侧边栏活动流 */
.activity-sidebar { background: #fff; border: 1px solid #EFEBE5; border-radius: 20px; padding: 24px; display: flex; flex-direction: column; }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.sidebar-header h3 { font-size: 1rem; font-weight: 700; margin: 0; }
.badge { font-size: 11px; background: #F5F2ED; padding: 4px 8px; border-radius: 6px; color: #8C827D; }

.activity-list { flex: 1; display: flex; flex-direction: column; gap: 20px; }
.activity-item { display: flex; gap: 12px; align-items: flex-start; }
.activity-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.activity-dot.success { background: #34A853; box-shadow: 0 0 0 4px rgba(52, 168, 83, 0.1); }
.activity-dot.info { background: #B08D6F; box-shadow: 0 0 0 4px rgba(176, 141, 111, 0.1); }
.activity-dot.warning { background: #FBBC04; box-shadow: 0 0 0 4px rgba(251, 188, 4, 0.1); }

.act-text { font-size: 13px; font-weight: 500; margin: 0; line-height: 1.4; }
.act-time { font-size: 11px; color: #BDB1A8; margin: 4px 0 0 0; }

.btn-more { margin-top: 24px; background: none; border: 1px solid #EFEBE5; padding: 10px; border-radius: 12px; font-size: 12px; color: #8C827D; cursor: pointer; transition: all 0.2s; }
.btn-more:hover { border-color: #B08D6F; color: #B08D6F; }

@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(229, 115, 115, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(229, 115, 115, 0); } 100% { box-shadow: 0 0 0 0 rgba(229, 115, 115, 0); } }

@media (max-width: 1400px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } .dashboard-layout { grid-template-columns: 1fr; } .activity-sidebar { margin-top: 24px; } }
@media (max-width: 768px) { .stats-grid { grid-template-columns: 1fr; } .charts-grid-compact { grid-template-columns: 1fr; } .chart-box:nth-child(3) { grid-column: span 1; } }
</style>

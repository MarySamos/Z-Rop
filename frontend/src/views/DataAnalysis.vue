<template>
  <div class="analysis-container">
    <!-- Header -->
    <header class="analysis-header">
      <div>
        <h1>数据深度分析</h1>
        <p class="subtitle">全面洞察：从描述性统计到客户智能画像</p>
      </div>
      <button class="download-btn" @click="downloadReport">
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" fill="currentColor"/></svg>
        下载 PDF 报告
      </button>
    </header>

    <!-- Tab Navigation -->
    <div class="tab-nav">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      
      <!-- 统计分析 Tab -->
      <div v-if="activeTab === 'statistics'" class="panel">
        <div class="panel-header">
          <h2>数据描述性统计</h2>
          <button class="action-btn" @click="loadStatistics" :disabled="loading">
            {{ loading ? '加载中...' : '刷新数据' }}
          </button>
        </div>
        
        <div class="stats-grid" v-if="statistics">
          <div class="stat-card" v-for="(stat, col) in statistics.statistics" :key="col">
            <h4>{{ col }}</h4>
            <div class="stat-row"><span>均值 (Mean)</span><strong>{{ stat.mean }}</strong></div>
            <div class="stat-row"><span>中位数 (Median)</span><strong>{{ stat.median }}</strong></div>
            <div class="stat-row"><span>标准差 (Std Dev)</span><strong>{{ stat.std }}</strong></div>
            <div class="stat-row"><span>范围 (Min~Max)</span><strong>{{ stat.min }} ~ {{ stat.max }}</strong></div>
            <div class="stat-row"><span>偏度 (Skewness)</span><strong>{{ stat.skewness }}</strong></div>
          </div>
        </div>
      </div>

      <!-- 数据质量 Tab -->
      <div v-if="activeTab === 'quality'" class="panel">
        <div class="panel-header">
          <h2>数据质量报告</h2>
          <button class="action-btn" @click="loadQuality" :disabled="loading">
            {{ loading ? '加载中...' : '刷新数据' }}
          </button>
        </div>
        
        <div class="quality-summary" v-if="quality">
          <div class="quality-card">
            <span class="quality-value">{{ quality.total_rows?.toLocaleString() }}</span>
            <span class="quality-label">总行数</span>
          </div>
          <div class="quality-card">
            <span class="quality-value">{{ quality.total_columns }}</span>
            <span class="quality-label">总列数</span>
          </div>
          <div class="quality-card">
            <span class="quality-value">{{ quality.completeness }}%</span>
            <span class="quality-label">数据完整性</span>
          </div>
          <div class="quality-card">
            <span class="quality-value">{{ Object.keys(quality.outliers_3sigma || {}).length }}</span>
            <span class="quality-label">含异常值列数</span>
          </div>
        </div>

        <div class="outliers-table" v-if="quality?.outliers_3sigma">
          <h3>异常值检测 (3σ法则)</h3>
          <table>
            <thead>
              <tr><th>列名</th><th>异常值数量</th><th>占比</th><th>正常范围</th></tr>
            </thead>
            <tbody>
              <tr v-for="(info, col) in quality.outliers_3sigma" :key="col">
                <td>{{ col }}</td>
                <td>{{ info.outlier_count }}</td>
                <td>{{ info.outlier_percentage }}%</td>
                <td>{{ info.lower_bound }} ~ {{ info.upper_bound }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 聚类分析 Tab -->
      <div v-if="activeTab === 'clustering'" class="panel">
        <div class="panel-header">
          <h2>客户群体画像 (K-Means)</h2>
          <div class="controls">
            <label>群体数量: </label>
            <select v-model="clusterCount">
              <option :value="null">自动推荐</option>
              <option v-for="n in 8" :key="n" :value="n + 1">{{ n + 1 }}</option>
            </select>
            <button class="action-btn primary" @click="runClustering" :disabled="loading">
              {{ loading ? '聚类分析中...' : '开始聚类' }}
            </button>
          </div>
        </div>

        <div class="clustering-results" v-if="clustering">
          <div class="cluster-meta">
            <span><strong>分类数:</strong> {{ clustering.n_clusters }}</span>
            <span><strong>轮廓系数 (Silhouette Score):</strong> {{ clustering.silhouette_score }}</span>
          </div>

          <div class="profiles-grid">
            <div 
              v-for="profile in clustering.cluster_profiles" 
              :key="profile.cluster_id"
              class="profile-card"
            >
              <div class="profile-header">
                <span class="cluster-id">群体 {{ profile.cluster_id }}</span>
                <span class="cluster-label">{{ profile.label }}</span>
              </div>
              <div class="profile-stats">
                <div class="profile-stat">
                  <span>群体规模</span>
                  <strong>{{ profile.size }} ({{ profile.percentage }}%)</strong>
                </div>
                <div class="profile-stat">
                  <span>转化率</span>
                  <strong>{{ profile.conversion_rate }}%</strong>
                </div>
                <div class="profile-stat" v-if="profile.dominant_job">
                  <span>主要职业</span>
                  <strong>{{ profile.dominant_job }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 特征工程 Tab -->
      <div v-if="activeTab === 'features'" class="panel">
        <div class="panel-header">
          <h2>特征重要性排序</h2>
          <button class="action-btn primary" @click="loadFeatures" :disabled="loading">
            {{ loading ? '加载中...' : '开始分析' }}
          </button>
        </div>

        <div class="feature-chart" v-if="features">
          <div class="feature-bar" v-for="f in features.features" :key="f.name">
            <span class="feature-name">{{ f.name }}</span>
            <div class="bar-container">
              <div class="bar-fill" :style="{ width: (f.importance * 100) + '%' }"></div>
            </div>
            <span class="feature-value">{{ (f.importance * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>

      <!-- 关联规则 Tab -->
      <div v-if="activeTab === 'association'" class="panel">
        <div class="panel-header">
          <h2>关联规则发现 (Apriori)</h2>
          <button class="action-btn primary" @click="loadAssociation" :disabled="loading">
            {{ loading ? '挖掘中...' : '运行 Apriori' }}
          </button>
        </div>

        <div v-if="association?.rules" class="rules-list">
          <div class="rule-card" v-for="(rule, idx) in association.rules" :key="idx">
            <div class="rule-content">
              <span class="antecedents">{{ rule.antecedents.join(' + ') }}</span>
              <span class="arrow">→</span>
              <span class="consequents">{{ rule.consequents.join(' + ') }}</span>
            </div>
            <div class="rule-metrics">
              <span>支持度: {{ (rule.support * 100).toFixed(1) }}%</span>
              <span>置信度: {{ (rule.confidence * 100).toFixed(1) }}%</span>
              <span class="lift">提升度: {{ rule.lift.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <div v-else-if="association?.error" class="error-msg">
          {{ association.error }}
        </div>
      </div>

      <!-- 相关性热力图 Tab -->
      <div v-if="activeTab === 'correlation'" class="panel">
        <div class="panel-header">
          <h2>相关性热力图</h2>
          <div class="controls">
            <select v-model="corrMethod" @change="loadCorrelation">
              <option value="pearson">Pearson</option>
              <option value="spearman">Spearman</option>
              <option value="kendall">Kendall</option>
            </select>
            <button class="action-btn primary" @click="loadCorrelation" :disabled="loading">
              {{ loading ? '加载中...' : '计算相关性' }}
            </button>
          </div>
        </div>
        <div ref="heatmapRef" class="chart-area-lg"></div>
        <div class="top-corr" v-if="correlation?.top_correlations">
          <h3>Top 10 相关性排序</h3>
          <div class="corr-item" v-for="(c, i) in correlation.top_correlations.slice(0, 10)" :key="i">
            <span class="corr-pair">{{ c.var1 }} ↔ {{ c.var2 }}</span>
            <div class="corr-bar-wrap">
              <div class="corr-bar" :style="{ width: Math.abs(c.correlation) * 100 + '%', background: c.correlation > 0 ? '#34C759' : '#FF3B30' }"></div>
            </div>
            <span class="corr-val" :style="{ color: c.correlation > 0 ? '#34C759' : '#FF3B30' }">{{ c.correlation }}</span>
          </div>
        </div>
      </div>

      <!-- PCA 降维可视化 Tab -->
      <div v-if="activeTab === 'pca'" class="panel">
        <div class="panel-header">
          <h2>PCA 降维分析</h2>
          <button class="action-btn primary" @click="loadPCA" :disabled="loading">
            {{ loading ? '计算中...' : '运行 PCA' }}
          </button>
        </div>
        <div v-if="pca" class="pca-info">
          <div class="quality-summary" style="margin-bottom:20px">
            <div class="quality-card" v-for="comp in pca.components" :key="comp.component">
              <span class="quality-value">{{ (comp.variance_ratio * 100).toFixed(1) }}%</span>
              <span class="quality-label">{{ comp.component }} 方差解释率</span>
            </div>
            <div class="quality-card">
              <span class="quality-value">{{ (pca.total_variance_explained * 100).toFixed(1) }}%</span>
              <span class="quality-label">总方差解释率</span>
            </div>
          </div>
        </div>
        <div ref="pcaChartRef" class="chart-area-lg"></div>
        <div v-if="pca?.components" class="loadings-section">
          <h3>主成分载荷</h3>
          <div class="loadings-grid">
            <div v-for="comp in pca.components" :key="comp.component" class="stat-card">
              <h4>{{ comp.component }}</h4>
              <div class="stat-row" v-for="(val, key) in comp.loadings" :key="key">
                <span>{{ key }}</span>
                <strong :style="{ color: Math.abs(val) > 0.3 ? '#0071E3' : '#86868B' }">{{ val }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 时间序列 Tab -->
      <div v-if="activeTab === 'timeseries'" class="panel">
        <div class="panel-header">
          <h2>时间序列趋势分析</h2>
          <button class="action-btn primary" @click="loadTimeSeries" :disabled="loading">
            {{ loading ? '加载中...' : '加载趋势' }}
          </button>
        </div>
        <div v-if="timeSeries?.summary" class="quality-summary" style="margin-bottom:20px">
          <div class="quality-card">
            <span class="quality-value">{{ timeSeries.summary.peak_month }}</span>
            <span class="quality-label">营销高峰月</span>
          </div>
          <div class="quality-card">
            <span class="quality-value">{{ timeSeries.summary.peak_count?.toLocaleString() }}</span>
            <span class="quality-label">高峰客户数</span>
          </div>
          <div class="quality-card">
            <span class="quality-value">{{ timeSeries.summary.best_conversion_month }}</span>
            <span class="quality-label">最佳转化月</span>
          </div>
          <div class="quality-card">
            <span class="quality-value">{{ timeSeries.summary.best_conversion_rate }}%</span>
            <span class="quality-label">最高转化率</span>
          </div>
        </div>
        <div ref="timeSeriesRef" class="chart-area-lg"></div>
        <div ref="conversionTrendRef" class="chart-area" style="margin-top:20px"></div>
      </div>

      <!-- 漏斗分析 Tab -->
      <div v-if="activeTab === 'funnel'" class="panel">
        <div class="panel-header">
          <h2>营销漏斗分析</h2>
          <button class="action-btn primary" @click="loadFunnel" :disabled="loading">
            {{ loading ? '加载中...' : '生成漏斗' }}
          </button>
        </div>
        <div v-if="funnel" class="funnel-container">
          <div class="funnel-summary quality-summary" style="margin-bottom:24px">
            <div class="quality-card">
              <span class="quality-value">{{ funnel.total_customers?.toLocaleString() }}</span>
              <span class="quality-label">总客户数</span>
            </div>
            <div class="quality-card">
              <span class="quality-value">{{ funnel.total_converted?.toLocaleString() }}</span>
              <span class="quality-label">转化客户</span>
            </div>
            <div class="quality-card">
              <span class="quality-value">{{ funnel.overall_conversion_rate }}%</span>
              <span class="quality-label">总转化率</span>
            </div>
          </div>
          <div class="funnel-stages">
            <div class="funnel-stage" v-for="(stage, idx) in funnel.stages" :key="idx">
              <div class="stage-bar-wrap">
                <div class="stage-bar" :style="{ width: stage.rate + '%', background: funnelColors[idx] }"></div>
              </div>
              <div class="stage-info">
                <span class="stage-name">{{ stage.name }}</span>
                <span class="stage-count">{{ stage.count?.toLocaleString() }} 人</span>
                <span class="stage-rate">{{ stage.rate }}%</span>
              </div>
              <div v-if="idx > 0" class="drop-badge">流失 {{ stage.drop_rate }}%</div>
            </div>
          </div>
          <div class="comparison-section" v-if="funnel.comparison">
            <h3>转化 vs 未转化客户对比</h3>
            <div class="comparison-grid">
              <div class="compare-card" v-for="(val, key) in funnel.comparison" :key="key">
                <h4>{{ formatCompareKey(key) }}</h4>
                <div class="compare-row">
                  <span class="compare-label converted">✅ 已转化</span>
                  <strong>{{ val.converted }}</strong>
                </div>
                <div class="compare-row">
                  <span class="compare-label">❌ 未转化</span>
                  <strong>{{ val.not_converted }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const tabs = [
  { id: 'statistics', name: '描述性统计' },
  { id: 'quality', name: '数据质量' },
  { id: 'correlation', name: '相关性热力图' },
  { id: 'pca', name: 'PCA 降维' },
  { id: 'clustering', name: '客户画像(聚类)' },
  { id: 'features', name: '特征重要性' },
  { id: 'association', name: '关联规则' },
  { id: 'timeseries', name: '时间趋势' },
  { id: 'funnel', name: '营销漏斗' }
]

const activeTab = ref('statistics')
const loading = ref(false)

// 数据状态
const statistics = ref(null)
const quality = ref(null)
const clustering = ref(null)
const clusterCount = ref(null)
const features = ref(null)
const association = ref(null)
const correlation = ref(null)
const corrMethod = ref('pearson')
const pca = ref(null)
const timeSeries = ref(null)
const funnel = ref(null)

// 图表引用
const heatmapRef = ref(null)
const pcaChartRef = ref(null)
const timeSeriesRef = ref(null)
const conversionTrendRef = ref(null)

// 漏斗配色
const funnelColors = ['#0071E3', '#34C759', '#FF9500', '#AF52DE', '#FF3B30']

// ===== 原有功能 =====

const loadStatistics = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/analysis/statistics')
    statistics.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadQuality = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/analysis/quality')
    quality.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const runClustering = async () => {
  loading.value = true
  try {
    const res = await axios.post('/api/v1/analysis/clustering', {
      n_clusters: clusterCount.value,
      max_k: 10
    })
    clustering.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadFeatures = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/analysis/feature-importance')
    features.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadAssociation = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/analysis/association?min_support=0.05&min_confidence=0.3')
    association.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const downloadReport = () => {
  window.open('/api/v1/analysis/report/pdf', '_blank')
}

// ===== 新增：相关性热力图 =====

const loadCorrelation = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/v1/analysis/correlation?method=${corrMethod.value}`)
    correlation.value = res.data
    await nextTick()
    renderHeatmap(res.data)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const renderHeatmap = (data) => {
  if (!heatmapRef.value) return
  const chart = echarts.init(heatmapRef.value)
  const columns = data.columns
  chart.setOption({
    tooltip: {
      formatter: (p) => `${columns[p.value[0]]} ↔ ${columns[p.value[1]]}<br/>相关系数: <b>${p.value[2]}</b>`
    },
    grid: { top: 10, right: 80, bottom: 80, left: 100 },
    xAxis: { type: 'category', data: columns, axisLabel: { rotate: 45, fontSize: 11 } },
    yAxis: { type: 'category', data: columns, axisLabel: { fontSize: 11 } },
    visualMap: {
      min: -1, max: 1, calculable: true,
      orient: 'vertical', right: 10, top: 'center',
      inRange: { color: ['#FF3B30', '#FFF5F5', '#FFFFFF', '#E8F5E9', '#34C759'] }
    },
    series: [{
      type: 'heatmap',
      data: data.heatmap_data,
      label: { show: columns.length <= 8, fontSize: 10 },
      emphasis: { itemStyle: { borderColor: '#333', borderWidth: 1 } }
    }]
  })
}

// ===== 新增：PCA 降维 =====

const loadPCA = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/analysis/pca')
    pca.value = res.data
    await nextTick()
    renderPCA(res.data)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const renderPCA = (data) => {
  if (!pcaChartRef.value) return
  const chart = echarts.init(pcaChartRef.value)
  const yesData = data.scatter_data.filter(p => p.label === 'yes').map(p => [p.x, p.y])
  const noData = data.scatter_data.filter(p => p.label === 'no').map(p => [p.x, p.y])
  chart.setOption({
    tooltip: { formatter: (p) => `PC1: ${p.data[0]}<br/>PC2: ${p.data[1]}` },
    legend: { data: ['已转化 (yes)', '未转化 (no)'], top: 0 },
    grid: { top: 40, right: 20, bottom: 40, left: 50 },
    xAxis: { name: `PC1 (${(data.components[0]?.variance_ratio * 100).toFixed(1)}%)`, nameLocation: 'center', nameGap: 25 },
    yAxis: { name: `PC2 (${(data.components[1]?.variance_ratio * 100).toFixed(1)}%)`, nameLocation: 'center', nameGap: 35 },
    series: [
      { name: '已转化 (yes)', type: 'scatter', data: yesData, symbolSize: 6, itemStyle: { color: '#34C759', opacity: 0.6 } },
      { name: '未转化 (no)', type: 'scatter', data: noData, symbolSize: 4, itemStyle: { color: '#FF3B30', opacity: 0.3 } }
    ]
  })
}

// ===== 新增：时间序列 =====

const loadTimeSeries = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/analysis/time-series')
    timeSeries.value = res.data
    await nextTick()
    renderTimeSeries(res.data)
    renderConversionTrend(res.data)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const renderTimeSeries = (data) => {
  if (!timeSeriesRef.value) return
  const chart = echarts.init(timeSeriesRef.value)
  chart.setOption({
    title: { text: '月度客户数量与移动平均', textStyle: { fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'axis' },
    legend: { data: ['客户数', '3月移动平均'], top: 0, right: 0 },
    grid: { top: 40, right: 20, bottom: 30, left: 60 },
    xAxis: { type: 'category', data: data.months },
    yAxis: { type: 'value', name: '客户数' },
    series: [
      { name: '客户数', type: 'bar', data: data.customer_count.values, itemStyle: { color: '#0071E3', borderRadius: [6, 6, 0, 0] } },
      { name: '3月移动平均', type: 'line', data: data.customer_count.moving_avg, smooth: true, lineStyle: { color: '#FF9500', width: 3 }, itemStyle: { color: '#FF9500' } }
    ]
  })
}

const renderConversionTrend = (data) => {
  if (!conversionTrendRef.value) return
  const chart = echarts.init(conversionTrendRef.value)
  chart.setOption({
    title: { text: '月度转化率趋势', textStyle: { fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'axis', formatter: (p) => p.map(s => `${s.seriesName}: ${s.value}%`).join('<br/>') },
    legend: { data: ['转化率', '3月均线'], top: 0, right: 0 },
    grid: { top: 40, right: 20, bottom: 30, left: 60 },
    xAxis: { type: 'category', data: data.months },
    yAxis: { type: 'value', name: '转化率 (%)', axisLabel: { formatter: '{value}%' } },
    series: [
      { name: '转化率', type: 'line', data: data.conversion_rate.values, smooth: true, areaStyle: { color: 'rgba(52, 199, 89, 0.15)' }, lineStyle: { color: '#34C759', width: 3 }, itemStyle: { color: '#34C759' }, symbol: 'circle', symbolSize: 8 },
      { name: '3月均线', type: 'line', data: data.conversion_rate.moving_avg, smooth: true, lineStyle: { color: '#AF52DE', width: 2, type: 'dashed' }, itemStyle: { color: '#AF52DE' } }
    ]
  })
}

// ===== 新增：漏斗分析 =====

const loadFunnel = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/analysis/funnel')
    funnel.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const formatCompareKey = (key) => {
  const map = { avg_duration: '平均通话时长(秒)', avg_campaign: '平均联系次数', avg_balance: '平均账户余额' }
  return map[key] || key
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.analysis-container {
  padding: 32px 40px;
  background: #F5F5F7;
  min-height: 100vh;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.analysis-header h1 {
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

.download-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #FF9500, #FF6B00);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 149, 0, 0.3);
}

.tab-nav {
  display: flex;
  gap: 8px;
  margin: 24px 0;
  background: white;
  padding: 6px;
  border-radius: 12px;
  width: fit-content;
}

.tab-btn {
  padding: 10px 24px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #86868B;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #0071E3;
  color: white;
}

.panel {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.panel-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid #D2D2D7;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.action-btn.primary {
  background: #0071E3;
  color: white;
  border: none;
}

.controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.controls select {
  padding: 8px 12px;
  border: 1px solid #D2D2D7;
  border-radius: 8px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: #F5F5F7;
  padding: 16px;
  border-radius: 12px;
}

.stat-card h4 {
  margin: 0 0 12px;
  color: #0071E3;
  font-size: 14px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
  border-bottom: 1px solid #E5E5EA;
}

.stat-row span { color: #86868B; }
.stat-row strong { color: #1D1D1F; }

/* Quality Summary */
.quality-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.quality-card {
  background: #F5F5F7;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.quality-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1D1D1F;
}

.quality-label {
  font-size: 13px;
  color: #86868B;
}

.outliers-table table {
  width: 100%;
  border-collapse: collapse;
}

.outliers-table th, .outliers-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #E5E5EA;
}

.outliers-table th {
  background: #F5F5F7;
  font-weight: 600;
}

/* Clustering */
.cluster-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  font-size: 14px;
}

.profiles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.profile-card {
  background: #F5F5F7;
  border-radius: 12px;
  overflow: hidden;
}

.profile-header {
  background: linear-gradient(135deg, #0071E3, #42a1ff);
  color: white;
  padding: 16px;
}

.cluster-id {
  font-weight: 600;
  display: block;
}

.cluster-label {
  font-size: 13px;
  opacity: 0.9;
}

.profile-stats {
  padding: 16px;
}

.profile-stat {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  border-bottom: 1px solid #E5E5EA;
}

.profile-stat:last-child { border: none; }
.profile-stat span { color: #86868B; }
.profile-stat strong { color: #1D1D1F; }

/* Feature Importance */
.feature-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.feature-name {
  width: 100px;
  font-size: 14px;
  font-weight: 500;
  color: #1D1D1F;
}

.bar-container {
  flex: 1;
  height: 24px;
  background: #F5F5F7;
  border-radius: 12px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #0071E3, #34C759);
  border-radius: 12px;
  transition: width 0.5s ease;
}

.feature-value {
  width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #0071E3;
}

/* Association Rules */
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-card {
  background: #F5F5F7;
  padding: 16px;
  border-radius: 12px;
}

.rule-content {
  font-size: 15px;
  margin-bottom: 8px;
}

.antecedents {
  color: #0071E3;
  font-weight: 500;
}

.arrow {
  margin: 0 8px;
  color: #86868B;
}

.consequents {
  color: #34C759;
  font-weight: 600;
}

.rule-metrics {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #86868B;
}

.rule-metrics .lift {
  color: #FF9500;
  font-weight: 600;
}

.error-msg {
  padding: 20px;
  background: #FFF3CD;
  border-radius: 8px;
  color: #856404;
}

/* ===== 图表区域 ===== */
.chart-area-lg {
  height: 420px;
  margin-bottom: 20px;
}

.chart-area {
  height: 300px;
}

/* ===== 相关性热力图 ===== */
.top-corr {
  margin-top: 24px;
}

.top-corr h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
}

.corr-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #F2F2F7;
}

.corr-pair {
  width: 200px;
  font-size: 13px;
  font-weight: 500;
  color: #1D1D1F;
}

.corr-bar-wrap {
  flex: 1;
  height: 8px;
  background: #F2F2F7;
  border-radius: 4px;
  overflow: hidden;
}

.corr-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.corr-val {
  width: 60px;
  text-align: right;
  font-size: 14px;
  font-weight: 700;
}

/* ===== PCA ===== */
.loadings-section {
  margin-top: 24px;
}

.loadings-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
}

.loadings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

/* ===== 漏斗分析 ===== */
.funnel-stages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 32px;
}

.funnel-stage {
  position: relative;
}

.stage-bar-wrap {
  height: 48px;
  background: #F5F5F7;
  border-radius: 12px;
  overflow: hidden;
}

.stage-bar {
  height: 100%;
  border-radius: 12px;
  transition: width 0.8s ease;
  display: flex;
  align-items: center;
}

.stage-info {
  position: absolute;
  top: 0;
  left: 16px;
  right: 16px;
  height: 48px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stage-name {
  font-size: 14px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  min-width: 120px;
}

.stage-count {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255,255,255,0.9);
}

.stage-rate {
  font-size: 15px;
  font-weight: 700;
  color: white;
  margin-left: auto;
}

.drop-badge {
  position: absolute;
  right: -8px;
  top: -8px;
  background: #FF3B30;
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(255, 59, 48, 0.3);
}

.comparison-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.compare-card {
  background: #F5F5F7;
  padding: 16px;
  border-radius: 12px;
}

.compare-card h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #0071E3;
}

.compare-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
  border-bottom: 1px solid #E5E5EA;
}

.compare-row:last-child { border: none; }
.compare-label { color: #86868B; }
.compare-label.converted { color: #34C759; }
</style>

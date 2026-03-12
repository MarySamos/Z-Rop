<template>
  <div class="data-container">
    <!-- Header -->
    <header class="data-header">
      <div class="header-left">
        <h1>数据管理</h1>
        <p class="subtitle">查看并管理您的营销数据集</p>
      </div>
      <div class="header-actions">
        <label class="action-btn upload" for="file-input">
          <svg viewBox="0 0 24 24"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z" fill="currentColor"/></svg>
          上传 CSV
        </label>
        <input id="file-input" type="file" accept=".csv" @change="handleUpload" hidden />
        <button class="action-btn secondary" @click="refreshData">
          <svg viewBox="0 0 24 24"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/></svg>
          刷新
        </button>
        <button class="action-btn primary" @click="exportData">
          <svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" fill="currentColor"/></svg>
          导出 CSV
        </button>
      </div>
    </header>

    <!-- Table Info -->
    <div class="table-info" v-if="tableInfo">
      <span class="info-item">
        <strong>数据表:</strong> {{ tableInfo.name }}
      </span>
      <span class="info-item">
        <strong>行数:</strong> {{ formatNumber(tableInfo.row_count) }}
      </span>
      <span class="info-item">
        <strong>列数:</strong> {{ tableInfo.columns?.length }}
      </span>
    </div>

    <!-- Data Table -->
    <div class="table-wrapper">
      <table class="data-table" v-if="tableData.length > 0">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in tableData" :key="idx">
            <td v-for="col in columns" :key="col">{{ formatCell(row[col]) }}</td>
          </tr>
        </tbody>
      </table>
      
      <div v-else class="empty-state">
        <p>正在加载数据...</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
        ← 上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
      </span>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
        下一页 →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const tableInfo = ref(null)
const tableData = ref([])
const columns = ref([])
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 50

const formatNumber = (num) => num?.toLocaleString() || '0'

const formatCell = (val) => {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'string' && val.length > 30) return val.substring(0, 30) + '...'
  return val
}

const loadTableInfo = async () => {
  try {
    const response = await axios.get('/api/v1/data/tables')
    if (response.data.length > 0) {
      tableInfo.value = response.data[0]
    }
  } catch (error) {
    console.error('Failed to load table info:', error)
  }
}

const loadTableData = async (page = 1) => {
  try {
    const response = await axios.get('/api/v1/data/table/marketing_data', {
      params: { page, page_size: pageSize }
    })
    tableData.value = response.data.data
    columns.value = response.data.columns
    currentPage.value = response.data.page
    totalPages.value = response.data.total_pages
  } catch (error) {
    console.error('Failed to load table data:', error)
  }
}

const goToPage = (page) => {
  loadTableData(page)
}

const refreshData = () => {
  loadTableInfo()
  loadTableData(currentPage.value)
}

const exportData = () => {
  window.open('/api/v1/data/export/marketing_data', '_blank')
}

const handleUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await axios.post('/api/v1/data/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success(`上传成功！导入 ${res.data.rows_imported} 条数据`)
    refreshData()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '上传失败')
  }

  event.target.value = ''
}

onMounted(() => {
  loadTableInfo()
  loadTableData()
})
</script>

<style scoped>
.data-container {
  padding: 32px 40px;
  background: transparent;
  height: 100%;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.data-header h1 {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--apple-radius-sm);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--apple-transition-fast);
  border: none;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn.primary {
  background: #0071E3;
  color: white;
}

.action-btn.primary:hover {
  background: #0077ED;
}

.action-btn.secondary {
  background: var(--apple-bg-light);
  color: var(--apple-text-primary);
  border: 1px solid var(--apple-border);
}

.action-btn.secondary:hover {
  background: var(--apple-bg);
}

.action-btn.upload {
  background: linear-gradient(135deg, #34C759, #30D158);
  color: white;
  cursor: pointer;
}

.action-btn.upload:hover {
  transform: translateY(-1px);
}

.table-info {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--apple-bg-light);
  border-radius: var(--apple-radius-md);
  box-shadow: var(--apple-shadow-sm);
  font-size: 14px;
  color: var(--apple-text-primary);
}

.info-item strong {
  color: var(--apple-text-secondary);
  margin-right: 4px;
}

.table-wrapper {
  background: var(--apple-bg-light);
  border-radius: var(--apple-radius-xl);
  overflow: hidden;
  box-shadow: var(--apple-shadow-md);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  background: #F8F8F9;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--apple-text-secondary);
  border-bottom: 1px solid var(--apple-border);
  position: sticky;
  top: 0;
  text-transform: uppercase;
  font-size: 13px;
  letter-spacing: 0.5px;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--apple-border);
  color: var(--apple-text-primary);
}

.data-table tr:hover td {
  background: rgba(0,0,0,0.01);
}

.empty-state {
  padding: 60px;
  text-align: center;
  color: #86868B;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  margin-top: 24px;
}

.page-btn {
  padding: 10px 20px;
  background: white;
  border: 1px solid #D2D2D7;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #F5F5F7;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #86868B;
}
</style>

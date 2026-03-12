<template>
  <div class="predict-container">
    <header class="predict-header">
      <h1>客户转化预测</h1>
      <p class="subtitle">输入客户信息，AI 预测其购买理财产品的概率</p>
    </header>

    <div class="predict-content">
      <!-- 输入表单 -->
      <div class="form-card">
        <h3>客户基本信息</h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label>年龄 (Age)</label>
            <input v-model.number="form.age" type="number" min="18" max="100" />
          </div>
          
          <div class="form-group">
            <label>职业 (Job)</label>
            <select v-model="form.job">
              <option v-for="j in jobs" :key="j" :value="j">{{ j }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>婚姻状况 (Marital)</label>
            <select v-model="form.marital">
              <option value="single">单身 (Single)</option>
              <option value="married">已婚 (Married)</option>
              <option value="divorced">离异 (Divorced)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>教育程度 (Education)</label>
            <select v-model="form.education">
              <option value="primary">小学 (Primary)</option>
              <option value="secondary">中学 (Secondary)</option>
              <option value="tertiary">大学 (Tertiary)</option>
              <option value="unknown">未知 (Unknown)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>账户余额 (Balance) - ¥</label>
            <input v-model.number="form.balance" type="number" />
          </div>
          
          <div class="form-group">
            <label>是否有房贷 (Housing Loan)</label>
            <select v-model="form.housing">
              <option value="yes">是 (Yes)</option>
              <option value="no">否 (No)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>个人贷款 (Personal Loan)</label>
            <select v-model="form.loan">
              <option value="yes">是 (Yes)</option>
              <option value="no">否 (No)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>联系方式 (Contact)</label>
            <select v-model="form.contact">
              <option value="cellular">手机 (Cellular)</option>
              <option value="telephone">固话 (Telephone)</option>
              <option value="unknown">未知 (Unknown)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>通话时长 (秒)</label>
            <input v-model.number="form.duration" type="number" min="0" />
          </div>
          
          <div class="form-group">
            <label>营销触达次数</label>
            <input v-model.number="form.campaign" type="number" min="1" />
          </div>
        </div>

        <button class="predict-btn" @click="runPrediction" :disabled="loading">
          {{ loading ? '正在预测...' : '开始预测' }}
        </button>
      </div>

      <!-- 预测结果 -->
      <div class="result-card" v-if="result">
        <div class="result-header" :class="result.prediction === 1 ? 'positive' : 'negative'">
          <span class="result-label">{{ result.label }}</span>
          <span class="result-prob">{{ result.probability }}%</span>
        </div>
        
        <div class="result-body">
          <div class="result-meter">
            <div class="meter-fill" :style="{ width: result.probability + '%' }"></div>
          </div>
          
          <div class="result-confidence">
            <span>置信度: </span>
            <strong :class="'conf-' + result.confidence.toLowerCase()">{{ result.confidence }}</strong>
          </div>

          <div class="result-advice">
            <p v-if="result.probability > 50">
              ✅ 该客户有 <strong>较高意向</strong> 购买理财产品。建议优先跟进！
            </p>
            <p v-else>
              ⚠️ 该客户转化意向 <strong>较低</strong>，建议将资源投向更有潜力的客户。
            </p>
          </div>
        </div>
      </div>

      <!-- 特征重要性 -->
      <div class="importance-card" v-if="importance.length > 0">
        <h3>特征重要性因子</h3>
        <div class="importance-list">
          <div v-for="f in importance" :key="f.name" class="importance-item">
            <span class="imp-name">{{ f.name }}</span>
            <div class="imp-bar">
              <div class="imp-fill" :style="{ width: (f.importance * 100) + '%' }"></div>
            </div>
            <span class="imp-value">{{ (f.importance * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const jobs = ['admin', 'blue-collar', 'entrepreneur', 'housemaid', 'management', 'retired', 'self-employed', 'services', 'student', 'technician', 'unemployed', 'unknown']

const form = reactive({
  age: 35,
  job: 'management',
  marital: 'married',
  education: 'secondary',
  default_credit: 'no',
  balance: 1000,
  housing: 'yes',
  loan: 'no',
  contact: 'cellular',
  day: 15,
  month: 'may',
  duration: 300,
  campaign: 2,
  pdays: -1,
  previous: 0,
  poutcome: 'unknown'
})

const loading = ref(false)
const result = ref(null)
const importance = ref([])

const runPrediction = async () => {
  loading.value = true
  result.value = null
  
  try {
    const res = await axios.post('/api/v1/predict/single', form)
    result.value = res.data
    ElMessage.success('预测完成！')
  } catch (error) {
    ElMessage.error('预测失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadImportance = async () => {
  try {
    const res = await axios.get('/api/v1/predict/importance')
    importance.value = res.data
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadImportance()
})
</script>

<style scoped>
.predict-container {
  padding: 32px 40px;
  background: #F5F5F7;
  min-height: 100vh;
}

.predict-header h1 {
  font-size: 34px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.subtitle {
  color: #86868B;
  margin-top: 4px;
}

.predict-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 24px;
}

.form-card, .result-card, .importance-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.form-card h3, .importance-card h3 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #1D1D1F;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #86868B;
  margin-bottom: 6px;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #D2D2D7;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.predict-btn {
  width: 100%;
  margin-top: 24px;
  padding: 14px;
  background: linear-gradient(135deg, #0071E3, #42a1ff);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.predict-btn:hover { transform: translateY(-2px); }
.predict-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* Result Card */
.result-header {
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  color: white;
}

.result-header.positive { background: linear-gradient(135deg, #34C759, #30D158); }
.result-header.negative { background: linear-gradient(135deg, #FF3B30, #FF6961); }

.result-label { display: block; font-size: 24px; font-weight: 700; }
.result-prob { font-size: 48px; font-weight: 800; }

.result-body { padding: 20px 0; }

.result-meter {
  height: 12px;
  background: #E5E5EA;
  border-radius: 6px;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF3B30, #FFCC00, #34C759);
  border-radius: 6px;
  transition: width 0.5s ease;
}

.result-confidence {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
}

.conf-高 { color: #34C759; }
.conf-中 { color: #FFCC00; }
.conf-低 { color: #FF3B30; }

.result-advice {
  margin-top: 20px;
  padding: 16px;
  background: #F5F5F7;
  border-radius: 10px;
  font-size: 14px;
}

/* Importance */
.importance-card { grid-column: span 2; }

.importance-list { display: flex; flex-direction: column; gap: 12px; }

.importance-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.imp-name { width: 100px; font-size: 14px; color: #1D1D1F; }

.imp-bar {
  flex: 1;
  height: 20px;
  background: #E5E5EA;
  border-radius: 10px;
  overflow: hidden;
}

.imp-fill {
  height: 100%;
  background: linear-gradient(90deg, #0071E3, #34C759);
  border-radius: 10px;
}

.imp-value { width: 50px; font-size: 14px; font-weight: 600; color: #0071E3; }
</style>

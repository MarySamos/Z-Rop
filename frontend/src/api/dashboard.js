/**
 * Dashboard API
 * 数据仪表盘相关接口
 */
import axios from 'axios'

const BASE_URL = '/api/v1'

/**
 * 获取统计数据
 */
export const getStats = async () => {
  return axios.get(`${BASE_URL}/dashboard/stats`)
}

/**
 * 获取转化率数据
 */
export const getConversionRate = async (groupBy = null) => {
  return axios.get(`${BASE_URL}/dashboard/conversion`, {
    params: { group_by: groupBy }
  })
}

/**
 * 获取分布数据
 */
export const getDistribution = async (column = 'job') => {
  return axios.get(`${BASE_URL}/dashboard/distribution`, {
    params: { column }
  })
}

/**
 * 获取图表数据
 */
export const getChartData = async (type) => {
  return axios.get(`${BASE_URL}/dashboard/charts/${type}`)
}

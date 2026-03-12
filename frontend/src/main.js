import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/main.css'
import axios from 'axios'

// Axios 拦截器：自动携带 Token
axios.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => Promise.reject(error)
)

// Axios 响应拦截器：处理 401 未授权
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

const app = createApp(App)

app.use(router)
app.use(ElementPlus)
app.mount('#app')

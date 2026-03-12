import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import MainLayout from '../views/MainLayout.vue'
import Chat from '../views/Chat.vue'
import Dashboard from '../views/Dashboard.vue'
import DataMgmt from '../views/DataMgmt.vue'
import DataAnalysis from '../views/DataAnalysis.vue'
import Predict from '../views/Predict.vue'
import Logs from '../views/Logs.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
    },
    {
        path: '/',
        component: MainLayout,
        redirect: '/chat',
        meta: { requiresAuth: true },
        children: [
            {
                path: 'chat',
                name: 'Chat',
                component: Chat
            },
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: Dashboard
            },
            {
                path: 'data',
                name: 'Data',
                component: DataMgmt
            },
            {
                path: 'analysis',
                name: 'Analysis',
                component: DataAnalysis
            },
            {
                path: 'predict',
                name: 'Predict',
                component: Predict
            },
            {
                path: 'logs',
                name: 'Logs',
                component: Logs
            },
            // 管理员路由
            {
                path: 'admin/dashboard',
                name: 'AdminDashboard',
                component: () => import('../views/AdminDashboard.vue'),
                meta: { requiresAuth: true, requiresAdmin: true }
            },
            {
                path: 'admin/users',
                name: 'UserMgmt',
                component: () => import('../views/UserMgmt.vue'),
                meta: { requiresAuth: true, requiresAdmin: true }
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫：未登录用户重定向到登录页，非管理员不可访问管理页
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if ((to.path === '/login' || to.path === '/register') && token) {
        next('/chat')
    } else if (to.meta.requiresAdmin) {
        if (!token) {
            next('/login')
            return
        }
        // 检查管理员权限
        const storedUser = localStorage.getItem('user')
        if (storedUser) {
            try {
                const user = JSON.parse(storedUser)
                if (user.role !== 'admin') {
                    next('/chat')
                    return
                }
            } catch (e) {
                next('/login')
                return
            }
        } else {
            next('/login')
            return
        }
        next()
    } else {
        next()
    }
})

export default router

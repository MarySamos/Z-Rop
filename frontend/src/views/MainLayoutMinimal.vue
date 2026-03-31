<template>
  <div class="main-layout">
    <!-- 沉浸式主内容区 -->
    <main class="main-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="page-transition" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- 悬浮版 OS 级 Dock 导航 -->
    <nav class="floating-dock" @mouseleave="hideSubMenu">
      <div class="dock-container">
        <!-- 品牌标识 -->
        <div class="dock-brand">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="18" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
            <circle cx="20" cy="20" r="12" stroke="currentColor" stroke-width="1.5" opacity="0.6"/>
            <circle cx="20" cy="20" r="6" fill="currentColor" opacity="0.9"/>
          </svg>
        </div>

        <div class="dock-separator"></div>

        <!-- 主导航项 -->
        <div class="dock-items">
          <template v-for="item in navItems" :key="item.path">
            <div 
              class="dock-item-wrapper"
              @click.stop="toggleSubMenu(item)"
            >
              <router-link
                v-if="!item.children"
                :to="item.path"
                class="dock-item"
                :class="{ active: isActive(item.path) }"
              >
                <component :is="item.icon" class="dock-icon" />
                <span class="dock-tooltip">{{ item.label }}</span>
              </router-link>
              <div 
                v-else
                class="dock-item"
                :class="{ active: isActive(item.path) }"
              >
                <component :is="item.icon" class="dock-icon" />
                <span class="dock-tooltip">{{ item.label }}</span>
              </div>
            </div>
          </template>

          <template v-if="isAdmin">
            <div class="dock-separator"></div>
            <template v-for="item in adminNavItems" :key="item.path">
              <div 
                class="dock-item-wrapper"
                @click.stop="toggleSubMenu(item)"
              >
                <router-link
                  v-if="!item.children"
                  :to="item.path"
                  class="dock-item"
                  :class="{ active: isActive(item.path) }"
                >
                  <component :is="item.icon" class="dock-icon" />
                  <span class="dock-tooltip">{{ item.label }}</span>
                </router-link>
                <div 
                  v-else
                  class="dock-item"
                  :class="{ active: isActive(item.path) }"
                >
                  <component :is="item.icon" class="dock-icon" />
                  <span class="dock-tooltip">{{ item.label }}</span>
                </div>
              </div>
            </template>
          </template>
        </div>

        <div class="dock-separator"></div>

        <!-- 个人中心 & 登出 -->
        <div class="dock-user">
          <div class="user-avatar" :title="userName">{{ userName?.charAt(0) || 'U' }}</div>
          <button class="dock-item logout-btn" @click="handleLogout" title="退出登录">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12h-9"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 悬浮子菜单 -->
      <transition name="submenu-fade">
        <div 
          v-show="activeSubMenu" 
          class="dock-submenu" 
          :style="{ left: subMenuLeft + 'px' }"
          @mouseenter="clearSubmenuTimeout"
          @mouseleave="hideSubMenu"
        >
          <div class="submenu-title">{{ activeSubMenu?.label }}</div>
          <div class="submenu-items">
            <router-link
              v-for="child in activeSubMenu?.children || []"
              :key="child.path"
              :to="child.path"
              class="submenu-item"
              :class="{ active: isActive(child.path) }"
              @click="hideSubMenu"
            >
              {{ child.label }}
            </router-link>
          </div>
        </div>
      </transition>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ChatDotRound,
  DataAnalysis,
  Document,
  FolderOpened,
  TrendCharts,
  Histogram,
  Connection,
  Grid,
  Promotion,
  Setting,
  User,
  Notebook,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const userName = ref('')
const userRole = ref('')
const isAdmin = ref(false)

const activeSubMenu = ref(null)
const subMenuLeft = ref(0)
let submenuTimeout = null

const navItems = ref([
  {
    path: '/dashboard',
    label: '仪表盘',
    icon: TrendCharts,
  },
  {
    path: '/chat',
    label: '智能对话',
    icon: ChatDotRound,
  },
  {
    path: '/analysis',
    label: '数据分析',
    icon: DataAnalysis,
    children: [
      { path: '/analysis/statistics', label: '描述性统计' },
      { path: '/analysis/correlation', label: '相关性分析' },
      { path: '/analysis/clustering', label: '客户聚类' },
      { path: '/analysis/features', label: '特征重要性' },
      { path: '/analysis/association', label: '关联规则' },
      { path: '/analysis/pca', label: 'PCA 降维' },
      { path: '/analysis/timeseries', label: '时间趋势' },
      { path: '/analysis/funnel', label: '漏斗分析' },
    ]
  },
  {
    path: '/data',
    label: '数据管理',
    icon: FolderOpened,
    children: [
      { path: '/data/list', label: '数据列表' },
      { path: '/data/import', label: '数据导入' },
    ]
  },
  {
    path: '/knowledge',
    label: '知识库',
    icon: Document,
    children: [
      { path: '/knowledge/list', label: '文档列表' },
      { path: '/knowledge/upload', label: '上传文档' },
    ]
  },
  {
    path: '/predict',
    label: '智能预测',
    icon: TrendCharts,
  },
])

// 管理功能菜单
const adminNavItems = [
  {
    path: '/admin',
    label: '系统管理',
    icon: Setting,
    children: [
      { path: '/admin/users', label: '用户管理' },
      { path: '/logs', label: '操作日志' },
    ]
  }
]

const isActive = (path) => route.path === path || route.path.startsWith(path + '/')

const toggleSubMenu = (item) => {
  // 如果没有子菜单，且配置了路径，则可能是单路径图标，不需要展开子菜单（如果使用了 router-link 则由 router 处理）
  if (!item.children) {
    activeSubMenu.value = null
    // 如果是 div 包裹的（没有用 router-link），则手动跳转
    if (item.path && !isActive(item.path)) {
      router.push(item.path)
    }
    return
  }
  
  if (activeSubMenu.value?.path === item.path) {
    activeSubMenu.value = null
  } else {
    activeSubMenu.value = item
    // 计算位置：需要合并 navItems 和 adminNavItems 进行计算
    const allItems = [...navItems.value]
    if (isAdmin.value) {
      allItems.push(...adminNavItems)
    }
    const index = allItems.findIndex(i => i.path === item.path)
    // 基础偏移 80px (左侧品牌与分隔符) + 每个项 56px (48px+8px gap)
    subMenuLeft.value = 80 + index * 56
  }
}

// 全局点击关闭菜单
onMounted(() => {
  window.addEventListener('click', () => {
    activeSubMenu.value = null
  })
})

const hideSubMenu = () => {
  // 点击模式下不再通过延时自动关闭，除非主动调用
}

const clearSubmenuTimeout = () => {
  // 点击模式下废弃
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('userId')
  router.push('/login')
  ElMessage.success('已退出登录')
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    userName.value = user.name
    userRole.value = user.role === 'admin' ? '管理员' : user.role === 'analyst' ? '分析师' : '普通用户'
    isAdmin.value = user.role === 'admin'
  }
})
</script>

<style scoped>
/* ============================================================
   布局结构
   ============================================================ */

.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--surface-primary);
}

/* ============================================================
   主内容区
   ============================================================ */

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  /* 为底部 Dock 留出足够的空间 */
  padding: 40px 40px 120px 40px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

/* ============================================================
   浮动 Dock 导航栏（暖白纸感）
   ============================================================ */

.floating-dock {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.dock-container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-full);
  box-shadow: 0 8px 32px rgba(44, 36, 32, 0.12), 0 2px 8px rgba(44, 36, 32, 0.06);
  transition: all var(--transition-base);
}

.dock-container:hover {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 12px 40px rgba(44, 36, 32, 0.16), 0 4px 12px rgba(44, 36, 32, 0.08);
}

.dock-brand {
  width: 40px;
  height: 40px;
  color: var(--accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-right: 4px;
}

.dock-brand svg {
  width: 24px;
  height: 24px;
}

.dock-separator {
  width: 1px;
  height: 24px;
  background: var(--border-primary);
  margin: 0 4px;
}

.dock-items {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dock-item-wrapper {
  position: relative;
}

.dock-item {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: var(--text-secondary);
  cursor: pointer;
  background: transparent;
  border: none;
  transition: all var(--transition-bounce);
}

.dock-item:hover {
  color: var(--accent-primary);
  background: var(--surface-hover);
  transform: translateY(-4px) scale(1.1);
}

.dock-item.active {
  color: var(--text-inverse);
  background: var(--accent-primary);
  box-shadow: 0 4px 12px rgba(44, 36, 32, 0.2);
}

.dock-icon {
  width: 20px;
  height: 20px;
}

/* Tooltip */
.dock-tooltip {
  position: absolute;
  top: -45px;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: var(--surface-white);
  color: var(--text-primary);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all var(--transition-base);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-card);
}

.dock-item-wrapper:hover .dock-tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* 用户区 */
.dock-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 4px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface-secondary);
  border: 1px solid var(--border-primary);
  color: var(--accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
}

.logout-btn {
  color: var(--error);
}

.logout-btn:hover {
  background: var(--error-light);
  color: var(--error);
}

/* 悬浮子菜单 */
.dock-submenu {
  position: absolute;
  bottom: calc(100% + 4px); /* 贴近 Dock 主体防止滑动时断空 */
  background: var(--surface-white);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: 16px;
  padding-bottom: 24px; /* 内部增大底部空间作为 Hover Bridge */
  min-width: 180px;
  box-shadow: var(--shadow-card-hover);
  transform-origin: bottom center;
}

.submenu-title {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 12px;
  padding-left: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
}

.submenu-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.submenu-item {
  padding: 10px 16px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.submenu-item:hover {
  background: var(--surface-hover);
  color: var(--accent-primary);
}

.submenu-item.active {
  background: var(--accent-light);
  color: var(--accent-primary);
}

.submenu-fade-enter-active,
.submenu-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.submenu-fade-enter-from,
.submenu-fade-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

/* ============================================================
   页面切换动画
   ============================================================ */

.page-transition-enter-active,
.page-transition-leave-active {
  transition: all 0.4s cubic-bezier(0.2, 0, 0, 1);
}

.page-transition-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}

.page-transition-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.98);
}

/* ============================================================
   响应式
   ============================================================ */

@media (max-width: 768px) {
  .floating-dock {
    width: 90%;
    bottom: 16px;
  }
  
  .dock-container {
    width: 100%;
    flex-wrap: wrap;
    justify-content: center;
    border-radius: var(--radius-lg);
    padding: 12px;
  }
  
  .dock-separator {
    display: none;
  }
  
  .dock-item {
    width: 40px;
    height: 40px;
  }
  
  .dock-tooltip {
    display: none;
  }
  
  .content-wrapper {
    padding: 20px 20px 140px 20px;
  }
}
</style>

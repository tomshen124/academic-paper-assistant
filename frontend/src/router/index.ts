import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import BasicLayout from '@/layouts/BasicLayout.vue'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  // 认证相关路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: BasicLayout,
    redirect: '/topics/recommend',
    meta: { requiresAuth: true },
    children: [
      // 主题相关路由
      {
        path: '/topics',
        name: 'Topics',
        redirect: '/topics/recommend',
        meta: { title: '论文主题' },
        children: [
          {
            path: 'recommend',
            name: 'TopicRecommend',
            component: () => import('@/views/topics/TopicRecommend.vue'),
            meta: { title: '主题推荐' }
          },
          {
            path: 'analyze/:topic',
            name: 'TopicAnalyze',
            component: () => import('@/views/topics/TopicAnalyze.vue'),
            meta: { title: '主题分析' }
          },
          {
            path: 'refine/:topic',
            name: 'TopicRefine',
            component: () => import('@/views/topics/TopicRefine.vue'),
            meta: { title: '主题优化' }
          }
        ]
      },

      // 提纲相关路由
      {
        path: '/outlines',
        name: 'Outlines',
        redirect: '/outlines/generate',
        meta: { title: '论文提纲' },
        children: [
          {
            path: 'generate',
            name: 'OutlineGenerate',
            component: () => import('@/views/outlines/OutlineGenerate.vue'),
            meta: { title: '提纲生成' }
          },
          {
            path: 'optimize/:id',
            name: 'OutlineOptimize',
            component: () => import('@/views/outlines/OutlineOptimize.vue'),
            meta: { title: '提纲优化' }
          },
          {
            path: 'validate/:id',
            name: 'OutlineValidate',
            component: () => import('@/views/outlines/OutlineValidate.vue'),
            meta: { title: '提纲验证' }
          }
        ]
      },

      // 论文相关路由
      {
        path: '/papers',
        name: 'Papers',
        redirect: '/papers/generate',
        meta: { title: '论文生成' },
        children: [
          {
            path: 'generate',
            name: 'PaperGenerate',
            component: () => import('@/views/papers/PaperGenerate.vue'),
            meta: { title: '论文生成' }
          },
          {
            path: 'improve/:sectionId',
            name: 'PaperImprove',
            component: () => import('@/views/papers/PaperImprove.vue'),
            meta: { title: '论文改进' }
          }
        ]
      },

      // 引用相关路由
      {
        path: '/citations',
        name: 'Citations',
        redirect: '/citations/format',
        meta: { title: '引用管理' },
        children: [
          {
            path: 'format',
            name: 'CitationFormat',
            component: () => import('@/views/citations/CitationFormat.vue'),
            meta: { title: '引用格式化' }
          },
          {
            path: 'extract',
            name: 'CitationExtract',
            component: () => import('@/views/citations/CitationExtract.vue'),
            meta: { title: '引用提取' }
          },
          {
            path: 'bibliography',
            name: 'Bibliography',
            component: () => import('@/views/citations/Bibliography.vue'),
            meta: { title: '参考文献' }
          }
        ]
      },

      // 搜索相关路由
      {
        path: '/search',
        name: 'Search',
        redirect: '/search/literature',
        meta: { title: '学术搜索' },
        children: [
          {
            path: 'literature',
            name: 'LiteratureSearch',
            component: () => import('@/views/search/LiteratureSearch.vue'),
            meta: { title: '文献搜索' }
          },
          {
            path: 'paper/:id',
            name: 'PaperDetail',
            component: () => import('@/views/search/PaperDetail.vue'),
            meta: { title: '文献详情' }
          },
          {
            path: 'trends',
            name: 'ResearchTrends',
            component: () => import('@/views/search/ResearchTrends.vue'),
            meta: { title: '研究趋势' }
          }
        ]
      },

      // Token管理路由
      {
        path: '/tokens',
        name: 'Tokens',
        component: () => import('@/views/tokens/TokenUsage.vue'),
        meta: { title: 'Token管理' }
      },

      // 用户相关路由
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/auth/Profile.vue'),
        meta: { title: '个人信息' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/auth/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 配置NProgress
NProgress.configure({
  showSpinner: false,
  minimum: 0.1,
  easing: 'ease',
  speed: 500
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 开始加载进度条
  NProgress.start()

  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 学术论文辅助平台` : '学术论文辅助平台'

  // 检查是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  const authStore = useAuthStore()

  // 如果需要认证但没有登录，重定向到登录页
  if (requiresAuth && !authStore.isLoggedIn()) {
    ElMessage.warning('请先登录')
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

router.afterEach(() => {
  // 结束加载进度条
  NProgress.done()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  NProgress.done()
  ElMessage.error('页面加载失败，请重试')
})

export default router
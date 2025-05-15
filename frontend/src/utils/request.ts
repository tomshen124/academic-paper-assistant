import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { isTokenExpired, refreshTokenIfNeeded } from './tokenUtils'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 120000, // 增加超时时间到120秒，因为LLM请求可能需要较长时间
  withCredentials: true // 允许跨域请求携带凭证
})

// 请求拦截器
service.interceptors.request.use(
  async (config) => {
    // 添加token认证信息
    let token = localStorage.getItem('token')

    // 如果有token，检查是否需要刷新
    if (token) {
      // 排除刷新令牌的请求，避免无限循环
      if (config.url !== '/auth/refresh') {
        try {
          // 检查令牌是否即将过期
          if (isTokenExpired(token, 5)) { // 5分钟内过期则刷新
            console.log('令牌即将过期，尝试刷新')
            token = await refreshTokenIfNeeded(token)
          }
        } catch (error) {
          console.error('刷新令牌失败:', error)
          // 如果刷新失败，继续使用原令牌
        }
      }

      // 设置认证头
      if (config.headers) {
        config.headers['Authorization'] = `Bearer ${token}`
      }
    }

    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 打印成功响应的详细信息（仅在开发环境）
    if (import.meta.env.DEV) {
      console.log('请求成功:', {
        url: response.config.url,
        method: response.config.method,
        status: response.status,
        data: response.data
      })
    }
    return response
  },
  (error) => {
    // 打印错误详细信息
    console.error('响应错误:', error)
    console.error('错误详情:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data
    })

    // 处理401认证错误
    if (error.response?.status === 401) {
      // 如果是登录页面，不跳转
      if (window.location.pathname.includes('/login')) {
        return Promise.reject(error)
      }

      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      // 跳转到登录页
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // 处理其他错误
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('请求失败，请稍后再试')
    }

    return Promise.reject(error)
  }
)

// 封装请求方法
const request = <T = any>(config: AxiosRequestConfig): Promise<T> => {
  return service(config).then(res => res.data);
};

export { request }
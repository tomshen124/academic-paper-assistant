import { defineStore } from 'pinia';
import { ref } from 'vue';
import { login, getUserInfo, register } from '@/api/modules/auth';
import type { LoginRequest, UserInfo, RegisterRequest } from '@/api/modules/auth';
import { ElMessage } from 'element-plus';
import router from '@/router';
import { clearAllUserData, migrateExistingData, migrateDataFromAnonymous } from '@/utils/userStorage';

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('token'));
  const userInfo = ref<UserInfo | null>(null);
  const loading = ref(false);

  // 初始化用户信息
  const initUserInfo = async () => {
    const storedUserInfo = localStorage.getItem('userInfo');
    if (storedUserInfo) {
      userInfo.value = JSON.parse(storedUserInfo);
      
      // 迁移已有的数据到用户特定存储
      migrateExistingData([
        'selectedTopic', 
        'topicsHistory', 
        'selectedOutline',
        'savedSections',
        'savedPaper'
      ]);
    } else if (token.value) {
      // 如果有token但没有用户信息，则获取用户信息
      await fetchUserInfo();
    }
  };

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      loading.value = true;
      const response = await getUserInfo();
      userInfo.value = response;
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value));
    } catch (error) {
      console.error('获取用户信息失败:', error);
      // 如果获取用户信息失败，清除token
      logout();
    } finally {
      loading.value = false;
    }
  };

  // 登录
  const loginAction = async (loginData: LoginRequest) => {
    try {
      loading.value = true;
      console.log('尝试登录，用户名:', loginData.username);

      // 确保密码长度符合要求
      if (loginData.password.length < 6) {
        ElMessage.warning('密码长度不能少于6个字符');
        return false;
      }

      const response = await login(loginData);
      console.log('登录响应:', response);

      token.value = response.access_token;
      localStorage.setItem('token', token.value);
      
      // 在登录前保存匿名标识
      const anonymousId = localStorage.getItem('anonymousId');
      
      // 获取用户信息
      await fetchUserInfo();
      
      // 登录成功后进行数据迁移
      if (anonymousId) {
        console.log('从匿名识别符迁移数据:', anonymousId);
        migrateDataFromAnonymous(anonymousId);
      }
      
      // 迁移传统存储中的数据
      migrateExistingData([
        'selectedTopic', 
        'topicsHistory', 
        'selectedOutline',
        'savedSections',
        'savedPaper'
      ]);
      
      ElMessage.success('登录成功');
      router.push('/');
      return true;
    } catch (error: any) {
      console.error('登录失败:', error);
      console.error('错误详情:', error.response?.data);
      ElMessage.error(error.detail || '登录失败，请检查用户名和密码');
      return false;
    } finally {
      loading.value = false;
    }
  };

  // 注册
  const registerAction = async (registerData: RegisterRequest) => {
    try {
      loading.value = true;
      await register(registerData);
      ElMessage.success('注册成功，请登录');
      router.push('/login');
      return true;
    } catch (error) {
      console.error('注册失败:', error);
      ElMessage.error('注册失败，请检查输入信息');
      return false;
    } finally {
      loading.value = false;
    }
  };

  // 登出
  const logout = () => {
    // 在清除用户信息前清除用户特定数据
    clearAllUserData();
    
    token.value = null;
    userInfo.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    router.push('/login');
    ElMessage.success('已退出登录');
  };

  // 检查是否已登录
  const isLoggedIn = () => {
    return !!token.value;
  };

  return {
    token,
    userInfo,
    loading,
    initUserInfo,
    loginAction,
    registerAction,
    logout,
    isLoggedIn,
    fetchUserInfo
  };
});

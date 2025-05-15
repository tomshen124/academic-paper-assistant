import { useAuthStore } from '@/stores/auth';

/**
 * 获取当前用户ID
 * @returns 当前用户ID或默认值
 */
export function getCurrentUserId(): string {
  // 尝试从本地存储获取用户信息
  const userInfoStr = localStorage.getItem('userInfo');
  if (userInfoStr) {
    try {
      const userInfo = JSON.parse(userInfoStr);
      if (userInfo && userInfo.id) {
        return userInfo.id.toString();
      }
    } catch (e) {
      console.error('解析用户信息失败:', e);
    }
  }
  
  // 获取token，如果有token但没有用户信息，可能是初始化问题
  const token = localStorage.getItem('token');
  if (token) {
    console.log('发现token但无用户信息，尝试使用默认用户ID');
    return '1'; // 默认使用ID 1，因为管理员通常是ID 1
  }
  
  // 如果无法获取用户ID，返回匿名标识符
  // 得到一个固定的标识符来保持数据的一致性
  let anonymousId = localStorage.getItem('anonymousId');
  if (!anonymousId) {
    anonymousId = 'anonymous_' + Date.now().toString();
    localStorage.setItem('anonymousId', anonymousId);
  }
  return anonymousId;
}

/**
 * 生成用户特定的存储键
 * @param key 原始键
 * @returns 带用户ID前缀的存储键
 */
export function getUserKey(key: string): string {
  const userId = getCurrentUserId();
  return `user_${userId}_${key}`;
}

/**
 * 保存用户数据
 * @param key 数据键
 * @param data 要保存的数据
 */
export function saveUserData(key: string, data: any): void {
  const userKey = getUserKey(key);
  localStorage.setItem(userKey, JSON.stringify(data));
}

/**
 * 获取用户数据
 * @param key 数据键
 * @returns 存储的数据，如果不存在则返回null
 */
export function getUserData<T>(key: string): T | null {
  const userKey = getUserKey(key);
  const data = localStorage.getItem(userKey);
  return data ? JSON.parse(data) : null;
}

/**
 * 删除用户数据
 * @param key 数据键
 */
export function removeUserData(key: string): void {
  const userKey = getUserKey(key);
  localStorage.removeItem(userKey);
}

/**
 * 清除当前用户的所有数据
 */
export function clearAllUserData(): void {
  const userId = getCurrentUserId();
  const prefix = `user_${userId}_`;
  
  // 遍历localStorage中的所有键
  Object.keys(localStorage).forEach(key => {
    if (key.startsWith(prefix)) {
      localStorage.removeItem(key);
    }
  });
}

/**
 * 迁移现有数据到用户特定存储
 * 此函数用于将已有的localStorage数据迁移到新的用户特定存储
 * @param keys 要迁移的键列表
 */
export function migrateExistingData(keys: string[]): void {
  const userId = getCurrentUserId();
  
  keys.forEach(key => {
    const existingData = localStorage.getItem(key);
    if (existingData) {
      try {
        // 保存到用户特定存储
        const userKey = getUserKey(key);
        localStorage.setItem(userKey, existingData);
        
        // 删除原始数据以避免混淆
        localStorage.removeItem(key);
        console.log(`迁移数据成功: ${key} -> ${userKey}`);
      } catch (e) {
        console.error(`迁移数据 "${key}" 失败:`, e);
      }
    }
  });
}

/**
 * 从匿名用户迁移数据到已登录用户
 * @param anonymousId 匿名用户ID
 */
export function migrateDataFromAnonymous(anonymousId: string): void {
  // 关键数据键
  const keysToMigrate = [
    'selectedTopic', 
    'topicsHistory', 
    'selectedOutline',
    'savedSections',
    'savedPaper'
  ];
  
  const currentUserId = getCurrentUserId();
  
  // 如果当前用户ID等于匿名ID，则不需要迁移
  if (currentUserId === anonymousId) {
    console.log('当前用户就是匿名用户，无需迁移');
    return;
  }
  
  console.log(`从匿名用户 ${anonymousId} 迁移数据到用户 ${currentUserId}`);
  
  // 遍历需要迁移的键
  keysToMigrate.forEach(key => {
    const anonymousKey = `user_${anonymousId}_${key}`;
    const currentUserKey = getUserKey(key);
    
    // 检查匿名用户是否存在该数据
    const anonymousData = localStorage.getItem(anonymousKey);
    if (anonymousData) {
      try {
        // 将匿名用户数据保存到当前用户
        localStorage.setItem(currentUserKey, anonymousData);
        console.log(`匿名数据迁移成功: ${anonymousKey} -> ${currentUserKey}`);
        
        // 可选：删除匿名用户数据
        // localStorage.removeItem(anonymousKey);
      } catch (e) {
        console.error(`从匿名用户迁移数据 "${key}" 失败:`, e);
      }
    }
  });
}

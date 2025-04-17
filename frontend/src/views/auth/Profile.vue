<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <h2>个人信息</h2>
        </div>
      </template>
      
      <div v-if="authStore.userInfo" class="profile-content">
        <div class="profile-avatar">
          <el-avatar :size="100" icon="UserFilled" />
        </div>
        
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">
            {{ authStore.userInfo.username }}
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">
            {{ authStore.userInfo.email }}
          </el-descriptions-item>
          <el-descriptions-item label="账户状态">
            <el-tag :type="authStore.userInfo.is_active ? 'success' : 'danger'">
              {{ authStore.userInfo.is_active ? '已激活' : '未激活' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="账户类型">
            <el-tag :type="authStore.userInfo.is_superuser ? 'warning' : 'info'">
              {{ authStore.userInfo.is_superuser ? '管理员' : '普通用户' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">
            {{ formatDate(authStore.userInfo.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="profile-actions">
          <el-button type="primary" disabled>编辑个人信息</el-button>
          <el-button type="warning" disabled>修改密码</el-button>
        </div>
        
        <el-alert
          title="功能开发中"
          type="info"
          description="个人信息编辑功能正在开发中，敬请期待！"
          show-icon
          :closable="false"
          style="margin-top: 20px"
        />
      </div>
      
      <div v-else class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import { UserFilled } from '@element-plus/icons-vue';

const authStore = useAuthStore();

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-content {
  padding: 20px 0;
}

.profile-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.profile-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.loading-container {
  padding: 40px 0;
}
</style>

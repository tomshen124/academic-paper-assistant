<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>系统设置</h2>
        </div>
      </template>
      
      <el-tabs>
        <el-tab-pane label="基本设置">
          <el-form label-position="top">
            <el-form-item label="界面主题">
              <el-radio-group v-model="settings.theme" disabled>
                <el-radio label="light">浅色</el-radio>
                <el-radio label="dark">深色</el-radio>
                <el-radio label="system">跟随系统</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="语言">
              <el-select v-model="settings.language" disabled style="width: 200px">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="通知设置">
          <el-form label-position="top">
            <el-form-item label="邮件通知">
              <el-switch v-model="settings.emailNotification" disabled />
            </el-form-item>
            
            <el-form-item label="系统通知">
              <el-switch v-model="settings.systemNotification" disabled />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="隐私设置">
          <el-form label-position="top">
            <el-form-item label="数据分享">
              <el-switch v-model="settings.dataSharing" disabled />
              <div class="setting-description">
                允许系统收集匿名使用数据以改进服务
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <div class="settings-actions">
        <el-button type="primary" disabled>保存设置</el-button>
        <el-button disabled>恢复默认</el-button>
      </div>
      
      <el-alert
        title="功能开发中"
        type="info"
        description="设置功能正在开发中，敬请期待！"
        show-icon
        :closable="false"
        style="margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';

// 设置数据
const settings = reactive({
  theme: 'light',
  language: 'zh-CN',
  emailNotification: false,
  systemNotification: true,
  dataSharing: false
});
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-description {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}
</style>

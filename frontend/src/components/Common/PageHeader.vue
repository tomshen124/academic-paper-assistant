<template>
  <el-header class="page-header">
    <div class="logo">
      <h1>教育知识图谱系统</h1>
    </div>
    <el-menu
      mode="horizontal"
      :router="true"
      :default-active="activeRoute"
    >
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/statistics">统计分析</el-menu-item>
      <el-menu-item index="/graph">知识图谱</el-menu-item>
    </el-menu>
  </el-header>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeRoute = ref(route.path)

watch(
  () => route.path,
  (newPath) => {
    activeRoute.value = newPath
  }
)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
}

.logo {
  margin-right: 40px;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  color: var(--el-text-color-primary);
}

:deep(.el-menu) {
  flex: 1;
  border-bottom: none;
}

:deep(.el-menu-item) {
  font-size: 16px;
}
</style> 
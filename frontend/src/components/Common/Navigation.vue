<template>
  <el-menu
    :default-active="activeIndex"
    class="nav-menu"
    mode="horizontal"
    router
  >
    <el-menu-item index="/">
      <el-icon><home-filled /></el-icon>
      首页
    </el-menu-item>
    
    <el-menu-item index="/graph">
      <el-icon><share /></el-icon>
      知识图谱
    </el-menu-item>
    
    <el-menu-item index="/statistics">
      <el-icon><data-line /></el-icon>
      统计分析
    </el-menu-item>

    <el-menu-item index="/import">
      <el-icon><upload /></el-icon>
      数据导入
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { HomeFilled, Share, DataLine, Upload } from '@element-plus/icons-vue'

const route = useRoute()
const activeIndex = ref(route.path)

// 监听路由变化更新激活菜单
watch(
  () => route.path,
  (newPath) => {
    activeIndex.value = newPath
  }
)

// 初始化激活菜单
onMounted(() => {
  activeIndex.value = route.path
})
</script>

<style scoped>
.nav-menu {
  padding: 0 20px;
}

:deep(.el-menu-item) {
  display: flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-icon) {
  margin-right: 4px;
}
</style> 
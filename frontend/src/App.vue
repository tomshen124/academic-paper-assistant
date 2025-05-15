<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeFilled,
  UploadFilled,
  PieChart,
  Share,
  Connection,
  Fold,
  ArrowDown
} from '@element-plus/icons-vue'

const activeMenu = ref('')
const isCollapse = ref(false)
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 初始化认证状态
const authStore = useAuthStore()
onMounted(() => {
  authStore.initUserInfo()
})

defineExpose({
  activeMenu,
  isCollapse,
  toggleSidebar
})
</script>

<template>
  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<style lang="scss">
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app {
  height: 100%;
  width: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
<template>
  <el-breadcrumb class="app-breadcrumb">
    <transition-group name="breadcrumb">
      <el-breadcrumb-item 
        v-for="(item, index) in breadcrumbs" 
        :key="item.path"
      >
        <span 
          v-if="index === breadcrumbs.length - 1" 
          class="no-redirect"
        >{{ item.meta?.title }}</span>
        <a 
          v-else 
          @click.prevent="handleLink(item)"
        >{{ item.meta?.title }}</a>
      </el-breadcrumb-item>
    </transition-group>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter, RouteLocationMatched } from 'vue-router'

const route = useRoute()
const router = useRouter()

const breadcrumbs = ref<RouteLocationMatched[]>([])

// 过滤路由
const getBreadcrumbs = () => {
  let matched = route.matched.filter(item => item.meta && item.meta.title)
  const first = matched[0]
  
  if (first && first.path !== '/') {
    matched = [{ path: '/', meta: { title: '首页' } } as RouteLocationMatched].concat(matched)
  }
  
  breadcrumbs.value = matched
}

// 处理面包屑点击
const handleLink = (item: RouteLocationMatched) => {
  const { path } = item
  router.push(path)
}

// 监听路由变化
watch(
  () => route.path,
  () => getBreadcrumbs(),
  { immediate: true }
)
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.app-breadcrumb {
  display: inline-block;
  
  .no-redirect {
    color: $text-regular;
    cursor: text;
  }
  
  a {
    color: $primary-color;
    cursor: pointer;
    
    &:hover {
      color: darken($primary-color, 10%);
    }
  }
}

// 面包屑动画
.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.5s;
}

.breadcrumb-enter-from,
.breadcrumb-leave-active {
  opacity: 0;
  transform: translateX(20px);
}

.breadcrumb-leave-active {
  position: absolute;
}
</style> 
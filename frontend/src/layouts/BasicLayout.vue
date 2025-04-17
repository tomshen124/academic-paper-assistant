<template>
  <div class="layout-container">
    <el-container>
      <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
        <div class="logo">
          <el-icon :size="24" color="#fff"><Document /></el-icon>
          <span v-if="!isCollapse">学术论文辅助</span>
        </div>
        <el-menu
          :collapse="isCollapse"
          :default-active="route.path"
          class="sidebar-menu"
          router
        >
          <el-sub-menu index="/topics">
            <template #title>
              <el-icon><Edit /></el-icon>
              <span>论文主题</span>
            </template>
            <el-menu-item index="/topics/recommend">
              <el-icon><Star /></el-icon>
              <template #title>主题推荐</template>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/outlines">
            <template #title>
              <el-icon><List /></el-icon>
              <span>论文提纲</span>
            </template>
            <el-menu-item index="/outlines/generate">
              <el-icon><DocumentAdd /></el-icon>
              <template #title>提纲生成</template>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/papers">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>论文生成</span>
            </template>
            <el-menu-item index="/papers/generate">
              <el-icon><Notebook /></el-icon>
              <template #title>论文生成</template>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/citations">
            <template #title>
              <el-icon><Link /></el-icon>
              <span>引用管理</span>
            </template>
            <el-menu-item index="/citations/format">
              <el-icon><Files /></el-icon>
              <template #title>引用格式化</template>
            </el-menu-item>
            <el-menu-item index="/citations/extract">
              <el-icon><Scissors /></el-icon>
              <template #title>引用提取</template>
            </el-menu-item>
            <el-menu-item index="/citations/bibliography">
              <el-icon><Collection /></el-icon>
              <template #title>参考文献</template>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/search">
            <template #title>
              <el-icon><Search /></el-icon>
              <span>学术搜索</span>
            </template>
            <el-menu-item index="/search/literature">
              <el-icon><Reading /></el-icon>
              <template #title>文献搜索</template>
            </el-menu-item>
            <el-menu-item index="/search/trends">
              <el-icon><TrendCharts /></el-icon>
              <template #title>研究趋势</template>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/tokens">
            <el-icon><Coin /></el-icon>
            <template #title>Token管理</template>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <el-button type="link" @click="toggleCollapse">
            <el-icon>
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </el-button>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                <el-avatar :size="32" icon="UserFilled" />
                <span v-if="authStore.userInfo" class="username">{{ authStore.userInfo.username }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item command="settings">设置</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'
import {
  Document,
  DocumentAdd,
  Edit,
  List,
  Notebook,
  Link,
  Files,
  Collection,
  Search,
  Reading,
  TrendCharts,
  Coin,
  Star,
  Setting,
  Fold,
  Expand,
  ArrowDown,
  UserFilled
} from '@element-plus/icons-vue'

const isCollapse = ref(false)
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        authStore.logout()
      }).catch(() => {})
      break
  }
}
</script>

<style lang="scss" scoped>
@use 'sass:color';
@use '@/styles/variables' as vars;

.layout-container {
  height: 100vh;
  .sidebar {
    background: linear-gradient(180deg, vars.$menuBg 0%, color.adjust(vars.$menuBg, $lightness: -5%) 100%);
    transition: width 0.3s;
    .logo {
      height: vars.$headerHeight;
      display: flex;
      align-items: center;
      padding: 0 16px;
      color: vars.$menuText;
      img {
        width: 32px;
        height: 32px;
        margin-right: 8px;
      }
      span {
        font-size: 18px;
        font-weight: 600;
        white-space: nowrap;
        opacity: 0.95;
      }
    }
    .sidebar-menu {
      border-right: none;
      &:not(.el-menu--collapse) {
        width: 200px;
      }
    }
  }
  .header {
    background: white;
    border-bottom: 1px solid vars.$borderColor;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    height: vars.$headerHeight;
    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;

      .user-dropdown {
        display: flex;
        align-items: center;
        cursor: pointer;
        padding: 0 8px;
        border-radius: 4px;
        transition: background-color 0.3s;

        &:hover {
          background-color: #f5f7fa;
        }

        .username {
          margin: 0 8px;
          font-size: 14px;
        }
      }
    }
  }
  .main {
    background: vars.$bgColor;
    padding: vars.$contentPadding;
  }
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
<template>
  <div class="home-container">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="logo">知识图谱系统</div>
      <el-menu
        default-active="1"
        class="sidebar-menu"
        :router="true"
      >
        <el-menu-item index="1" route="/">
          <el-icon><home /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="2" route="/graph">
          <el-icon><share /></el-icon>
          <span>知识图谱</span>
        </el-menu-item>
        <el-menu-item index="3" route="/association">
          <el-icon><connection /></el-icon>
          <span>关联度分析</span>
        </el-menu-item>
        <el-menu-item index="4" route="/import">
          <el-icon><upload /></el-icon>
          <span>数据导入</span>
        </el-menu-item>
        <el-menu-item index="5" route="/export">
          <el-icon><download /></el-icon>
          <span>数据导出</span>
        </el-menu-item>
        <el-menu-item index="6" route="/statistics">
          <el-icon><data-analysis /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <h1 class="page-title">知识图谱系统总览</h1>
      
      <!-- 统计卡片 -->
      <div class="stats-cards">
        <el-row :gutter="20">
          <el-col :span="6">
            <stat-card
              title="实体总数"
              :value="overview.entityCount || 0"
              icon="Document"
              :trend="{ value: '+20%', label: '较上月', type: 'up' }"
            />
          </el-col>
          <el-col :span="6">
            <stat-card
              title="关系总数"
              :value="overview.relationCount || 0"
              icon="Link"
              :trend="{ value: '+15%', label: '较上月', type: 'up' }"
            />
          </el-col>
          <el-col :span="6">
            <stat-card
              title="属性总数"
              :value="overview.attributeCount || 0"
              icon="List"
              :trend="{ value: '+10%', label: '较上月', type: 'up' }"
            />
          </el-col>
          <el-col :span="6">
            <stat-card
              title="数据完整度"
              :value="overview.completeness ? overview.completeness + '%' : '0%'"
              icon="DataLine"
              :trend="{ value: '+5%', label: '较上月', type: 'up' }"
            />
          </el-col>
        </el-row>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <chart-card
              title="实体类型分布"
              :loading="loading"
              :options="entityTypeChartOptions"
            />
          </el-col>
          <el-col :span="12">
            <chart-card
              title="关系类型分布"
              :loading="loading"
              :options="relationTypeChartOptions"
            />
          </el-col>
        </el-row>
        <el-row :gutter="20" class="mt-20">
          <el-col :span="24">
            <chart-card
              title="知识图谱增长趋势"
              :loading="loading"
              :options="growthTrendOptions"
            />
          </el-col>
        </el-row>
      </div>

      <!-- 快速入口 -->
      <div class="quick-access">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="access-card" @click="$router.push('/graph')">
              <el-icon><Share /></el-icon>
              <h3>知识图谱</h3>
              <p>可视化展示知识网络</p>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="access-card" @click="$router.push('/association')">
              <el-icon><Connection /></el-icon>
              <h3>关联分析</h3>
              <p>发现知识间的关联</p>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="access-card" @click="$router.push('/import')">
              <el-icon><Upload /></el-icon>
              <h3>数据导入</h3>
              <p>导入新的知识数据</p>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="access-card" @click="$router.push('/statistics')">
              <el-icon><DataAnalysis /></el-icon>
              <h3>统计分析</h3>
              <p>数据统计与分析</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { EChartsOption } from 'echarts'
import {
  Home,
  Share,
  Connection,
  Upload,
  DataAnalysis,
  Document,
  Link,
  List,
  DataLine
} from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import ChartCard from '@/components/ChartCard.vue'
import { statisticsApi } from '@/api/modules/statistics'

const router = useRouter()
const loading = ref(false)
const overview = ref({
  entityCount: 0,
  relationCount: 0,
  attributeCount: 0,
  completeness: 0
})

// 实体类型分布图表配置
const entityTypeChartOptions = ref<EChartsOption>({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  series: [
    {
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '14',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: []
    }
  ]
})

// 关系类型分布图表配置
const relationTypeChartOptions = ref<EChartsOption>({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  series: [
    {
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '14',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: []
    }
  ]
})

// 增长趋势图表配置
const growthTrendOptions = ref<EChartsOption>({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['实体数量', '关系数量']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: []
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '实体数量',
      type: 'line',
      smooth: true,
      data: []
    },
    {
      name: '关系数量',
      type: 'line',
      smooth: true,
      data: []
    }
  ]
})

// 获取统计数据
const fetchStatistics = async () => {
  try {
    loading.value = true
    const data = await statisticsApi.getOverview()
    
    // 更新概览数据
    overview.value = {
      entityCount: data.实体总数,
      relationCount: data.关系总数,
      attributeCount: data.属性总数,
      completeness: data.填充率
    }
    
    // 更新实体类型分布
    entityTypeChartOptions.value.series[0].data = data.实体类型分布.map(item => ({
      name: item.name,
      value: item.value
    }))
    
    // 更新关系类型分布
    relationTypeChartOptions.value.series[0].data = data.关系类型分布.map(item => ({
      name: item.name,
      value: item.value
    }))
    
    // 更新增长趋势
    const trendData = data.增长趋势
    growthTrendOptions.value.xAxis.data = trendData.map(item => item.date)
    growthTrendOptions.value.series[0].data = trendData.map(item => item.value)
    
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStatistics()
})
</script>

<style lang="scss" scoped>
.home-container {
  display: flex;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.sidebar {
  width: 240px;
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  border-bottom: 1px solid #e6e6e6;
}

.main-content {
  flex: 1;
  padding: 20px;
}

.page-title {
  margin: 0 0 20px;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stats-cards {
  margin-bottom: 24px;
}

.charts-section {
  margin-bottom: 24px;
  
  .mt-20 {
    margin-top: 20px;
  }
}

.quick-access {
  .access-card {
    height: 160px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
    }
    
    .el-icon {
      font-size: 36px;
      color: #1890ff;
      margin-bottom: 16px;
    }
    
    h3 {
      margin: 0 0 8px;
      font-size: 18px;
      color: #333;
    }
    
    p {
      margin: 0;
      color: #666;
    }
  }
}
</style> 
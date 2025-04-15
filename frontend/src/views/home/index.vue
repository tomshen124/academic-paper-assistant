<template>
  <div class="home-container">
    <div class="overview-section">
      <el-row :gutter="20">
        <el-col :span="6" v-for="(item, index) in statistics" :key="index">
          <el-card class="stat-card" :body-style="{ padding: '20px' }">
            <div class="stat-icon">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-label">{{ item.label }}</div>
              <div class="stat-trend" :class="{ 'up': item.trend > 0 }">
                {{ item.trend > 0 ? '+' : '' }}{{ item.trend }}% 较上月
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="charts-section">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>概念增长趋势</span>
                <el-radio-group v-model="timeRange" size="small">
                  <el-radio-button label="week">周</el-radio-button>
                  <el-radio-button label="month">月</el-radio-button>
                  <el-radio-button label="year">年</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div class="chart-content" ref="trendChartRef"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>用户活动统计</span>
              </div>
            </template>
            <div class="chart-content" ref="activityChartRef"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="action-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="feature-header">
                <span>快速操作</span>
              </div>
            </template>
            <div class="feature-content">
              <el-button type="primary" class="action-btn" @click="$router.push('/graph')">
                <el-icon><Share /></el-icon>查看知识图谱
              </el-button>
              <el-button type="primary" class="action-btn" @click="$router.push('/import')">
                <el-icon><Upload /></el-icon>导入数据
              </el-button>
              <el-button type="primary" class="action-btn" @click="$router.push('/statistics')">
                <el-icon><DataLine /></el-icon>查看统计
              </el-button>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="feature-header">
                <span>最近添加的概念</span>
              </div>
            </template>
            <div class="feature-content">
              <el-tag
                v-for="concept in recentConcepts"
                :key="concept"
                class="concept-tag"
                effect="plain"
              >
                {{ concept }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="feature-header">
                <span>系统公告</span>
              </div>
            </template>
            <div class="feature-content">
              <div class="announcement" v-for="(notice, index) in announcements" :key="index">
                <div class="notice-title">{{ notice.title }}</div>
                <div class="notice-content">{{ notice.content }}</div>
                <div class="notice-time">{{ notice.time }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Share, Upload, DataLine, TrendCharts, User, Link } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const timeRange = ref('month')
const trendChartRef = ref<HTMLElement>()
const activityChartRef = ref<HTMLElement>()

const statistics = ref([
  { label: '总概念数', value: '1,234', trend: 20, icon: 'TrendCharts' },
  { label: '总关系数', value: '5,678', trend: 15, icon: 'Link' },
  { label: '活跃用户', value: '573', trend: 5, icon: 'User' },
  { label: '本周新增', value: '1,234', trend: 10, icon: 'DataLine' }
])

const recentConcepts = ref([
  '人工智能', '机器学习', '深度学习', '自然语言处理', '计算机视觉'
])

const announcements = ref([
  {
    title: '系统维护通知',
    content: '系统将于本周日进行维护，预计停机2小时',
    time: '2024-01-20'
  },
  {
    title: '新功能上线',
    content: '关联度分析功能已上线，欢迎体验',
    time: '2024-01-18'
  }
])

onMounted(() => {
  initTrendChart()
  initActivityChart()
})

const initTrendChart = () => {
  const chart = echarts.init(trendChartRef.value!)
  chart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '概念数量',
      type: 'line',
      smooth: true,
      data: [120, 150, 180, 220, 260, 300],
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
          offset: 0,
          color: 'rgba(64,158,255,0.3)'
        }, {
          offset: 1,
          color: 'rgba(64,158,255,0.1)'
        }])
      }
    }]
  })
}

const initActivityChart = () => {
  const chart = echarts.init(activityChartRef.value!)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['新增概念', '编辑次数']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '新增概念',
        type: 'bar',
        data: [20, 25, 30, 22, 28, 15, 12],
        itemStyle: {
          color: '#67C23A'
        }
      },
      {
        name: '编辑次数',
        type: 'bar',
        data: [48, 58, 70, 52, 65, 35, 32],
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  })
}
</script>

<style lang="scss" scoped>
.home-container {
  .overview-section {
    margin-bottom: 20px;
    
    .stat-card {
      height: 120px;
      display: flex;
      align-items: center;
      
      .stat-icon {
        font-size: 48px;
        color: var(--el-color-primary);
        opacity: 0.8;
        margin-right: 20px;
      }
      
      .stat-content {
        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: var(--el-text-color-primary);
          line-height: 1.2;
        }
        
        .stat-label {
          font-size: 14px;
          color: var(--el-text-color-secondary);
          margin: 4px 0;
        }
        
        .stat-trend {
          font-size: 12px;
          color: var(--el-color-danger);
          
          &.up {
            color: var(--el-color-success);
          }
        }
      }
    }
  }
  
  .charts-section {
    margin-bottom: 20px;
    
    .chart-card {
      .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .chart-content {
        height: 300px;
      }
    }
  }
  
  .action-section {
    .feature-card {
      height: 100%;
      
      .feature-content {
        .action-btn {
          display: block;
          width: 100%;
          margin-bottom: 12px;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
        
        .concept-tag {
          margin: 0 8px 8px 0;
        }
        
        .announcement {
          padding: 12px 0;
          border-bottom: 1px solid var(--el-border-color-lighter);
          
          &:last-child {
            border-bottom: none;
          }
          
          .notice-title {
            font-weight: bold;
            margin-bottom: 4px;
          }
          
          .notice-content {
            color: var(--el-text-color-secondary);
            font-size: 14px;
            margin-bottom: 4px;
          }
          
          .notice-time {
            color: var(--el-text-color-secondary);
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style> 
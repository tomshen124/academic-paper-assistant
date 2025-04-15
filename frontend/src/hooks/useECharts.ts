import { onMounted, onUnmounted, watch } from 'vue'
import type { Ref } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

export function useECharts(chartRef: Ref<HTMLElement | undefined>) {
  let chart: echarts.ECharts | null = null

  // 初始化图表
  function initChart(option: EChartsOption) {
    if (!chartRef.value) return
    
    if (!chart) {
      chart = echarts.init(chartRef.value)
    }
    
    chart.setOption(option)
  }

  // 监听窗口大小变化
  function handleResize() {
    chart?.resize()
  }

  // 组件挂载时初始化
  onMounted(() => {
    window.addEventListener('resize', handleResize)
  })

  // 组件卸载时清理
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    chart?.dispose()
    chart = null
  })

  // 监听容器引用变化
  watch(() => chartRef.value, (el) => {
    if (el && !chart) {
      chart = echarts.init(el)
    }
  })

  return {
    initChart
  }
} 
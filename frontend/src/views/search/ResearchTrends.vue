<template>
  <div class="research-trends-container">
    <el-card class="trends-card">
      <template #header>
        <div class="card-header">
          <h2>研究趋势分析</h2>
          <p>了解学术领域的最新研究趋势</p>
        </div>
      </template>
      
      <div class="trends-form">
        <el-form :model="formData" label-position="top">
          <el-form-item label="学术领域" prop="field">
            <el-select v-model="formData.field" placeholder="请选择学术领域" style="width: 100%">
              <el-option v-for="field in academicFields" :key="field" :label="field" :value="field" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="getTrends">
              获取研究趋势
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <el-card v-if="trends" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>{{ trends.field }} 领域研究趋势</h2>
        </div>
      </template>
      
      <div class="trends-result">
        <el-empty v-if="trends.trends.length === 0" description="未找到研究趋势数据" />
        
        <div v-else class="trends-list">
          <h3>热门研究方向</h3>
          
          <el-timeline>
            <el-timeline-item
              v-for="(trend, index) in trends.trends"
              :key="index"
              :timestamp="trend.year"
              placement="top"
              :type="getTimelineItemType(index)"
            >
              <el-card class="trend-card">
                <h4>{{ trend.title }}</h4>
                <p class="trend-abstract">{{ trend.abstract }}</p>
                <div class="trend-meta">
                  <el-tag size="small" type="info">引用: {{ trend.citations }}</el-tag>
                  <el-button type="primary" size="small" @click="openPaperUrl(trend.url)">
                    查看论文
                  </el-button>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { getResearchTrends } from '@/api/modules/search';
import type { TrendRequest, TrendResponse } from '@/types/search';

// 表单数据
const formData = reactive<TrendRequest>({
  field: ''
});

// 学术领域选项
const academicFields = [
  '计算机科学',
  '人工智能',
  '医学',
  '生物学',
  '物理学',
  '化学',
  '数学',
  '经济学',
  '社会学',
  '心理学',
  '教育学',
  '文学',
  '历史学',
  '哲学',
  '法学',
  '工程学',
  '环境科学',
  '地理学',
  '农学',
  '管理学'
];

// 研究趋势结果
const trends = ref<TrendResponse | null>(null);

const loading = ref(false);

// 获取研究趋势
const getTrends = async () => {
  if (!formData.field) {
    ElMessage.warning('请选择学术领域');
    return;
  }
  
  loading.value = true;
  try {
    const result = await getResearchTrends(formData);
    trends.value = result;
    
    if (result.trends.length === 0) {
      ElMessage.info('未找到研究趋势数据');
    } else {
      ElMessage.success('研究趋势获取成功');
    }
  } catch (error) {
    console.error('获取研究趋势失败:', error);
    ElMessage.error('获取研究趋势失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 获取时间线项目类型
const getTimelineItemType = (index: number) => {
  const types = ['primary', 'success', 'warning', 'danger', 'info'];
  return types[index % types.length];
};

// 打开论文URL
const openPaperUrl = (url: string) => {
  if (!url) return;
  
  window.open(url, '_blank');
};
</script>

<style scoped>
.research-trends-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.trends-card, .result-card {
  margin-bottom: 30px;
}

.card-header {
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.card-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.trends-result {
  margin-top: 20px;
}

.trends-list h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
}

.trend-card {
  margin-bottom: 10px;
}

.trend-card h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.trend-abstract {
  margin: 0 0 15px 0;
  color: #606266;
  line-height: 1.6;
}

.trend-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

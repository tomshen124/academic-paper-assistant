<template>
  <div class="outline-validate-container">
    <el-card class="validate-card">
      <template #header>
        <div class="card-header">
          <h2>提纲验证</h2>
          <p>验证论文提纲的完整性、连贯性和平衡性</p>
        </div>
      </template>
      
      <div v-if="!outline" class="no-outline">
        <el-empty description="未找到提纲信息">
          <template #description>
            <p>请先生成或选择一个提纲</p>
          </template>
          <el-button type="primary" @click="goToOutlineGenerate">创建提纲</el-button>
        </el-empty>
      </div>
      
      <div v-else class="validate-form">
        <div class="current-outline">
          <h3>当前提纲</h3>
          <div class="outline-preview">
            <h4>{{ outline.title }}</h4>
            <div class="outline-sections">
              <div v-for="(section, index) in outline.sections" :key="index" class="section-item">
                <div class="section-title">{{ section.title }}</div>
                <div v-if="section.subsections && section.subsections.length > 0" class="subsections">
                  <div v-for="(subsection, subIndex) in section.subsections" :key="subIndex" class="subsection-item">
                    - {{ subsection.title }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="validate-actions">
          <el-button type="primary" :loading="loading" @click="validateOutline">验证提纲</el-button>
        </div>
      </div>
    </el-card>
    
    <el-card v-if="validation" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>验证结果</h2>
          <div class="score-badge">
            <el-tag :type="getScoreType(validation.overall_score)" size="large">
              总体评分: {{ validation.overall_score }}/10
            </el-tag>
          </div>
        </div>
      </template>
      
      <div class="validation-result">
        <el-tabs type="border-card">
          <el-tab-pane label="完整性">
            <div class="validation-category">
              <div class="category-header">
                <h3>完整性评估</h3>
                <el-rate
                  v-model="validation.completeness.score"
                  :max="10"
                  disabled
                  show-score
                  text-color="#ff9900"
                />
              </div>
              
              <div v-if="validation.completeness.issues.length > 0" class="issues">
                <h4>存在的问题</h4>
                <ul>
                  <li v-for="(issue, index) in validation.completeness.issues" :key="index">
                    {{ issue }}
                  </li>
                </ul>
              </div>
              
              <div v-if="validation.completeness.suggestions.length > 0" class="suggestions">
                <h4>改进建议</h4>
                <ul>
                  <li v-for="(suggestion, index) in validation.completeness.suggestions" :key="index">
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="连贯性">
            <div class="validation-category">
              <div class="category-header">
                <h3>连贯性评估</h3>
                <el-rate
                  v-model="validation.coherence.score"
                  :max="10"
                  disabled
                  show-score
                  text-color="#ff9900"
                />
              </div>
              
              <div v-if="validation.coherence.issues.length > 0" class="issues">
                <h4>存在的问题</h4>
                <ul>
                  <li v-for="(issue, index) in validation.coherence.issues" :key="index">
                    {{ issue }}
                  </li>
                </ul>
              </div>
              
              <div v-if="validation.coherence.suggestions.length > 0" class="suggestions">
                <h4>改进建议</h4>
                <ul>
                  <li v-for="(suggestion, index) in validation.coherence.suggestions" :key="index">
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="平衡性">
            <div class="validation-category">
              <div class="category-header">
                <h3>平衡性评估</h3>
                <el-rate
                  v-model="validation.balance.score"
                  :max="10"
                  disabled
                  show-score
                  text-color="#ff9900"
                />
              </div>
              
              <div v-if="validation.balance.issues.length > 0" class="issues">
                <h4>存在的问题</h4>
                <ul>
                  <li v-for="(issue, index) in validation.balance.issues" :key="index">
                    {{ issue }}
                  </li>
                </ul>
              </div>
              
              <div v-if="validation.balance.suggestions.length > 0" class="suggestions">
                <h4>改进建议</h4>
                <ul>
                  <li v-for="(suggestion, index) in validation.balance.suggestions" :key="index">
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="方法适当性">
            <div class="validation-category">
              <div class="category-header">
                <h3>方法适当性评估</h3>
                <el-rate
                  v-model="validation.methodology.score"
                  :max="10"
                  disabled
                  show-score
                  text-color="#ff9900"
                />
              </div>
              
              <div v-if="validation.methodology.issues.length > 0" class="issues">
                <h4>存在的问题</h4>
                <ul>
                  <li v-for="(issue, index) in validation.methodology.issues" :key="index">
                    {{ issue }}
                  </li>
                </ul>
              </div>
              
              <div v-if="validation.methodology.suggestions.length > 0" class="suggestions">
                <h4>改进建议</h4>
                <ul>
                  <li v-for="(suggestion, index) in validation.methodology.suggestions" :key="index">
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
        
        <div class="overall-assessment">
          <h3>总体评价</h3>
          <p>{{ validation.overall_assessment }}</p>
        </div>
        
        <div class="result-actions">
          <el-button type="primary" @click="continueWithOutline">继续使用此提纲</el-button>
          <el-button type="success" @click="optimizeOutline">优化提纲</el-button>
          <el-button @click="generatePaper">生成论文</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { validateOutline } from '@/api/modules/outlines';
import type { OutlineResponse, OutlineValidationRequest, OutlineValidationResponse } from '@/types/outlines';

const router = useRouter();
const route = useRoute();

// 当前提纲
const outline = ref<OutlineResponse | null>(null);

// 验证结果
const validation = ref<OutlineValidationResponse | null>(null);

const loading = ref(false);

// 从本地存储中获取提纲
onMounted(() => {
  const storedOutline = localStorage.getItem('selectedOutline');
  if (storedOutline) {
    try {
      outline.value = JSON.parse(storedOutline);
    } catch (error) {
      console.error('解析提纲失败:', error);
    }
  }
});

// 跳转到提纲生成页面
const goToOutlineGenerate = () => {
  router.push({ name: 'OutlineGenerate' });
};

// 验证提纲
const validateOutline = async () => {
  if (!outline.value) {
    ElMessage.warning('请先选择提纲');
    return;
  }
  
  loading.value = true;
  try {
    const request: OutlineValidationRequest = {
      outline: outline.value
    };
    
    const result = await validateOutline(request);
    validation.value = result;
    ElMessage.success('提纲验证完成');
  } catch (error) {
    console.error('验证提纲失败:', error);
    ElMessage.error('验证提纲失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 获取评分类型
const getScoreType = (score: number) => {
  if (score >= 8) return 'success';
  if (score >= 6) return 'warning';
  return 'danger';
};

// 继续使用此提纲
const continueWithOutline = () => {
  ElMessage.success('继续使用当前提纲');
};

// 优化提纲
const optimizeOutline = () => {
  router.push({
    name: 'OutlineOptimize',
    params: {
      id: 'current'
    }
  });
};

// 生成论文
const generatePaper = () => {
  router.push({
    name: 'PaperGenerate'
  });
};
</script>

<style scoped>
.outline-validate-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.validate-card, .result-card {
  margin-bottom: 30px;
}

.card-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.score-badge {
  margin-left: 20px;
}

.no-outline {
  padding: 40px 0;
  text-align: center;
}

.current-outline {
  margin-bottom: 30px;
}

.current-outline h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.outline-preview {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.outline-preview h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
  text-align: center;
}

.section-item {
  margin-bottom: 10px;
}

.section-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.subsections {
  margin-left: 20px;
}

.subsection-item {
  margin-bottom: 5px;
  color: #606266;
}

.validate-actions {
  margin-top: 20px;
  text-align: center;
}

.validation-result {
  margin-top: 20px;
}

.validation-category {
  padding: 15px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.category-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.issues, .suggestions {
  margin-bottom: 20px;
}

.issues h4, .suggestions h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.issues ul, .suggestions ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.issues li, .suggestions li {
  margin-bottom: 5px;
}

.issues {
  color: #f56c6c;
}

.suggestions {
  color: #67c23a;
}

.overall-assessment {
  margin: 30px 0;
  padding: 20px;
  background-color: #f0f9eb;
  border-radius: 4px;
  border-left: 4px solid #67c23a;
}

.overall-assessment h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.overall-assessment p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.result-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
  }
  
  .score-badge {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .category-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .category-header .el-rate {
    margin-top: 10px;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>

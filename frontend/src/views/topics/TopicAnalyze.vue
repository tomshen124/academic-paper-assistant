<template>
  <div class="topic-analyze-container">
    <el-card class="analyze-card">
      <template #header>
        <div class="card-header">
          <h2>主题可行性分析</h2>
          <p>分析论文主题的可行性，帮助您做出更好的选择</p>
        </div>
      </template>

      <div class="analyze-form">
        <el-form :model="formData" label-position="top" :rules="rules" ref="formRef">
          <el-form-item label="论文主题" prop="topic">
            <el-input
              v-model="formData.topic"
              placeholder="请输入论文主题"
            />
          </el-form-item>

          <el-form-item label="学术领域" prop="academic_field">
            <el-select v-model="formData.academic_field" placeholder="请选择学术领域" style="width: 100%">
              <el-option v-for="field in academicFields" :key="field" :label="field" :value="field" />
            </el-select>
          </el-form-item>

          <el-form-item label="学术级别">
            <el-select v-model="formData.academic_level" placeholder="请选择学术级别" style="width: 100%">
              <el-option v-for="level in academicLevels" :key="level" :label="level" :value="level" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="submitForm">分析可行性</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-card v-if="analysis" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>可行性分析结果</h2>
          <div class="score-badge">
            <el-tag :type="getScoreType(analysis.overall_score)" size="large">
              总体评分: {{ analysis.overall_score }}/10
            </el-tag>
          </div>
        </div>
      </template>

      <div class="analysis-result">
        <div class="result-section">
          <h3>难度评估</h3>
          <p>{{ analysis.difficulty }}</p>
        </div>

        <div class="result-section">
          <h3>资源需求</h3>
          <p>{{ analysis.resources }}</p>
        </div>

        <div class="result-section">
          <h3>时间估计</h3>
          <p>{{ analysis.time_estimate }}</p>
        </div>

        <div class="result-section">
          <h3>研究空白</h3>
          <p>{{ analysis.research_gaps }}</p>
        </div>

        <div class="result-section">
          <h3>潜在挑战</h3>
          <p>{{ analysis.challenges }}</p>
        </div>

        <div class="result-section">
          <h3>改进建议</h3>
          <p>{{ analysis.suggestions }}</p>
        </div>

        <div class="result-section recommendation">
          <h3>最终建议</h3>
          <p>{{ analysis.recommendation }}</p>
        </div>

        <div class="result-actions">
          <el-button type="primary" @click="useThisTopic">使用此主题</el-button>
          <el-button type="success" @click="refineTopic">优化主题</el-button>
          <el-button @click="generateOutline">生成提纲</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, FormInstance } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { analyzeTopicFeasibility } from '@/api/modules/topics';
import { saveUserData, getUserData } from '@/utils/userStorage';
import type { TopicFeasibilityRequest, TopicFeasibilityResponse } from '@/types/topics';

const router = useRouter();
const route = useRoute();

// 表单数据
const formData = reactive<TopicFeasibilityRequest>({
  topic: '',
  academic_field: '',
  academic_level: ''
});

// 表单验证规则
const rules = {
  topic: [
    { required: true, message: '请输入论文主题', trigger: 'blur' },
    { min: 5, message: '主题不能少于5个字符', trigger: 'blur' }
  ],
  academic_field: [
    { required: true, message: '请选择学术领域', trigger: 'change' }
  ]
};

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

// 学术级别选项
const academicLevels = [
  '本科',
  '硕士',
  '博士',
  '博士后'
];

const formRef = ref<FormInstance>();
const loading = ref(false);
const analysis = ref<TopicFeasibilityResponse | null>(null);

// 从路由参数中获取主题
onMounted(() => {
  const topicParam = route.params.topic;
  if (topicParam) {
    formData.topic = decodeURIComponent(topicParam as string);
  }
});

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const result = await analyzeTopicFeasibility(formData);
        analysis.value = result;
        ElMessage.success('主题分析完成');
      } catch (error) {
        console.error('分析主题失败:', error);
        ElMessage.error('分析主题失败，请稍后重试');
      } finally {
        loading.value = false;
      }
    }
  });
};

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  analysis.value = null;
};

// 获取评分类型
const getScoreType = (score: number) => {
  if (score >= 8) return 'success';
  if (score >= 6) return 'warning';
  return 'danger';
};

// 使用此主题
const useThisTopic = () => {
  if (!formData.topic) return;

  // 创建主题对象
  const topic = {
    title: formData.topic,
    academic_field: formData.academic_field,
    academic_level: formData.academic_level
  };

  // 将主题存储到用户存储
  saveUserData('selectedTopic', topic);

  // 保存到主题历史记录
  const topicsHistory = getUserData<any[]>('topicsHistory') || [];
  const exists = topicsHistory.some(t => t.title === topic.title);

  if (!exists) {
    // 生成唯一ID
    const id = `topic-${Date.now()}`;
    topicsHistory.push({
      ...topic,
      id
    });

    // 如果历史记录超过10个，删除最早的
    if (topicsHistory.length > 10) {
      topicsHistory.shift();
    }

    // 保存到用户存储
    saveUserData('topicsHistory', topicsHistory);
  }

  ElMessage.success(`已选择主题: ${formData.topic}`);
};

// 优化主题
const refineTopic = () => {
  router.push({
    name: 'TopicRefine',
    params: {
      topic: encodeURIComponent(formData.topic)
    }
  });
};

// 生成提纲
const generateOutline = () => {
  router.push({
    name: 'OutlineGenerate'
  });
};
</script>

<style scoped>
.topic-analyze-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.analyze-card, .result-card {
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

.analysis-result {
  margin-top: 20px;
}

.result-section {
  margin-bottom: 25px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.result-section h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.result-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.recommendation {
  background-color: #ecf5ff;
  border-left: 4px solid #409eff;
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

  .result-actions {
    flex-direction: column;
  }
}
</style>

<template>
  <div class="topic-refine-container">
    <el-card class="refine-card">
      <template #header>
        <div class="card-header">
          <h2>主题优化</h2>
          <p>根据您的反馈优化论文主题，使其更加明确和可行</p>
        </div>
      </template>
      
      <div class="refine-form">
        <el-form :model="formData" label-position="top" :rules="rules" ref="formRef">
          <el-form-item label="原始主题" prop="topic">
            <el-input
              v-model="formData.topic"
              placeholder="请输入原始论文主题"
            />
          </el-form-item>
          
          <el-form-item label="您的反馈" prop="feedback">
            <el-input
              v-model="formData.feedback"
              type="textarea"
              :rows="4"
              placeholder="请描述您希望如何改进这个主题，例如：缩小研究范围、更加具体化、调整研究方向等"
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
            <el-button type="primary" :loading="loading" @click="submitForm">优化主题</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <el-card v-if="refinedTopic" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>优化结果</h2>
        </div>
      </template>
      
      <div class="refine-result">
        <div class="comparison">
          <div class="original-topic">
            <h3>原始主题</h3>
            <p>{{ formData.topic }}</p>
          </div>
          
          <div class="arrow">
            <el-icon :size="24"><Right /></el-icon>
          </div>
          
          <div class="refined-topic">
            <h3>优化后的主题</h3>
            <p>{{ refinedTopic.refined_title }}</p>
          </div>
        </div>
        
        <el-divider />
        
        <div class="result-section">
          <h3>明确的研究问题</h3>
          <p>{{ refinedTopic.research_question }}</p>
        </div>
        
        <div class="result-section">
          <h3>研究范围</h3>
          <p>{{ refinedTopic.scope }}</p>
        </div>
        
        <div class="result-section">
          <h3>建议的研究方法</h3>
          <p>{{ refinedTopic.methodology }}</p>
        </div>
        
        <div class="result-section">
          <h3>关键词</h3>
          <div class="keywords">
            <el-tag v-for="(keyword, i) in refinedTopic.keywords" :key="i" size="small" class="keyword-tag">
              {{ keyword }}
            </el-tag>
          </div>
        </div>
        
        <div class="result-section improvements">
          <h3>改进之处</h3>
          <p>{{ refinedTopic.improvements }}</p>
        </div>
        
        <div class="result-actions">
          <el-button type="primary" @click="useRefinedTopic">使用此主题</el-button>
          <el-button type="success" @click="analyzeFeasibility">分析可行性</el-button>
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
import { Right } from '@element-plus/icons-vue';
import { refineTopic } from '@/api/modules/topics';
import type { TopicRefinementRequest, TopicRefinementResponse } from '@/types/topics';

const router = useRouter();
const route = useRoute();

// 表单数据
const formData = reactive<TopicRefinementRequest>({
  topic: '',
  feedback: '',
  academic_field: '',
  academic_level: ''
});

// 表单验证规则
const rules = {
  topic: [
    { required: true, message: '请输入原始论文主题', trigger: 'blur' },
    { min: 5, message: '主题不能少于5个字符', trigger: 'blur' }
  ],
  feedback: [
    { required: true, message: '请输入您的反馈', trigger: 'blur' },
    { min: 10, message: '反馈不能少于10个字符', trigger: 'blur' }
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
const refinedTopic = ref<TopicRefinementResponse | null>(null);

// 从路由参数中获取主题
onMounted(() => {
  const topicParam = route.params.topic;
  if (topicParam) {
    formData.topic = decodeURIComponent(topicParam as string);
  }
  
  // 从本地存储中获取选中的主题
  const selectedTopic = localStorage.getItem('selectedTopic');
  if (selectedTopic && !formData.topic) {
    try {
      const topic = JSON.parse(selectedTopic);
      formData.topic = topic.title;
      formData.academic_field = topic.academic_field;
      formData.academic_level = topic.academic_level;
    } catch (error) {
      console.error('解析选中主题失败:', error);
    }
  }
});

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const result = await refineTopic(formData);
        refinedTopic.value = result;
        ElMessage.success('主题优化完成');
      } catch (error) {
        console.error('优化主题失败:', error);
        ElMessage.error('优化主题失败，请稍后重试');
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
  refinedTopic.value = null;
};

// 使用优化后的主题
const useRefinedTopic = () => {
  if (!refinedTopic.value) return;
  
  // 将优化后的主题存储到本地存储
  localStorage.setItem('selectedTopic', JSON.stringify({
    title: refinedTopic.value.refined_title,
    academic_field: formData.academic_field,
    academic_level: formData.academic_level,
    keywords: refinedTopic.value.keywords
  }));
  
  ElMessage.success(`已选择主题: ${refinedTopic.value.refined_title}`);
};

// 分析可行性
const analyzeFeasibility = () => {
  if (!refinedTopic.value) return;
  
  router.push({
    name: 'TopicAnalyze',
    params: {
      topic: encodeURIComponent(refinedTopic.value.refined_title)
    }
  });
};

// 生成提纲
const generateOutline = () => {
  if (!refinedTopic.value) return;
  
  // 将优化后的主题存储到本地存储
  localStorage.setItem('selectedTopic', JSON.stringify({
    title: refinedTopic.value.refined_title,
    academic_field: formData.academic_field,
    academic_level: formData.academic_level,
    keywords: refinedTopic.value.keywords
  }));
  
  router.push({
    name: 'OutlineGenerate'
  });
};
</script>

<style scoped>
.topic-refine-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.refine-card, .result-card {
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

.refine-result {
  margin-top: 20px;
}

.comparison {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.original-topic, .refined-topic {
  flex: 1;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.refined-topic {
  background-color: #ecf5ff;
}

.arrow {
  margin: 0 20px;
  color: #909399;
}

.original-topic h3, .refined-topic h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.original-topic p, .refined-topic p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
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

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  margin-right: 5px;
}

.improvements {
  background-color: #f0f9eb;
  border-left: 4px solid #67c23a;
}

.result-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .comparison {
    flex-direction: column;
  }
  
  .arrow {
    margin: 20px 0;
    transform: rotate(90deg);
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>

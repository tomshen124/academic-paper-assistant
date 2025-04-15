<template>
  <div class="topic-recommend-container">
    <el-card class="topic-form-card">
      <template #header>
        <div class="card-header">
          <h2>论文主题推荐</h2>
          <p>根据您的研究兴趣和学术领域，我们将为您推荐合适的论文主题</p>
        </div>
      </template>
      
      <el-form :model="formData" label-position="top" :rules="rules" ref="formRef">
        <el-form-item label="研究兴趣" prop="user_interests">
          <el-input
            v-model="formData.user_interests"
            type="textarea"
            :rows="4"
            placeholder="请描述您的研究兴趣，例如：人工智能在医疗诊断中的应用"
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
          <el-button type="primary" :loading="loading" @click="submitForm">获取推荐主题</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="topics.length > 0" class="topic-results-card">
      <template #header>
        <div class="card-header">
          <h2>推荐主题</h2>
          <p>基于您的兴趣，我们推荐以下研究主题</p>
        </div>
      </template>
      
      <div class="topics-list">
        <el-collapse v-model="activeTopics">
          <el-collapse-item v-for="(topic, index) in topics" :key="index" :name="index">
            <template #title>
              <div class="topic-title">
                <span class="topic-number">{{ index + 1 }}</span>
                <h3>{{ topic.title }}</h3>
              </div>
            </template>
            
            <div class="topic-details">
              <div class="topic-detail-item">
                <h4>研究问题</h4>
                <p>{{ topic.research_question }}</p>
              </div>
              
              <div class="topic-detail-item">
                <h4>可行性</h4>
                <p>{{ topic.feasibility }}</p>
              </div>
              
              <div class="topic-detail-item">
                <h4>创新点</h4>
                <p>{{ topic.innovation }}</p>
              </div>
              
              <div class="topic-detail-item">
                <h4>研究方法</h4>
                <p>{{ topic.methodology }}</p>
              </div>
              
              <div class="topic-detail-item">
                <h4>所需资源</h4>
                <p>{{ topic.resources }}</p>
              </div>
              
              <div class="topic-detail-item">
                <h4>预期成果</h4>
                <p>{{ topic.expected_outcomes }}</p>
              </div>
              
              <div class="topic-detail-item">
                <h4>关键词</h4>
                <div class="keywords">
                  <el-tag v-for="(keyword, i) in topic.keywords" :key="i" size="small" class="keyword-tag">
                    {{ keyword }}
                  </el-tag>
                </div>
              </div>
              
              <div class="topic-actions">
                <el-button type="primary" @click="selectTopic(topic)">选择此主题</el-button>
                <el-button type="success" @click="analyzeFeasibility(topic)">分析可行性</el-button>
                <el-button @click="refineTopic(topic)">优化主题</el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage, FormInstance } from 'element-plus';
import { useRouter } from 'vue-router';
import { recommendTopics } from '@/api/modules/topics';
import type { TopicRequest, TopicResponse } from '@/types/topics';

const router = useRouter();

// 表单数据
const formData = reactive<TopicRequest>({
  user_interests: '',
  academic_field: '',
  academic_level: ''
});

// 表单验证规则
const rules = {
  user_interests: [
    { required: true, message: '请描述您的研究兴趣', trigger: 'blur' },
    { min: 10, message: '研究兴趣描述不能少于10个字符', trigger: 'blur' }
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
const topics = ref<TopicResponse[]>([]);
const activeTopics = ref<number[]>([0]); // 默认展开第一个主题

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const result = await recommendTopics(formData);
        topics.value = result;
        if (topics.value.length === 0) {
          ElMessage.warning('未找到匹配的主题，请尝试调整您的研究兴趣或学术领域');
        }
      } catch (error) {
        console.error('获取推荐主题失败:', error);
        ElMessage.error('获取推荐主题失败，请稍后重试');
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
  topics.value = [];
};

// 选择主题
const selectTopic = (topic: TopicResponse) => {
  // 将选中的主题存储到本地存储或状态管理中
  localStorage.setItem('selectedTopic', JSON.stringify(topic));
  ElMessage.success(`已选择主题: ${topic.title}`);
  
  // 导航到提纲生成页面
  router.push({
    name: 'OutlineGenerate',
    params: {
      topic: encodeURIComponent(topic.title)
    }
  });
};

// 分析可行性
const analyzeFeasibility = (topic: TopicResponse) => {
  router.push({
    name: 'TopicAnalyze',
    params: {
      topic: encodeURIComponent(topic.title)
    }
  });
};

// 优化主题
const refineTopic = (topic: TopicResponse) => {
  router.push({
    name: 'TopicRefine',
    params: {
      topic: encodeURIComponent(topic.title)
    }
  });
};
</script>

<style scoped>
.topic-recommend-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.topic-form-card {
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

.topics-list {
  margin-top: 20px;
}

.topic-title {
  display: flex;
  align-items: center;
}

.topic-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #409eff;
  color: white;
  font-weight: bold;
  margin-right: 15px;
}

.topic-title h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.topic-details {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.topic-detail-item {
  margin-bottom: 20px;
}

.topic-detail-item h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.topic-detail-item p {
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

.topic-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .topic-actions {
    flex-direction: column;
  }
}
</style>

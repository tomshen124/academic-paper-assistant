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

        <el-form-item label="推荐主题数量">
          <el-slider
            v-model="formData.topic_count"
            :min="1"
            :max="10"
            :step="1"
            :marks="topicCountMarks"
            show-stops
          />
          <div class="slider-description">
            <span>少量主题，更精准</span>
            <span>多量主题，更多选择</span>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm">获取推荐主题</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 加载中状态 -->
    <el-card v-if="loading" class="loading-card">
      <div class="loading-container">
        <el-skeleton :rows="5" animated />
        <div class="loading-text">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在生成主题，这可能需要一分钟左右的时间...</span>
        </div>
      </div>
    </el-card>

    <!-- 主题结果 -->
    <el-card v-if="topics.length > 0" class="topic-results-card">
      <template #header>
        <div class="card-header">
          <h2>推荐主题 ({{ topics.length }})</h2>
          <p>基于您的兴趣，我们推荐以下研究主题</p>
        </div>
      </template>

      <div class="topics-list">
        <!-- 显示主题总数 -->
        <div class="topics-summary">
          <el-alert
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              共找到 <strong>{{ topics.length }}</strong> 个推荐主题，点击展开查看详情
            </template>
          </el-alert>
        </div>

        <el-collapse v-model="activeTopics">
          <!-- 调试信息 -->
          <div class="debug-info" v-if="isDev">
            <p>主题数量: {{ topics.length }}</p>
            <pre>{{ JSON.stringify(topics, null, 2) }}</pre>
          </div>

          <el-collapse-item v-for="(topic, index) in topics" :key="index" :name="index">
            <template #title>
              <div class="topic-title">
                <span class="topic-number">{{ index + 1 }}</span>
                <h3>{{ topic.title || '未命名主题' }}</h3>
              </div>
            </template>

            <div class="topic-details">
              <div class="topic-detail-item">
                <h4>研究问题</h4>
                <p>{{ topic.research_question || '无研究问题' }}</p>
              </div>

              <div class="topic-detail-item">
                <h4>可行性</h4>
                <p>{{ topic.feasibility || '未评估' }}</p>
              </div>

              <div class="topic-detail-item">
                <h4>创新点</h4>
                <p>{{ topic.innovation || '无创新点' }}</p>
              </div>

              <div class="topic-detail-item">
                <h4>研究方法</h4>
                <p>{{ topic.methodology || '无研究方法' }}</p>
              </div>

              <div class="topic-detail-item">
                <h4>所需资源</h4>
                <p>{{ topic.resources || '无资源需求' }}</p>
              </div>

              <div class="topic-detail-item">
                <h4>预期成果</h4>
                <p>{{ topic.expected_outcomes || '无预期成果' }}</p>
              </div>

              <div class="topic-detail-item">
                <h4>关键词</h4>
                <div class="keywords" v-if="topic.keywords && topic.keywords.length > 0">
                  <el-tag v-for="(keyword, i) in topic.keywords" :key="i" size="small" class="keyword-tag">
                    {{ keyword }}
                  </el-tag>
                </div>
                <p v-else>无关键词</p>
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
import { Loading } from '@element-plus/icons-vue';
import { recommendTopics } from '@/api/modules/topics';
import { analyzeInterests } from '@/api/modules/interests';
import type { TopicRequest, TopicResponse } from '@/types/topics';

const router = useRouter();

// 判断是否为开发环境
// 在script中定义变量，而不是在模板中直接使用import.meta
// 这样可以避免模板解析错误
const isDev = import.meta.env.DEV;

// 表单数据
const formData = reactive<TopicRequest>({
  user_interests: '',
  academic_field: '',
  academic_level: '',
  topic_count: 3 // 默认推荐3个主题
});

// 主题数量标记
const topicCountMarks = {
  1: '1',
  3: '3',
  5: '5',
  7: '7',
  10: '10'
};

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
      topics.value = []; // 清空之前的主题数据

      try {
        // 显示正在生成的提示
        ElMessage.info('正在分析研究兴趣并生成主题，这可能需要一分钟左右的时间...');

        // 清除之前的主题数据，确保不会显示旧数据
        topics.value = [];

        // 第一步：分析用户兴趣
        console.log('开始分析用户兴趣...');
        const interestAnalysis = await analyzeInterests(formData);
        console.log('兴趣分析结果:', interestAnalysis);

        if (!interestAnalysis || Object.keys(interestAnalysis).length === 0) {
          ElMessage.warning('分析用户兴趣失败，请尝试修改您的输入或稍后重试');
          loading.value = false;
          return;
        }

        // 第二步：生成主题推荐
        console.log('开始生成主题推荐...');
        // 将兴趣分析结果添加到请求中，使后端可以使用这些信息
        const enhancedFormData = {
          ...formData,
          interest_analysis: interestAnalysis
        };

        const result = await recommendTopics(enhancedFormData);
        console.log('接收到的主题数据:', result);

        // 确保结果是数组
        if (Array.isArray(result) && result.length > 0) {
          // 深拷贝结果，避免引用问题
          topics.value = JSON.parse(JSON.stringify(result));
          console.log('设置主题数组:', topics.value);
        } else if (result && typeof result === 'object') {
          // 如果结果是单个对象，将其包装为数组
          topics.value = [JSON.parse(JSON.stringify(result))];
          console.log('设置单个主题对象:', topics.value);
        } else {
          // 如果结果为空或格式不正确，显示错误信息
          topics.value = [];
          ElMessage.warning('未能生成有效的主题，请尝试修改您的输入或稍后重试');
          console.error('返回的主题数据格式不正确或为空:', result);
          loading.value = false;
          return;
        }

        // 再次检查主题数组是否有效
        if (topics.value.length === 0) {
          ElMessage.warning('未能生成有效的主题，请尝试修改您的输入或稍后重试');
          loading.value = false;
          return;
        }

        console.log('设置后的topics值:', topics.value);
        console.log('主题数量:', topics.value.length);

        if (topics.value.length === 0) {
          ElMessage.warning('未找到匹配的主题，请尝试调整您的研究兴趣或学术领域');
        } else {
          ElMessage.success(`成功获取 ${topics.value.length} 个推荐主题`);
          // 强制展开所有主题
          activeTopics.value = topics.value.map((_, index) => index);

          // 滚动到主题列表
          setTimeout(() => {
            const topicsElement = document.querySelector('.topic-results-card');
            if (topicsElement) {
              topicsElement.scrollIntoView({ behavior: 'smooth' });
            }
          }, 100);
        }
      } catch (error) {
        console.error('获取推荐主题失败:', error);
        ElMessage.error('获取推荐主题失败，请稍后重试');
        topics.value = [];
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
  // 将选中的主题存储到本地存储
  const topicWithFields = {
    ...topic,
    academic_field: formData.academic_field,
    academic_level: formData.academic_level
  };
  localStorage.setItem('selectedTopic', JSON.stringify(topicWithFields));
  ElMessage.success(`已选择主题: ${topic.title}`);

  // 保存到主题历史记录
  saveTopicToHistory(topicWithFields);

  // 导航到提纲生成页面
  router.push({
    name: 'OutlineGenerate',
    params: {
      topic: encodeURIComponent(topic.title)
    }
  });
};

// 将主题保存到历史记录
const saveTopicToHistory = (topic: TopicResponse & { academic_field?: string, academic_level?: string }) => {
  // 从本地存储中获取历史记录
  let topicsHistory: Array<TopicResponse & { id: string }> = [];
  const historyStr = localStorage.getItem('topicsHistory');

  if (historyStr) {
    try {
      topicsHistory = JSON.parse(historyStr);
    } catch (error) {
      console.error('解析主题历史记录失败:', error);
    }
  }

  // 检查主题是否已存在
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

    // 保存到本地存储
    localStorage.setItem('topicsHistory', JSON.stringify(topicsHistory));
  }
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

.topics-summary {
  margin-bottom: 20px;
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

/* 调试信息样式 */
.debug-info {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.debug-info pre {
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
}

/* 加载中状态样式 */
.loading-card {
  margin-bottom: 30px;
}

.loading-container {
  padding: 20px 0;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  color: #909399;
}

/* 滑块描述样式 */
.slider-description {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}

.loading-text .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

@media (max-width: 768px) {
  .topic-actions {
    flex-direction: column;
  }
}
</style>

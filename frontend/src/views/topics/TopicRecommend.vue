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
          <el-select
            v-model="formData.academic_field"
            placeholder="请选择学术领域"
            style="width: 100%"
            @change="saveAcademicSettings"
          >
            <el-option v-for="field in academicFields" :key="field" :label="field" :value="field" />
          </el-select>
        </el-form-item>

        <el-form-item label="学术级别">
          <el-select
            v-model="formData.academic_level"
            placeholder="请选择学术级别"
            style="width: 100%"
            @change="saveAcademicSettings"
          >
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
          <span>正在生成主题，这可能需要一到两分钟的时间...</span>
          <div class="loading-tips">
            <p>提示：生成过程中请不要刷新页面或关闭浏览器标签页</p>
            <p>如果等待时间过长，可能是网络问题或服务器繁忙，请稍后再试</p>
          </div>
        </div>
        <el-progress :percentage="loadingProgress" :duration="120" :format="progressFormat" />
      </div>
    </el-card>

    <!-- 主题结果 -->
    <el-card v-if="topics.length > 0 || isLoadingSavedTopics" class="topic-results-card">
      <!-- 加载已保存主题的状态 -->
      <div v-if="isLoadingSavedTopics" class="loading-saved-topics">
        <el-skeleton :rows="3" animated />
        <div class="loading-text">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在加载已保存的主题...</span>
        </div>
      </div>
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

          <el-collapse-item v-for="(topic, index) in topics" :key="index" :name="index">
            <template #title>
              <div class="topic-title">
                <span class="topic-number">{{ index + 1 }}</span>
                <h3>{{ topic.title || '未命名主题' }}</h3>
                <span v-if="topic.created_at_formatted" class="topic-timestamp">
                  创建于: {{ topic.created_at_formatted }}
                </span>
              </div>
            </template>

            <div class="topic-details">
              <!-- 标题翻译 -->
              <div class="topic-detail-item">
                <h4>主题标题</h4>
                <translatable-content :original-content="topic.title || '未命名主题'" />
              </div>

              <!-- 研究问题翻译 -->
              <div class="topic-detail-item">
                <h4>研究问题</h4>
                <translatable-content :original-content="topic.research_question || '无研究问题'" />
              </div>

              <!-- 可行性翻译 -->
              <div class="topic-detail-item">
                <h4>可行性</h4>
                <translatable-content :original-content="topic.feasibility || '未评估'" />
              </div>

              <!-- 创新点翻译 -->
              <div class="topic-detail-item">
                <h4>创新点</h4>
                <translatable-content :original-content="topic.innovation || '无创新点'" />
              </div>

              <!-- 研究方法翻译 -->
              <div class="topic-detail-item">
                <h4>研究方法</h4>
                <translatable-content :original-content="topic.methodology || '无研究方法'" />
              </div>

              <!-- 所需资源翻译 -->
              <div class="topic-detail-item">
                <h4>所需资源</h4>
                <translatable-content :original-content="topic.resources || '无资源需求'" />
              </div>

              <!-- 预期成果翻译 -->
              <div class="topic-detail-item">
                <h4>预期成果</h4>
                <translatable-content :original-content="topic.expected_outcomes || '无预期成果'" />
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
import { ref, reactive, onUnmounted, onMounted } from 'vue';
import { saveUserData, getUserData } from '@/utils/userStorage';
import { ElMessage, FormInstance } from 'element-plus';
import { useRouter } from 'vue-router';
import { Loading } from '@element-plus/icons-vue';
import { recommendTopics, recommendTopicsStream, getUserTopics } from '@/api/modules/topics';
import { analyzeInterests } from '@/api/modules/interests';
import { translateContent } from '@/api/modules/translation';
import TranslatableContent from '@/components/Translation/TranslatableContent.vue';
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
const loadingProgress = ref(0);
const topics = ref<TopicResponse[]>([]);
const activeTopics = ref<number[]>([0]); // 默认展开第一个主题

// 标记是否为加载已保存的主题
const isLoadingSavedTopics = ref(false);

// 格式化日期时间
const formatDateTime = (dateTimeString: string) => {
  if (!dateTimeString) return '未知时间';
  const date = new Date(dateTimeString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 从后端获取已保存的主题
const fetchSavedTopics = async () => {
  try {
    isLoadingSavedTopics.value = true;
    const result = await getUserTopics();
    if (result && Array.isArray(result) && result.length > 0) {
      // 将已保存的主题转换为前端需要的格式，并添加时间信息
      topics.value = result.map(topic => ({
        id: topic.id,
        title: topic.title || '未命名主题',
        research_question: topic.research_question || '无研究问题',
        feasibility: topic.feasibility || '未评估',
        innovation: topic.innovation || '无创新点',
        methodology: topic.methodology || '无研究方法',
        resources: topic.resources || '无资源需求',
        expected_outcomes: topic.expected_outcomes || '无预期成果',
        keywords: Array.isArray(topic.keywords) ? topic.keywords : [],
        created_at: topic.created_at,
        created_at_formatted: formatDateTime(topic.created_at)
      }));

      // 按创建时间降序排序（最新的在前面）
      topics.value.sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
        const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
        return dateB - dateA;
      });

      // 默认展开第一个主题
      if (topics.value.length > 0) {
        activeTopics.value = [0];
      }

      console.log('获取到已保存的主题:', topics.value);
      ElMessage.info(`已加载${topics.value.length}个已保存的主题（按时间排序）`);
    }
  } catch (error) {
    console.error('获取已保存主题失败:', error);
  } finally {
    isLoadingSavedTopics.value = false;
  }
};

// 进度条格式化函数
const progressFormat = (percentage: number) => {
  return percentage < 100 ? `正在生成主题 ${percentage.toFixed(0)}%` : '生成完成';
};

// 在组件挂载时获取已保存的主题和学术设置
onMounted(() => {
  // 获取已保存的主题
  fetchSavedTopics();

  // 加载已保存的学术设置
  const savedSettings = getUserData<{academic_field: string; academic_level: string}>('academicSettings');
  if (savedSettings) {
    if (savedSettings.academic_field) {
      formData.academic_field = savedSettings.academic_field;
    }
    if (savedSettings.academic_level) {
      formData.academic_level = savedSettings.academic_level;
    }
    console.log('已加载学术设置:', savedSettings);
  }
});

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      loadingProgress.value = 0;
      topics.value = []; // 清空之前的主题数据

      // 启动进度条自动更新
      const progressInterval = setInterval(() => {
        if (loadingProgress.value < 95) {
          loadingProgress.value += 1;
        }
      }, 1000);

      try {
        // 显示正在生成的提示
        ElMessage.info('正在分析研究兴趣并生成主题，这可能需要一分钟左右的时间...');

        // 清除之前的主题数据，确保不会显示旧数据
        topics.value = [];

        // 使用流式推荐主题API
        console.log('开始流式生成主题...');

        // 定义事件处理函数
        const closeStream = recommendTopicsStream(formData, {
          // 状态更新
          onStatus: (message) => {
            console.log('状态更新:', message);
            ElMessage.info(message);
          },

          // 兴趣分析结果
          onInterestAnalysis: (data) => {
            console.log('兴趣分析结果:', data);
            // 可以在这里显示兴趣分析结果
            ElMessage.success('兴趣分析完成，正在生成主题...');

            // 更新进度
            loadingProgress.value = 30;
          },

          // 收到主题
          onTopic: (topic) => {
            console.log('收到主题:', topic);

            // 添加到主题列表
            topics.value.push(topic);

            // 展开新主题
            activeTopics.value.push(topics.value.length - 1);

            // 更新进度
            const progress = 30 + (topics.value.length / formData.topic_count) * 60;
            loadingProgress.value = Math.min(progress, 90);

            // 滚动到主题列表
            setTimeout(() => {
              const topicsElement = document.querySelector('.topic-results-card');
              if (topicsElement) {
                topicsElement.scrollIntoView({ behavior: 'smooth' });
              }
            }, 100);
          },

          // 完成
          onComplete: (message) => {
            console.log('生成完成:', message);
            ElMessage.success(`成功获取 ${topics.value.length} 个推荐主题`);

            // 设置进度为100%
            loadingProgress.value = 100;

            // 清除定时器
            clearInterval(progressInterval);

            // 关闭加载状态
            setTimeout(() => {
              loading.value = false;
            }, 1000);
          },

          // 错误处理
          onError: (message) => {
            console.error('生成主题错误:', message);
            ElMessage.error(`生成主题错误: ${message}`);

            // 清除定时器
            clearInterval(progressInterval);

            // 关闭加载状态
            loading.value = false;
          }
        });

        // 在组件卸载时关闭流
        onUnmounted(() => {
          closeStream();
        });

      } catch (error) {
        console.error('获取推荐主题失败:', error);
        ElMessage.error('获取推荐主题失败，请稍后重试');
        topics.value = [];

        // 清除定时器
        clearInterval(progressInterval);

        // 关闭加载状态
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
  // 确保主题有ID
  const topicId = topic.id || `topic-${Date.now()}`;

  // 将选中的主题存储到用户特定存储
  const topicWithFields = {
    ...topic,
    id: topicId, // 确保ID被包含
    academic_field: formData.academic_field,
    academic_level: formData.academic_level
  };
  saveUserData('selectedTopic', topicWithFields);
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
const saveTopicToHistory = (topic: TopicResponse) => {
  // 从用户存储获取历史记录
  let topicsHistory = getUserData<any[]>('topicsHistory') || [];

  // 检查是否已存在
  const exists = topicsHistory.some((t: any) => t.title === topic.title);
  if (!exists) {
    // 添加新主题到历史记录
    topicsHistory.unshift({
      ...topic,
      timestamp: new Date().toISOString()
    });

    // 限制记录数量
    if (topicsHistory.length > 20) {
      topicsHistory = topicsHistory.slice(0, 20);
    }

    // 保存到用户存储
    saveUserData('topicsHistory', topicsHistory);
  }
};

// 保存学术领域和学术级别设置
const saveAcademicSettings = () => {
  if (formData.academic_field || formData.academic_level) {
    // 保存学术设置到用户存储
    const academicSettings = {
      academic_field: formData.academic_field,
      academic_level: formData.academic_level
    };
    saveUserData('academicSettings', academicSettings);
    console.log('已保存学术设置:', academicSettings);
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
/* 加载已保存主题的样式 */
.loading-saved-topics {
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.loading-saved-topics .loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 15px;
  color: #606266;
}

.loading-saved-topics .loading-text .el-icon {
  margin-right: 10px;
}

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
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.topic-timestamp {
  margin-left: 10px;
  font-size: 0.8rem;
  font-weight: normal;
  color: #909399;
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
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
  color: #909399;
}

.loading-text > span {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 16px;
}

.loading-tips {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f8f8;
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
  max-width: 600px;
  text-align: center;
}

.loading-tips p {
  margin: 5px 0;
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

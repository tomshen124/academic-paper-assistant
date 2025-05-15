<template>
  <div class="outline-generate-container">
    <el-card class="outline-form-card">
      <template #header>
        <div class="card-header">
          <h2>论文提纲生成</h2>
          <p>根据您的主题和要求，我们将为您生成详细的论文提纲</p>
        </div>
      </template>

      <el-form :model="formData" label-position="top" :rules="rules" ref="formRef">
        <el-form-item label="选择已有主题">
          <el-select
            v-model="selectedTopicId"
            placeholder="选择已有主题"
            style="width: 100%"
            @change="handleTopicChange"
            clearable
          >
            <el-option
              v-for="topic in savedTopics"
              :key="topic.id"
              :label="topic.title"
              :value="topic.id"
            />
          </el-select>
          <div class="topic-actions" v-if="selectedTopicId">
            <el-button type="text" @click="goToTopicRecommend">生成新主题</el-button>
            <el-button type="text" @click="clearSelectedTopic">清除选择</el-button>
          </div>
        </el-form-item>

        <el-form-item label="论文主题" prop="topic">
          <el-input
            v-model="formData.topic"
            placeholder="请输入论文主题"
            @input="handleManualTopicInput"
          />
        </el-form-item>

        <el-form-item label="论文类型" prop="paper_type">
          <el-select v-model="formData.paper_type" placeholder="请选择论文类型" style="width: 100%">
            <el-option v-for="type in paperTypes" :key="type" :label="type" :value="type" />
          </el-select>
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

        <el-form-item label="预期长度">
          <el-select v-model="formData.length" placeholder="请选择预期长度" style="width: 100%">
            <el-option v-for="length in paperLengths" :key="length" :label="length" :value="length" />
          </el-select>
        </el-form-item>

        <div class="outline-form-actions">
          <el-button type="primary" :loading="loading" @click="submitForm">生成提纲</el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button type="info" @click="getTemplates">查看提纲模板</el-button>
          <el-button type="success" @click="savedOutlinesDialogVisible = true" :disabled="savedOutlines.length === 0">
            浏览已保存提纲 <el-badge v-if="savedOutlines.length > 0" :value="savedOutlines.length" />
          </el-button>
        </div>
      </el-form>
    </el-card>

    <el-card v-if="outline" class="outline-result-card">
      <template #header>
        <div class="card-header">
          <h2>{{ outline.title }}</h2>
          <div class="outline-meta">
            <div class="keywords">
              <span class="meta-label">关键词：</span>
              <el-tag v-for="(keyword, i) in outline.keywords" :key="i" size="small" class="keyword-tag">
                {{ keyword }}
              </el-tag>
            </div>
          </div>
        </div>
      </template>

      <div class="outline-content">
        <div class="abstract-section">
          <h3>摘要</h3>
          <translatable-content :original-content="outline.abstract" />
        </div>

        <div class="sections-container">
          <h3>论文结构</h3>

          <el-tree
            :data="formatSections(outline.sections)"
            :props="defaultProps"
            node-key="id"
            default-expand-all
          >
            <template #default="{ node, data }">
              <div class="section-node">
                <span class="section-title">{{ data.title }}</span>
                <span v-if="data.expected_length" class="section-length">({{ data.expected_length }})</span>
                <el-popover
                  placement="right"
                  :width="300"
                  trigger="click"
                  v-if="data.purpose || data.content_points"
                >
                  <template #reference>
                    <el-button size="small" type="primary" text circle>
                      <el-icon><InfoFilled /></el-icon>
                    </el-button>
                  </template>
                  <div class="section-details">
                    <div v-if="data.purpose" class="section-purpose">
                      <h4>目的</h4>
                      <translatable-content :original-content="data.purpose" />
                    </div>
                    <div v-if="data.content_points && data.content_points.length > 0" class="section-points">
                      <h4>内容要点</h4>
                      <ul>
                        <li v-for="(point, i) in data.content_points" :key="i">
                          <translatable-content :original-content="point" />
                        </li>
                      </ul>
                    </div>
                  </div>
                </el-popover>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <div class="outline-actions">
        <el-button type="primary" @click="useOutline">使用此提纲</el-button>
        <el-button type="success" @click="optimizeOutline">优化提纲</el-button>
        <el-button @click="validateOutline">验证提纲</el-button>
        <el-button type="warning" @click="generatePaper">生成论文</el-button>
      </div>
    </el-card>

    <!-- 提纲模板对话框 -->
    <el-dialog
      v-model="templatesDialogVisible"
      title="提纲模板"
      width="70%"
    >
      <div v-if="templates.length > 0" class="templates-container">
        <el-collapse v-model="activeTemplate">
          <el-collapse-item v-for="(template, index) in templates" :key="index" :name="index">
            <template #title>
              <div class="template-title">
                <h3>{{ template.name }}</h3>
                <span class="template-suitable">适用于: {{ template.suitable_for }}</span>
              </div>
            </template>

            <div class="template-details">
              <h4>结构</h4>
              <ul class="template-structure">
                <li v-for="(item, i) in template.structure" :key="i">{{ item.title }}</li>
              </ul>

              <h4>特点</h4>
              <ul class="template-features">
                <li v-for="(feature, i) in template.features" :key="i">{{ feature }}</li>
              </ul>

              <el-button type="primary" @click="applyTemplate(template)">应用此模板</el-button>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      <div v-else class="no-templates">
        <el-empty description="暂无可用模板" />
      </div>
    </el-dialog>

    <!-- 已保存提纲对话框 -->
    <el-dialog
      v-model="savedOutlinesDialogVisible"
      title="已保存的提纲"
      width="800px"
    >
      <div class="saved-outlines-container">
        <div v-if="isLoadingSavedOutlines" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="savedOutlines.length === 0" class="empty-outlines">
          <el-empty description="暂无已保存的提纲" />
        </div>

        <div v-else class="saved-outlines-list">
          <el-table :data="savedOutlines" style="width: 100%" stripe>
            <el-table-column prop="title" label="提纲标题" min-width="200">
              <template #default="{row}">
                <div class="outline-title">
                  {{ row.title || '未命名提纲' }}
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="topic" label="论文主题" min-width="150" />

            <el-table-column prop="paper_type" label="论文类型" width="120" />

            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{row}">
                {{ new Date(row.created_at).toLocaleString('zh-CN') }}
              </template>
            </el-table-column>

            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{row}">
                <el-button type="primary" size="small" @click="loadOutlineById(row.id); savedOutlinesDialogVisible = false">
                  加载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { saveUserData, getUserData } from '@/utils/userStorage';
import { ElMessage, FormInstance, ElMessageBox } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { InfoFilled } from '@element-plus/icons-vue';
import { generateOutline, getOutlineTemplates, getUserOutlines, getOutlineById } from '@/api/modules/outlines';
import { translateContent } from '@/api/modules/translation';
import TranslatableContent from '@/components/Translation/TranslatableContent.vue';
import type { OutlineRequest, OutlineResponse, OutlineTemplate } from '@/types/outlines';
import type { Section, SubSection } from '@/types/outlines';
import type { TopicResponse } from '@/types/topics';

const router = useRouter();
const route = useRoute();

// 表单数据
const formData = reactive<OutlineRequest>({
  topic: '',
  paper_type: '',
  academic_field: '',
  academic_level: '',
  length: ''
});

// 表单验证规则
const rules = {
  topic: [
    { required: true, message: '请输入论文主题', trigger: 'blur' },
    { min: 5, message: '主题不能少于5个字符', trigger: 'blur' }
  ],
  paper_type: [
    { required: true, message: '请选择论文类型', trigger: 'change' }
  ],
  academic_field: [
    { required: true, message: '请选择学术领域', trigger: 'change' }
  ]
};

// 论文类型选项
const paperTypes = [
  '综述',
  '实验研究',
  '理论研究',
  '案例分析',
  '调查研究',
  '比较研究',
  '方法学研究',
  '应用研究'
];

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

// 论文长度选项
const paperLengths = [
  '3000字',
  '5000字',
  '8000字',
  '10000字',
  '15000字',
  '20000字',
  '30000字'
];

const formRef = ref<FormInstance>();
const loading = ref(false);
// 提纲数据
const outline = ref<OutlineResponse | null>(null);

// 保存的提纲列表
const savedOutlines = ref<any[]>([]);

// 加载已保存的提纲状态
const isLoadingSavedOutlines = ref(false);

// 获取用户已保存的提纲
const fetchSavedOutlines = async () => {
  try {
    isLoadingSavedOutlines.value = true;
    const result = await getUserOutlines(0, 10); // 获取最新的10个提纲

    if (result && Array.isArray(result) && result.length > 0) {
      savedOutlines.value = result;
      console.log('获取到已保存的提纲:', savedOutlines.value);
      ElMessage.info(`已加载${savedOutlines.value.length}个已生成的提纲`);

      // 如果本地没有已选择的提纲，但服务器有保存的提纲，可以浏览最近生成的提纲
      if (!outline.value && savedOutlines.value.length > 0) {
        const lastOutline = savedOutlines.value[0]; // 获取最新的提纲
        const shouldLoadLastOutline = await ElMessageBox.confirm(
          `发现您有一个最近生成的提纲："${lastOutline.title}"，是否要加载该提纲？`,
          '加载已有提纲',
          {
            confirmButtonText: '是',
            cancelButtonText: '否',
            type: 'info',
          }
        ).catch(() => false);

        if (shouldLoadLastOutline) {
          loadOutlineById(lastOutline.id);
        }
      }
    }
  } catch (error) {
    console.error('获取已保存提纲失败:', error);
  } finally {
    isLoadingSavedOutlines.value = false;
  }
};

// 根据ID加载提纲
const loadOutlineById = async (outlineId: number) => {
  if (!outlineId) return;

  try {
    loading.value = true;
    const result = await getOutlineById(outlineId);
    if (result) {
      outline.value = result;

      // 更新表单数据
      if (result.topic) {
        formData.topic = result.topic;
      }
      if (result.academic_field) {
        formData.academic_field = result.academic_field;
      }
      if (result.paper_type) {
        formData.paper_type = result.paper_type;
      }

      ElMessage.success(`已加载提纲: ${result.title || '未命名提纲'}`);
    }
  } catch (error) {
    console.error('加载提纲失败:', error);
    ElMessage.error('加载提纲失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 展示提纲模板对话框
const templatesDialogVisible = ref(false);
const templates = ref<OutlineTemplate[]>([]);
const activeTemplate = ref<number[]>([0]);

// 展示已保存提纲对话框
const savedOutlinesDialogVisible = ref(false);

// 选题相关状态
const savedTopics = ref<Array<TopicResponse & { id: string }>>([]);
const selectedTopicId = ref<string>('');

// 树形控件配置
const defaultProps = {
  children: 'children',
  label: 'title'
};

// 格式化章节数据为树形结构
const formatSections = (sections: Section[]) => {
  return sections.map((section) => {
    const result: any = {
      id: section.id,
      title: section.title,
      purpose: section.purpose,
      content_points: section.content_points,
      expected_length: section.expected_length
    };

    if (section.subsections && section.subsections.length > 0) {
      result.children = section.subsections.map((subsection: SubSection) => ({
        id: `${section.id}-${subsection.id}`,
        title: subsection.title,
        purpose: subsection.purpose,
        content_points: subsection.content_points,
        expected_length: subsection.expected_length
      }));
    }

    return result;
  });
};

// 加载保存的主题和提纲
onMounted(async () => {
  // 加载已保存的提纲
  await fetchSavedOutlines();
  // 加载保存的所有选题
  loadSavedTopics();

  const topicParam = route.params.topic;
  if (topicParam) {
    formData.topic = decodeURIComponent(topicParam as string);
  }

  // 从本地存储中获取选中的主题
  const selectedTopic = getUserData<any>('selectedTopic');
  if (selectedTopic) {
    try {
      formData.topic = selectedTopic.title;
      formData.academic_field = selectedTopic.academic_field || formData.academic_field;
      formData.academic_level = selectedTopic.academic_level || formData.academic_level;

      // 如果该主题已经在保存的主题列表中，选中它
      const existingTopic = savedTopics.value.find(t => t.title === selectedTopic.title);
      if (existingTopic) {
        selectedTopicId.value = existingTopic.id;
      }
    } catch (error) {
      console.error('解析选中主题失败:', error);
    }
  } else {
    // 如果没有选中的主题，尝试从学术设置中加载
    const academicSettings = getUserData<{academic_field: string; academic_level: string}>('academicSettings');
    if (academicSettings) {
      if (academicSettings.academic_field) {
        formData.academic_field = academicSettings.academic_field;
      }
      if (academicSettings.academic_level) {
        formData.academic_level = academicSettings.academic_level;
      }
      console.log('已加载学术设置:', academicSettings);
    }
  }
});

// 从用户存储中加载保存的所有选题
const loadSavedTopics = () => {
  // 从历史记录中加载
  const topicsHistory = getUserData<any[]>('topicsHistory');
  if (topicsHistory) {
    savedTopics.value = topicsHistory;
  } else {
    savedTopics.value = [];
  }

  // 如果有选中的主题但不在历史中，添加到历史
  const selectedTopic = getUserData<any>('selectedTopic');
  if (selectedTopic) {
    console.log('从本地存储加载的选中主题:', selectedTopic);

    // 检查是否已存在相同标题的主题
    const existingTopic = savedTopics.value.find(t => t.title === selectedTopic.title);

    if (existingTopic) {
      // 如果存在，使用现有主题的ID
      console.log('找到匹配的主题:', existingTopic);
      selectedTopicId.value = existingTopic.id;
    } else {
      // 如果不存在，添加到历史记录
      // 确保主题有ID
      const topicId = selectedTopic.id || `topic-${Date.now()}`;
      const newTopic = {
        ...selectedTopic,
        id: topicId
      };

      savedTopics.value.push(newTopic);
      selectedTopicId.value = topicId;

      // 保存到用户存储
      saveUserData('topicsHistory', savedTopics.value);
      console.log('添加新主题到历史记录:', newTopic);
    }
  }

  console.log('加载到的主题列表:', savedTopics.value);
  console.log('当前选中的主题ID:', selectedTopicId.value);
};

// 处理选题变化
const handleTopicChange = (topicId: string) => {
  if (!topicId) {
    return;
  }

  const selectedTopic = savedTopics.value.find(t => t.id === topicId);
  if (selectedTopic) {
    // 如果已经有提纲且主题不同，则提示用户
    if (outline.value && formData.topic !== selectedTopic.title) {
      ElMessageBox.confirm(
        '更换主题将清除当前提纲，是否继续？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(() => {
        // 更新表单数据
        updateFormWithTopic(selectedTopic);
        // 清除提纲
        outline.value = null;
      }).catch(() => {
        // 恢复选择
        selectedTopicId.value = '';
      });
    } else {
      // 直接更新表单
      updateFormWithTopic(selectedTopic);
    }
  }
};

// 使用选中的主题更新表单
const updateFormWithTopic = (topic: TopicResponse & { id: string }) => {
  formData.topic = topic.title;
  if (topic.academic_field) {
    formData.academic_field = topic.academic_field;
  }
  if (topic.academic_level) {
    formData.academic_level = topic.academic_level;
  }

  // 将选中的主题保存到用户存储
  saveUserData('selectedTopic', topic);
  ElMessage.success(`已选择主题: ${topic.title}`);
};

// 清除选中的主题
const clearSelectedTopic = () => {
  selectedTopicId.value = '';
  // 不清除表单中的主题，只清除选择
};

// 处理手动输入主题
const handleManualTopicInput = () => {
  // 当用户手动输入主题时，清除选中的主题ID
  if (selectedTopicId.value) {
    selectedTopicId.value = '';
  }

  // 创建一个新的主题对象，包含当前输入的主题和学术设置
  const manualTopic = {
    title: formData.topic,
    academic_field: formData.academic_field,
    academic_level: formData.academic_level
  };

  // 保存到用户存储
  saveUserData('manualTopic', manualTopic);
};

// 前往主题推荐页面
const goToTopicRecommend = () => {
  router.push({ name: 'TopicRecommend' });
};

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        // 如果是手动输入的主题，保存到manualTopic
        if (!selectedTopicId.value) {
          const manualTopic = {
            title: formData.topic,
            academic_field: formData.academic_field,
            academic_level: formData.academic_level
          };
          saveUserData('manualTopic', manualTopic);
        }

        // 保存学术设置
        const academicSettings = {
          academic_field: formData.academic_field,
          academic_level: formData.academic_level
        };
        saveUserData('academicSettings', academicSettings);

        const result = await generateOutline(formData);
        outline.value = result;

        // 将生成的提纲与表单数据关联
        const outlineWithFormData = {
          ...result,
          topic: formData.topic,
          academic_field: formData.academic_field,
          academic_level: formData.academic_level,
          paper_type: formData.paper_type
        };

        // 保存到用户存储
        saveUserData('currentOutline', outlineWithFormData);

        ElMessage.success('提纲生成成功');
      } catch (error) {
        console.error('生成提纲失败:', error);
        ElMessage.error('生成提纲失败，请稍后重试');
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
  outline.value = null;
};

// 获取提纲模板
const getTemplates = async () => {
  if (!formData.paper_type || !formData.academic_field) {
    ElMessage.warning('请先选择论文类型和学术领域');
    return;
  }

  try {
    loading.value = true;
    const result = await getOutlineTemplates({
      paper_type: formData.paper_type,
      academic_field: formData.academic_field
    });
    templates.value = result;
    templatesDialogVisible.value = true;

    if (templates.value.length === 0) {
      ElMessage.info('暂无匹配的提纲模板');
    }
  } catch (error) {
    console.error('获取提纲模板失败:', error);
    ElMessage.error('获取提纲模板失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 应用模板
const applyTemplate = (template: OutlineTemplate) => {
  // 将模板应用到表单
  templatesDialogVisible.value = false;
  ElMessage.success(`已应用模板: ${template.name}`);

  // 重新生成提纲
  submitForm();
};

// 使用提纲
const useOutline = () => {
  if (!outline.value) return;

  // 将提纲存储到用户存储，并添加学术领域和学术级别
  const outlineWithSettings = {
    ...outline.value,
    topic: formData.topic, // 确保包含主题
    academic_field: formData.academic_field,
    academic_level: formData.academic_level,
    paper_type: formData.paper_type
  };
  saveUserData('selectedOutline', outlineWithSettings);

  // 同时更新学术设置
  const academicSettings = {
    academic_field: formData.academic_field,
    academic_level: formData.academic_level
  };
  saveUserData('academicSettings', academicSettings);

  // 如果是手动输入的主题，也保存到manualTopic
  if (!selectedTopicId.value) {
    const manualTopic = {
      title: formData.topic,
      academic_field: formData.academic_field,
      academic_level: formData.academic_level
    };
    saveUserData('manualTopic', manualTopic);
  }

  ElMessage.success('已选择此提纲');

  // 导航到论文生成页面
  router.push({
    name: 'PaperGenerate'
  });
};

// 优化提纲
const optimizeOutline = () => {
  if (!outline.value) return;

  router.push({
    name: 'OutlineOptimize',
    params: {
      id: 'current'
    }
  });
};

// 验证提纲
const validateOutline = () => {
  if (!outline.value) return;

  router.push({
    name: 'OutlineValidate',
    params: {
      id: 'current'
    }
  });
};

// 生成论文
const generatePaper = () => {
  if (!outline.value) return;

  router.push({
    name: 'PaperGenerate'
  });
};
</script>

<style scoped>
.outline-generate-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.outline-form-card {
  margin-bottom: 30px;
}

.topic-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
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

.outline-meta {
  display: flex;
  margin-top: 10px;
}

.meta-label {
  font-weight: bold;
  margin-right: 10px;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.keyword-tag {
  margin-right: 5px;
}

.outline-content {
  margin-top: 20px;
}

.abstract-section {
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.abstract-section h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
}

.abstract-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.sections-container {
  margin-bottom: 30px;
}

.sections-container h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.section-node {
  display: flex;
  align-items: center;
  height: 32px;
}

.section-title {
  font-weight: bold;
}

.section-length {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.section-details h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.section-details p {
  margin: 0 0 10px 0;
  color: #606266;
}

.section-details ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.outline-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
}

.template-title {
  display: flex;
  align-items: center;
}

.template-title h3 {
  margin: 0;
  font-size: 16px;
}

.template-suitable {
  margin-left: 15px;
  color: #909399;
  font-size: 12px;
}

.template-details {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.template-details h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.template-structure, .template-features {
  margin: 0 0 20px 0;
  padding-left: 20px;
  color: #606266;
}

.no-templates {
  padding: 30px 0;
}

@media (max-width: 768px) {
  .outline-actions {
    flex-direction: column;
  }
}
</style>

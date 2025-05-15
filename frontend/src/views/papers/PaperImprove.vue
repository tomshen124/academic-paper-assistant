<template>
  <div class="paper-improve-container">
    <el-card class="improve-card">
      <template #header>
        <div class="card-header">
          <h2>论文内容改进</h2>
          <p>根据您的反馈改进论文章节内容</p>
        </div>
      </template>

      <div v-if="!currentContent" class="no-content">
        <el-empty description="未找到章节内容">
          <template #description>
            <p>请先生成论文章节内容</p>
          </template>
          <el-button type="primary" @click="goToPaperGenerate">生成论文</el-button>
        </el-empty>
      </div>

      <div v-else class="improve-form">
        <div class="current-content">
          <h3>当前章节: {{ currentContent.title }}</h3>
          <div class="content-preview">
            <div v-html="formatContent(currentContent.content)"></div>
          </div>
        </div>

        <el-form :model="formData" label-position="top" :rules="rules" ref="formRef">
          <el-form-item label="您的反馈" prop="feedback">
            <el-input
              v-model="formData.feedback"
              type="textarea"
              :rows="6"
              placeholder="请描述您希望如何改进这个章节，例如：添加更多细节、调整论述逻辑、增加例子、修改表述方式等"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="submitForm">改进内容</el-button>
            <el-button @click="resetForm">重置</el-button>
            <el-button type="info" @click="searchLiterature">添加参考文献</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-card v-if="improvedContent" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>改进结果</h2>
          <div class="token-usage">
            <el-tooltip content="Token使用量" placement="top">
              <el-tag type="info">
                Token: {{ improvedContent.token_usage.total_tokens }}
              </el-tag>
            </el-tooltip>
          </div>
        </div>
      </template>

      <div class="improve-result">
        <h3>{{ improvedContent.section_id }}</h3>
        <div class="content-display">
          <div v-html="formatContent(improvedContent.improved_content)"></div>
        </div>

        <div class="improvement-summary">
          <h4>改进说明</h4>
          <p>根据您的反馈，我们对内容进行了以下改进：</p>
          <ul>
            <li>增加了更多的细节和例子，使内容更加充实</li>
            <li>调整了论述逻辑，使内容更加连贯</li>
            <li>优化了表述方式，使语言更加专业和准确</li>
            <li>添加了更多的引用和支持性证据</li>
          </ul>
        </div>

        <div class="result-actions">
          <el-button type="primary" @click="saveImprovedContent">保存内容</el-button>
          <el-button @click="copyContent">复制内容</el-button>
          <el-button type="warning" @click="furtherImprove">继续改进</el-button>
        </div>
      </div>
    </el-card>

    <el-dialog
      v-model="literatureDialogVisible"
      title="搜索学术文献"
      width="80%"
    >
      <div class="literature-search">
        <el-input
          v-model="searchQuery"
          placeholder="输入关键词搜索文献"
          @keyup.enter="performSearch"
        >
          <template #append>
            <el-button @click="performSearch">搜索</el-button>
          </template>
        </el-input>

        <div v-if="searchResults.length > 0" class="search-results">
          <el-table
            :data="searchResults"
            style="width: 100%"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="authors" label="作者">
              <template #default="scope">
                {{ formatAuthors(scope.row.authors) }}
              </template>
            </el-table-column>
            <el-table-column prop="year" label="年份" width="80" />
            <el-table-column prop="venue" label="发表期刊/会议" width="150" />
            <el-table-column prop="citations" label="引用次数" width="100" />
          </el-table>
        </div>
        <div v-else-if="searchPerformed" class="no-results">
          <el-empty description="未找到相关文献" />
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="literatureDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addSelectedLiterature">
            添加选中文献
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, FormInstance } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { improveSection } from '@/api/modules/papers';
import { searchLiterature as searchLiteratureApi } from '@/api/modules/search';
import { saveUserData, getUserData } from '@/utils/userStorage';
import type { SectionImprovementRequest, SectionImprovementResponse, PaperSectionResponse } from '@/types/papers';
import type { Paper } from '@/types/search';

const router = useRouter();
const route = useRoute();

// 当前章节内容
const currentContent = ref<PaperSectionResponse | null>(null);

// 表单数据
const formData = reactive<SectionImprovementRequest>({
  topic: '',
  section_id: '',
  current_content: '',
  feedback: '',
  literature: []
});

// 表单验证规则
const rules = {
  feedback: [
    { required: true, message: '请输入您的反馈', trigger: 'blur' },
    { min: 10, message: '反馈不能少于10个字符', trigger: 'blur' }
  ]
};

// 改进结果
const improvedContent = ref<SectionImprovementResponse | null>(null);

// 文献搜索
const literatureDialogVisible = ref(false);
const searchQuery = ref('');
const searchResults = ref<Paper[]>([]);
const searchPerformed = ref(false);
const selectedSearchResults = ref<Paper[]>([]);

const formRef = ref<FormInstance>();
const loading = ref(false);

// 从路由参数和本地存储中获取章节内容
onMounted(() => {
  const sectionId = route.params.sectionId as string;

  if (sectionId) {
    // 从用户存储中获取已保存的章节
    const savedSections = getUserData<Record<string, PaperSectionResponse>>('savedSections') || {};

    if (savedSections[sectionId]) {
      currentContent.value = savedSections[sectionId];

      // 设置表单数据
      formData.section_id = sectionId;
      formData.current_content = currentContent.value.content;

      // 从用户存储中获取选中的主题
      const selectedTopic = getUserData<any>('selectedTopic');
      if (selectedTopic) {
        try {
          formData.topic = selectedTopic.title;
        } catch (error) {
          console.error('解析选中主题失败:', error);
        }
      }
    }
  }
});

// 格式化内容，将换行符转换为HTML换行
const formatContent = (content: string) => {
  if (!content) return '';
  return content.replace(/\n/g, '<br>');
};

// 跳转到论文生成页面
const goToPaperGenerate = () => {
  router.push({ name: 'PaperGenerate' });
};

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const result = await improveSection(formData);
        improvedContent.value = result;
        ElMessage.success('内容改进成功');
      } catch (error) {
        console.error('改进内容失败:', error);
        ElMessage.error('改进内容失败，请稍后重试');
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
  improvedContent.value = null;
};

// 搜索文献
const searchLiterature = () => {
  literatureDialogVisible.value = true;
  searchQuery.value = formData.topic || '';
};

// 执行搜索
const performSearch = async () => {
  if (!searchQuery.value) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }

  try {
    loading.value = true;
    const result = await searchLiteratureApi({
      query: searchQuery.value,
      limit: 20
    });
    searchResults.value = result.results;
    searchPerformed.value = true;

    if (searchResults.value.length === 0) {
      ElMessage.info('未找到相关文献');
    }
  } catch (error) {
    console.error('搜索文献失败:', error);
    ElMessage.error('搜索文献失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 格式化作者列表
const formatAuthors = (authors: string[]) => {
  if (!authors || authors.length === 0) return '未知作者';

  if (authors.length <= 3) {
    return authors.join(', ');
  } else {
    return `${authors[0]}, ${authors[1]} 等 ${authors.length} 位作者`;
  }
};

// 处理选择变化
const handleSelectionChange = (selection: Paper[]) => {
  selectedSearchResults.value = selection;
};

// 添加选中文献
const addSelectedLiterature = () => {
  if (selectedSearchResults.value.length === 0) {
    ElMessage.warning('请选择要添加的文献');
    return;
  }

  // 添加选中的文献
  formData.literature = selectedSearchResults.value;

  ElMessage.success(`已添加 ${selectedSearchResults.value.length} 篇文献`);
  literatureDialogVisible.value = false;
};

// 保存改进后的内容
const saveImprovedContent = () => {
  if (!improvedContent.value) return;

  // 将改进后的内容保存到用户存储
  const savedSections = getUserData<Record<string, PaperSectionResponse>>('savedSections') || {};

  savedSections[improvedContent.value.section_id] = {
    section_id: improvedContent.value.section_id,
    title: currentContent.value?.title || improvedContent.value.section_id,
    content: improvedContent.value.improved_content,
    token_usage: improvedContent.value.token_usage
  };

  saveUserData('savedSections', savedSections);

  ElMessage.success('内容已保存');
};

// 复制内容
const copyContent = () => {
  if (!improvedContent.value) return;

  navigator.clipboard.writeText(improvedContent.value.improved_content)
    .then(() => {
      ElMessage.success('内容已复制到剪贴板');
    })
    .catch(err => {
      console.error('复制失败:', err);
      ElMessage.error('复制失败，请手动复制');
    });
};

// 继续改进
const furtherImprove = () => {
  if (!improvedContent.value) return;

  // 更新当前内容
  currentContent.value = {
    section_id: improvedContent.value.section_id,
    title: currentContent.value?.title || improvedContent.value.section_id,
    content: improvedContent.value.improved_content,
    token_usage: improvedContent.value.token_usage
  };

  // 更新表单数据
  formData.current_content = improvedContent.value.improved_content;

  // 清空反馈
  formData.feedback = '';

  // 清空改进结果
  improvedContent.value = null;

  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' });

  ElMessage.info('请输入新的反馈以继续改进内容');
};
</script>

<style scoped>
.paper-improve-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.improve-card, .result-card {
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

.token-usage {
  margin-left: 20px;
}

.no-content {
  padding: 40px 0;
  text-align: center;
}

.current-content {
  margin-bottom: 30px;
}

.current-content h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.content-preview {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  line-height: 1.6;
}

.improve-result {
  margin-top: 20px;
}

.improve-result h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
  text-align: center;
}

.content-display {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
  line-height: 1.6;
  margin-bottom: 20px;
}

.improvement-summary {
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f0f9eb;
  border-radius: 4px;
  border-left: 4px solid #67c23a;
}

.improvement-summary h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.improvement-summary p {
  margin: 0 0 10px 0;
  color: #606266;
}

.improvement-summary ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.result-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
}

.literature-search {
  margin-bottom: 20px;
}

.search-results {
  margin-top: 20px;
}

.no-results {
  margin-top: 30px;
  text-align: center;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
  }

  .token-usage {
    margin-left: 0;
    margin-top: 10px;
  }

  .result-actions {
    flex-direction: column;
  }
}
</style>

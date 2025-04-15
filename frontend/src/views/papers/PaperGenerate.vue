<template>
  <div class="paper-generate-container">
    <el-card class="paper-form-card">
      <template #header>
        <div class="card-header">
          <h2>论文生成</h2>
          <p>根据您的提纲，我们将为您生成论文内容</p>
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
      
      <div v-else class="outline-summary">
        <h3>当前提纲: {{ outline.title }}</h3>
        <div class="outline-meta">
          <div class="keywords">
            <span class="meta-label">关键词：</span>
            <el-tag v-for="(keyword, i) in outline.keywords" :key="i" size="small" class="keyword-tag">
              {{ keyword }}
            </el-tag>
          </div>
        </div>
        
        <el-divider />
        
        <div class="generation-options">
          <h3>生成选项</h3>
          
          <el-radio-group v-model="generationType" class="generation-type">
            <el-radio-button label="section">生成单个章节</el-radio-button>
            <el-radio-button label="full">生成完整论文</el-radio-button>
          </el-radio-group>
          
          <template v-if="generationType === 'section'">
            <div class="section-selector">
              <h4>选择要生成的章节</h4>
              <el-cascader
                v-model="selectedSection"
                :options="sectionOptions"
                :props="{ checkStrictly: true }"
                placeholder="请选择章节"
                style="width: 100%"
              />
            </div>
          </template>
          
          <div class="literature-option">
            <h4>添加参考文献</h4>
            <el-button @click="searchLiterature">搜索文献</el-button>
            <div v-if="selectedLiterature.length > 0" class="selected-literature">
              <h5>已选择 {{ selectedLiterature.length }} 篇文献</h5>
              <el-tag
                v-for="(lit, index) in selectedLiterature"
                :key="index"
                closable
                @close="removeLiterature(index)"
                class="literature-tag"
              >
                {{ lit.title }}
              </el-tag>
            </div>
          </div>
          
          <el-button
            type="primary"
            :loading="loading"
            @click="generatePaper"
            class="generate-button"
          >
            {{ generationType === 'section' ? '生成章节' : '生成完整论文' }}
          </el-button>
        </div>
      </div>
    </el-card>
    
    <el-card v-if="paperContent" class="paper-result-card">
      <template #header>
        <div class="card-header">
          <h2>{{ generationType === 'section' ? '章节内容' : '论文内容' }}</h2>
          <div class="token-usage">
            <el-tooltip content="Token使用量" placement="top">
              <el-tag type="info">
                Token: {{ typeof paperContent.token_usage === 'object' 
                  ? paperContent.token_usage.total_tokens 
                  : paperContent.token_usage }}
              </el-tag>
            </el-tooltip>
          </div>
        </div>
      </template>
      
      <div v-if="generationType === 'section'" class="section-content">
        <h3>{{ paperContent.title }}</h3>
        <div class="content-display">
          <div v-html="formatContent(paperContent.content)"></div>
        </div>
        
        <div class="content-actions">
          <el-button type="primary" @click="saveContent">保存内容</el-button>
          <el-button @click="copyContent">复制内容</el-button>
          <el-button type="warning" @click="improveContent">改进内容</el-button>
        </div>
      </div>
      
      <div v-else class="full-paper-content">
        <h3>{{ paperContent.title }}</h3>
        
        <div class="abstract-section">
          <h4>摘要</h4>
          <div v-html="formatContent(paperContent.abstract)"></div>
        </div>
        
        <div class="keywords-section">
          <h4>关键词</h4>
          <div class="keywords">
            <el-tag v-for="(keyword, i) in paperContent.keywords" :key="i" size="small" class="keyword-tag">
              {{ keyword }}
            </el-tag>
          </div>
        </div>
        
        <div v-for="(section, sectionId) in paperContent.sections" :key="sectionId" class="paper-section">
          <h4>{{ section.title }}</h4>
          <div class="content-display">
            <div v-html="formatContent(section.content)"></div>
          </div>
        </div>
        
        <div class="content-actions">
          <el-button type="primary" @click="saveFullPaper">保存论文</el-button>
          <el-button @click="copyFullPaper">复制论文</el-button>
          <el-button type="warning" @click="exportPaper">导出论文</el-button>
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
                {{ scope.row.authors.join(', ') }}
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
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { generatePaperSection, generateFullPaper } from '@/api/modules/papers';
import { searchLiterature as searchLiteratureApi } from '@/api/modules/search';
import type { OutlineResponse } from '@/types/outlines';
import type { PaperSectionResponse, FullPaperResponse } from '@/types/papers';
import type { Paper } from '@/types/search';

const router = useRouter();

// 提纲数据
const outline = ref<OutlineResponse | null>(null);

// 生成类型
const generationType = ref<'section' | 'full'>('section');

// 选中的章节
const selectedSection = ref<string[]>([]);

// 章节选项
const sectionOptions = computed(() => {
  if (!outline.value) return [];
  
  return outline.value.sections.map(section => {
    const option: any = {
      value: section.id,
      label: section.title,
    };
    
    if (section.subsections && section.subsections.length > 0) {
      option.children = section.subsections.map(subsection => ({
        value: `${section.id}-${subsection.id}`,
        label: subsection.title
      }));
    }
    
    return option;
  });
});

// 选中的文献
const selectedLiterature = ref<Paper[]>([]);

// 生成结果
const paperContent = ref<PaperSectionResponse | FullPaperResponse | null>(null);

// 加载状态
const loading = ref(false);

// 文献搜索对话框
const literatureDialogVisible = ref(false);
const searchQuery = ref('');
const searchResults = ref<Paper[]>([]);
const searchPerformed = ref(false);
const selectedSearchResults = ref<Paper[]>([]);

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

// 搜索文献
const searchLiterature = () => {
  literatureDialogVisible.value = true;
  searchQuery.value = outline.value?.title || '';
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
  
  // 添加选中的文献，避免重复
  const existingIds = new Set(selectedLiterature.value.map(lit => `${lit.title}-${lit.authors.join(',')}`));
  
  selectedSearchResults.value.forEach(lit => {
    const id = `${lit.title}-${lit.authors.join(',')}`;
    if (!existingIds.has(id)) {
      selectedLiterature.value.push(lit);
      existingIds.add(id);
    }
  });
  
  ElMessage.success(`已添加 ${selectedSearchResults.value.length} 篇文献`);
  literatureDialogVisible.value = false;
};

// 移除文献
const removeLiterature = (index: number) => {
  selectedLiterature.value.splice(index, 1);
};

// 生成论文
const generatePaper = async () => {
  if (!outline.value) {
    ElMessage.warning('请先选择提纲');
    return;
  }
  
  if (generationType.value === 'section' && !selectedSection.value.length) {
    ElMessage.warning('请选择要生成的章节');
    return;
  }
  
  try {
    loading.value = true;
    
    if (generationType.value === 'section') {
      const sectionId = selectedSection.value[0];
      
      const result = await generatePaperSection({
        topic: outline.value.title,
        outline: outline.value,
        section_id: sectionId,
        literature: selectedLiterature.value.length > 0 ? selectedLiterature.value : undefined
      });
      
      paperContent.value = result;
      ElMessage.success('章节生成成功');
    } else {
      const result = await generateFullPaper({
        topic: outline.value.title,
        outline: outline.value,
        literature: selectedLiterature.value.length > 0 ? selectedLiterature.value : undefined
      });
      
      paperContent.value = result;
      ElMessage.success('论文生成成功');
    }
  } catch (error) {
    console.error('生成论文失败:', error);
    ElMessage.error('生成论文失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 格式化内容，将换行符转换为HTML换行
const formatContent = (content: string) => {
  if (!content) return '';
  return content.replace(/\n/g, '<br>');
};

// 保存内容
const saveContent = () => {
  if (!paperContent.value || generationType.value !== 'section') return;
  
  const content = paperContent.value as PaperSectionResponse;
  
  // 将内容保存到本地存储
  const savedSections = JSON.parse(localStorage.getItem('savedSections') || '{}');
  savedSections[content.section_id] = content;
  localStorage.setItem('savedSections', JSON.stringify(savedSections));
  
  ElMessage.success('内容已保存');
};

// 复制内容
const copyContent = () => {
  if (!paperContent.value || generationType.value !== 'section') return;
  
  const content = (paperContent.value as PaperSectionResponse).content;
  navigator.clipboard.writeText(content)
    .then(() => {
      ElMessage.success('内容已复制到剪贴板');
    })
    .catch(err => {
      console.error('复制失败:', err);
      ElMessage.error('复制失败，请手动复制');
    });
};

// 改进内容
const improveContent = () => {
  if (!paperContent.value || generationType.value !== 'section') return;
  
  const content = paperContent.value as PaperSectionResponse;
  
  router.push({
    name: 'PaperImprove',
    params: {
      sectionId: content.section_id
    }
  });
};

// 保存完整论文
const saveFullPaper = () => {
  if (!paperContent.value || generationType.value !== 'full') return;
  
  const paper = paperContent.value as FullPaperResponse;
  
  // 将论文保存到本地存储
  localStorage.setItem('savedPaper', JSON.stringify(paper));
  
  ElMessage.success('论文已保存');
};

// 复制完整论文
const copyFullPaper = () => {
  if (!paperContent.value || generationType.value !== 'full') return;
  
  const paper = paperContent.value as FullPaperResponse;
  
  // 构建论文文本
  let text = `${paper.title}\n\n`;
  text += `摘要\n${paper.abstract}\n\n`;
  text += `关键词: ${paper.keywords.join(', ')}\n\n`;
  
  // 添加各章节内容
  Object.entries(paper.sections).forEach(([id, section]) => {
    text += `${section.title}\n${section.content}\n\n`;
  });
  
  navigator.clipboard.writeText(text)
    .then(() => {
      ElMessage.success('论文已复制到剪贴板');
    })
    .catch(err => {
      console.error('复制失败:', err);
      ElMessage.error('复制失败，请手动复制');
    });
};

// 导出论文
const exportPaper = () => {
  if (!paperContent.value || generationType.value !== 'full') return;
  
  const paper = paperContent.value as FullPaperResponse;
  
  // 构建论文文本
  let text = `${paper.title}\n\n`;
  text += `摘要\n${paper.abstract}\n\n`;
  text += `关键词: ${paper.keywords.join(', ')}\n\n`;
  
  // 添加各章节内容
  Object.entries(paper.sections).forEach(([id, section]) => {
    text += `${section.title}\n${section.content}\n\n`;
  });
  
  // 创建Blob对象
  const blob = new Blob([text], { type: 'text/plain' });
  
  // 创建下载链接
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${paper.title}.txt`;
  document.body.appendChild(a);
  a.click();
  
  // 清理
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 0);
  
  ElMessage.success('论文已导出');
};
</script>

<style scoped>
.paper-generate-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.paper-form-card {
  margin-bottom: 30px;
}

.card-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.card-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.no-outline {
  padding: 40px 0;
  text-align: center;
}

.outline-summary h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.outline-meta {
  display: flex;
  margin-bottom: 20px;
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

.generation-options {
  margin-top: 20px;
}

.generation-options h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.generation-options h4 {
  margin: 15px 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.generation-options h5 {
  margin: 10px 0;
  font-size: 14px;
  color: #606266;
}

.generation-type {
  margin-bottom: 20px;
}

.section-selector {
  margin-bottom: 20px;
}

.literature-option {
  margin-bottom: 20px;
}

.selected-literature {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.literature-tag {
  margin: 5px;
}

.generate-button {
  margin-top: 20px;
}

.section-content h3, .full-paper-content h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #303133;
  text-align: center;
}

.content-display {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
  line-height: 1.8;
  margin-bottom: 20px;
}

.abstract-section, .keywords-section {
  margin-bottom: 30px;
}

.abstract-section h4, .keywords-section h4, .paper-section h4 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
}

.paper-section {
  margin-bottom: 30px;
}

.content-actions {
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
  .content-actions {
    flex-direction: column;
  }
}
</style>

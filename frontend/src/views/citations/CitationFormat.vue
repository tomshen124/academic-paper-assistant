<template>
  <div class="citation-format-container">
    <el-card class="format-card">
      <template #header>
        <div class="card-header">
          <h2>引用格式化</h2>
          <p>将文本中的引用格式化为标准引用格式</p>
        </div>
      </template>
      
      <div class="format-form">
        <el-form :model="formData" label-position="top">
          <el-form-item label="内容">
            <el-input
              v-model="formData.content"
              type="textarea"
              :rows="10"
              placeholder="输入包含引用的文本内容"
            />
          </el-form-item>
          
          <el-form-item label="引用样式">
            <el-select v-model="formData.style" placeholder="选择引用样式" style="width: 100%">
              <el-option
                v-for="(label, value) in citationStyles"
                :key="value"
                :label="label"
                :value="value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="formatCitations">
              格式化引用
            </el-button>
            <el-button @click="resetForm">重置</el-button>
            <el-button type="info" @click="loadReferences">
              加载已保存的参考文献
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>格式化结果</h2>
        </div>
      </template>
      
      <div class="formatted-content">
        <h3>格式化后的内容</h3>
        <div class="content-display">
          <div v-html="formatContent(result.formatted_content)"></div>
        </div>
        
        <el-button type="primary" @click="copyContent">
          复制内容
        </el-button>
      </div>
      
      <el-divider />
      
      <div class="references">
        <h3>引用列表</h3>
        <el-empty v-if="result.references.length === 0" description="未找到引用" />
        <el-collapse v-else>
          <el-collapse-item
            v-for="(citation, index) in result.references"
            :key="index"
            :title="`引用 ${index + 1}`"
          >
            <div class="citation-details">
              <div class="citation-item">
                <h4>原始文本</h4>
                <p>{{ citation.original_text }}</p>
              </div>
              <div class="citation-item">
                <h4>格式化引用</h4>
                <p>{{ citation.formatted_citation }}</p>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      
      <el-divider />
      
      <div class="bibliography">
        <h3>参考文献列表</h3>
        <el-empty v-if="result.bibliography.length === 0" description="未生成参考文献列表" />
        <div v-else class="bibliography-list">
          <div
            v-for="(item, index) in result.bibliography"
            :key="index"
            class="bibliography-item"
          >
            <p>{{ item }}</p>
          </div>
        </div>
        
        <el-button type="primary" @click="copyBibliography">
          复制参考文献列表
        </el-button>
      </div>
    </el-card>
    
    <el-dialog
      v-model="referencesDialogVisible"
      title="已保存的参考文献"
      width="70%"
    >
      <div v-if="savedReferences.length === 0" class="no-references">
        <el-empty description="暂无保存的参考文献">
          <template #description>
            <p>您可以在文献搜索页面添加参考文献</p>
          </template>
        </el-empty>
      </div>
      
      <div v-else class="saved-references">
        <el-table
          :data="savedReferences"
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
        </el-table>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="referencesDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="useSelectedReferences">
            使用选中文献
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { formatCitations, getCitationStyles } from '@/api/modules/citations';
import type { CitationFormatResponse, CitationFormatRequest } from '@/types/citations';
import type { Paper } from '@/types/search';

// 表单数据
const formData = reactive<CitationFormatRequest>({
  content: '',
  literature: [],
  style: 'apa'
});

// 状态
const loading = ref(false);
const result = ref<CitationFormatResponse | null>(null);
const citationStyles = ref<Record<string, string>>({});
const referencesDialogVisible = ref(false);
const savedReferences = ref<Paper[]>([]);
const selectedReferences = ref<Paper[]>([]);

// 获取引用样式
const fetchCitationStyles = async () => {
  try {
    const result = await getCitationStyles();
    citationStyles.value = result.styles;
  } catch (error) {
    console.error('获取引用样式失败:', error);
    ElMessage.error('获取引用样式失败，请稍后重试');
  }
};

// 格式化引用
const formatCitations = async () => {
  if (!formData.content.trim()) {
    ElMessage.warning('请输入内容');
    return;
  }
  
  loading.value = true;
  try {
    const response = await formatCitations(formData);
    result.value = response;
    ElMessage.success('引用格式化成功');
  } catch (error) {
    console.error('格式化引用失败:', error);
    ElMessage.error('格式化引用失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  formData.content = '';
  result.value = null;
};

// 加载参考文献
const loadReferences = () => {
  // 从本地存储中获取已保存的参考文献
  const references = localStorage.getItem('savedReferences');
  if (references) {
    try {
      savedReferences.value = JSON.parse(references);
      if (savedReferences.value.length === 0) {
        ElMessage.info('暂无保存的参考文献');
      } else {
        referencesDialogVisible.value = true;
      }
    } catch (error) {
      console.error('解析参考文献失败:', error);
      ElMessage.error('加载参考文献失败');
    }
  } else {
    ElMessage.info('暂无保存的参考文献');
  }
};

// 处理选择变化
const handleSelectionChange = (selection: Paper[]) => {
  selectedReferences.value = selection;
};

// 使用选中的参考文献
const useSelectedReferences = () => {
  if (selectedReferences.value.length === 0) {
    ElMessage.warning('请选择参考文献');
    return;
  }
  
  formData.literature = selectedReferences.value;
  referencesDialogVisible.value = false;
  
  ElMessage.success(`已添加 ${selectedReferences.value.length} 篇参考文献`);
};

// 格式化内容，将换行符转换为HTML换行
const formatContent = (content: string) => {
  if (!content) return '';
  return content.replace(/\n/g, '<br>');
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

// 复制内容
const copyContent = () => {
  if (!result.value) return;
  
  navigator.clipboard.writeText(result.value.formatted_content)
    .then(() => {
      ElMessage.success('内容已复制到剪贴板');
    })
    .catch(err => {
      console.error('复制失败:', err);
      ElMessage.error('复制失败，请手动复制');
    });
};

// 复制参考文献列表
const copyBibliography = () => {
  if (!result.value || !result.value.bibliography.length) return;
  
  const text = result.value.bibliography.join('\n\n');
  
  navigator.clipboard.writeText(text)
    .then(() => {
      ElMessage.success('参考文献列表已复制到剪贴板');
    })
    .catch(err => {
      console.error('复制失败:', err);
      ElMessage.error('复制失败，请手动复制');
    });
};

// 页面加载时获取引用样式
onMounted(() => {
  fetchCitationStyles();
});
</script>

<style scoped>
.citation-format-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.format-card, .result-card {
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

.formatted-content, .references, .bibliography {
  margin-bottom: 30px;
}

.formatted-content h3, .references h3, .bibliography h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.content-display {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
  line-height: 1.8;
  margin-bottom: 20px;
}

.citation-details {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.citation-item {
  margin-bottom: 15px;
}

.citation-item h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.citation-item p {
  margin: 0;
  color: #606266;
}

.bibliography-list {
  margin-bottom: 20px;
}

.bibliography-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.bibliography-item p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.no-references {
  padding: 30px 0;
  text-align: center;
}

.saved-references {
  margin-bottom: 20px;
}
</style>

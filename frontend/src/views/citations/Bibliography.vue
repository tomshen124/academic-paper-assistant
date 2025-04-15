<template>
  <div class="bibliography-container">
    <el-card class="bibliography-card">
      <template #header>
        <div class="card-header">
          <h2>参考文献生成</h2>
          <p>生成格式化的参考文献列表</p>
        </div>
      </template>
      
      <div class="bibliography-form">
        <el-form :model="formData" label-position="top">
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
            <el-button type="primary" @click="loadReferences">
              加载已保存的参考文献
            </el-button>
            <el-button type="success" @click="searchLiterature">
              搜索新文献
            </el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="selectedLiterature.length > 0" class="selected-literature">
          <h3>已选择的参考文献 ({{ selectedLiterature.length }})</h3>
          <el-table :data="selectedLiterature" style="width: 100%">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="authors" label="作者">
              <template #default="scope">
                {{ formatAuthors(scope.row.authors) }}
              </template>
            </el-table-column>
            <el-table-column prop="year" label="年份" width="80" />
            <el-table-column prop="venue" label="发表期刊/会议" width="150" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="danger" size="small" @click="removeLiterature(scope.$index)">
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="generate-actions">
            <el-button type="primary" :loading="loading" @click="generateBibliography">
              生成参考文献列表
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
    
    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>参考文献列表</h2>
          <div class="style-info">
            <el-tag type="info">
              样式: {{ formData.style || 'apa' }}
            </el-tag>
          </div>
        </div>
      </template>
      
      <div class="bibliography-result">
        <div class="bibliography-list">
          <div
            v-for="(item, index) in result.bibliography"
            :key="index"
            class="bibliography-item"
          >
            <p>{{ item }}</p>
          </div>
        </div>
        
        <div class="result-actions">
          <el-button type="primary" @click="copyBibliography">
            复制参考文献列表
          </el-button>
          <el-button @click="exportBibliography">
            导出参考文献列表
          </el-button>
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
import { ElMessage } from 'element-plus';
import { generateBibliography as generateBibliographyApi, getCitationStyles } from '@/api/modules/citations';
import { searchLiterature as searchLiteratureApi } from '@/api/modules/search';
import type { BibliographyRequest, BibliographyResponse } from '@/types/citations';
import type { Paper } from '@/types/search';

// 表单数据
const formData = reactive<BibliographyRequest>({
  literature: [],
  style: 'apa'
});

// 引用样式
const citationStyles = ref<Record<string, string>>({});

// 选中的文献
const selectedLiterature = ref<Paper[]>([]);

// 生成结果
const result = ref<BibliographyResponse | null>(null);

// 文献搜索
const literatureDialogVisible = ref(false);
const searchQuery = ref('');
const searchResults = ref<Paper[]>([]);
const searchPerformed = ref(false);
const selectedSearchResults = ref<Paper[]>([]);

const loading = ref(false);

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

// 加载已保存的参考文献
const loadReferences = () => {
  // 从本地存储中获取已保存的参考文献
  const references = localStorage.getItem('savedReferences');
  if (references) {
    try {
      selectedLiterature.value = JSON.parse(references);
      formData.literature = selectedLiterature.value;
      
      if (selectedLiterature.value.length === 0) {
        ElMessage.info('暂无保存的参考文献');
      } else {
        ElMessage.success(`已加载 ${selectedLiterature.value.length} 篇参考文献`);
      }
    } catch (error) {
      console.error('解析参考文献失败:', error);
      ElMessage.error('加载参考文献失败');
    }
  } else {
    ElMessage.info('暂无保存的参考文献');
  }
};

// 搜索文献
const searchLiterature = () => {
  literatureDialogVisible.value = true;
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
  
  // 添加选中的文献，避免重复
  const existingIds = new Set(selectedLiterature.value.map(lit => `${lit.title}-${lit.authors.join(',')}`));
  
  selectedSearchResults.value.forEach(lit => {
    const id = `${lit.title}-${lit.authors.join(',')}`;
    if (!existingIds.has(id)) {
      selectedLiterature.value.push(lit);
      existingIds.add(id);
    }
  });
  
  // 更新表单数据
  formData.literature = selectedLiterature.value;
  
  ElMessage.success(`已添加 ${selectedSearchResults.value.length} 篇文献`);
  literatureDialogVisible.value = false;
};

// 移除文献
const removeLiterature = (index: number) => {
  selectedLiterature.value.splice(index, 1);
  formData.literature = selectedLiterature.value;
};

// 生成参考文献列表
const generateBibliography = async () => {
  if (selectedLiterature.value.length === 0) {
    ElMessage.warning('请先添加参考文献');
    return;
  }
  
  loading.value = true;
  try {
    const response = await generateBibliographyApi(formData);
    result.value = response;
    ElMessage.success('参考文献列表生成成功');
  } catch (error) {
    console.error('生成参考文献列表失败:', error);
    ElMessage.error('生成参考文献列表失败，请稍后重试');
  } finally {
    loading.value = false;
  }
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

// 导出参考文献列表
const exportBibliography = () => {
  if (!result.value || !result.value.bibliography.length) return;
  
  const text = result.value.bibliography.join('\n\n');
  
  // 创建Blob对象
  const blob = new Blob([text], { type: 'text/plain' });
  
  // 创建下载链接
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `bibliography_${formData.style || 'apa'}.txt`;
  document.body.appendChild(a);
  a.click();
  
  // 清理
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 0);
  
  ElMessage.success('参考文献列表已导出');
};

// 页面加载时获取引用样式
onMounted(() => {
  fetchCitationStyles();
});
</script>

<style scoped>
.bibliography-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.bibliography-card, .result-card {
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

.style-info {
  margin-left: 20px;
}

.selected-literature {
  margin-top: 30px;
}

.selected-literature h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.generate-actions {
  margin-top: 20px;
  text-align: center;
}

.bibliography-result {
  margin-top: 20px;
}

.bibliography-list {
  margin-bottom: 30px;
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

.result-actions {
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
  
  .style-info {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>

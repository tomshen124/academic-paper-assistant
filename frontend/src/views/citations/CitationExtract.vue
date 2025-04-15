<template>
  <div class="citation-extract-container">
    <el-card class="extract-card">
      <template #header>
        <div class="card-header">
          <h2>引用提取</h2>
          <p>从文本中提取引用信息</p>
        </div>
      </template>
      
      <div class="extract-form">
        <el-form :model="formData" label-position="top">
          <el-form-item label="内容">
            <el-input
              v-model="formData.content"
              type="textarea"
              :rows="10"
              placeholder="输入包含引用的文本内容"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="extractCitations">
              提取引用
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>提取结果</h2>
          <div class="citation-count">
            <el-tag type="info">
              共找到 {{ result.total_count }} 个引用
            </el-tag>
          </div>
        </div>
      </template>
      
      <div class="extract-result">
        <el-empty v-if="result.citations.length === 0" description="未找到引用" />
        <el-table v-else :data="result.citations" style="width: 100%">
          <el-table-column prop="text" label="引用文本" />
          <el-table-column prop="position" label="位置" width="100" />
          <el-table-column prop="author" label="可能的作者" width="150" />
          <el-table-column prop="year" label="可能的年份" width="100" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button type="primary" size="small" @click="searchCitation(scope.row)">
                搜索文献
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { extractCitations as extractCitationsApi } from '@/api/modules/citations';
import type { CitationExtractRequest, CitationExtractResponse, ExtractedCitation } from '@/types/citations';

const router = useRouter();

// 表单数据
const formData = reactive<CitationExtractRequest>({
  content: ''
});

// 提取结果
const result = ref<CitationExtractResponse | null>(null);

const loading = ref(false);

// 提取引用
const extractCitations = async () => {
  if (!formData.content.trim()) {
    ElMessage.warning('请输入内容');
    return;
  }
  
  loading.value = true;
  try {
    const response = await extractCitationsApi(formData);
    result.value = response;
    
    if (response.citations.length === 0) {
      ElMessage.info('未找到引用');
    } else {
      ElMessage.success(`成功提取 ${response.total_count} 个引用`);
    }
  } catch (error) {
    console.error('提取引用失败:', error);
    ElMessage.error('提取引用失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  formData.content = '';
  result.value = null;
};

// 搜索引用
const searchCitation = (citation: ExtractedCitation) => {
  // 构建搜索查询
  let query = citation.text;
  
  if (citation.author) {
    query = `${citation.author} ${query}`;
  }
  
  if (citation.year) {
    query = `${query} ${citation.year}`;
  }
  
  // 导航到文献搜索页面
  router.push({
    name: 'LiteratureSearch',
    query: {
      q: encodeURIComponent(query)
    }
  });
};
</script>

<style scoped>
.citation-extract-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.extract-card, .result-card {
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

.citation-count {
  margin-left: 20px;
}

.extract-result {
  margin-top: 20px;
}
</style>

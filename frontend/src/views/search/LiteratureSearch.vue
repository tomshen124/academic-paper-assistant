<template>
  <div class="literature-search-container">
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <h2>学术文献搜索</h2>
          <p>搜索和浏览学术文献，为您的研究提供支持</p>
        </div>
      </template>
      
      <div class="search-form">
        <el-input
          v-model="searchQuery"
          placeholder="输入关键词、作者、标题等搜索文献"
          class="search-input"
          @keyup.enter="performSearch"
        >
          <template #append>
            <el-button @click="performSearch" :loading="loading">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </template>
        </el-input>
        
        <div class="search-options">
          <el-form :inline="true" :model="searchOptions" size="small">
            <el-form-item label="结果数量">
              <el-select v-model="searchOptions.limit" style="width: 120px">
                <el-option :value="10" label="10条" />
                <el-option :value="20" label="20条" />
                <el-option :value="50" label="50条" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      
      <div v-else-if="!searchPerformed" class="search-tips">
        <el-empty description="输入关键词开始搜索">
          <template #description>
            <p>搜索提示：</p>
            <ul>
              <li>使用引号包围精确短语，如 "深度学习"</li>
              <li>使用 AND、OR 组合关键词，如 人工智能 AND 医疗</li>
              <li>使用作者名搜索特定作者的论文</li>
              <li>添加年份范围，如 深度学习 2020..2023</li>
            </ul>
          </template>
        </el-empty>
      </div>
      
      <div v-else-if="searchResults.length === 0" class="no-results">
        <el-empty description="未找到相关文献">
          <template #description>
            <p>未找到与 "{{ searchQuery }}" 相关的文献</p>
            <p>尝试使用不同的关键词或扩大搜索范围</p>
          </template>
        </el-empty>
      </div>
      
      <div v-else class="search-results">
        <div class="results-header">
          <h3>搜索结果: {{ searchResults.length }} 条</h3>
          <p>查询: "{{ searchQuery }}"</p>
        </div>
        
        <el-divider />
        
        <div class="results-list">
          <el-card v-for="(paper, index) in searchResults" :key="index" class="paper-card">
            <div class="paper-title">
              <h4>
                <a :href="paper.url" target="_blank" class="paper-link">{{ paper.title }}</a>
              </h4>
            </div>
            
            <div class="paper-meta">
              <span class="authors">{{ formatAuthors(paper.authors) }}</span>
              <span v-if="paper.year" class="year">({{ paper.year }})</span>
              <span v-if="paper.venue" class="venue">{{ paper.venue }}</span>
              <el-tag v-if="paper.citations" size="small" type="info" class="citations">
                引用: {{ paper.citations }}
              </el-tag>
              <el-tag size="small" type="success" class="source">
                {{ paper.source }}
              </el-tag>
            </div>
            
            <div v-if="paper.abstract" class="paper-abstract">
              <p>{{ truncateAbstract(paper.abstract) }}</p>
            </div>
            
            <div class="paper-actions">
              <el-button type="primary" size="small" @click="viewPaperDetails(paper)">
                查看详情
              </el-button>
              <el-button size="small" @click="addToReferences(paper)">
                添加到参考文献
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { Search } from '@element-plus/icons-vue';
import { searchLiterature } from '@/api/modules/search';
import type { Paper } from '@/types/search';

const router = useRouter();

// 搜索状态
const searchQuery = ref('');
const searchOptions = reactive({
  limit: 20
});
const loading = ref(false);
const searchPerformed = ref(false);
const searchResults = ref<Paper[]>([]);

// 执行搜索
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }
  
  loading.value = true;
  try {
    const result = await searchLiterature({
      query: searchQuery.value,
      limit: searchOptions.limit
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

// 截断摘要
const truncateAbstract = (abstract: string, maxLength = 200) => {
  if (!abstract) return '';
  
  if (abstract.length <= maxLength) {
    return abstract;
  } else {
    return abstract.substring(0, maxLength) + '...';
  }
};

// 查看论文详情
const viewPaperDetails = (paper: Paper) => {
  // 将论文信息存储到本地存储
  localStorage.setItem('selectedPaper', JSON.stringify(paper));
  
  // 导航到论文详情页面
  router.push({
    name: 'PaperDetail',
    params: {
      id: paper.title.replace(/\s+/g, '-').toLowerCase()
    }
  });
};

// 添加到参考文献
const addToReferences = (paper: Paper) => {
  // 获取已有的参考文献
  const savedReferences = JSON.parse(localStorage.getItem('savedReferences') || '[]');
  
  // 检查是否已存在
  const exists = savedReferences.some((ref: Paper) => 
    ref.title === paper.title && ref.authors.join(',') === paper.authors.join(',')
  );
  
  if (exists) {
    ElMessage.warning('该文献已在参考文献列表中');
    return;
  }
  
  // 添加到参考文献
  savedReferences.push(paper);
  localStorage.setItem('savedReferences', JSON.stringify(savedReferences));
  
  ElMessage.success('已添加到参考文献');
};
</script>

<style scoped>
.literature-search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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

.search-form {
  margin-bottom: 30px;
}

.search-input {
  margin-bottom: 15px;
}

.search-options {
  display: flex;
  justify-content: flex-end;
}

.loading-container {
  padding: 20px 0;
}

.search-tips {
  padding: 40px 0;
  text-align: center;
}

.search-tips ul {
  text-align: left;
  display: inline-block;
  margin: 10px 0 0 0;
  padding-left: 20px;
  color: #606266;
}

.no-results {
  padding: 40px 0;
  text-align: center;
}

.results-header {
  margin-bottom: 15px;
}

.results-header h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #303133;
}

.results-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.results-list {
  margin-top: 20px;
}

.paper-card {
  margin-bottom: 20px;
}

.paper-title h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  line-height: 1.4;
}

.paper-link {
  color: #409eff;
  text-decoration: none;
}

.paper-link:hover {
  text-decoration: underline;
}

.paper-meta {
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.paper-abstract {
  margin-bottom: 15px;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.paper-abstract p {
  margin: 0;
}

.paper-actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .paper-actions {
    flex-direction: column;
  }
}
</style>

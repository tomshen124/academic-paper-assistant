<template>
  <div class="paper-detail-container">
    <el-card class="paper-card">
      <template #header>
        <div class="card-header">
          <h2>论文详情</h2>
          <div class="source-tag">
            <el-tag type="success">
              {{ paper ? paper.source : '未知来源' }}
            </el-tag>
          </div>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      
      <div v-else-if="!paper" class="no-paper">
        <el-empty description="未找到论文信息">
          <template #description>
            <p>请从搜索结果中选择一篇论文</p>
          </template>
          <el-button type="primary" @click="goToSearch">搜索文献</el-button>
        </el-empty>
      </div>
      
      <div v-else class="paper-content">
        <h1 class="paper-title">{{ paper.title }}</h1>
        
        <div class="paper-meta">
          <div class="authors">
            <h3>作者</h3>
            <p>{{ formatAuthors(paper.authors) }}</p>
          </div>
          
          <div class="meta-info">
            <div v-if="paper.year" class="year">
              <h3>年份</h3>
              <p>{{ paper.year }}</p>
            </div>
            
            <div v-if="paper.venue" class="venue">
              <h3>发表期刊/会议</h3>
              <p>{{ paper.venue }}</p>
            </div>
            
            <div v-if="paper.citations" class="citations">
              <h3>引用次数</h3>
              <p>{{ paper.citations }}</p>
            </div>
          </div>
        </div>
        
        <div class="paper-abstract">
          <h3>摘要</h3>
          <p>{{ paper.abstract }}</p>
        </div>
        
        <div v-if="paper.references && paper.references.length > 0" class="paper-references">
          <h3>参考文献 ({{ paper.references.length }})</h3>
          <el-collapse>
            <el-collapse-item title="查看参考文献" name="1">
              <ul class="references-list">
                <li v-for="(ref, index) in paper.references" :key="index">
                  {{ ref.title }} - {{ formatAuthors(ref.authors) }}
                  <span v-if="ref.year">({{ ref.year }})</span>
                </li>
              </ul>
            </el-collapse-item>
          </el-collapse>
        </div>
        
        <div class="paper-actions">
          <el-button type="primary" @click="addToReferences">
            添加到参考文献
          </el-button>
          <el-button v-if="paper.url" type="success" @click="openPaperUrl">
            查看原文
          </el-button>
          <el-button @click="goToSearch">
            返回搜索
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { getPaperDetails } from '@/api/modules/search';
import type { PaperDetailResponse } from '@/types/search';

const router = useRouter();
const route = useRoute();

const paper = ref<PaperDetailResponse | null>(null);
const loading = ref(false);

// 从路由参数和本地存储中获取论文信息
onMounted(async () => {
  // 从本地存储中获取选中的论文
  const selectedPaper = localStorage.getItem('selectedPaper');
  if (selectedPaper) {
    try {
      paper.value = JSON.parse(selectedPaper);
    } catch (error) {
      console.error('解析论文信息失败:', error);
    }
  }
  
  // 如果有论文ID参数，则获取论文详情
  const paperId = route.params.id;
  if (paperId && (!paper.value || paper.value.title !== paperId)) {
    await fetchPaperDetails(paperId as string);
  }
});

// 获取论文详情
const fetchPaperDetails = async (paperId: string) => {
  loading.value = true;
  try {
    // 这里假设paperId是从URL中获取的，实际上可能需要解析
    // 在实际应用中，可能需要从URL参数中提取真正的ID和来源
    const result = await getPaperDetails({
      paper_id: paperId,
      source: 'semantic_scholar' // 默认来源
    });
    
    paper.value = result;
  } catch (error) {
    console.error('获取论文详情失败:', error);
    ElMessage.error('获取论文详情失败，请稍后重试');
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

// 跳转到搜索页面
const goToSearch = () => {
  router.push({ name: 'LiteratureSearch' });
};

// 添加到参考文献
const addToReferences = () => {
  if (!paper.value) return;
  
  // 获取已有的参考文献
  const savedReferences = JSON.parse(localStorage.getItem('savedReferences') || '[]');
  
  // 检查是否已存在
  const exists = savedReferences.some((ref: any) => 
    ref.title === paper.value?.title && ref.authors.join(',') === paper.value?.authors.join(',')
  );
  
  if (exists) {
    ElMessage.warning('该文献已在参考文献列表中');
    return;
  }
  
  // 添加到参考文献
  savedReferences.push(paper.value);
  localStorage.setItem('savedReferences', JSON.stringify(savedReferences));
  
  ElMessage.success('已添加到参考文献');
};

// 打开论文URL
const openPaperUrl = () => {
  if (!paper.value || !paper.value.url) return;
  
  window.open(paper.value.url, '_blank');
};
</script>

<style scoped>
.paper-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.source-tag {
  margin-left: 20px;
}

.loading-container {
  padding: 20px 0;
}

.no-paper {
  padding: 40px 0;
  text-align: center;
}

.paper-content {
  margin-top: 20px;
}

.paper-title {
  margin: 0 0 20px 0;
  font-size: 24px;
  color: #303133;
  text-align: center;
}

.paper-meta {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 30px;
  gap: 20px;
}

.authors {
  flex: 1;
  min-width: 200px;
}

.meta-info {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.year, .venue, .citations {
  flex: 1;
  min-width: 100px;
}

.paper-meta h3, .paper-abstract h3, .paper-references h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.paper-meta p {
  margin: 0;
  color: #606266;
}

.paper-abstract {
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.paper-abstract p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.paper-references {
  margin-bottom: 30px;
}

.references-list {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.references-list li {
  margin-bottom: 10px;
}

.paper-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
  }
  
  .source-tag {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .paper-meta {
    flex-direction: column;
  }
  
  .paper-actions {
    flex-direction: column;
  }
}
</style>

<template>
  <div class="topic-summary">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>
    
    <div v-else class="topics-container">
      <div class="topics-header">
        <h3>{{ title || '主题列表' }}</h3>
        <div class="topics-count">
          <el-tag type="info">共找到 {{ topics.length }} 个主题</el-tag>
        </div>
      </div>
      
      <el-empty v-if="topics.length === 0" description="没有找到主题" />
      
      <div v-else class="topics-list">
        <el-card v-for="(topic, index) in topics" :key="index" class="topic-card" shadow="hover">
          <div class="topic-header">
            <span class="topic-number">{{ index + 1 }}</span>
            <h4>{{ topic.title || '未命名主题' }}</h4>
          </div>
          
          <div class="topic-meta">
            <span v-if="topic.created_at" class="topic-time">
              创建于: {{ formatDateTime(topic.created_at) }}
            </span>
            <el-tag v-if="topic.academic_field" size="small" class="topic-field">
              {{ topic.academic_field }}
            </el-tag>
          </div>
          
          <div class="topic-content">
            <p v-if="topic.research_question" class="topic-question">
              <strong>研究问题:</strong> {{ topic.research_question }}
            </p>
            
            <div v-if="topic.keywords && topic.keywords.length > 0" class="topic-keywords">
              <strong>关键词:</strong>
              <el-tag 
                v-for="(keyword, i) in topic.keywords" 
                :key="i" 
                size="small" 
                class="keyword-tag"
              >
                {{ keyword }}
              </el-tag>
            </div>
          </div>
          
          <div class="topic-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="$emit('select', topic)"
            >
              使用此主题
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="$emit('view-details', topic)"
            >
              查看详情
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  topics: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  }
});

defineEmits(['select', 'view-details']);

// 格式化日期时间函数
const formatDateTime = (dateTimeString: string) => {
  if (!dateTimeString) return '未知时间';
  
  const date = new Date(dateTimeString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
.topic-summary {
  margin-bottom: 20px;
}

.topics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.topics-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.topics-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.topic-card {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.topic-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.topic-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.topic-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background-color: #f2f6fc;
  color: #606266;
  border-radius: 50%;
  margin-right: 10px;
  font-size: 14px;
  font-weight: bold;
}

.topic-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  flex: 1;
}

.topic-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 12px;
  color: #909399;
}

.topic-content {
  margin-bottom: 15px;
}

.topic-question {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #606266;
}

.topic-keywords {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
}

.keyword-tag {
  margin-right: 5px;
}

.topic-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.loading-container {
  padding: 20px;
}
</style>

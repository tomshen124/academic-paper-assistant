<template>
  <div class="outline-optimize-container">
    <el-card class="optimize-card">
      <template #header>
        <div class="card-header">
          <h2>提纲优化</h2>
          <p>根据您的反馈优化论文提纲，使其更加完善和合理</p>
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
      
      <div v-else class="optimize-form">
        <div class="current-outline">
          <h3>当前提纲</h3>
          <div class="outline-preview">
            <h4>{{ outline.title }}</h4>
            <div class="outline-sections">
              <div v-for="(section, index) in outline.sections" :key="index" class="section-item">
                <div class="section-title">{{ section.title }}</div>
                <div v-if="section.subsections && section.subsections.length > 0" class="subsections">
                  <div v-for="(subsection, subIndex) in section.subsections" :key="subIndex" class="subsection-item">
                    - {{ subsection.title }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <el-form :model="formData" label-position="top" :rules="rules" ref="formRef">
          <el-form-item label="您的反馈" prop="feedback">
            <el-input
              v-model="formData.feedback"
              type="textarea"
              :rows="6"
              placeholder="请描述您希望如何改进这个提纲，例如：调整章节顺序、添加新章节、合并章节、修改章节内容等"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="submitForm">优化提纲</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <el-card v-if="optimizedOutline" class="result-card">
      <template #header>
        <div class="card-header">
          <h2>优化结果</h2>
        </div>
      </template>
      
      <div class="optimize-result">
        <h3>{{ optimizedOutline.title }}</h3>
        <div class="outline-meta">
          <div class="keywords">
            <span class="meta-label">关键词：</span>
            <el-tag v-for="(keyword, i) in optimizedOutline.keywords" :key="i" size="small" class="keyword-tag">
              {{ keyword }}
            </el-tag>
          </div>
        </div>
        
        <div class="abstract-section">
          <h4>摘要</h4>
          <p>{{ optimizedOutline.abstract }}</p>
        </div>
        
        <div class="sections-container">
          <h4>论文结构</h4>
          
          <el-tree
            :data="formatSections(optimizedOutline.sections)"
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
                      <p>{{ data.purpose }}</p>
                    </div>
                    <div v-if="data.content_points && data.content_points.length > 0" class="section-points">
                      <h4>内容要点</h4>
                      <ul>
                        <li v-for="(point, i) in data.content_points" :key="i">{{ point }}</li>
                      </ul>
                    </div>
                  </div>
                </el-popover>
              </div>
            </template>
          </el-tree>
        </div>
        
        <div class="optimization-summary">
          <h4>优化说明</h4>
          <p>根据您的反馈，我们对提纲进行了以下优化：</p>
          <ul>
            <li>调整了章节结构，使论文逻辑更加清晰</li>
            <li>完善了各章节的内容要点，使内容更加充实</li>
            <li>优化了章节标题，使其更加准确和专业</li>
            <li>平衡了各章节的长度，使论文结构更加合理</li>
          </ul>
        </div>
        
        <div class="result-actions">
          <el-button type="primary" @click="useOptimizedOutline">使用此提纲</el-button>
          <el-button type="success" @click="validateOutline">验证提纲</el-button>
          <el-button @click="generatePaper">生成论文</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, FormInstance } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { InfoFilled } from '@element-plus/icons-vue';
import { optimizeOutline } from '@/api/modules/outlines';
import type { OutlineOptimizationRequest, OutlineResponse } from '@/types/outlines';
import type { Section, SubSection } from '@/types/outlines';

const router = useRouter();
const route = useRoute();

// 当前提纲
const outline = ref<OutlineResponse | null>(null);

// 表单数据
const formData = reactive<OutlineOptimizationRequest>({
  outline: {},
  feedback: ''
});

// 表单验证规则
const rules = {
  feedback: [
    { required: true, message: '请输入您的反馈', trigger: 'blur' },
    { min: 10, message: '反馈不能少于10个字符', trigger: 'blur' }
  ]
};

// 优化结果
const optimizedOutline = ref<OutlineResponse | null>(null);

// 树形控件配置
const defaultProps = {
  children: 'children',
  label: 'title'
};

const formRef = ref<FormInstance>();
const loading = ref(false);

// 从本地存储中获取提纲
onMounted(() => {
  const storedOutline = localStorage.getItem('selectedOutline');
  if (storedOutline) {
    try {
      outline.value = JSON.parse(storedOutline);
      formData.outline = outline.value;
    } catch (error) {
      console.error('解析提纲失败:', error);
    }
  }
});

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

// 跳转到提纲生成页面
const goToOutlineGenerate = () => {
  router.push({ name: 'OutlineGenerate' });
};

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const result = await optimizeOutline(formData);
        optimizedOutline.value = result;
        ElMessage.success('提纲优化成功');
      } catch (error) {
        console.error('优化提纲失败:', error);
        ElMessage.error('优化提纲失败，请稍后重试');
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
  optimizedOutline.value = null;
};

// 使用优化后的提纲
const useOptimizedOutline = () => {
  if (!optimizedOutline.value) return;
  
  // 将优化后的提纲存储到本地存储
  localStorage.setItem('selectedOutline', JSON.stringify(optimizedOutline.value));
  
  ElMessage.success('已选择优化后的提纲');
};

// 验证提纲
const validateOutline = () => {
  if (!optimizedOutline.value) return;
  
  // 将优化后的提纲存储到本地存储
  localStorage.setItem('selectedOutline', JSON.stringify(optimizedOutline.value));
  
  router.push({
    name: 'OutlineValidate',
    params: {
      id: 'current'
    }
  });
};

// 生成论文
const generatePaper = () => {
  if (!optimizedOutline.value) return;
  
  // 将优化后的提纲存储到本地存储
  localStorage.setItem('selectedOutline', JSON.stringify(optimizedOutline.value));
  
  router.push({
    name: 'PaperGenerate'
  });
};
</script>

<style scoped>
.outline-optimize-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.optimize-card, .result-card {
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

.no-outline {
  padding: 40px 0;
  text-align: center;
}

.current-outline {
  margin-bottom: 30px;
}

.current-outline h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.outline-preview {
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.outline-preview h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
  text-align: center;
}

.section-item {
  margin-bottom: 10px;
}

.section-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.subsections {
  margin-left: 20px;
}

.subsection-item {
  margin-bottom: 5px;
  color: #606266;
}

.optimize-result {
  margin-top: 20px;
}

.optimize-result h3 {
  margin: 0 0 15px 0;
  font-size: 20px;
  color: #303133;
  text-align: center;
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

.abstract-section {
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.abstract-section h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
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

.sections-container h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
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

.optimization-summary {
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f0f9eb;
  border-radius: 4px;
  border-left: 4px solid #67c23a;
}

.optimization-summary h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.optimization-summary p {
  margin: 0 0 10px 0;
  color: #606266;
}

.optimization-summary ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.result-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .result-actions {
    flex-direction: column;
  }
}
</style>

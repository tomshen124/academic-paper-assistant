<template>
  <div class="citation-editor-container">
    <!-- 引用编辑对话框 -->
    <el-dialog
      :modelValue="dialogVisible"
      @update:modelValue="updateVisible"
      title="编辑论文引用"
      width="70%"
      destroy-on-close
    >
      <div class="citation-editor">
        <div class="editor-description">
          <p>在此编辑器中，您可以直接编辑论文中的引用。</p>
        </div>
        
        <div v-if="paperContent" class="content-editor">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="编辑内容" name="edit">
              <el-form label-position="top">
                <el-form-item label="论文内容">
                  <el-input
                    v-model="editableContent"
                    type="textarea"
                    :rows="15"
                    placeholder="编辑论文内容，包括引用"
                  />
                </el-form-item>
              </el-form>
              
              <div class="citation-tools">
                <h4>引用工具</h4>
                <el-button type="primary" @click="insertCitation">插入引用</el-button>
                <el-button type="success" @click="extractCitations">提取现有引用</el-button>
                <el-button type="warning" @click="formatAllCitations">格式化所有引用</el-button>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="引用列表" name="citations">
              <div class="citation-list">
                <h4>文章中的引用</h4>
                <el-empty v-if="extractedCitations.length === 0" description="未找到引用" />
                <el-table v-else :data="extractedCitations" style="width: 100%">
                  <el-table-column prop="text" label="引用文本" />
                  <el-table-column prop="author" label="作者" width="120" />
                  <el-table-column prop="year" label="年份" width="80" />
                  <el-table-column label="操作" width="180">
                    <template #default="scope">
                      <el-button type="primary" size="small" @click="editCitation(scope.row)">
                        编辑
                      </el-button>
                      <el-button type="danger" size="small" @click="removeCitationAt(scope.$index)">
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="参考文献预览" name="bibliography">
              <div class="bibliography-preview">
                <h4>参考文献预览</h4>
                
                <el-form :model="bibliographyForm" label-width="100px">
                  <el-form-item label="引用样式">
                    <el-select v-model="bibliographyForm.style" placeholder="选择引用样式">
                      <el-option label="APA" value="apa" />
                      <el-option label="MLA" value="mla" />
                      <el-option label="Chicago" value="chicago" />
                      <el-option label="Harvard" value="harvard" />
                      <el-option label="IEEE" value="ieee" />
                    </el-select>
                  </el-form-item>
                </el-form>
                
                <el-button type="primary" @click="generateBibliography">生成参考文献</el-button>
                
                <div v-if="bibliographyResult" class="bibliography-result">
                  <h5>参考文献</h5>
                  <div class="bibliography-content" v-html="bibliographyResult.formatted_text"></div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancel">取消</el-button>
          <el-button type="primary" @click="save">保存更改</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 引用插入对话框 -->
    <el-dialog
      v-model="insertDialogVisible"
      title="插入引用"
      width="50%"
      destroy-on-close
    >
      <el-form :model="newCitation" label-width="100px">
        <el-form-item label="作者">
          <el-input v-model="newCitation.author" placeholder="输入作者姓名" />
        </el-form-item>
        
        <el-form-item label="年份">
          <el-input v-model="newCitation.year" placeholder="输入发表年份" />
        </el-form-item>
        
        <el-form-item label="标题">
          <el-input v-model="newCitation.title" placeholder="输入文献标题" />
        </el-form-item>
        
        <el-form-item label="来源">
          <el-input v-model="newCitation.source" placeholder="期刊/会议/出版社" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="insertDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmInsertCitation">确认插入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, defineProps, defineEmits, watch, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { extractCitations as extractCitationsApi, formatCitations as formatCitationsApi, generateBibliography as generateBibliographyApi } from '@/api/modules/citations';
import type { ExtractedCitation, BibliographyResponse } from '@/types/citations';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  content: {
    type: String,
    default: ''
  },
  paperContent: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['update:visible', 'save']);

// 使用计算属性处理对话框显示状态
const dialogVisible = computed(() => props.visible);

// 更新visible属性
const updateVisible = (value: boolean) => {
  emit('update:visible', value);
};

// 内部状态
const activeTab = ref('edit');
const editableContent = ref('');
const extractedCitations = ref<ExtractedCitation[]>([]);
const bibliographyForm = reactive({
  style: 'apa'
});
const bibliographyResult = ref<BibliographyResponse | null>(null);
const insertDialogVisible = ref(false);
const newCitation = reactive({
  author: '',
  year: '',
  title: '',
  source: ''
});

// 监听内容变化
watch(() => props.content, (newValue) => {
  editableContent.value = newValue;
}, { immediate: true });

// 提取引用
const extractCitations = async () => {
  if (!editableContent.value) return;
  
  try {
    const result = await extractCitationsApi({
      content: editableContent.value
    });
    
    extractedCitations.value = result.citations;
    
    if (result.citations.length === 0) {
      ElMessage.info('未找到引用');
    } else {
      ElMessage.success(`成功提取 ${result.total_count} 个引用`);
      activeTab.value = 'citations';
    }
  } catch (error) {
    console.error('提取引用失败:', error);
    ElMessage.error('提取引用失败，请稍后重试');
  }
};

// 插入引用
const insertCitation = () => {
  // 重置新引用表单
  Object.keys(newCitation).forEach(key => {
    newCitation[key] = '';
  });
  
  insertDialogVisible.value = true;
};

// 确认插入引用
const confirmInsertCitation = () => {
  if (!newCitation.author || !newCitation.year) {
    ElMessage.warning('作者和年份为必填项');
    return;
  }
  
  // 生成引用文本
  const citationText = `[${newCitation.author}, ${newCitation.year}]`;
  
  // 在当前位置插入引用
  const textarea = document.querySelector('.content-editor textarea') as HTMLTextAreaElement;
  let cursorPosition = editableContent.value.length;
  
  if (textarea) {
    cursorPosition = textarea.selectionStart || cursorPosition;
  }
  
  // 在光标位置插入引用
  const text = editableContent.value;
  editableContent.value = text.substring(0, cursorPosition) + 
                         citationText + 
                         text.substring(cursorPosition);
  
  insertDialogVisible.value = false;
  ElMessage.success('引用已插入');
};

// 编辑引用
const editCitation = (citation: ExtractedCitation) => {
  // 实现编辑引用的逻辑
  ElMessage.info('编辑引用功能开发中');
};

// 删除引用
const removeCitationAt = (index: number) => {
  const citation = extractedCitations.value[index];
  
  // 从文本中删除引用
  editableContent.value = editableContent.value.replace(citation.text, '');
  
  // 从引用列表中删除
  extractedCitations.value.splice(index, 1);
  
  ElMessage.success('引用已删除');
};

// 生成参考文献
const generateBibliography = async () => {
  if (extractedCitations.value.length === 0) {
    ElMessage.warning('未找到引用，请先提取引用');
    return;
  }
  
  try {
    // 构造参考文献请求
    const request = {
      literature: extractedCitations.value.map(citation => ({
        author: citation.author || 'Unknown',
        year: citation.year || 'Unknown',
        title: citation.title || 'Unknown',
        source: citation.source || 'Unknown'
      })),
      style: bibliographyForm.style
    };
    
    const result = await generateBibliographyApi(request);
    bibliographyResult.value = result;
    
    ElMessage.success('参考文献生成成功');
  } catch (error) {
    console.error('生成参考文献失败:', error);
    ElMessage.error('生成参考文献失败，请稍后重试');
  }
};

// 格式化所有引用
const formatAllCitations = async () => {
  if (!editableContent.value || extractedCitations.value.length === 0) {
    ElMessage.warning('请先提取引用');
    return;
  }
  
  try {
    // 构造格式化请求
    const request = {
      content: editableContent.value,
      literature: extractedCitations.value.map(citation => ({
        author: citation.author || 'Unknown',
        year: citation.year || 'Unknown', 
        title: citation.title || 'Unknown',
        source: citation.source || 'Unknown'
      })),
      style: bibliographyForm.style
    };
    
    const result = await formatCitationsApi(request);
    // 更新编辑器内容
    editableContent.value = result.formatted_text;
    
    ElMessage.success('引用格式化成功');
    // 重新提取引用
    extractCitations();
  } catch (error) {
    console.error('格式化引用失败:', error);
    ElMessage.error('格式化引用失败，请稍后重试');
  }
};

// 取消
const cancel = () => {
  emit('update:visible', false);
};

// 保存
const save = () => {
  emit('save', editableContent.value);
  emit('update:visible', false);
};
</script>

<style scoped>
.citation-editor-container {
  width: 100%;
}

.editor-description {
  margin-bottom: 20px;
}

.citation-tools {
  margin-top: 20px;
}

.bibliography-result {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.bibliography-content {
  margin-top: 10px;
  line-height: 1.5;
  white-space: pre-line;
}
</style>

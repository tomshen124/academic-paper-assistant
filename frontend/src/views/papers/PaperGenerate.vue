<template>
  <div class="paper-generate-container">
    <el-card class="paper-form-card">
      <template #header>
        <div class="card-header">
          <h2>论文生成</h2>
          <p>根据您的提纲，我们将为您生成论文内容</p>
          <el-button-group class="header-buttons">
            <el-button type="success" plain size="small" @click="openCitationManager">
              引用管理
            </el-button>
            <el-button type="info" plain size="small" @click="showHelp">
              使用帮助
            </el-button>
          </el-button-group>
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
              <h4>选择要生成的章节（可多选）</h4>
              <el-transfer
                v-model="selectedSections"
                :data="transferSectionOptions"
                :titles="['可选章节', '已选章节']"
                :button-texts="['移除', '添加']"
                filterable
                filter-placeholder="搜索章节"
                class="section-transfer"
                :props="{
                  key: 'key',
                  label: 'label'
                }"
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

          <div class="citation-option">
            <h4>编辑引用</h4>
            <el-button
              type="success"
              :disabled="!paperContent"
              @click="openCitationEditor"
            >
              编辑引用
            </el-button>
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
        <div class="result-header">
          <h3>{{ paperContent.title }}</h3>
          <div class="actions">
            <el-button type="primary" @click="openCitationEditor">
              <el-icon><EditPen /></el-icon>
              编辑引用
            </el-button>
            <el-button type="success" @click="saveContent">保存内容</el-button>
            <el-button @click="copyContent">复制内容</el-button>
            <el-button type="warning" @click="improveContent">改进内容</el-button>
          </div>
        </div>

        <div class="content-display">
          <div v-html="formatContent(paperContent.content)"></div>
        </div>
      </div>

      <div v-else class="full-paper-content">
        <div class="result-header">
          <h3>{{ paperContent.title }}</h3>
          <div class="actions">
            <el-button type="primary" @click="openCitationEditor">
              <el-icon><EditPen /></el-icon>
              编辑引用
            </el-button>
            <el-button type="success" @click="saveFullPaper">保存论文</el-button>
            <el-button @click="copyContent">复制内容</el-button>
          </div>
        </div>

        <div class="content-display">
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
            <div class="section-content">
              <div v-html="formatContent(section.content)"></div>
            </div>
          </div>
        </div>

        <div class="paper-actions">
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
      <MultiSelect
        v-model="selectedSearchResults"
        :results="searchResults"
        :loading="loading"
        :search-performed="searchPerformed"
        placeholder="输入关键词搜索文献"
        empty-text="未找到相关文献"
        @search="performSearchWithParams"
        @confirm="addSelectedLiterature"
        @cancel="literatureDialogVisible = false"
      >
        <template #table-columns>
          <el-table-column prop="title" label="标题" show-overflow-tooltip />
          <el-table-column prop="authors" label="作者" width="220" show-overflow-tooltip>
            <template #default="scope">
              {{ scope.row.authors.join(', ') }}
            </template>
          </el-table-column>
          <el-table-column prop="year" label="年份" width="80" />
          <el-table-column prop="venue" label="发表期刊/会议" width="150" show-overflow-tooltip />
          <el-table-column prop="citations" label="引用次数" width="100" sortable />
        </template>

        <template #item-label="{ item }">
          {{ item.title }} ({{ item.year }})
        </template>

        <template #actions="{ selection }">
          <el-button @click="literatureDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addSelectedLiterature" :disabled="selectedSearchResults.length === 0">
            添加选中文献 ({{ selectedSearchResults.length }})
          </el-button>
        </template>
      </MultiSelect>
    </el-dialog>

    <!-- 引用编辑器组件 -->
    <CitationEditor
      :visible="citationEditorVisible"
      @update:visible="citationEditorVisible = $event"
      :content="currentEditContent"
      :paper-content="paperContent"
      @save="handleSaveEditedContent"
    />

    <!-- 帮助对话框 -->
    <el-dialog
      v-model="helpDialogVisible"
      title="论文引用编辑功能说明"
      width="60%"
    >
      <div class="help-content">
        <h3>如何编辑论文中的引用</h3>
        <p>论文引用管理功能让您可以直接在编写论文时添加和管理引用，提高论文的学术质量。</p>

        <h4>主要功能</h4>
        <ul>
          <li><strong>添加引用</strong>：您可以在编辑器中任意位置添加引用标记。</li>
          <li><strong>提取引用</strong>：系统能自动识别您文本中的引用，并提供管理界面。</li>
          <li><strong>生成参考文献</strong>：根据论文中的引用，自动生成格式化的参考文献列表。</li>
        </ul>

        <h4>使用建议</h4>
        <ul>
          <li>完成论文初稿后，使用引用工具为论点提供支持</li>
          <li>利用引用格式化工具保持引用风格一致</li>
          <li>定期保存您的工作</li>
        </ul>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { saveUserData, getUserData } from '@/utils/userStorage';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { generatePaperSection, generateFullPaper } from '@/api/modules/papers';
import { searchLiterature as searchLiteratureApi } from '@/api/modules/search';
import CitationEditor from './CitationEditor.vue';
import MultiSelect from '@/components/Common/MultiSelect.vue';
import { EditPen } from '@element-plus/icons-vue';
import type { OutlineResponse } from '@/types/outlines';
import type { PaperSectionResponse, FullPaperResponse } from '@/types/papers';
import type { Paper } from '@/types/search';

const router = useRouter();

// 提纲数据
const outline = ref<OutlineResponse | null>(null);

// 生成类型
const generationType = ref<'section' | 'full'>('section');

// 已移除旧版单选，使用多选替代

// 选中的章节（多选）
const selectedSections = ref<string[]>([]);

// 监听选中章节变化，用于调试
watch(selectedSections, (newVal: string[]) => {
  console.log('选中的章节已更新:', newVal);
}, { deep: true });

// 已移除级联选择器相关代码，使用穿梭框替代

// 章节选项（穿梭框用）
const transferSectionOptions = computed(() => {
  if (!outline.value) return [];

  const options: Array<{key: string; label: string; disabled: boolean}> = [];

  // 添加主章节
  outline.value.sections.forEach(section => {
    options.push({
      key: section.id,
      label: section.title,
      disabled: false
    });

    // 添加子章节
    if (section.subsections && section.subsections.length > 0) {
      section.subsections.forEach(subsection => {
        options.push({
          key: `${section.id}-${subsection.id}`,
          label: `${section.title} > ${subsection.title}`,
          disabled: false
        });
      });
    }
  });

  return options;
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

// 引用编辑相关
const citationEditorVisible = ref(false);
const helpDialogVisible = ref(false);
const currentEditContent = ref('');

// 从用户存储中获取提纲和论文数据
onMounted(() => {
  // 加载提纲
  const storedOutline = getUserData<OutlineResponse>('selectedOutline');
  if (storedOutline) {
    outline.value = storedOutline;
  } else {
    // 如果没有选中的提纲，尝试加载当前生成的提纲
    const currentOutline = getUserData<OutlineResponse>('currentOutline');
    if (currentOutline) {
      outline.value = currentOutline;
    }
  }

  // 如果仍然没有提纲，尝试从手动输入的主题创建一个基本提纲
  if (!outline.value) {
    const manualTopic = getUserData<{title: string; academic_field: string; academic_level: string}>('manualTopic');
    if (manualTopic && manualTopic.title) {
      // 创建一个基本的提纲对象
      outline.value = {
        title: manualTopic.title,
        academic_field: manualTopic.academic_field,
        academic_level: manualTopic.academic_level,
        abstract: '',
        keywords: [],
        sections: []
      } as any;

      console.log('已从手动输入的主题创建基本提纲:', outline.value);
    }
  }

  // 如果仍然没有提纲，尝试从学术设置创建一个空提纲
  if (!outline.value) {
    const academicSettings = getUserData<{academic_field: string; academic_level: string}>('academicSettings');
    if (academicSettings) {
      // 创建一个空的提纲对象，但包含学术设置
      outline.value = {
        title: '',
        academic_field: academicSettings.academic_field,
        academic_level: academicSettings.academic_level,
        abstract: '',
        keywords: [],
        sections: []
      } as any;

      console.log('已从学术设置创建空提纲:', outline.value);
    }
  }

  // 加载完整论文（如果有）
  const storedPaper = getUserData<FullPaperResponse>('savedPaper');
  if (storedPaper) {
    // 确保加载的论文与当前提纲匹配
    if (outline.value && storedPaper.title && storedPaper.title.includes(outline.value.title)) {
      paperContent.value = storedPaper;
      generationType.value = 'full';
      ElMessage.info('已加载保存的论文');
    }
  }

  // 加载保存的章节
  const storedSections = getUserData<Record<string, PaperSectionResponse>>('savedSections');
  if (storedSections && generationType.value === 'section' && !paperContent.value) {
    // 如果有选中的章节并且该章节有保存的内容
    if (selectedSections.value.length > 0) {
      // 检查选中的章节是否有保存的内容
      const sectionId = selectedSections.value[0]; // 只加载第一个选中的章节
      if (storedSections[sectionId]) {
        paperContent.value = storedSections[sectionId];
        ElMessage.info('已加载保存的章节内容');
      }
    } else if (Object.keys(storedSections).length > 0) {
      // 如果没有选中章节但有保存的内容，加载第一个
      const firstSectionId = Object.keys(storedSections)[0];
      paperContent.value = storedSections[firstSectionId];
      // 设置选中的章节
      selectedSections.value = [firstSectionId];
      ElMessage.info('已加载上次保存的章节内容');
    }
  }
});

// 前往提纲生成页面
const goToOutlineGenerate = () => {
  router.push({
    name: 'OutlineGenerate'
  });
};

// 打开引用编辑对话框
const openCitationEditor = () => {
  if (!paperContent.value) return;

  // 根据生成类型获取正文内容
  if (generationType.value === 'full') {
    const fullPaper = paperContent.value as FullPaperResponse;
    // 合并所有章节内容
    let combinedContent = '';
    Object.entries(fullPaper.sections).forEach(([_, section]) => {
      combinedContent += `## ${section.title}\n\n${section.content}\n\n`;
    });
    currentEditContent.value = combinedContent;
  } else {
    const section = paperContent.value as PaperSectionResponse;
    currentEditContent.value = section.content;
  }

  citationEditorVisible.value = true;
};

// 打开引用管理器
const openCitationManager = () => {
  router.push({ name: 'Bibliography' });
};

// 显示帮助信息
const showHelp = () => {
  helpDialogVisible.value = true;
};

// 搜索文献
const searchLiterature = () => {
  literatureDialogVisible.value = true;
  searchQuery.value = outline.value?.title || '';
};

// 使用performSearchWithParams替代

// 处理来自MultiSelect组件的搜索请求
const performSearchWithParams = async (params: { query: string; pageSize?: number; page?: number }) => {
  if (!params.query) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }

  try {
    loading.value = true;
    searchQuery.value = params.query; // 同步搜索框的值

    // 使用扩展的搜索参数
    const searchParams: any = {
      query: params.query,
      limit: params.pageSize || 20
    };

    // 添加可选参数
    if (params.page) searchParams.page = params.page;

    const result = await searchLiteratureApi(searchParams);

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

// 处理引用编辑器保存的内容
const handleSaveEditedContent = (content: string) => {
  if (!content || !paperContent.value) return;

  // 根据生成类型更新内容
  if (generationType.value === 'full') {
    const fullPaper = paperContent.value as FullPaperResponse;

    // 尝试解析编辑后的内容，将其分配回各个章节
    // 假设内容格式为: ## 章节标题\n\n章节内容\n\n
    const sections = content.split(/(?=## )/);

    for (const sectionText of sections) {
      if (!sectionText.trim()) continue;

      const titleMatch = sectionText.match(/## (.*?)(?:\n|$)/);
      if (titleMatch) {
        const title = titleMatch[1].trim();

        // 查找匹配的章节
        for (const [_, section] of Object.entries(fullPaper.sections)) {
          if (section.title.trim() === title) {
            // 提取章节内容（标题后的所有内容）
            const contentStart = sectionText.indexOf('\n', sectionText.indexOf(title));
            if (contentStart > -1) {
              section.content = sectionText.substring(contentStart).trim();
            }
            break;
          }
        }
      }
    }

    saveFullPaper();
  } else {
    const section = paperContent.value as PaperSectionResponse;
    section.content = content;
    saveContent();
  }

  ElMessage.success('引用编辑已保存');
};

// 已在MultiSelect组件中处理选择变化

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

  if (generationType.value === 'section' && selectedSections.value.length === 0) {
    ElMessage.warning('请选择要生成的章节');
    return;
  }

  try {
    loading.value = true;

    if (generationType.value === 'section') {
      // 使用新的多选章节
      if (selectedSections.value.length === 1) {
        // 单章节生成
        const sectionId = selectedSections.value[0];

        const result = await generatePaperSection({
          topic: outline.value.title,
          outline: outline.value,
          section_id: sectionId,
          literature: selectedLiterature.value.length > 0 ? selectedLiterature.value : undefined
        });

        paperContent.value = result;
        ElMessage.success('章节生成成功');
      } else {
        // 多章节生成
        const sections: Record<string, any> = {};
        let totalTokens = 0;

        // 显示进度消息
        ElMessage.info(`开始生成 ${selectedSections.value.length} 个章节，请耐心等待...`);

        // 依次生成每个章节
        for (let i = 0; i < selectedSections.value.length; i++) {
          const sectionId = selectedSections.value[i];

          try {
            const result = await generatePaperSection({
              topic: outline.value.title,
              outline: outline.value,
              section_id: sectionId,
              literature: selectedLiterature.value.length > 0 ? selectedLiterature.value : undefined
            });

            // 保存章节内容
            sections[sectionId] = {
              title: result.title,
              content: result.content
            };

            // 累计token使用量
            totalTokens += result.token_usage.total_tokens || 0;

            // 保存到本地存储
            const savedSections = getUserData<Record<string, PaperSectionResponse>>('savedSections') || {};
            savedSections[sectionId] = result;
            saveUserData('savedSections', savedSections);

            // 显示进度
            ElMessage.success(`已生成 ${i + 1}/${selectedSections.value.length} 个章节`);
          } catch (error) {
            console.error(`生成章节 ${sectionId} 失败:`, error);
            ElMessage.error(`生成章节 ${sectionId} 失败，将继续生成其他章节`);
          }
        }

        // 创建一个类似FullPaperResponse的结构
        const fullPaperResult = {
          title: outline.value.title,
          abstract: outline.value.abstract || "",
          keywords: outline.value.keywords || [],
          sections: sections,
          token_usage: totalTokens
        };

        paperContent.value = fullPaperResult as any;
        generationType.value = 'full'; // 切换到完整论文视图以显示多个章节
        ElMessage.success(`已完成 ${selectedSections.value.length} 个章节的生成`);
      }
    } else {
      // 生成完整论文
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

  // 将内容保存到用户存储
  const savedSections = getUserData<Record<string, PaperSectionResponse>>('savedSections') || {};
  savedSections[content.section_id] = content;
  saveUserData('savedSections', savedSections);

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

  // 将论文保存到用户存储
  saveUserData('savedPaper', paper);

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
  Object.entries(paper.sections).forEach(([_, section]) => {
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
  Object.entries(paper.sections).forEach(([_, section]) => {
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

.section-transfer {
  margin: 15px 0;
  height: 300px;
  width: 100%;
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

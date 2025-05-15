<template>
  <div class="translate-button">
    <el-button
      type="primary"
      size="small"
      @click="translate"
      :loading="loading"
      :disabled="!content"
    >
      <el-icon><ChatLineSquare /></el-icon>
      {{ buttonText }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps, defineEmits } from 'vue';
import { ElMessage } from 'element-plus';
import { ChatLineSquare } from '@element-plus/icons-vue';
import { translateContent } from '@/api/modules/translation';

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  sourceLang: {
    type: String,
    default: 'en'
  },
  targetLang: {
    type: String,
    default: 'zh-CN'
  },
  isAcademic: {
    type: Boolean,
    default: true
  },
  buttonText: {
    type: String,
    default: '翻译成中文'
  }
});

const emit = defineEmits(['translated']);
const loading = ref(false);

const translate = async () => {
  if (!props.content) {
    ElMessage.warning('没有可翻译的内容');
    return;
  }

  loading.value = true;
  try {
    const result = await translateContent({
      content: props.content,
      source_lang: props.sourceLang,
      target_lang: props.targetLang,
      is_academic: props.isAcademic
    });

    emit('translated', result.translated_content);
    ElMessage.success('翻译成功');
  } catch (error) {
    console.error('翻译失败:', error);
    ElMessage.error('翻译失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.translate-button {
  margin: 10px 0;
}
</style>

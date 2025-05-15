<template>
  <div class="translatable-content">
    <div class="content-actions">
      <translate-button 
        :content="originalContent" 
        @translated="handleTranslated" 
        :button-text="buttonText"
        :is-academic="isAcademic"
      />
      
      <el-switch
        v-if="translatedContent"
        v-model="showOriginal"
        active-text="显示原文"
        inactive-text="隐藏原文"
        class="content-switch"
      />
    </div>
    
    <div v-if="showOriginal" class="original-content">
      <h4>原文</h4>
      <div v-html="originalContent"></div>
    </div>
    
    <div v-if="translatedContent" class="translated-content">
      <h4>译文</h4>
      <div v-html="translatedContent"></div>
    </div>
    
    <div v-if="!showOriginal && !translatedContent" class="original-content">
      <div v-html="originalContent"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps } from 'vue';
import TranslateButton from './TranslateButton.vue';

const props = defineProps({
  originalContent: {
    type: String,
    required: true
  },
  buttonText: {
    type: String,
    default: '翻译成中文'
  },
  isAcademic: {
    type: Boolean,
    default: true
  }
});

const translatedContent = ref('');
const showOriginal = ref(true);

const handleTranslated = (content: string) => {
  translatedContent.value = content;
};
</script>

<style scoped>
.translatable-content {
  margin: 15px 0;
}

.content-actions {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.content-switch {
  margin-left: 15px;
}

.original-content, .translated-content {
  margin-top: 10px;
  padding: 10px;
  border-radius: 4px;
}

.original-content {
  background-color: #f5f7fa;
}

.translated-content {
  background-color: #ecf5ff;
}

h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #606266;
}
</style>

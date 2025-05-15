<template>
  <div class="multi-select-container">
    <div class="search-section">
      <el-input
        v-model="searchQuery"
        :placeholder="placeholder"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>
    
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>
    
    <div v-else-if="results.length > 0" class="results-section">
      <el-table
        ref="multiTable"
        :data="results"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <slot name="table-columns"></slot>
      </el-table>
      
      <div class="pagination-section" v-if="showPagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next"
          :total="totalCount"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
    
    <div v-else-if="searchPerformed" class="no-results">
      <el-empty :description="emptyText" />
    </div>
    
    <div class="selected-items" v-if="modelValue && modelValue.length > 0">
      <h5>已选择 {{ modelValue.length }} 项</h5>
      <div class="selected-tags">
        <el-tag
          v-for="(item, index) in modelValue"
          :key="getItemKey(item, index)"
          closable
          @close="removeSelectedItem(index)"
          class="selected-tag"
        >
          <slot name="item-label" :item="item">
            {{ item.title || item.name || '未命名项' }}
          </slot>
        </el-tag>
      </div>
    </div>
    
    <div class="action-buttons">
      <slot name="actions">
        <el-button @click="$emit('cancel')">取消</el-button>
        <el-button type="primary" @click="confirmSelection" :disabled="!modelValue || modelValue.length === 0">
          确认选择
        </el-button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

const props = defineProps({
  modelValue: {
    type: Array,
    required: true
  },
  results: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  searchPerformed: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '请输入搜索关键词'
  },
  emptyText: {
    type: String,
    default: '未找到相关数据'
  },
  totalCount: {
    type: Number,
    default: 0
  },
  showPagination: {
    type: Boolean,
    default: false
  },
  itemKey: {
    type: String,
    default: 'id'
  }
});

const emit = defineEmits([
  'update:modelValue',
  'search',
  'selection-change',
  'confirm',
  'cancel',
  'size-change',
  'current-change'
]);

const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const multiTable = ref(null);

// 处理搜索事件
const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }
  
  currentPage.value = 1;
  emit('search', {
    query: searchQuery.value,
    page: currentPage.value,
    pageSize: pageSize.value
  });
};

// 处理选择变化
const handleSelectionChange = (selection) => {
  emit('selection-change', selection);
};

// 确认选择
const confirmSelection = () => {
  emit('confirm', props.modelValue);
};

// 移除已选项
const removeSelectedItem = (index) => {
  const newSelection = [...props.modelValue];
  newSelection.splice(index, 1);
  emit('update:modelValue', newSelection);
  
  // 如果表格已加载，尝试更新表格选择状态
  updateTableSelection();
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size;
  emit('size-change', size);
};

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page;
  emit('current-change', page);
};

// 获取项的唯一键
const getItemKey = (item, index) => {
  return item[props.itemKey] || `item-${index}`;
};

// 更新表格选择状态以匹配modelValue
const updateTableSelection = () => {
  if (multiTable.value && props.results) {
    // 清除当前选择
    multiTable.value.clearSelection();
    
    // 为每个在modelValue中的项设置选中状态
    if (props.modelValue && props.modelValue.length > 0) {
      // 获取每个项的唯一标识，用于比较
      const selectedKeys = props.modelValue.map(item => getItemKey(item));
      
      props.results.forEach((row, index) => {
        const rowKey = getItemKey(row);
        if (selectedKeys.includes(rowKey)) {
          multiTable.value.toggleRowSelection(row, true);
        }
      });
    }
  }
};

// 当结果变化时更新表格选择状态
watch(() => props.results, () => {
  setTimeout(() => {
    updateTableSelection();
  }, 0);
}, { deep: true });

// 组件挂载时初始化
onMounted(() => {
  updateTableSelection();
});
</script>

<style scoped>
.multi-select-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.results-section {
  margin: 16px 0;
}

.pagination-section {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.selected-items {
  margin: 16px 0;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.selected-tag {
  margin-right: 0;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.loading-state {
  margin: 16px 0;
}
</style>

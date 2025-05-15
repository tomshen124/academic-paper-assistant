<template>
  <div class="mcp-external-connector-page">
    <page-header title="外部MCP服务器连接" />
    
    <div class="page-content">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>连接到外部MCP服务器</span>
            <el-tooltip content="MCP (Model Context Protocol) 是一个用于连接大型语言模型和工具的协议。通过连接到外部MCP服务器，您可以使用其提供的工具和资源。">
              <el-icon><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
        </template>
        
        <mcp-external-connector />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '@/components/Common/PageHeader.vue'
import MCPExternalConnector from '@/components/MCPExternalConnector.vue'
import { QuestionFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.mcp-external-connector-page {
  padding: 20px;
}

.page-content {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>

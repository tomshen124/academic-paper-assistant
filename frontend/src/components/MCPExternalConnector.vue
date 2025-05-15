<template>
  <div class="mcp-external-connector">
    <h2>连接到外部MCP服务器</h2>
    
    <div class="connection-form">
      <div class="form-group">
        <label for="server-type">服务器类型</label>
        <select id="server-type" v-model="serverType">
          <option value="stdio">标准输入/输出</option>
          <option value="http">HTTP</option>
          <option value="claude">Claude Desktop</option>
        </select>
      </div>
      
      <div v-if="serverType === 'stdio'" class="form-group">
        <label for="command">服务器命令</label>
        <input id="command" v-model="command" placeholder="例如: python mcp_server.py" />
        
        <label for="args">命令行参数</label>
        <input id="args" v-model="args" placeholder="例如: --port 8000" />
      </div>
      
      <div v-if="serverType === 'http'" class="form-group">
        <label for="url">服务器URL</label>
        <input id="url" v-model="url" placeholder="例如: http://localhost:8000/mcp" />
      </div>
      
      <div class="form-actions">
        <button @click="connectToServer" :disabled="isConnecting || isConnected">连接</button>
        <button @click="disconnectFromServer" :disabled="isConnecting || !isConnected">断开连接</button>
      </div>
    </div>
    
    <div v-if="isConnected" class="server-info">
      <h3>服务器信息</h3>
      <p><strong>名称:</strong> {{ serverInfo.name }}</p>
      <p><strong>版本:</strong> {{ serverInfo.version }}</p>
    </div>
    
    <div v-if="isConnected" class="server-capabilities">
      <h3>服务器功能</h3>
      
      <div class="tabs">
        <div class="tab" :class="{ active: activeTab === 'tools' }" @click="activeTab = 'tools'">工具</div>
        <div class="tab" :class="{ active: activeTab === 'resources' }" @click="activeTab = 'resources'">资源</div>
        <div class="tab" :class="{ active: activeTab === 'prompts' }" @click="activeTab = 'prompts'">提示模板</div>
      </div>
      
      <div class="tab-content">
        <!-- 工具 -->
        <div v-if="activeTab === 'tools'" class="tools-tab">
          <button @click="listTools" :disabled="isLoading">刷新工具列表</button>
          
          <div v-if="isLoading" class="loading">加载中...</div>
          
          <div v-else-if="tools.length === 0" class="empty-state">
            没有可用的工具
          </div>
          
          <div v-else class="tools-list">
            <div v-for="tool in tools" :key="tool.name" class="tool-item">
              <h4>{{ tool.name }}</h4>
              <p>{{ tool.description }}</p>
              
              <div class="tool-parameters">
                <h5>参数:</h5>
                <div v-for="param in tool.parameters" :key="param.name" class="tool-param">
                  <span class="param-name">{{ param.name }}</span>
                  <span class="param-type">({{ param.type }})</span>
                  <span v-if="param.description" class="param-desc">: {{ param.description }}</span>
                </div>
              </div>
              
              <button @click="selectTool(tool)" class="call-tool-btn">调用工具</button>
            </div>
          </div>
          
          <!-- 工具调用表单 -->
          <div v-if="selectedTool" class="tool-call-form">
            <h4>调用工具: {{ selectedTool.name }}</h4>
            
            <div v-for="param in selectedTool.parameters" :key="param.name" class="form-group">
              <label :for="'param-' + param.name">{{ param.name }}</label>
              <input :id="'param-' + param.name" v-model="toolParams[param.name]" :placeholder="param.description || param.name" />
            </div>
            
            <div class="form-actions">
              <button @click="callTool" :disabled="isCallingTool">调用</button>
              <button @click="selectedTool = null">取消</button>
            </div>
            
            <div v-if="toolResult" class="tool-result">
              <h5>调用结果:</h5>
              <pre>{{ JSON.stringify(toolResult, null, 2) }}</pre>
            </div>
          </div>
        </div>
        
        <!-- 资源 -->
        <div v-if="activeTab === 'resources'" class="resources-tab">
          <button @click="listResources" :disabled="isLoading">刷新资源列表</button>
          
          <div v-if="isLoading" class="loading">加载中...</div>
          
          <div v-else-if="resources.length === 0" class="empty-state">
            没有可用的资源
          </div>
          
          <div v-else class="resources-list">
            <div v-for="resource in resources" :key="resource.uri_template" class="resource-item">
              <h4>{{ resource.uri_template }}</h4>
              <p>{{ resource.description }}</p>
              
              <div class="resource-parameters">
                <h5>参数:</h5>
                <div v-for="param in resource.parameters" :key="param.name" class="resource-param">
                  <span class="param-name">{{ param.name }}</span>
                  <span class="param-type">({{ param.type }})</span>
                  <span v-if="param.description" class="param-desc">: {{ param.description }}</span>
                </div>
              </div>
              
              <button @click="selectResource(resource)" class="read-resource-btn">读取资源</button>
            </div>
          </div>
          
          <!-- 资源读取表单 -->
          <div v-if="selectedResource" class="resource-read-form">
            <h4>读取资源: {{ selectedResource.uri_template }}</h4>
            
            <div v-for="param in selectedResource.parameters" :key="param.name" class="form-group">
              <label :for="'resource-param-' + param.name">{{ param.name }}</label>
              <input :id="'resource-param-' + param.name" v-model="resourceParams[param.name]" :placeholder="param.description || param.name" />
            </div>
            
            <div class="form-actions">
              <button @click="readResource" :disabled="isReadingResource">读取</button>
              <button @click="selectedResource = null">取消</button>
            </div>
            
            <div v-if="resourceContent" class="resource-content">
              <h5>资源内容:</h5>
              <pre>{{ resourceContent }}</pre>
            </div>
          </div>
        </div>
        
        <!-- 提示模板 -->
        <div v-if="activeTab === 'prompts'" class="prompts-tab">
          <button @click="listPrompts" :disabled="isLoading">刷新提示模板列表</button>
          
          <div v-if="isLoading" class="loading">加载中...</div>
          
          <div v-else-if="prompts.length === 0" class="empty-state">
            没有可用的提示模板
          </div>
          
          <div v-else class="prompts-list">
            <div v-for="prompt in prompts" :key="prompt.name" class="prompt-item">
              <h4>{{ prompt.name }}</h4>
              <p>{{ prompt.description }}</p>
              
              <div class="prompt-arguments">
                <h5>参数:</h5>
                <div v-for="arg in prompt.arguments" :key="arg.name" class="prompt-arg">
                  <span class="arg-name">{{ arg.name }}</span>
                  <span v-if="arg.description" class="arg-desc">: {{ arg.description }}</span>
                </div>
              </div>
              
              <button @click="selectPrompt(prompt)" class="get-prompt-btn">获取提示模板</button>
            </div>
          </div>
          
          <!-- 提示模板获取表单 -->
          <div v-if="selectedPrompt" class="prompt-get-form">
            <h4>获取提示模板: {{ selectedPrompt.name }}</h4>
            
            <div v-for="arg in selectedPrompt.arguments" :key="arg.name" class="form-group">
              <label :for="'prompt-arg-' + arg.name">{{ arg.name }}</label>
              <input :id="'prompt-arg-' + arg.name" v-model="promptArgs[arg.name]" :placeholder="arg.description || arg.name" />
            </div>
            
            <div class="form-actions">
              <button @click="getPrompt" :disabled="isGettingPrompt">获取</button>
              <button @click="selectedPrompt = null">取消</button>
            </div>
            
            <div v-if="promptResult" class="prompt-result">
              <h5>提示模板内容:</h5>
              <pre>{{ JSON.stringify(promptResult, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'MCPExternalConnector',
  
  data() {
    return {
      // 连接设置
      serverType: 'stdio',
      command: '',
      args: '',
      url: '',
      
      // 连接状态
      isConnecting: false,
      isConnected: false,
      serverInfo: {
        name: '',
        version: ''
      },
      
      // 标签页
      activeTab: 'tools',
      isLoading: false,
      
      // 工具
      tools: [],
      selectedTool: null,
      toolParams: {},
      isCallingTool: false,
      toolResult: null,
      
      // 资源
      resources: [],
      selectedResource: null,
      resourceParams: {},
      isReadingResource: false,
      resourceContent: null,
      
      // 提示模板
      prompts: [],
      selectedPrompt: null,
      promptArgs: {},
      isGettingPrompt: false,
      promptResult: null
    };
  },
  
  methods: {
    // 连接到服务器
    async connectToServer() {
      this.isConnecting = true;
      
      try {
        const requestData = {
          server_type: this.serverType
        };
        
        if (this.serverType === 'stdio') {
          requestData.command = this.command;
          requestData.args = this.args.split(' ').filter(arg => arg.trim() !== '');
        } else if (this.serverType === 'http') {
          requestData.url = this.url;
        }
        
        const response = await axios.post('/api/v1/mcp-external/connect', requestData);
        
        if (response.data.connected) {
          this.isConnected = true;
          this.serverInfo.name = response.data.server_name;
          this.serverInfo.version = response.data.server_version;
          
          // 加载初始数据
          this.listTools();
        } else {
          alert(`连接失败: ${response.data.message}`);
        }
      } catch (error) {
        console.error('连接到服务器时出错:', error);
        alert(`连接到服务器时出错: ${error.response?.data?.detail || error.message}`);
      } finally {
        this.isConnecting = false;
      }
    },
    
    // 断开连接
    async disconnectFromServer() {
      try {
        await axios.post('/api/v1/mcp-external/disconnect');
        this.isConnected = false;
        this.serverInfo = { name: '', version: '' };
        this.tools = [];
        this.resources = [];
        this.prompts = [];
        this.selectedTool = null;
        this.selectedResource = null;
        this.selectedPrompt = null;
      } catch (error) {
        console.error('断开连接时出错:', error);
        alert(`断开连接时出错: ${error.response?.data?.detail || error.message}`);
      }
    },
    
    // 列出工具
    async listTools() {
      this.isLoading = true;
      
      try {
        const response = await axios.get('/api/v1/mcp-external/tools');
        this.tools = response.data.tools;
      } catch (error) {
        console.error('列出工具时出错:', error);
        alert(`列出工具时出错: ${error.response?.data?.detail || error.message}`);
      } finally {
        this.isLoading = false;
      }
    },
    
    // 选择工具
    selectTool(tool) {
      this.selectedTool = tool;
      this.toolParams = {};
      this.toolResult = null;
    },
    
    // 调用工具
    async callTool() {
      this.isCallingTool = true;
      
      try {
        const response = await axios.post('/api/v1/mcp-external/tools/call', {
          tool_name: this.selectedTool.name,
          arguments: this.toolParams
        });
        
        this.toolResult = response.data.result;
      } catch (error) {
        console.error('调用工具时出错:', error);
        alert(`调用工具时出错: ${error.response?.data?.detail || error.message}`);
      } finally {
        this.isCallingTool = false;
      }
    },
    
    // 列出资源
    async listResources() {
      this.isLoading = true;
      
      try {
        const response = await axios.get('/api/v1/mcp-external/resources');
        this.resources = response.data.resources;
      } catch (error) {
        console.error('列出资源时出错:', error);
        alert(`列出资源时出错: ${error.response?.data?.detail || error.message}`);
      } finally {
        this.isLoading = false;
      }
    },
    
    // 选择资源
    selectResource(resource) {
      this.selectedResource = resource;
      this.resourceParams = {};
      this.resourceContent = null;
    },
    
    // 读取资源
    async readResource() {
      this.isReadingResource = true;
      
      try {
        // 替换URI模板中的参数
        let uri = this.selectedResource.uri_template;
        
        for (const [key, value] of Object.entries(this.resourceParams)) {
          uri = uri.replace(`{${key}}`, value);
        }
        
        const response = await axios.post('/api/v1/mcp-external/resources/read', {
          uri: uri
        });
        
        this.resourceContent = response.data.content;
      } catch (error) {
        console.error('读取资源时出错:', error);
        alert(`读取资源时出错: ${error.response?.data?.detail || error.message}`);
      } finally {
        this.isReadingResource = false;
      }
    },
    
    // 列出提示模板
    async listPrompts() {
      this.isLoading = true;
      
      try {
        const response = await axios.get('/api/v1/mcp-external/prompts');
        this.prompts = response.data.prompts;
      } catch (error) {
        console.error('列出提示模板时出错:', error);
        alert(`列出提示模板时出错: ${error.response?.data?.detail || error.message}`);
      } finally {
        this.isLoading = false;
      }
    },
    
    // 选择提示模板
    selectPrompt(prompt) {
      this.selectedPrompt = prompt;
      this.promptArgs = {};
      this.promptResult = null;
    },
    
    // 获取提示模板
    async getPrompt() {
      this.isGettingPrompt = true;
      
      try {
        const response = await axios.post('/api/v1/mcp-external/prompts/get', {
          name: this.selectedPrompt.name,
          arguments: this.promptArgs
        });
        
        this.promptResult = response.data.prompt;
      } catch (error) {
        console.error('获取提示模板时出错:', error);
        alert(`获取提示模板时出错: ${error.response?.data?.detail || error.message}`);
      } finally {
        this.isGettingPrompt = false;
      }
    }
  }
};
</script>

<style scoped>
.mcp-external-connector {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 20px;
}

.connection-form {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input, select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 10px;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.server-info {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 15px;
}

.tab {
  padding: 10px 15px;
  cursor: pointer;
}

.tab.active {
  border-bottom: 2px solid #4CAF50;
  font-weight: bold;
}

.loading {
  padding: 20px;
  text-align: center;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: #666;
}

.tools-list, .resources-list, .prompts-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.tool-item, .resource-item, .prompt-item {
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 15px;
}

.tool-parameters, .resource-parameters, .prompt-arguments {
  margin-top: 10px;
  margin-bottom: 15px;
}

.tool-param, .resource-param, .prompt-arg {
  margin-bottom: 5px;
}

.param-name, .arg-name {
  font-weight: bold;
}

.param-type {
  color: #666;
  margin-left: 5px;
}

.param-desc, .arg-desc {
  margin-left: 5px;
}

.tool-call-form, .resource-read-form, .prompt-get-form {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.tool-result, .resource-content, .prompt-result {
  margin-top: 15px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 5px;
  overflow-x: auto;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>

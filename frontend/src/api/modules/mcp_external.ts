import request from '@/utils/request'

/**
 * 连接到外部MCP服务器
 * @param serverType 服务器类型
 * @param command 服务器命令
 * @param args 命令行参数
 * @param url 服务器URL
 * @returns 连接结果
 */
export function connectToServer(serverType: string, command?: string, args?: string[], url?: string) {
  return request({
    url: '/api/v1/mcp-external/connect',
    method: 'post',
    data: {
      server_type: serverType,
      command,
      args,
      url
    }
  })
}

/**
 * 断开与外部MCP服务器的连接
 * @returns 断开连接结果
 */
export function disconnectFromServer() {
  return request({
    url: '/api/v1/mcp-external/disconnect',
    method: 'post'
  })
}

/**
 * 列出可用的工具
 * @returns 工具列表
 */
export function listTools() {
  return request({
    url: '/api/v1/mcp-external/tools',
    method: 'get'
  })
}

/**
 * 调用工具
 * @param toolName 工具名称
 * @param arguments 工具参数
 * @returns 工具执行结果
 */
export function callTool(toolName: string, arguments: Record<string, any>) {
  return request({
    url: '/api/v1/mcp-external/tools/call',
    method: 'post',
    data: {
      tool_name: toolName,
      arguments
    }
  })
}

/**
 * 列出可用的资源
 * @returns 资源列表
 */
export function listResources() {
  return request({
    url: '/api/v1/mcp-external/resources',
    method: 'get'
  })
}

/**
 * 读取资源
 * @param uri 资源URI
 * @returns 资源内容
 */
export function readResource(uri: string) {
  return request({
    url: '/api/v1/mcp-external/resources/read',
    method: 'post',
    data: {
      uri
    }
  })
}

/**
 * 列出可用的提示模板
 * @returns 提示模板列表
 */
export function listPrompts() {
  return request({
    url: '/api/v1/mcp-external/prompts',
    method: 'get'
  })
}

/**
 * 获取提示模板
 * @param name 提示模板名称
 * @param arguments 提示模板参数
 * @returns 提示模板内容
 */
export function getPrompt(name: string, arguments?: Record<string, string>) {
  return request({
    url: '/api/v1/mcp-external/prompts/get',
    method: 'post',
    data: {
      name,
      arguments
    }
  })
}

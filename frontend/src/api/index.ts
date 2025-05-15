// 导出统一的 request 实例
import { request } from '@/utils/request';

// 导出所有 API 模块
export * from './modules/auth';
export * from './modules/topics';
export * from './modules/outlines';
export * from './modules/papers';
export * from './modules/citations';
export * from './modules/search';
export * from './modules/agents';
export * from './modules/tokens';
export * from './modules/interests';
export * from './modules/translation';
export * from './modules/mcp_external';

// 导出 request 实例
export { request };
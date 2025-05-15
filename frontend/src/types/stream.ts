/**
 * 流式事件处理器接口
 */
export interface StreamEventHandler {
  /**
   * 处理状态消息
   * @param message 状态消息
   */
  onStatus?: (message: string) => void;
  
  /**
   * 处理兴趣分析结果
   * @param data 兴趣分析数据
   */
  onInterestAnalysis?: (data: any) => void;
  
  /**
   * 处理主题数据
   * @param topic 主题数据
   */
  onTopic?: (topic: any) => void;
  
  /**
   * 处理完成消息
   * @param message 完成消息
   */
  onComplete?: (message: string) => void;
  
  /**
   * 处理错误消息
   * @param message 错误消息
   */
  onError?: (message: string) => void;
}

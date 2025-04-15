// 通用类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 知识图谱类型
export interface Entity {
  id: number
  name: string
  entity_type: string
  attributes?: Array<{
    name: string
    value: string
  }>
}

export interface EntityRelation {
  id: number
  source_id: number
  target_id: number
  relation_type: string
}

export interface GraphData {
  nodes: Array<{
    id: number
    name: string
    entity_type: string
    symbolSize?: number
    category?: string
  }>
  links: Array<{
    source: number
    target: number
    relation_type: string
  }>
  categories: Array<{
    name: string
  }>
}

// 统计类型
export interface EntityTypeStats {
  total_count: number
  type_distribution: Record<string, number>
}

export interface EntityGrowthStats {
  start_date: string
  end_date: string
  interval: 'day' | 'week' | 'month'
  data_points: Array<{
    date: string
    count: number
  }>
}

export interface EntityAttributeStats {
  entity_type: string | null
  attribute_stats: Array<{
    name: string
    total: number
    percentage: number
  }>
}

export interface RelationTypeStats {
  total_count: number
  type_distribution: Record<string, number>
}

export interface StatisticsOverview {
  entity_stats: EntityTypeStats
  growth_stats: EntityGrowthStats
  attribute_stats: EntityAttributeStats
} 
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class EntityTypeStats(BaseModel):
    entity_type: str
    count: int
    avg_relations: float
    max_relations: int
    min_relations: int

class RelationTypeStats(BaseModel):
    relation_type: str
    count: int
    avg_weight: float
    max_weight: int
    min_weight: int

class ImportRecord(BaseModel):
    id: int
    file_name: str
    status: str
    entities_count: int
    relationships_count: int
    created_at: datetime

class EntityStats(BaseModel):
    total_entities: int
    entity_types: List[EntityTypeStats]

class RelationStats(BaseModel):
    total_relations: int
    relation_types: List[RelationTypeStats]

class ImportStats(BaseModel):
    total_imports: int
    successful_imports: int
    failed_imports: int
    total_entities_imported: int
    total_relationships_imported: int
    recent_imports: List[ImportRecord]

class StatisticsOverview(BaseModel):
    entity_stats: EntityStats
    relation_stats: RelationStats
    import_stats: ImportStats

    class Config:
        from_attributes = True

class GrowthDataPoint(BaseModel):
    """增长趋势数据点"""
    timestamp: datetime
    count: int
    type_distribution: Optional[Dict[str, int]] = None

class EntityGrowthStats(BaseModel):
    """实体增长趋势统计"""
    start_date: datetime
    end_date: datetime
    daily_counts: Dict[str, int]

class AttributeStats(BaseModel):
    """属性统计信息"""
    total_count: int
    filled_count: int
    null_count: int
    fill_rate: float
    value_distribution: Optional[Dict[str, int]] = None

class EntityAttributeStats(BaseModel):
    """实体属性统计"""
    entity_type: Optional[str] = None
    attribute_stats: Dict[str, AttributeStats]

class StatisticsResponse(BaseModel):
    """统计概览响应"""
    entity_stats: EntityTypeStats
    relation_stats: RelationTypeStats
    growth_stats: EntityGrowthStats
    attribute_stats: EntityAttributeStats 
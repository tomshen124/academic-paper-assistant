from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from redis import Redis

from app.models.entity import Entity
from app.models.relation import Relation
from app.models.attribute import Attribute
from app.schemas.statistics import (
    EntityTypeStats,
    EntityGrowthStats,
    RelationTypeStats,
    AttributeStats,
    EntityAttributeStats,
    StatisticsResponse
)

class StatisticsService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis
        self.cache_ttl = 3600  # 1小时缓存过期

    async def get_entity_type_stats(self) -> EntityTypeStats:
        """获取实体类型分布统计"""
        cache_key = "entity_type_stats"
        
        # 尝试从缓存获取
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return EntityTypeStats.parse_raw(cached_data)
        
        # 数据库查询
        stats = (
            self.db.query(
                Entity.type,
                func.count(Entity.id).label("count")
            )
            .group_by(Entity.type)
            .all()
        )
        
        result = EntityTypeStats(
            total_count=sum(item[1] for item in stats),
            type_distribution={item[0]: item[1] for item in stats}
        )
        
        # 更新缓存
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            result.json()
        )
        
        return result

    async def get_entity_growth_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> EntityGrowthStats:
        """获取实体增长趋势统计"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        cache_key = f"entity_growth_{start_date.date()}_{end_date.date()}"
        
        # 尝试从缓存获取
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return EntityGrowthStats.parse_raw(cached_data)
            
        # 数据库查询
        stats = (
            self.db.query(
                func.date(Entity.created_at).label("date"),
                func.count(Entity.id).label("count")
            )
            .filter(Entity.created_at.between(start_date, end_date))
            .group_by(func.date(Entity.created_at))
            .order_by(func.date(Entity.created_at))
            .all()
        )
        
        result = EntityGrowthStats(
            start_date=start_date,
            end_date=end_date,
            daily_counts={str(item[0]): item[1] for item in stats}
        )
        
        # 更新缓存
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            result.json()
        )
        
        return result

    async def get_relation_type_stats(self) -> RelationTypeStats:
        """获取关系类型分布统计"""
        cache_key = "relation_type_stats"
        
        # 尝试从缓存获取
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return RelationTypeStats.parse_raw(cached_data)
        
        # 数据库查询
        stats = (
            self.db.query(
                Relation.type,
                func.count(Relation.id).label("count")
            )
            .group_by(Relation.type)
            .all()
        )
        
        result = RelationTypeStats(
            total_count=sum(item[1] for item in stats),
            type_distribution={item[0]: item[1] for item in stats}
        )
        
        # 更新缓存
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            result.json()
        )
        
        return result

    async def get_entity_attribute_stats(
        self,
        entity_type: Optional[str] = None
    ) -> EntityAttributeStats:
        """获取实体属性统计
        
        Args:
            entity_type: 可选的实体类型过滤
        """
        cache_key = f"entity_attribute_stats_{entity_type or 'all'}"
        
        # 尝试从缓存获取
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return EntityAttributeStats.parse_raw(cached_data)
        
        # 基础查询
        base_query = self.db.query(
            Entity.type,
            Attribute.name,
            func.count(Attribute.id).label("total"),
            func.count(Attribute.value).label("filled"),
            func.count(func.nullif(Attribute.value, None)).label("null_count")
        ).join(
            Attribute,
            Entity.id == Attribute.entity_id
        )
        
        # 添加实体类型过滤
        if entity_type:
            base_query = base_query.filter(Entity.type == entity_type)
        
        # 分组统计
        stats = base_query.group_by(
            Entity.type,
            Attribute.name
        ).all()
        
        # 处理结果
        attribute_stats = {}
        for stat in stats:
            total = stat.total
            filled = stat.filled
            
            attribute_stats[stat.name] = AttributeStats(
                total_count=total,
                filled_count=filled,
                null_count=total - filled,
                fill_rate=filled / total if total > 0 else 0.0,
                value_distribution=None  # TODO: 实现值分布统计
            )
        
        result = EntityAttributeStats(
            entity_type=entity_type,
            attribute_stats=attribute_stats
        )
        
        # 更新缓存
        self.redis.setex(
            cache_key,
            self.cache_ttl,
            result.json()
        )
        
        return result

    async def get_statistics_overview(self) -> StatisticsResponse:
        """获取统计概览"""
        entity_stats = await self.get_entity_type_stats()
        relation_stats = await self.get_relation_type_stats()
        growth_stats = await self.get_entity_growth_stats()
        attribute_stats = await self.get_entity_attribute_stats()
        
        return StatisticsResponse(
            entity_stats=entity_stats,
            relation_stats=relation_stats,
            growth_stats=growth_stats,
            attribute_stats=attribute_stats
        ) 
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, select, union_all
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.models.import_record import DBImportRecord

class StatisticsService:
    """统计服务"""
    
    def __init__(self, db: Session):
        self.db = db

    def get_entity_stats(self) -> Dict[str, Any]:
        """获取实体统计信息"""
        try:
            # 学术论文辅助平台不再使用知识图谱，返回空统计
            return {
                "total_entities": 0,
                "entity_types": [],
                "top_entities": [],
                "recent_entities": []
            }
        except Exception as e:
            logger.error(f"获取实体统计信息失败: {str(e)}")
            return {
                "total_entities": 0,
                "entity_types": [],
                "top_entities": [],
                "recent_entities": [],
                "error": str(e)
            }

    def get_relationship_stats(self) -> Dict[str, Any]:
        """获取关系统计信息"""
        try:
            # 学术论文辅助平台不再使用知识图谱，返回空统计
            return {
                "total_relationships": 0,
                "relationship_types": [],
                "top_relationships": []
            }
        except Exception as e:
            logger.error(f"获取关系统计信息失败: {str(e)}")
            return {
                "total_relationships": 0,
                "relationship_types": [],
                "top_relationships": [],
                "error": str(e)
            }

    def get_import_stats(self) -> Dict[str, Any]:
        """获取导入统计信息"""
        try:
            # 获取导入记录总数
            total_imports = self.db.query(DBImportRecord).count()
            
            # 获取成功和失败的导入数量
            status_counts = (
                self.db.query(
                    DBImportRecord.status,
                    func.count().label('count')
                )
                .group_by(DBImportRecord.status)
                .all()
            )
            
            # 获取最近的导入记录
            recent_imports = (
                self.db.query(DBImportRecord)
                .order_by(DBImportRecord.created_at.desc())
                .limit(5)
                .all()
            )
            
            # 按文件类型统计
            file_type_stats = (
                self.db.query(
                    DBImportRecord.file_type,
                    func.count().label('count')
                )
                .group_by(DBImportRecord.file_type)
                .all()
            )
            
            return {
                "total_imports": total_imports,
                "status_counts": [
                    {"status": status, "count": count}
                    for status, count in status_counts
                ],
                "recent_imports": [
                    {
                        "id": imp.id,
                        "file_name": imp.file_name,
                        "file_type": imp.file_type,
                        "status": imp.status,
                        "created_at": imp.created_at.isoformat() if imp.created_at else None,
                        "entities_count": imp.entities_count,
                        "relationships_count": imp.relationships_count
                    }
                    for imp in recent_imports
                ],
                "file_type_stats": [
                    {"file_type": ft, "count": count}
                    for ft, count in file_type_stats
                ]
            }
        except Exception as e:
            logger.error(f"获取导入统计信息失败: {str(e)}")
            return {
                "total_imports": 0,
                "status_counts": [],
                "recent_imports": [],
                "file_type_stats": [],
                "error": str(e)
            }

    def get_overall_stats(self) -> Dict[str, Any]:
        """获取总体统计信息"""
        entity_stats = self.get_entity_stats()
        relationship_stats = self.get_relationship_stats()
        import_stats = self.get_import_stats()
        
        return {
            "entities": entity_stats,
            "relationships": relationship_stats,
            "imports": import_stats,
            "timestamp": datetime.now().isoformat()
        }

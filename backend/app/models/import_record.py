from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.sql import func
from app.db.base_class import Base
from enum import Enum as PyEnum

class ImportStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class DBImportRecord(Base):
    """导入记录模型"""
    __tablename__ = "import_records"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default=ImportStatus.PENDING)
    error_message = Column(Text, nullable=True)
    entities_count = Column(Integer, default=0)
    relationships_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ImportRecord(id={self.id}, file_name='{self.file_name}', status='{self.status}')>" 
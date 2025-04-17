from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Outline(Base):
    """论文提纲模型"""
    __tablename__ = "outlines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(255), nullable=False)
    abstract = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # 存储关键词列表
    sections = Column(JSON, nullable=False)  # 存储章节结构
    paper_type = Column(String(100), nullable=False)
    academic_field = Column(String(100), nullable=False)
    academic_level = Column(String(50), nullable=False)
    length = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="outlines")
    topic = relationship("Topic", back_populates="outlines")
    papers = relationship("Paper", back_populates="outline", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Outline(id={self.id}, title='{self.title}', topic_id={self.topic_id})>"

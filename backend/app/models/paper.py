from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Paper(Base):
    """论文模型"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outline_id = Column(Integer, ForeignKey("outlines.id"), nullable=False)
    title = Column(String(255), nullable=False)
    abstract = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # 存储关键词列表
    content = Column(Text, nullable=False)  # 存储论文内容
    status = Column(String(50), default="draft")  # draft, completed, reviewing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="papers")
    outline = relationship("Outline", back_populates="papers")
    citations = relationship("Citation", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title}', outline_id={self.outline_id})>"

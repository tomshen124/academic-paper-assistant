from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Topic(Base):
    """论文主题模型"""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    research_question = Column(Text, nullable=True)
    academic_field = Column(String(100), nullable=False)
    academic_level = Column(String(50), nullable=False)
    feasibility = Column(String(50), nullable=True)
    innovation = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    resources = Column(Text, nullable=True)
    expected_outcomes = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # 存储关键词列表
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="topics")
    outlines = relationship("Outline", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Topic(id={self.id}, title='{self.title}', user_id={self.user_id})>"

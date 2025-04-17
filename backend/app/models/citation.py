from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Citation(Base):
    """引用模型"""
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    title = Column(String(255), nullable=False)
    authors = Column(JSON, nullable=True)  # 存储作者列表
    year = Column(String(10), nullable=True)
    source = Column(String(100), nullable=True)  # 来源，如期刊名、会议名
    url = Column(String(255), nullable=True)
    citation_text = Column(Text, nullable=False)  # 格式化的引用文本
    citation_style = Column(String(50), default="apa")  # 引用样式，如apa, mla, chicago
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    paper = relationship("Paper", back_populates="citations")

    def __repr__(self):
        return f"<Citation(id={self.id}, title='{self.title}', paper_id={self.paper_id})>"

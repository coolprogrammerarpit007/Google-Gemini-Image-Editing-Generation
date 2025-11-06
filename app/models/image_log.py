from sqlalchemy import Column, Integer, String, DateTime, func
from core.database import Base

class ImageLog(Base):
    __tablename__ = "image_logs"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String(500), nullable=True)
    image_path = Column(String(255), nullable=True)
    type = Column(String(50), nullable=False)  # "generate" or "edit"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

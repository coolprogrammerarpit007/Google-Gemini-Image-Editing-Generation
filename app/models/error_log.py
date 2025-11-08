from sqlalchemy import Column, Integer, String, Text, DateTime, func
from core.database import Base

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    error_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    prompt = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base

class StopList(Base):
    __tablename__ = "stop_list"

    id = Column(Integer, primary_key=True)
    product_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric, default=0)
    is_active = Column(Boolean, default=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

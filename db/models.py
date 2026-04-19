from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    alert_type = Column(String, nullable=False)
    condition_value = Column(String, nullable=False)
    last_triggered = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class AlertThreshold(Base):
    __tablename__ = 'alert_thresholds'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    metric = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

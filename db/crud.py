from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update, delete
from db.models import Base, User, Alert, AlertThreshold
from config import DB_PATH
from typing import List, Optional
from datetime import datetime, timedelta

engine = create_async_engine(DB_PATH, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def register_user(user_id: int, username: str = None):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(user_id=user_id, username=username)
            session.add(user)
            await session.commit()
        return user

async def add_periodic_alert(user_id: int, interval_minutes: int):
    async with AsyncSessionLocal() as session:
        alert = Alert(
            user_id=user_id,
            alert_type='periodic',
            condition_value=str(interval_minutes)
        )
        session.add(alert)
        await session.commit()
        return alert

async def add_threshold_alert(user_id: int, metric: str, operator: str, value: float):
    async with AsyncSessionLocal() as session:
        alert = AlertThreshold(
            user_id=user_id,
            metric=metric,
            operator=operator,
            value=value
        )
        session.add(alert)
        await session.commit()
        return alert

async def get_user_alerts(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Alert).where(Alert.user_id == user_id, Alert.is_active == True)
        )
        return result.scalars().all()

async def get_active_periodic_alerts():
    async with AsyncSessionLocal() as session:
        now = datetime.utcnow()
        result = await session.execute(
            select(Alert).where(
                Alert.alert_type == 'periodic',
                Alert.is_active == True,
                (Alert.last_triggered == None) | 
                (Alert.last_triggered < now - timedelta(minutes=int(Alert.condition_value)))
            )
        )
        return result.scalars().all()

async def update_alert_trigger_time(alert_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(Alert)
            .where(Alert.id == alert_id)
            .values(last_triggered=datetime.utcnow())
        )
        await session.commit()

async def get_all_threshold_alerts():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AlertThreshold).where(AlertThreshold.is_active == True)
        )
        return result.scalars().all()

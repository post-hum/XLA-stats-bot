from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update, delete, text
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
    """Register user if not exists, otherwise update username"""
    async with AsyncSessionLocal() as session:
        # Проверяем существование пользователя
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем username если изменился
            if username and user.username != username:
                user.username = username
                await session.commit()
            return user
        else:
            # Создаем нового пользователя
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
    """Get all active periodic alerts that are ready to trigger"""
    async with AsyncSessionLocal() as session:
        now = datetime.utcnow()
        # Получаем все активные периодические алерты
        result = await session.execute(
            select(Alert).where(
                Alert.alert_type == 'periodic',
                Alert.is_active == True
            )
        )
        alerts = result.scalars().all()
        
        # Фильтруем в Python по времени
        ready_alerts = []
        for alert in alerts:
            interval = int(alert.condition_value)
            if alert.last_triggered is None:
                ready_alerts.append(alert)
            elif alert.last_triggered < now - timedelta(minutes=interval):
                ready_alerts.append(alert)
        
        return ready_alerts

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

async def delete_user_alerts(user_id: int, alert_id: int = None):
    """Delete all alerts for user or specific alert"""
    async with AsyncSessionLocal() as session:
        if alert_id:
            await session.execute(
                delete(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
            )
        else:
            await session.execute(
                delete(Alert).where(Alert.user_id == user_id)
            )
        await session.commit()

# Добавь эту функцию в конец файла db/crud.py

async def get_alert_by_id(alert_id: int, user_id: int):
    """Get alert by ID and verify it belongs to user"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
        )
        return result.scalar_one_or_none()

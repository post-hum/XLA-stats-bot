import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from fetcher import fetch_pool_stats
from db.crud import get_active_periodic_alerts, update_alert_trigger_time, get_all_threshold_alerts
from keyboards import get_main_menu

logger = logging.getLogger(__name__)

# Используем UTC для избежания проблем с таймзонами
scheduler = AsyncIOScheduler(timezone="UTC")

# Словарь для отслеживания последних срабатываний threshold алертов
_last_threshold_trigger = {}

async def check_alerts(bot: Bot):
    try:
        data = await fetch_pool_stats()
        if not data:
            return
        
        # Periodic alerts
        periodic_alerts = await get_active_periodic_alerts()
        for alert in periodic_alerts:
            try:
                stats_text = (
                    f"⏰ *Periodic Update*\n\n"
                    f"🌐 Difficulty: `{data.network_difficulty / 1e9:.2f} G`\n"
                    f"🏊 Pool HR: `{data.pool_hashrate_kh:.2f} KH/s`\n"
                    f"👥 Miners: `{data.active_miners}`\n"
                    f"🧱 Last Block: `{data.last_block_height}`\n"
                    f"📊 Effort: `{data.round_effort:.1f}%`"
                )
                await bot.send_message(
                    alert.user_id,
                    stats_text,
                    parse_mode="Markdown",
                    reply_markup=get_main_menu()
                )
                await update_alert_trigger_time(alert.id)
            except Exception as e:
                logger.error(f"Failed to send periodic alert to {alert.user_id}: {e}")
        
        # Threshold alerts - с защитой от спама
        threshold_alerts = await get_all_threshold_alerts()
        for alert in threshold_alerts:
            try:
                # Получаем текущее значение метрики
                if alert.metric == 'hashrate':
                    current_value = data.pool_hashrate_kh
                elif alert.metric == 'difficulty':
                    current_value = data.network_difficulty / 1e9
                elif alert.metric == 'miners':
                    current_value = data.active_miners
                else:
                    continue
                
                # Проверяем условие
                triggered = False
                if alert.operator == 'lt' and current_value < alert.value:
                    triggered = True
                elif alert.operator == 'gt' and current_value > alert.value:
                    triggered = True
                
                # Проверяем, не отправляли ли уже алерт за последние 5 минут
                import time
                now = time.time()
                key = f"{alert.id}_{alert.metric}"
                last_trigger = _last_threshold_trigger.get(key, 0)
                
                if triggered and (now - last_trigger) > 300:  # 5 минут коолдаун
                    _last_threshold_trigger[key] = now
                    await bot.send_message(
                        alert.user_id,
                        f"🚨 *Threshold Alert!*\n\n"
                        f"📊 `{alert.metric}`: `{current_value:.2f}`\n"
                        f"Condition: `{alert.operator} {alert.value}`",
                        parse_mode="Markdown"
                    )
                    logger.info(f"Threshold alert sent to {alert.user_id}: {alert.metric} {alert.operator} {alert.value}")
                    
            except Exception as e:
                logger.error(f"Failed to process threshold alert {alert.id}: {e}")
    except Exception as e:
        logger.error(f"Global error in check_alerts: {e}")

def setup_scheduler(bot: Bot):
    scheduler.add_job(
        check_alerts,
        trigger=IntervalTrigger(minutes=1, timezone="UTC"),
        args=[bot],
        id='check_alerts',
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

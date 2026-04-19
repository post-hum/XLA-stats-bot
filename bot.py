import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientTimeout
from config import BOT_TOKEN, USE_PROXY, PROXY_URL
from handlers import routers
from db.crud import init_db
from scheduler import setup_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing database...")
    await init_db()
    
    # Настройка прокси правильным способом
    if USE_PROXY and PROXY_URL:
        from aiohttp_socks import ProxyConnector
        connector = ProxyConnector.from_url(PROXY_URL)
        timeout = ClientTimeout(total=60, connect=30)
        session = AiohttpSession()
        # Правильный способ в aiogram 3.x
        session._connector = connector
        session._timeout = timeout
        logger.info(f"Using proxy: {PROXY_URL}")
    else:
        session = AiohttpSession()
    
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())
    
    for router in routers:
        dp.include_router(router)
    
    try:
        logger.info("Testing Telegram connection...")
        # Увеличиваем таймаут для медленного Tor
        me = await bot.get_me(request_timeout=30)
        logger.info(f"Bot @{me.username} connected successfully!")
        
        setup_scheduler(bot)
        logger.info("Bot is running!")
        await dp.start_polling(bot, request_timeout=30)
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        raise
    finally:
        stop_scheduler()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

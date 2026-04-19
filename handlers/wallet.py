from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_main_menu
import aiohttp
import logging
import json

logger = logging.getLogger(__name__)

router = Router()

class WalletStates(StatesGroup):
    waiting_for_address = State()

@router.message(Command("wallet"))
async def cmd_wallet(message: Message, state: FSMContext):
    text = (
        "💰 *XLA Wallet Stats*\n\n"
        "Send me your XLA wallet address to see:\n"
        "• Balance\n"
        "• Total hashes\n"
        "• Last share time\n"
        "• Worker stats\n\n"
        "Example: `SvkFweFR7GeAGus6pt7jpg5ZYEvZgqjaUEnYnkqqBRQg57LUuKCMY849e79oVsmDbH9jYH5BVyLJMSweBAQ6YdPB1ekUGaPwc`\n\n"
        "Type /cancel to abort"
    )
    await message.answer(text, parse_mode="Markdown")
    await state.set_state(WalletStates.waiting_for_address)

@router.message(WalletStates.waiting_for_address)
async def process_wallet_address(message: Message, state: FSMContext):
    address = message.text.strip()
    
    # Базовая валидация XLA адреса
    if not (address.startswith('S') and len(address) > 90):
        await message.answer("❌ Invalid XLA address format. Please send a valid address.")
        return
    
    status_msg = await message.answer("🔄 *Fetching wallet statistics...*", parse_mode="Markdown")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://pool.scalaproject.io/api/stats_address?address={address}"
            logger.info(f"Fetching: {url}")
            
            # Увеличиваем таймаут до 120 секунд
            async with session.get(url, timeout=120) as resp:
                logger.info(f"Response status: {resp.status}")
                
                if resp.status != 200:
                    await status_msg.edit_text(f"❌ API returned status {resp.status}")
                    await state.clear()
                    return
                
                data = await resp.json()
                logger.info(f"Response data keys: {list(data.keys()) if data else 'None'}")
                
                if not data:
                    await status_msg.edit_text("❌ Empty response from API")
                    await state.clear()
                    return
                
                stats = data.get('stats', {})
                workers_data = data.get('workers', [])
                
                # Получаем значения из stats
                balance = int(stats.get('balance', 0)) / 100
                paid = int(stats.get('paid', 0)) / 100
                hashes = int(stats.get('hashes', 0))
                last_share = int(stats.get('lastShare', 0))
                hashrate = float(stats.get('hashrate', 0))
                hashrate_1h = float(stats.get('hashrate_1h', 0))
                hashrate_6h = float(stats.get('hashrate_6h', 0))
                hashrate_24h = float(stats.get('hashrate_24h', 0))
                min_payout = int(stats.get('minPayoutLevel', 1000000)) / 100
                donations = int(stats.get('donations', 0)) / 100
                
                from datetime import datetime
                last_share_str = datetime.fromtimestamp(last_share).strftime("%Y-%m-%d %H:%M:%S") if last_share else "N/A"
                
                text = (
                    "💰 *XLA Wallet Statistics*\n\n"
                    f"📫 *Address:* `{address[:20]}...{address[-10:]}`\n\n"
                    f"💎 *Balance:* `{balance:.2f} XLA`\n"
                    f"💸 *Total Paid:* `{paid:.2f} XLA`\n"
                    f"⚡ *Total Hashes:* `{hashes:,}`\n"
                    f"🕐 *Last Share:* `{last_share_str}`\n"
                    f"🎁 *Donations:* `{donations:.2f} XLA`\n\n"
                    f"📊 *Hashrate:*\n"
                    f"• Current: `{hashrate:.2f} H/s`\n"
                    f"• 1h avg: `{hashrate_1h:.2f} H/s`\n"
                    f"• 6h avg: `{hashrate_6h:.2f} H/s`\n"
                    f"• 24h avg: `{hashrate_24h:.2f} H/s`\n"
                )
                
                # Добавляем информацию о воркерах
                if workers_data and isinstance(workers_data, list):
                    text += f"\n🖥️ *Workers:*\n"
                    for worker in workers_data:
                        if isinstance(worker, dict):
                            worker_name = worker.get('name', 'unknown')
                            worker_hashrate = float(worker.get('hashrate', 0))
                            worker_hashes = int(worker.get('hashes', 0))
                            worker_last_share = int(worker.get('lastShare', 0))
                            worker_last_share_str = datetime.fromtimestamp(worker_last_share).strftime("%H:%M:%S") if worker_last_share else "N/A"
                            text += f"• `{worker_name}`: {worker_hashrate:.0f} H/s | {worker_hashes:,} hashes\n"
                
                text += f"\n💰 *Min payout:* `{min_payout:.2f} XLA`"
                
                # Правильная обработка последней выплаты
                payments = data.get('payments', [])
                if payments and len(payments) > 0:
                    text += f"\n\n📜 *Last payment:*"
                    # Проверяем последний элемент в payments
                    last_payment = payments[-1]
                    if isinstance(last_payment, str):
                        # Формат: "txid:amount:confirmations:timestamp"
                        parts = last_payment.split(':')
                        if len(parts) >= 2:
                            try:
                                amount = int(parts[1]) / 100
                                text += f"\n• Amount: `{amount:.2f} XLA`"
                                if len(parts) >= 4:
                                    timestamp = int(parts[3])
                                    date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                                    text += f"\n• Date: `{date_str}`"
                            except:
                                pass
                    elif isinstance(last_payment, dict):
                        amount = int(last_payment.get('amount', 0)) / 100
                        text += f"\n• Amount: `{amount:.2f} XLA`"
                
                await status_msg.edit_text(text, parse_mode="Markdown", reply_markup=get_main_menu())
                await state.clear()
                
    except aiohttp.ClientError as e:
        logger.error(f"Network error: {e}")
        await status_msg.edit_text("❌ Network error. Please try again later.")
        await state.clear()
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        await status_msg.edit_text("❌ Invalid response from API. Please try again later.")
        await state.clear()
    except Exception as e:
        logger.error(f"Wallet stats error: {type(e).__name__}: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)[:100]}")
        await state.clear()

@router.message(Command("cancel"))
async def cancel_wallet(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == WalletStates.waiting_for_address:
        await state.clear()
        await message.answer("✅ Cancelled.", reply_markup=get_main_menu())
    else:
        await message.answer("❌ Nothing to cancel.", reply_markup=get_main_menu())

# Обработчик для кнопки Wallet
@router.callback_query(F.data == "wallet")
async def callback_wallet(callback: CallbackQuery, state: FSMContext):
    from handlers.wallet import cmd_wallet
    await cmd_wallet(callback.message, state)
    await callback.answer()

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from fetcher import fetch_pool_stats
from keyboards import get_main_menu

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    await send_stats_message(message)

@router.callback_query(F.data == "stats")
@router.callback_query(F.data == "refresh")
async def callback_stats(callback: CallbackQuery):
    await send_stats_message(callback.message, edit=True)
    await callback.answer("Updated!")

async def send_stats_message(target: Message, edit: bool = False):
    text = "⛏️ *Fetching Scala Pool data...*"
    if edit:
        msg = await target.edit_text(text, parse_mode="Markdown")
    else:
        msg = await target.answer(text, parse_mode="Markdown")
    
    data = await fetch_pool_stats()
    if not data:
        error_text = "❌ Failed to fetch pool stats. Try again later."
        if edit:
            await msg.edit_text(error_text, reply_markup=get_main_menu())
        else:
            await msg.edit_text(error_text, reply_markup=get_main_menu())
        return
    
    effort_emoji = "🟢" if data.round_effort < 100 else "🟡" if data.round_effort < 200 else "🔴"
    
    stats_text = (
        f"🪙 *Scala (XLA) Pool Statistics*\n\n"
        f"🌐 *Network*\n"
        f"├ Height: `{data.network_height}`\n"
        f"├ Difficulty: `{data.network_difficulty / 1e9:.2f} G`\n"
        f"└ Hashrate: `{data.network_hashrate_mh:.2f} MH/s`\n\n"
        f"🏊 *Pool*\n"
        f"├ Hashrate: `{data.pool_hashrate_kh:.2f} KH/s`\n"
        f"├ Miners: `{data.active_miners}`\n"
        f"├ Workers: `{data.active_workers}`\n"
        f"└ 24h Blocks: `{data.blocks_found_24h}`\n\n"
        f"🧱 *Last Block*\n"
        f"├ Height: `{data.last_block_height}`\n"
        f"├ Reward: `{data.last_block_reward:.2f} XLA`\n"
        f"├ Time: `{data.last_block_time}`\n"
        f"└ {effort_emoji} Effort: `{data.round_effort:.1f}%`\n\n"
        f"🕐 *Updated:* {data.last_block_time}"
    )
    
    if edit:
        await msg.edit_text(stats_text, parse_mode="Markdown", reply_markup=get_main_menu())
    else:
        await msg.edit_text(stats_text, parse_mode="Markdown", reply_markup=get_main_menu())

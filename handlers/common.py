from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu, get_alert_type_menu, get_about_menu
from db.crud import register_user
from fetcher import fetch_pool_stats

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await register_user(message.from_user.id, message.from_user.username)
    text = (
        "🪙 *Scala (XLA) Pool Bot*\n\n"
        "I monitor pool.scalaproject.io and provide:\n"
        "• Network difficulty & hashrate\n"
        "• Pool stats & block info\n"
        "• Custom alerts (periodic/threshold)\n"
        "• Wallet statistics\n\n"
        "Use menu below or commands:\n"
        "/stats - Current pool statistics\n"
        "/wallet - Check wallet stats\n"
        "/menu - Show main menu\n"
        "/help - Help information"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu())

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("📋 *Main Menu*", parse_mode="Markdown", reply_markup=get_main_menu())

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "ℹ️ *XLA Stats Bot - Help*\n\n"
        "*Commands:*\n"
        "• /start - Launch the bot\n"
        "• /stats - Get current pool statistics\n"
        "• /wallet - Check wallet balance and stats\n"
        "• /menu - Show main menu\n"
        "• /help - Show this message\n\n"
        "*Alert Types:*\n"
        "• ⏰ *Periodic* - Receive stats every N minutes\n"
        "• 📊 *Hashrate* - Alert when pool hashrate crosses threshold\n"
        "• 🎯 *Difficulty* - Alert when network difficulty changes\n"
        "• 👥 *Miners* - Alert when miner count changes\n\n"
        "*Links:*\n"
        "• GitHub: [Scala-Network](https://github.com/scala-network)\n"
        "• GitHub: [XLA-stats-bot](https://github.com/post-hum/XLA-stats-bot)\n"
        "• Example: [@xlastatsbot](https://t.me/xlastatsbot)\n"
        "• Discord: [XLA Community](https://discord.gg/W9W6CxSTt8)\n"
        "• Matrix: [#scala:unredacted.org](https://matrix.to/#/#scala:unredacted.org)\n"
        "• Explorer: [Scala Explorer](https://explorer.scalaproject.io)\n"
        "• Telegram: [Scala Chat](https://t.me/scalaofficial)\n"
        "• Pool: [pool.scalaproject.io](https://pool.scalaproject.io)\n\n"
        "*Donations (XLA):*\n"
        "`SvkFweFR7GeAGus6pt7jpg5ZYEvZgqjaUEnYnkqqBRQg57LUuKCMY849e79oVsmDbH9jYH5BVyLJMSweBAQ6YdPB1ekUGaPwc`"
    )
    await message.answer(help_text, parse_mode="Markdown", disable_web_page_preview=True)

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    await message.answer("🔄 *Fetching latest statistics...*", parse_mode="Markdown")
    
    data = await fetch_pool_stats()
    if not data:
        await message.answer("❌ *Failed to fetch statistics.* Please try again later.", parse_mode="Markdown")
        return
    
    stats_text = (
        "📊 *XLA Pool Statistics*\n\n"
        f"🌐 *Network:*\n"
        f"• Height: `{data.network_height:,}`\n"
        f"• Difficulty: `{data.network_difficulty / 1e9:.2f} G`\n"
        f"• Hashrate: `{data.network_hashrate_mh:.2f} MH/s`\n\n"
        f"🏊 *Pool:*\n"
        f"• Hashrate: `{data.pool_hashrate_kh:.2f} KH/s`\n"
        f"• Miners: `{data.active_miners}`\n"
        f"• Workers: `{data.active_workers}`\n\n"
        f"🧱 *Last Block:*\n"
        f"• Height: `{data.last_block_height}`\n"
        f"• Reward: `{data.last_block_reward:.2f} XLA`\n"
        f"• Time: `{data.last_block_time}`\n\n"
        f"📈 *Round Effort:* `{data.round_effort:.1f}%`\n"
        f"⏰ *24h Blocks:* `{data.blocks_found_24h}`"
    )
    
    await message.answer(stats_text, parse_mode="Markdown", reply_markup=get_main_menu())

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "📋 *Main Menu*", 
            parse_mode="Markdown", 
            reply_markup=get_main_menu()
        )
    except Exception as e:
        if "message is not modified" in str(e):
            await callback.answer("Already on main menu")
        else:
            await callback.answer()
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text(
            "📋 *Main Menu*", 
            parse_mode="Markdown", 
            reply_markup=get_main_menu()
        )
    except Exception as e:
        if "message is not modified" in str(e):
            await callback.answer("Already on main menu")
        else:
            await callback.answer()
    await callback.answer()

@router.callback_query(F.data == "stats")
async def callback_stats(callback: CallbackQuery):
    await callback.message.answer("🔄 *Fetching latest statistics...*", parse_mode="Markdown")
    
    data = await fetch_pool_stats()
    if not data:
        await callback.message.answer("❌ *Failed to fetch statistics.* Please try again later.", parse_mode="Markdown")
        await callback.answer()
        return
    
    stats_text = (
        "📊 *XLA Pool Statistics*\n\n"
        f"🌐 *Network:*\n"
        f"• Height: `{data.network_height:,}`\n"
        f"• Difficulty: `{data.network_difficulty / 1e9:.2f} G`\n"
        f"• Hashrate: `{data.network_hashrate_mh:.2f} MH/s`\n\n"
        f"🏊 *Pool:*\n"
        f"• Hashrate: `{data.pool_hashrate_kh:.2f} KH/s`\n"
        f"• Miners: `{data.active_miners}`\n"
        f"• Workers: `{data.active_workers}`\n\n"
        f"🧱 *Last Block:*\n"
        f"• Height: `{data.last_block_height}`\n"
        f"• Reward: `{data.last_block_reward:.2f} XLA`\n"
        f"• Time: `{data.last_block_time}`\n\n"
        f"📈 *Round Effort:* `{data.round_effort:.1f}%`\n"
        f"⏰ *24h Blocks:* `{data.blocks_found_24h}`"
    )
    
    await callback.message.answer(stats_text, parse_mode="Markdown", reply_markup=get_main_menu())
    await callback.answer()

@router.callback_query(F.data == "refresh")
async def callback_refresh(callback: CallbackQuery):
    await callback.message.answer("🔄 *Refreshing statistics...*", parse_mode="Markdown")
    
    data = await fetch_pool_stats()
    if not data:
        await callback.message.answer("❌ *Failed to fetch statistics.* Please try again later.", parse_mode="Markdown")
        await callback.answer()
        return
    
    stats_text = (
        "📊 *XLA Pool Statistics (Updated)*\n\n"
        f"🌐 *Network:*\n"
        f"• Height: `{data.network_height:,}`\n"
        f"• Difficulty: `{data.network_difficulty / 1e9:.2f} G`\n"
        f"• Hashrate: `{data.network_hashrate_mh:.2f} MH/s`\n\n"
        f"🏊 *Pool:*\n"
        f"• Hashrate: `{data.pool_hashrate_kh:.2f} KH/s`\n"
        f"• Miners: `{data.active_miners}`\n"
        f"• Workers: `{data.active_workers}`\n\n"
        f"🧱 *Last Block:*\n"
        f"• Height: `{data.last_block_height}`\n"
        f"• Reward: `{data.last_block_reward:.2f} XLA`\n"
        f"• Time: `{data.last_block_time}`\n\n"
        f"📈 *Round Effort:* `{data.round_effort:.1f}%`\n"
        f"⏰ *24h Blocks:* `{data.blocks_found_24h}`"
    )
    
    await callback.message.answer(stats_text, parse_mode="Markdown", reply_markup=get_main_menu())
    await callback.answer("🔄 Statistics refreshed!")

@router.callback_query(F.data == "about")
async def cmd_about(callback: CallbackQuery):
    about_text = (
        "🤖 *XLA Stats Bot*\n\n"
        "Real-time monitoring bot for Scala (XLA) mining pool.\n\n"
        "*Features:*\n"
        "• Live pool statistics\n"
        "• Periodic notifications\n"
        "• Threshold alerts\n"
        "• Wallet balance & stats\n\n"
        "*Links:*\n"
        "• [GitHub: Scala-Network](https://github.com/scala-network)\n"
        "• [GitHub: XLA-stats-bot](https://github.com/post-hum/XLA-stats-bot)\n"
        "• [Example Bot](https://t.me/xlastatsbot)\n"
        "• [Discord Community](https://discord.gg/W9W6CxSTt8)\n"
        "• [Matrix Chat](https://matrix.to/#/#scala:unredacted.org)\n"
        "• [Scala Explorer](https://explorer.scalaproject.io)\n"
        "• [Telegram Chat](https://t.me/scalaofficial)\n"
        "• [Mining Pool](https://pool.scalaproject.io)\n\n"
        "*Open Source:*\n"
        "Check the code on GitHub\n\n"
        "*Donations (XLA):*\n"
        "`SvkFweFR7GeAGus6pt7jpg5ZYEvZgqjaUEnYnkqqBRQg57LUuKCMY849e79oVsmDbH9jYH5BVyLJMSweBAQ6YdPB1ekUGaPwc`\n\n"
        "❤️ Thanks for using this bot!"
    )
    await callback.message.edit_text(about_text, parse_mode="Markdown", reply_markup=get_about_menu())
    await callback.answer()

@router.callback_query(F.data == "wallet")
async def callback_wallet(callback: CallbackQuery, state: FSMContext):
    from handlers.wallet import cmd_wallet
    await cmd_wallet(callback.message, state)
    await callback.answer()

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards import get_main_menu, get_alert_type_menu
from db.crud import register_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await register_user(message.from_user.id, message.from_user.username)
    text = (
        "🪙 *Scala (XLA) Pool Bot*\n\n"
        "I monitor pool.scalaproject.io and provide:\n"
        "• Network difficulty & hashrate\n"
        "• Pool stats & block info\n"
        "• Custom alerts (periodic/threshold)\n\n"
        "Use menu below or commands:\n"
        "/stats - Current pool statistics\n"
        "/menu - Show main menu\n"
        "/help - Help information"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu())

@router.message(Command("menu"))
@router.message(Command("help"))
async def cmd_menu(message: Message):
    await message.answer("📋 *Main Menu*", parse_mode="Markdown", reply_markup=get_main_menu())

@router.callback_query(F.data == "back_to_main")
@router.callback_query(F.data == "cancel")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 *Main Menu*", 
        parse_mode="Markdown", 
        reply_markup=get_main_menu()
    )
    await callback.answer()

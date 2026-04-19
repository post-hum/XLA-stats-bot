from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Stats", callback_data="stats"),
        InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Wallet", callback_data="wallet"),
        InlineKeyboardButton(text="⏰ Periodic Alert", callback_data="alert_periodic")
    )
    builder.row(
        InlineKeyboardButton(text="📋 My Alerts", callback_data="my_alerts"),
        InlineKeyboardButton(text="ℹ About", callback_data="about")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
    )
    return builder.as_markup()

def get_alert_type_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏰ Every N minutes", callback_data="set_periodic"),
        InlineKeyboardButton(text="📊 Hashrate", callback_data="set_hashrate")
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Difficulty", callback_data="set_difficulty"),
        InlineKeyboardButton(text="👥 Miners", callback_data="set_miners")
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main"))
    return builder.as_markup()

def get_about_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🐙 GitHub", url="https://github.com/post-hum/XLA-stats-bot"),
        InlineKeyboardButton(text="📱 Example Bot", url="https://t.me/xlastatsbot")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")
    )
    return builder.as_markup()

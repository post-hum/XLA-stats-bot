from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_main_menu, get_alert_type_menu
from db.crud import add_periodic_alert, add_threshold_alert, get_user_alerts, delete_user_alerts, get_alert_by_id
import re

router = Router()

class AlertStates(StatesGroup):
    waiting_for_interval = State()
    waiting_for_threshold = State()

@router.callback_query(F.data == "alert_periodic")
async def alert_periodic_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⏰ *Set Periodic Alert*\n\n"
        "Send me interval in minutes (5-1440)\n"
        "Example: `30` for every 30 minutes\n\n"
        "Type /cancel to abort",
        parse_mode="Markdown"
    )
    await state.set_state(AlertStates.waiting_for_interval)
    await callback.answer()

@router.message(AlertStates.waiting_for_interval)
async def process_interval(message: Message, state: FSMContext):
    try:
        minutes = int(message.text.strip())
        if minutes < 5 or minutes > 1440:
            await message.answer("❌ Interval must be between 5 and 1440 minutes")
            return
        
        await add_periodic_alert(message.from_user.id, minutes)
        await message.answer(
            f"✅ Periodic alert set! You'll receive updates every {minutes} minutes.",
            reply_markup=get_main_menu()
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Please send a valid number (5-1440)")

@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("❌ Nothing to cancel.", reply_markup=get_main_menu())
        return
    
    await state.clear()
    await message.answer(
        "✅ Operation cancelled. Returning to main menu.",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "alert_threshold")
async def alert_threshold_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "📊 *Set Threshold Alert*\n\n"
        "Choose metric to monitor:",
        parse_mode="Markdown",
        reply_markup=get_alert_type_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_"))
async def process_threshold_type(callback: CallbackQuery, state: FSMContext):
    metric = callback.data.replace("set_", "")
    await state.update_data(metric=metric)
    
    metric_names = {
        "hashrate": "Pool Hashrate (KH/s)",
        "difficulty": "Network Difficulty (G)",
        "miners": "Active Miners"
    }
    
    await callback.message.edit_text(
        f"📊 *Set {metric_names.get(metric, metric)} Alert*\n\n"
        f"Send condition in format: `lt:VALUE` or `gt:VALUE`\n"
        f"Examples:\n"
        f"• `lt:1000` - alert when below 1000\n"
        f"• `gt:5000` - alert when above 5000\n\n"
        f"Type /cancel to abort",
        parse_mode="Markdown"
    )
    await state.set_state(AlertStates.waiting_for_threshold)
    await callback.answer()

@router.message(AlertStates.waiting_for_threshold)
async def process_threshold_value(message: Message, state: FSMContext):
    pattern = r'^(lt|gt):(\d+(?:\.\d+)?)$'
    match = re.match(pattern, message.text.strip().lower())
    
    if not match:
        await message.answer("❌ Invalid format. Use `lt:VALUE` or `gt:VALUE`")
        return
    
    operator, value = match.groups()
    data = await state.get_data()
    metric = data.get("metric", "hashrate")
    
    await add_threshold_alert(
        message.from_user.id,
        metric=metric,
        operator=operator,
        value=float(value)
    )
    
    await message.answer(
        f"✅ Threshold alert set!\n"
        f"Will notify when {metric} {operator} {float(value)}",
        reply_markup=get_main_menu()
    )
    await state.clear()

@router.callback_query(F.data == "my_alerts")
async def show_my_alerts(callback: CallbackQuery):
    alerts = await get_user_alerts(callback.from_user.id)
    
    if not alerts:
        text = "📋 *Your Alerts*\n\nNo active alerts set."
    else:
        text = "📋 *Your Active Alerts*\n\n"
        for alert in alerts:
            if alert.alert_type == 'periodic':
                text += f"• ⏰ Periodic: every {alert.condition_value} min (ID: `{alert.id}`)\n"
            else:
                text += f"• 📊 Threshold: {alert.alert_type} (ID: `{alert.id}`)\n"
    
    text += "\nTo delete an alert, send: `/delete_alert <ID>`"
    
    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        if "can't parse entities" in str(e):
            await callback.message.edit_text(
                text.replace("*", "").replace("`", ""),
                reply_markup=get_main_menu()
            )
    await callback.answer()

@router.message(Command("delete_alert"))
async def delete_alert(message: Message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("❌ Usage: `/delete_alert <alert_id>`", parse_mode="Markdown")
            return
        
        alert_id = int(parts[1])
        
        # Проверяем существует ли алерт
        alert = await get_alert_by_id(alert_id, message.from_user.id)
        
        if alert:
            await delete_user_alerts(message.from_user.id, alert_id)
            await message.answer(f"✅ Alert `{alert_id}` deleted!", parse_mode="Markdown", reply_markup=get_main_menu())
        else:
            await message.answer(f"❌ Alert `{alert_id}` not found or doesn't belong to you.", parse_mode="Markdown", reply_markup=get_main_menu())
            
    except ValueError:
        await message.answer("❌ Invalid alert ID. Use: `/delete_alert 123`", parse_mode="Markdown")

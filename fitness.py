# -*- coding: utf-8 -*-
import os
import html
import logging
import requests 
from aiogram.enums import ParseMode 
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from config import BOT_TOKEN, YANDEX_API_KEY, YANDEX_CATALOG_ID
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
class Form(StatesGroup):
    age = State()
    height = State()
    weight = State()
    goal = State()
    equipment = State()
YANDEX_MODEL_URI = f"gpt://{YANDEX_CATALOG_ID}/yandexgpt/latest"
YANDEX_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers = {
    "Authorization": f"Api-Key {YANDEX_API_KEY}",
    "x-folder-id": YANDEX_CATALOG_ID,
    "Content-Type": "application/json; charset=utf-8"
}
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])
def get_goal_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Похудеть"), KeyboardButton(text="Набрать массу")],
            [KeyboardButton(text="Поддержание формы")]
        ],
        resize_keyboard=True
    )
def get_equipment_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Гантели"), KeyboardButton(text="Турник")],
            [KeyboardButton(text="Скакалка")],
            [KeyboardButton(text="Коврик для йоги"), KeyboardButton(text="Ничего")]
        ],
        resize_keyboard=True
    )
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="start_yes"),
         InlineKeyboardButton(text="Нет", callback_data="start_no")]
    ])
    await message.answer(
        "🏋️ Привет! Я ваш персональный фитнес-тренер!\n"
        "Ответьте на несколько вопросов для создания индивидуальной программы.\n\n"
        "Начнем?",
        reply_markup=keyboard
    )
@dp.callback_query(lambda c: c.data == "start_yes")
async def handle_yes(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.age)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🔢 Введите ваш возраст (целое число от 14 до 100):",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()
@dp.callback_query(lambda c: c.data == "start_no")
async def handle_no(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Хорошо, если передумаете - напишите /start")
    await state.clear()
    await callback.answer()
@dp.callback_query(lambda c: c.data == "cancel")
async def handle_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("❌ Операция отменена. Для начала напишите /start")
    await callback.answer()
@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if not 14 <= age <= 100:
            raise ValueError
            
        await state.update_data(age=age)
        await state.set_state(Form.height)
        await message.answer(
            "📏 Введите ваш рост в сантиметрах (например: 180):",
            reply_markup=get_cancel_keyboard()
        )
    except ValueError:
        await message.answer("❌ Некорректный возраст. Введите целое число от 14 до 100:")
@dp.message(Form.height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        if not 100 <= height <= 250:
            raise ValueError
        await state.update_data(height=height)
        await state.set_state(Form.weight)
        await message.answer(
            "⚖️ Введите ваш вес в килограммах (например: 75):",
            reply_markup=get_cancel_keyboard()
        )
    except ValueError:
        await message.answer("❌ Некорректный рост. Введите целое число от 100 до 250 см:")
@dp.message(Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        if not 30 <= weight <= 300:
            raise ValueError
        await state.update_data(weight=weight)
        await state.set_state(Form.goal)
        await message.answer(
            "✅ Данные сохранены! Выберите вашу цель:",
            reply_markup=get_goal_keyboard()
        )
    except ValueError:
        await message.answer("❌ Некорректный вес. Введите целое число от 30 до 300 кг:")
@dp.message(Form.goal)
async def process_goal(message: types.Message, state: FSMContext):
    goal = message.text.lower()
    valid_goals = ["похудеть", "набрать массу", "поддержание формы"]
    if goal not in valid_goals:
        await message.answer("⚠️ Пожалуйста, выберите цель из предложенных кнопок")
        return
    await state.update_data(goal=goal)
    await state.set_state(Form.equipment)
    await message.answer("🏋️ Выберите доступное оборудование:", reply_markup=get_equipment_keyboard())
@dp.message(Form.equipment)
async def process_equipment(message: types.Message, state: FSMContext):
    try:
        equipment = message.text.lower()
        valid_equipment = ["гантели", "турник", "ничего", "скакалка", "коврик для йоги"]
        if equipment not in valid_equipment:
            raise ValueError
        user_data = await state.get_data()
        prompt = (
            "Создай персональную программу тренировок и питания:\n"
            f"• Возраст: {user_data['age']} лет\n"
            f"• Рост: {user_data['height']} см\n"
            f"• Вес: {user_data['weight']} кг\n"
            f"• Цель: {user_data['goal']}\n"
            f"• Оборудование: {equipment}\n\n"
            "Требования:\n"
            "1. Детальное меню на день с калорийностью\n"
            "2. 3 разные тренировки с описанием упражнений\n"
            "3. Используй дружелюбный стиль общения и используй мотивирующие слова"
        )
        data = {
            "modelUri": YANDEX_MODEL_URI,
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 2000
            },
            "messages": [{
                "role": "user",
                "text": prompt
            }]
        }
        response = requests.post(
            YANDEX_URL,
            headers=headers,
            json=data,
            timeout=35
        )
        response.encoding = 'utf-8'
        response.raise_for_status()
        result = response.json()
        plan = result['result']['alternatives'][0]['message']['text']
        logging.info(f"YandexGPT response: {plan}")
        escaped_plan = html.escape(plan)
        await message.answer(
            f"📋 Ваш персональный план:\n{escaped_plan}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await message.answer("❌ Произошла ошибка при генерации плана. Попробуйте позже.")
    await state.clear()
@dp.message()
async def handle_other_messages(message: types.Message):
    await message.answer("ℹ️ Для начала работы используйте команду /start")
if __name__ == "__main__":
    dp.run_polling(bot)
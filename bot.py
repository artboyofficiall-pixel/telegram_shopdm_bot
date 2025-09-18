import os
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# 🔹 Логирование
logging.basicConfig(level=logging.INFO)

# 🔹 Токены
API_TOKEN = os.getenv("BOT_TOKEN")
NP_API_KEY = os.getenv("NP_API_KEY")

if not API_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь его в Render → Environment Variables")
if not NP_API_KEY:
    raise ValueError("❌ NP_API_KEY не найден! Добавь его в Render → Environment Variables")

# 🔹 Инициализация
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 🔹 Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📦 Отследить заказ")],
        [KeyboardButton("📞 Контакты"), KeyboardButton("💬 Связь с менеджером")],
        [KeyboardButton("❓ FAQ")]
    ],
    resize_keyboard=True
)

# 🔹 Старт
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот магазина **ЗАМІСТЬ СЛІВ**.\n\n"
        "Выберите действие из меню ниже ⬇️",
        reply_markup=main_menu
    )

# 🔹 Контакты
@dp.message_handler(lambda msg: msg.text == "📞 Контакты")
async def contacts(message: types.Message):
    await message.answer("📍 Наши контакты:\nТелефон: +380XXXXXXXXX\nInstagram: @zamistsliv")

# 🔹 Связь с менеджером
@dp.message_handler(lambda msg: msg.text == "💬 Связь с менеджером")
async def manager(message: types.Message):
    await message.answer("👩‍💼 Напишите нашему менеджеру: @username_manager")

# 🔹 FAQ
@dp.message_handler(lambda msg: msg.text == "❓ FAQ")
async def faq(message: types.Message):
    await message.answer(
        "❓ Часто задаваемые вопросы:\n\n"
        "— Как оформить заказ?\nЧерез сайт или менеджера.\n\n"
        "— Как отследить заказ?\nВыберите «📦 Отследить заказ» и введите номер ТТН.\n\n"
        "— Какие есть способы доставки?\nНовая Почта и Укрпочта."
    )

# 🔹 Отслеживание заказа
@dp.message_handler(lambda msg: msg.text == "📦 Отследить заказ")
async def track_order(message: types.Message):
    await message.answer("✍️ Введите номер ТТН для отслеживания:")

@dp.message_handler(lambda msg: msg.text.isdigit() and len(msg.text) >= 10)
async def check_ttn(message: types.Message):
    ttn = message.text.strip()

    # 🔹 Запрос к API Новой Почты
    url = "https://api.novaposhta.ua/v2.0/json/"
    payload = {
        "apiKey": NP_API_KEY,
        "modelName": "TrackingDocument",
        "calledMethod": "getStatusDocuments",
        "methodProperties": {
            "Documents": [{"DocumentNumber": ttn}]
        }
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()

        if data.get("success") and data["data"]:
            status = data["data"][0].get("Status", "Статус не найден")
            await message.answer(f"🔎 ТТН: {ttn}\n📦 Статус: {status}")
        else:
            await message.answer("⚠️ Не удалось найти информацию по этому ТТН.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при запросе к API: {e}")

# 🔹 Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

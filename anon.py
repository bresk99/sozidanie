import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

# ==== Настройки ====
BOT_TOKEN = "7945070793:AAESMab7P7IBQVB-AgiJQQtFVm9D1VQuITQ"
ADMIN_CHAT_ID = 1558568390
CHAT_LINK = "https://t.me/+9TrpV2C2UIY0MWEy"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ==== Состояния анкеты ====
class Form(StatesGroup):
    full_name = State()
    birth_date = State()
    location = State()
    diagnosis = State()
    treatment_status = State()
    phone = State()
    referral = State()

# ==== Кнопка "Продолжить" ====
start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продолжить", callback_data="start_form")]
    ]
)

# ==== Хранилище пользователей для рассылки ====
user_ids = set()

# ==== Команда /start ====
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! Вас приветствует команда АНО «Созидание». 🙏\n\n"
        "В нашем чате вы получите:\n"
        "🧠 психологическую\n⚖ юридическую\n🤝 моральную\n✝ духовную помощь.\n\n"
        "Для регистрации, пожалуйста, заполните анкету-опрос.\n"
        "Все данные являются конфиденциальными и не будут переданы третьим лицам.\n\n"
        "Продолжая, вы даёте согласие на обработку ваших персональных данных.",
        reply_markup=start_keyboard
    )

# ==== Кнопка "Продолжить" ====
@dp.callback_query(F.data == "start_form")
async def start_form(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.full_name)
    await callback.message.answer("👉 Введите ФИО:")
    await callback.answer()

# ==== Анкета по шагам ====
@dp.message(Form.full_name)
async def form_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Form.birth_date)
    await message.answer("📅 Дата рождения:")

@dp.message(Form.birth_date)
async def form_birth_date(message: Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await state.set_state(Form.location)
    await message.answer("🏙 Место проживания:")

@dp.message(Form.location)
async def form_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(Form.diagnosis)
    await message.answer("💊 Заболевание / диагноз:")

@dp.message(Form.diagnosis)
async def form_diagnosis(message: Message, state: FSMContext):
    await state.update_data(diagnosis=message.text)
    await state.set_state(Form.treatment_status)
    await message.answer("🩺 Вы в ремиссии или на лечении?")

@dp.message(Form.treatment_status)
async def form_treatment_status(message: Message, state: FSMContext):
    await state.update_data(treatment_status=message.text)
    await state.set_state(Form.phone)
    await message.answer("📞 Номер контактного телефона:")

@dp.message(Form.phone)
async def form_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Form.referral)
    await message.answer("📢 Как вы о нас узнали?")

@dp.message(Form.referral)
async def form_referral(message: Message, state: FSMContext):
    await state.update_data(referral=message.text)
    data = await state.get_data()

    form_text = (
        "📝 Новая анкета от пользователя:\n\n"
        f"👤 ФИО: {data['full_name']}\n"
        f"📅 Дата рождения: {data['birth_date']}\n"
        f"🏙 Место проживания: {data['location']}\n"
        f"💊 Диагноз: {data['diagnosis']}\n"
        f"🩺 Статус: {data['treatment_status']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📢 Как узнал: {data['referral']}\n"
        f"\n🔗 Telegram: @{message.from_user.username or 'не указан'}"
    )
    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=form_text)
        print("Анкета успешно отправлена админу.")
    except Exception as e:
        print(f"Ошибка при отправке анкеты админу: {e}")

    # Кнопка входа в чат
    chat_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡ Перейти в чат", url=CHAT_LINK)]
        ]
    )

    await message.answer(
        "✅ Спасибо! Ваша анкета отправлена администратору.\n"
        "Теперь вы можете перейти в наш закрытый чат 👇",
        reply_markup=chat_button
    )

    # Сохраняем ID пользователя
    user_ids.add(message.from_user.id)

    # Сообщение о рассылке
    await message.answer(
        "🧾 Электронный помощник будет напоминать вам о наших мероприятиях.\n"
        "Отказаться от рассылки можно, написав команду /stop."
    )

    await state.clear()

# ==== Рассылка от администратора ====
@dp.message(Command("broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_CHAT_ID:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return

    await message.answer("✉️ Введите текст для рассылки всем пользователям:")

    @dp.message()
    async def get_broadcast_text(msg: Message):
        count = 0
        for user_id in user_ids:
            try:
                await bot.send_message(chat_id=user_id, text=msg.text)
                count += 1
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
        await msg.answer(f"✅ Рассылка завершена. Сообщение получено {count} пользователям.")
        dp.message.unregister(get_broadcast_text)

# ==== Команда /stop для отказа от рассылки ====
@dp.message(Command("stop"))
async def stop_notifications(message: Message):
    user_ids.discard(message.from_user.id)
    await message.answer("❌ Вы отписались от рассылки. Возвращайтесь, когда будете готовы.")

# ==== Запуск бота ====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from handlers import router

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Пример: https://your-bot.onrender.com

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

async def on_startup(app: web.Application):
    await bot.set_webhook(url=WEBHOOK_URL + WEBHOOK_PATH)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()

async def handle_request(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response(text="ok")

def create_app():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_request)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

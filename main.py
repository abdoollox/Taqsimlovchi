import asyncio
import logging
import sys
import random
import os  # Portni olish uchun kerak
from aiohttp import web # Render portini band qilish uchun
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = '8400967993:AAHl9cpqZdDZ7sfe_2Tsmba0PQ2MKMYNS3w'

# Botni sozlash
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RASM ID LARINI SHU YERGA YOZING ---
HAT_IMG_ID = "AgACAgIAAxkBA..." # Shlyapa rasmi ID si
GRYFFINDOR_ID = "AgACAgIAAxkBA..." # Gryffindor gerbi ID si
SLYTHERIN_ID = "AgACAgIAAxkBA..."  # Slytherin gerbi ID si
RAVENCLAW_ID = "AgACAgIAAxkBA..."  # Ravenclaw gerbi ID si
HUFFLEPUFF_ID = "AgACAgIAAxkBA..."  # Hufflepuff gerbi ID si
SORTING_TOPIC_ID = None # Agar guruhda topic bo'lmasa None, bo'lsa raqamini yozing

# Faqat shundan keyingina HOUSES lug'ati kelishi kerak
HOUSES = {
    "Gryffindor": {"id": GRYFFINDOR_ID, "desc": "🦁 **GRYFFINDOR!**\n\nSiz jasur va mardsiz!", "emoji": "🦁"},
    "Slytherin": {"id": SLYTHERIN_ID, "desc": "🐍 **SLYTHERIN!**\n\nSiz ayor va uddaburonsiz!", "emoji": "🐍"},
    "Ravenclaw": {"id": RAVENCLAW_ID, "desc": "🦅 **RAVENCLAW!**\n\nSiz aqlli va donosiz!", "emoji": "🦅"},
    "Hufflepuff": {"id": HUFFLEPUFF_ID, "desc": "🦡 **HUFFLEPUFF!**\n\nSiz mehnatkash va sodiqsiz!", "emoji": "🦡"}
}

USER_HOUSES = {} 

# --- RENDER PORTINI ALDASH UCHUN KICHIK SERVER ---
async def handle(request):
    return web.Response(text="Bot is running smoothly!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render avtomatik beradigan PORT ni oladi, bo'lmasa 10000
    port = int(os.environ.get("PORT", 10000)) 
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server {port} portida ishga tushdi.")

# --- BOT LOGIKASI (ID olish) ---
@dp.message(F.photo)
async def get_photo_id(message: types.Message):
    file_id = message.photo[-1].file_id
    await message.reply(f"🖼 <b>Rasm ID:</b>\n<code>{file_id}</code>", parse_mode="HTML")

# --- YANGI A'ZO KELGANDA ---
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    for user in message.new_chat_members:
        if user.id == bot.id: continue
        caption_text = f"🧙‍♂️ **Xush kelibsiz, {user.first_name}!**\n\nSizni fakultetga taqsimlashimiz kerak."
        tugma = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎩 Qalpoqni kiyish", callback_data=f"wear_hat_{user.id}")]])
        await bot.send_photo(chat_id=message.chat.id, message_thread_id=SORTING_TOPIC_ID, photo=HAT_IMG_ID, caption=caption_text, reply_markup=tugma, parse_mode="Markdown")

# --- TAQSIMLASH JARAYONI ---
@dp.callback_query(F.data.startswith("wear_hat_"))
async def sorting_hat_process(callback: types.CallbackQuery):
    target_id = int(callback.data.split("_")[2])
    if callback.from_user.id != target_id:
        await callback.answer("Bu siz uchun emas! ✋", show_alert=True)
        return
    
    await callback.answer("Hmm... O'ylayapman...")
    house_name = random.choice(list(HOUSES.keys()))
    house_data = HOUSES[house_name]
    USER_HOUSES[target_id] = house_name
    
    await callback.message.delete()
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        message_thread_id=SORTING_TOPIC_ID,
        photo=house_data['id'],
        caption=f"🎉 **{callback.from_user.first_name}**, sizning fakultetingiz:\n\n{house_data['desc']}",
        parse_mode="Markdown"
    )

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # MUHIM: Web serverni fonda ishga tushiramiz (Render uchun)
    asyncio.create_task(start_web_server()) 
    
    # Botni polling rejimida ishga tushiramiz
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot to'xtadi!")




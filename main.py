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
HAT_IMG_ID = "AgACAgIAAxkBAAMEaYSnRQbDnr2YuCqkbNqQdg8v2W4AAk4OaxscMChI831GZTNaiJsBAAMCAAN5AAM4BA" 
GRYFFINDOR_ID = "AgACAgIAAxkBAAMHaYXIIPDphgbohdWYJEK5OA47R1MAArITaxtyUClIUB8w7cOd6M4BAAMCAAN5AAM4BA"
SLYTHERIN_ID = "AgACAgIAAxkBAAMJaYXJD5GlhcgYyejILR8JTvHz0gwAAsgTaxtyUClINaIi3c1LUW8BAAMCAAN5AAM4BA"
RAVENCLAW_ID = "AgACAgIAAxkBAAMLaYXJiweH5Eh-GTvd5Ht6L66WCjQAAtoTaxtyUClIkKj5p860ReUBAAMCAAN5AAM4BA"
HUFFLEPUFF_ID = "AgACAgIAAxkBAAMNaYXKHqkLLw-QQufj4D533Ld9QB8AAuQTaxtyUClIP6F1JQTQnokBAAMCAAN5AAM4BA"

SORTING_TOPIC_ID = 505 # Agar guruhda topic bo'lmasa None, bo'lsa raqamini yozing

# Faqat shundan keyingina HOUSES lug'ati kelishi kerak
HOUSES = {
    "Gryffindor": {
        "id": GRYFFINDOR_ID,
        "desc": (
            "🧙‍♂️ {mention}, sening qalbingda jasorat va qat’iyat bor!\n\n"
            
            "🦁 Sening fakulteting — <b>GRYFFINDOR!</b>\n\n"
            
            "🔥 Gryffindor — jasur, mard va yetakchi sehrgarlar uyi. Bu yerda qo‘rquv emas, jasorat hukmron.\n\n"
            
            "✨ Fakulteting bilan faxrlan!"
        ),
        "emoji": "🦁"
    },
    "Slytherin": {
        "id": SLYTHERIN_ID,
        "desc": (
            "🧙‍♂️ {mention}, sening qalbingda ulkan ambitsiyalar yashirin!\n\n"
            
            "🐍 Sening fakulteting — <b>SLYTHERIN!</b>\n\n"
            
            "🟢 Slytherin — aql, strategiya va ambitsiya fakulteti. Buyuk sehrgarlar aynan shu yerdan chiqqan.\n\n"
            
            "🔐 Sirlaringni asra!"
        ),
        "emoji": "🐍"
    },
    "Ravenclaw": {
        "id": RAVENCLAW_ID,
        "desc": (
            "🧙‍♂️ {mention}, sening zehning va aqling tengsiz!\n\n"
            
            "🦅 Sening fakulteting — <b>RAVENCLAW!</b>\n\n"
            
            "🔵 Ravenclaw — aql, bilim va donolik fakulteti. Bu yerda savollar javoblardan muhimroq.\n\n"
            
            "📘 O'rganishdan toxtama!"
        ),
        "emoji": "🦅"
    },
    "Hufflepuff": {
        "id": HUFFLEPUFF_ID,
        "desc": (
           "🧙‍♂️ {mention}, sening yuraging toza va sadoqatli!\n\n"
            
            "🦡 Sening fakulteting — <b>HUFFLEPUFF!</b>\n\n"
            
            "🟡 Hufflepuff — sodiq, mehnatkash va adolatli sehrgarlar uyi. Bu yerda har kim o‘z o‘rnini topadi.\n\n"
            
            "🤝 Xush kelibsan!"
        ),
        "emoji": "🦡"
    }
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
        
        # O'ZGARISH: Ismni havola (link) ichiga oldik va HTML formatladik
        caption_text = f"🧙‍♂️ <b>Xush kelibsiz, <a href='tg://user?id={user.id}'>{user.first_name}</a>!</b>\n\nSizni fakultetga taqsimlashimiz kerak."
        
        tugma = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🧙 Qalpoqni kiyish", callback_data=f"wear_hat_{user.id}")]])
        
        await bot.send_photo(
            chat_id=message.chat.id, 
            message_thread_id=SORTING_TOPIC_ID, 
            photo=HAT_IMG_ID, 
            caption=caption_text, 
            reply_markup=tugma, 
            parse_mode="HTML"
        )

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
    USER_HOUSES[target_id] = {
        "house": house_name,
        "name": callback.from_user.first_name, # Ismi
        "mention": f"<a href='tg://user?id={target_id}'>{callback.from_user.first_name}</a>" # Linki
    }
    
    await callback.message.delete()
    
    # Ismni MENTION (bosiladigan ko'k yozuv) qilish
    user_mention = f"<a href='tg://user?id={callback.from_user.id}'>{callback.from_user.first_name}</a>"
    
    # HOUSES lug'atidagi {mention} so'zini haqiqiy ismga almashtiramiz
    final_caption = house_data['desc'].format(mention=user_mention)
    
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        message_thread_id=SORTING_TOPIC_ID,
        photo=house_data['id'],
        caption=final_caption, # Ortiqcha so'zlarsiz, faqat tayyor matn
        parse_mode="HTML"
    )

# --- STATISTIKA (RO'YXAT) - FAQAT ADMINLAR UCHUN ---
@dp.message(Command("statistika"))
async def show_statistics(message: types.Message):
    # 1. ADMINLIKNI TEKSHIRISH
    # Foydalanuvchining guruhdagi statusini olamiz
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    
    # Agar status 'administrator' yoki 'creator' bo'lmasa, kod shu yerda to'xtaydi
    if member.status not in ['administrator', 'creator']:
        await message.reply("⛔️ <b>Bu buyruq faqat guruh adminlari uchun!</b>", parse_mode="HTML")
        return

    # 2. Ma'lumotlarni yig'amiz (Agar admin bo'lsa, kod davom etadi)
    stats = {
        "Gryffindor": [],
        "Slytherin": [],
        "Ravenclaw": [],
        "Hufflepuff": []
    }
    
    for user_id, info in USER_HOUSES.items():
        h_name = info["house"]
        if h_name in stats:
            stats[h_name].append(info["mention"])
            
    # 3. Chiroyli matn tuzamiz
    text = "📜 <b>HOGWARTS O'QUVCHILARI RO'YXATI:</b>\n\n"
    
    # Gryffindor
    text += f"🦁 <b>Gryffindor ({len(stats['Gryffindor'])}):</b>\n"
    text += ", ".join(stats['Gryffindor']) if stats['Gryffindor'] else "<i>Hozircha hech kim yo'q</i>"
    text += "\n\n"
    
    # Slytherin
    text += f"🐍 <b>Slytherin ({len(stats['Slytherin'])}):</b>\n"
    text += ", ".join(stats['Slytherin']) if stats['Slytherin'] else "<i>Hozircha hech kim yo'q</i>"
    text += "\n\n"

    # Ravenclaw
    text += f"🦅 <b>Ravenclaw ({len(stats['Ravenclaw'])}):</b>\n"
    text += ", ".join(stats['Ravenclaw']) if stats['Ravenclaw'] else "<i>Hozircha hech kim yo'q</i>"
    text += "\n\n"

    # Hufflepuff
    text += f"🦡 <b>Hufflepuff ({len(stats['Hufflepuff'])}):</b>\n"
    text += ", ".join(stats['Hufflepuff']) if stats['Hufflepuff'] else "<i>Hozircha hech kim yo'q</i>"
    
    await message.reply(text, parse_mode="HTML")

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





















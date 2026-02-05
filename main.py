import asyncio
import logging
import sys
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
# Yangi botning TOKENini shu yerga qo'ying:
API_TOKEN = '8400967993:AAHl9cpqZdDZ7sfe_2Tsmba0PQ2MKMYNS3w'

# Botni sozlash
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- FAKULTETLAR MA'LUMOTI ---
# KODNI ISHLATISH OLDIDAN:
# 1. Botni ishga tushiring.
# 2. Botga 5 ta rasmni (Shlyapa + 4 fakultet) yuboring.
# 3. Bot sizga ID larni qaytaradi. O'shalarni shu yerga yozing.

HAT_IMG_ID = "AgACAgIAAxkBA..."       # Shlyapa rasmi
GRYFFINDOR_ID = "AgACAgIAAxkBA..."    # Arslon
SLYTHERIN_ID = "AgACAgIAAxkBA..."     # Ilon
RAVENCLAW_ID = "AgACAgIAAxkBA..."     # Burgut
HUFFLEPUFF_ID = "AgACAgIAAxkBA..."    # Bo'rsiq

# "Sorting Hat" mavzusi (Topic) ID si. 
# Agar guruhda Topiclar yoqilgan bo'lsa, o'sha topic ID sini yozing.
# Agar oddiy guruh bo'lsa, None qoldiring.
SORTING_TOPIC_ID = None 

# Fakultetlar bazasi
HOUSES = {
    "Gryffindor": {
        "id": GRYFFINDOR_ID, 
        "desc": "🦁 **GRYFFINDOR!**\n\nSiz jasur, mard va olijanobsiz!\nGarri Potter ham shu yerda o'qigan.", 
        "emoji": "🦁"
    },
    "Slytherin": {
        "id": SLYTHERIN_ID, 
        "desc": "🐍 **SLYTHERIN!**\n\nSiz ayor, uddaburon va buyuklikka intiluvchisiz!", 
        "emoji": "🐍"
    },
    "Ravenclaw": {
        "id": RAVENCLAW_ID, 
        "desc": "🦅 **RAVENCLAW!**\n\nSiz o'tkir aql, zakovat va ijodkorlik sohibisiz!", 
        "emoji": "🦅"
    },
    "Hufflepuff": {
        "id": HUFFLEPUFF_ID, 
        "desc": "🦡 **HUFFLEPUFF!**\n\nSiz mehnatkash, sabrli va eng sodiq do'stsiz!", 
        "emoji": "🦡"
    }
}

# Foydalanuvchilar qaysi uyda ekanligi (Vaqtinchalik xotira)
USER_HOUSES = {} 

# --- 1. ID OLISH UCHUN YORDAMCHI ---
@dp.message(F.photo)
async def get_photo_id(message: types.Message):
    # Faqat admin (siz) yuborganda ishlashi uchun ID'ingizni tekshirsa bo'ladi
    # Hozircha hamma yuborsa ham ID beradi (sozlash uchun qulay)
    file_id = message.photo[-1].file_id
    await message.reply(f"🖼 <b>Rasm ID:</b>\n<code>{file_id}</code>", parse_mode="HTML")

# --- 2. TOPIC ID NI ANIQLASH ---
# Guruhdagi kerakli topicga /id deb yozsangiz, bot topic ID sini aytadi
@dp.message(Command("id"))
async def get_topic_id(message: types.Message):
    topic_id = message.message_thread_id
    chat_id = message.chat.id
    await message.reply(f"📍 <b>Chat ID:</b> {chat_id}\n📌 <b>Topic ID:</b> {topic_id}", parse_mode="HTML")

# --- 3. YANGI A'ZO QO'SHILGANDA ---
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    for user in message.new_chat_members:
        if user.id == bot.id:
            continue
            
        caption_text = (
            f"🧙‍♂️ **Xush kelibsiz, {user.first_name}!**\n\n"
            "Siz Hogwarts Cinema ostonasidasiz. \n"
            "An'anaga ko'ra, sizni 4 ta buyuk fakultetdan biriga taqsimlashimiz kerak.\n\n"
            "Qalpoq sizning qalbingizni o'qib, to'g'ri qaror qabul qiladi.\n\n"
            "👇 **Qalpoqni kiyish uchun tugmani bosing:**"
        )
        
        tugma = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎩 Qalpoqni kiyish", callback_data=f"wear_hat_{user.id}")]
        ])
        
        # Xabarni kerakli topicga yuborish
        try:
            await bot.send_photo(
                chat_id=message.chat.id,
                message_thread_id=SORTING_TOPIC_ID, 
                photo=HAT_IMG_ID,
                caption=caption_text,
                reply_markup=tugma,
                parse_mode="Markdown"
            )
        except Exception as e:
            # Agar rasm ID xato bo'lsa yoki boshqa xatolik bo'lsa
            logging.error(f"Xatolik: {e}")
            await message.answer(caption_text, reply_markup=tugma)

# --- 4. QALPOQNI KIYISH JARAYONI ---
@dp.callback_query(F.data.startswith("wear_hat_"))
async def sorting_hat_process(callback: types.CallbackQuery):
    target_user_id = int(callback.data.split("_")[2])
    clicker_id = callback.from_user.id
    
    # 1. Birovning tugmasini bosib qo'ymaslik uchun
    if clicker_id != target_user_id:
        await callback.answer("Bu qalpoq siz uchun emas! ✋", show_alert=True)
        return

    # 2. Allaqachon tanlangan bo'lsa
    if clicker_id in USER_HOUSES:
        house_name = USER_HOUSES[clicker_id]
        await callback.answer(f"Siz allaqachon {house_name} fakultetiga qabul qilingansiz!", show_alert=True)
        return

    # 3. Jarayon (Suspense effekti)
    await callback.answer("Hmm... Qiziq... Juda qiziq...")
    await callback.message.edit_caption(caption="🎩 <i>Hmm... Sizda jasorat bor, lekin aql ham yetarli... Qayerga joylasak ekan?</i>", parse_mode="HTML")
    await asyncio.sleep(2) # 2 soniya o'ylaydi
    
    # 4. Tanlash
    house_name = random.choice(list(HOUSES.keys()))
    house_data = HOUSES[house_name]
    USER_HOUSES[clicker_id] = house_name
    
    # 5. Natija
    stats_tugma = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Maktab ro'yxati", callback_data="show_house_stats")]
    ])
    
    await callback.message.delete() # Eski xabarni o'chiramiz
    
    # Yangi xabarni (Natijani) Topicga yuboramiz
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        message_thread_id=SORTING_TOPIC_ID,
        photo=house_data['id'],
        caption=f"🎉 **TABRIKLAYMIZ!**\n\nSorting Hat qaror qildi:\n**{callback.from_user.first_name}** endi...\n\n{house_data['desc']}",
        reply_markup=stats_tugma,
        parse_mode="Markdown"
    )

# --- 5. STATISTIKA ---
@dp.callback_query(F.data == "show_house_stats")
async def show_stats(callback: types.CallbackQuery):
    counts = {"Gryffindor": 0, "Slytherin": 0, "Ravenclaw": 0, "Hufflepuff": 0}
    
    for house in USER_HOUSES.values():
        if house in counts:
            counts[house] += 1
            
    text = (
        "📊 **Hogwarts O'quvchilari Ro'yxati:**\n\n"
        f"🦁 Gryffindor: **{counts['Gryffindor']}**\n"
        f"🐍 Slytherin: **{counts['Slytherin']}**\n"
        f"🦅 Ravenclaw: **{counts['Ravenclaw']}**\n"
        f"🦡 Hufflepuff: **{counts['Hufflepuff']}**\n\n"
        f"Jami sehrgarlar: **{len(USER_HOUSES)}**"
    )
    
    await callback.answer()
    await callback.message.answer(text, parse_mode="Markdown", message_thread_id=SORTING_TOPIC_ID)

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# --- SERVER SOZLAMALARI ---
async def health_check(request):
    return web.Response(text="Bot ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

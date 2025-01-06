import json
import asyncio
from fpdf import FPDF
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime
from aiogram.types import InputFile
from aiogram.types import FSInputFile



# Global variables ////
ADMIN_PASSWORD = "Abbosbek"
ruxsat_etilgan_foydalanuvchilar = {}  # {user_id: {"first_name": "Ism", "username": "username"}}
database = {"savdolar": [], "ombor": {}, "xarajatlar": []}

# Helper functions
def save_data():
    with open("database.json", "w") as db:
        json.dump(database, db, indent=4)

def load_data():
    global database
    try:
        with open("database.json", "r") as db:
            database = json.load(db)
    except FileNotFoundError:
        save_data()

# Foydalanuvchi tizimga kirganini tekshirish
async def foydalanuvchini_tekshirish(message: Message):
    user_id = message.from_user.id
    if user_id in ruxsat_etilgan_foydalanuvchilar:
        return True
    await message.answer("Avval /start bosing va parolni kiriting.")
    return False

# `# `/start` buyrug‘i
async def start_command(message: Message):
    user_id = message.from_user.id

    if user_id in ruxsat_etilgan_foydalanuvchilar:
        # Tugmalarni yaratish
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(
            KeyboardButton(text="Yakuniy savdo"),
            KeyboardButton(text="Ombordagi mahsulot")
        )
        keyboard.row(
            KeyboardButton(text="Mahsulot qabul qilish"),
            KeyboardButton(text="Mahsulot chiqarish")
        )
        keyboard.row(
            KeyboardButton(text="Kunlik hisobot"),
            KeyboardButton(text="Oylik hisobot PDF"),
        )
        keyboard.row(
            KeyboardButton(text="Xarajat kiritish"),
            KeyboardButton(text="Tushum kiritish")
        )
        keyboard.row(
            KeyboardButton(text="Foyda-lar ro‘yxati"),
            KeyboardButton(text="Barcha foy-ni tozalash")
        )
        await message.answer("Buyruqlar ro‘yxati:", reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        await message.answer("🔑 Parolni kiriting:")

async def tugmalar_ishlovchi(message: Message):
    if not await foydalanuvchini_tekshirish(message):
        return

    user_id = message.from_user.id
    print(f"Tugma bosildi: {message.text}")  # Debug uchun

    # Tugmalar uchun matnni tekshirish
    if message.text == "Yakuniy savdo":
        user_states[user_id] = "yakuniy_savdo"
        await message.answer("❓ Mahsulot nomi, soni va narxini kiriting. Masalan: Somsa 10")
    elif message.text == "Ombordagi mahsulot":
        await ombor(message)
    elif message.text == "Mahsulot qabul qilish":
        user_states[user_id] = "qabul"
        await message.answer("❓ Mahsulot nomi va sonini kiriting. Masalan: Un 10")
    elif message.text == "Mahsulot chiqarish":
        user_states[user_id] = "chiqarish"
        await message.answer("❓ Mahsulot nomi va sonini kiriting. Masalan: Un 2")
    elif message.text == "Kunlik hisobot":
        await kunlik_hisobot(message)
    elif message.text == "Oylik hisobot PDF":
        await oylik_hisobot(message)
    elif message.text == "Xarajat kiritish":
        user_states[user_id] = "xarajat"
        await message.answer("❓ Xarajat nomi va narxini kiriting. Masalan: Elektr 50000")
    elif message.text == "Tushum kiritish":
        user_states[user_id] = "tushum_kiritish"
        await message.answer(
            "❓ Tushumlarni uch turda kiriting. Masalan: 20000 15000 10000\n"
            "Bu yerda: Karta - 20000, Hisob - 15000, Naqd - 10000."
        )
    elif message.text == "Foyda-lar ro‘yxati":
        await foydalanuvchilar(message)
    elif message.text == "Barcha foy-ni tozalash":
        await foydalanuvchilarni_tozalash(message)
    elif user_id in user_states:
        # Foydalanuvchining holati asosida operatsiya
        action = user_states[user_id]
        if action == "yakuniy_savdo":
            await yakuniy_savdo(message)
        elif action == "qabul":
            await qabul(message)
        elif action == "chiqarish":
            await chiqarish(message)
        elif action == "xarajat":
            await xarajat(message)
        elif action == "tushum_kiritish":
            await kunlik_tushum(message)
        else:
            await message.answer("❌ Noma'lum buyruq yoki tugma bosildi.")
        del user_states[user_id]  # Holatni tozalash
    else:
        await message.answer("❌ Noma'lum buyruq yoki tugma bosildi.")

# Foydalanuvchilar ro‘yxatini tozalash funksiyasi
async def foydalanuvchilarni_tozalash(message: Message):
    print("Foydalanuvchilarni tozalash funksiyasi chaqirildi")
    if not await foydalanuvchini_tekshirish(message):
        return

    global ruxsat_etilgan_foydalanuvchilar
    ruxsat_etilgan_foydalanuvchilar.clear()  # Barcha foydalanuvchilarni tozalash
    save_data()  # Tozalanish ma'lumotlarini saqlash
    await message.answer("✅ Barcha foydalanuvchilar muvaffaqiyatli tozalandi.")


async def parol_tekshirish(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Ismsiz"
    username = message.from_user.username or "Username yo'q"

    if user_id in ruxsat_etilgan_foydalanuvchilar:
        await tugmalar_ishlovchi(message)  # Forward to button handler
        return
    
    if message.text == ADMIN_PASSWORD:
            ruxsat_etilgan_foydalanuvchilar[user_id] = {"first_name": first_name, "username": username}
            await message.answer("✅ Parol to'g'ri! Endi tizimga kirdingiz.")
            await start_command(message)
    else:
        await message.answer("❌ Parol noto'g'ri! Qaytadan urinib ko'ring.")


async def foydalanuvchilar(message: Message):
    print("Foydalanuvchilar funksiyasi chaqirildi")
    if not await foydalanuvchini_tekshirish(message):
        return

    print("Ruxsat etilgan foydalanuvchilar:", ruxsat_etilgan_foydalanuvchilar)
    if ruxsat_etilgan_foydalanuvchilar:
        javob = "✅ Ruxsat etilgan foydalanuvchilar ro‘yxati:\n"
        for user_id, info in ruxsat_etilgan_foydalanuvchilar.items():
            ism = info["first_name"]
            username = f"@{info['username']}" if info["username"] != "Username yo'q" else "Username yo‘q"
            javob += f"👤 {ism} (ID: {user_id}) {username}\n"
        await message.answer(javob)
    else:
        await message.answer("❗ Ruxsat etilgan foydalanuvchilar yo‘q.")



def generate_monthly_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    # Hisobot uchun oyning nomi va yili
    oy = datetime.now().strftime("%Y-%m")
    yil_va_oy = datetime.now().strftime("%Y yil, %B")

    # Hisobot sarlavhasi
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt=f"Oylik Hisobot ({yil_va_oy})", ln=True, align="C")
    pdf.ln(10)

    # Ma'lumotlarni yig'ish
    savdolar = [savdo for savdo in database.get("savdolar", []) if savdo.get("sana", "").startswith(oy)]
    xarajatlar = [xarajat for xarajat in database.get("xarajatlar", []) if xarajat.get("sana", "").startswith(oy)]
    tushumlar = [tushum for tushum in database.get("tushumlar", []) if tushum.get("sana", "").startswith(oy)]

    # Sanalar bo‘yicha ma'lumotlarni guruhlash
    kunlik_hisobot = {}
    for savdo in savdolar:
        sana = savdo.get("sana", "")
        if sana not in kunlik_hisobot:
            kunlik_hisobot[sana] = {"savdolar": [], "xarajatlar": [], "tushumlar": [], "umumiy_savdo": 0, "umumiy_xarajat": 0, "umumiy_tushum": {"karta": 0, "hisob": 0, "naqd": 0}}
        kunlik_hisobot[sana]["savdolar"].append(savdo)
        kunlik_hisobot[sana]["umumiy_savdo"] += savdo.get("soni", 0)

    for xarajat in xarajatlar:
        sana = xarajat.get("sana", "")
        if sana not in kunlik_hisobot:
            kunlik_hisobot[sana] = {"savdolar": [], "xarajatlar": [], "tushumlar": [], "umumiy_savdo": 0, "umumiy_xarajat": 0, "umumiy_tushum": {"karta": 0, "hisob": 0, "naqd": 0}}
        kunlik_hisobot[sana]["xarajatlar"].append(xarajat)
        kunlik_hisobot[sana]["umumiy_xarajat"] += xarajat.get("narxi", 0)

    for tushum in tushumlar:
        sana = tushum.get("sana", "")
        if sana not in kunlik_hisobot:
            kunlik_hisobot[sana] = {"savdolar": [], "xarajatlar": [], "tushumlar": [], "umumiy_savdo": 0, "umumiy_xarajat": 0, "umumiy_tushum": {"karta": 0, "hisob": 0, "naqd": 0}}
        kunlik_hisobot[sana]["tushumlar"].append(tushum)
        kunlik_hisobot[sana]["umumiy_tushum"]["karta"] += tushum.get("karta", 0)
        kunlik_hisobot[sana]["umumiy_tushum"]["hisob"] += tushum.get("hisob", 0)
        kunlik_hisobot[sana]["umumiy_tushum"]["naqd"] += tushum.get("naqd", 0)

    # Tablitsa chizish
    for sana, data in sorted(kunlik_hisobot.items()):
        # Sana sarlavhasi
        pdf.set_font("Arial", style="B", size=10)
        pdf.set_text_color(0, 0, 255)  # Moviy rang
        pdf.cell(200, 8, txt=f"Sana: {sana}", ln=True, align="L")
        pdf.set_text_color(0, 0, 0)  # Rangni qora qilib qaytarish
        pdf.ln(2)

        # Savdolar bo'limi
        if data["savdolar"]:
            pdf.set_font("Arial", style="B", size=8)
            pdf.cell(50, 6, "Mahsulot", border=1, align="C")
            pdf.cell(20, 6, "Soni", border=1, align="C")
            pdf.ln()
            pdf.set_font("Arial", size=8)
            for savdo in data["savdolar"]:
                pdf.cell(50, 6, savdo.get("mahsulot", ""), border=1)
                pdf.cell(20, 6, str(savdo.get("soni", 0)), border=1, align="R")
                pdf.ln()
            pdf.cell(70, 6, f"Kunlik savdo jami: {data['umumiy_savdo']} dona", border=0, ln=True)
        else:
            pdf.cell(70, 6, "Savdolar yo'q", ln=True)

        pdf.ln(4)

        # Tushumlar bo'limi
        pdf.set_font("Arial", style="B", size=8)
        pdf.cell(60, 6, "Tushumlar:", ln=True)
        pdf.set_font("Arial", size=8)
        pdf.cell(70, 6, f"Karta: {data['umumiy_tushum']['karta']} so'm", ln=True)
        pdf.cell(70, 6, f"Hisob: {data['umumiy_tushum']['hisob']} so'm", ln=True)
        pdf.cell(70, 6, f"Naqd: {data['umumiy_tushum']['naqd']} so'm", ln=True)
        pdf.ln(4)

        # Xarajatlar bo'limi
        if data["xarajatlar"]:
            pdf.set_font("Arial", style="B", size=8)
            pdf.cell(50, 6, "Mahsulot", border=1, align="C")
            pdf.cell(30, 6, "Narxi (so'm)", border=1, align="C")
            pdf.cell(40, 6, "Ism", border=1, align="C")
            pdf.ln()
            pdf.set_font("Arial", size=8)
            for xarajat in data["xarajatlar"]:
                pdf.cell(50, 6, xarajat.get("mahsulot", ""), border=1)
                pdf.cell(30, 6, f"{xarajat.get('narxi', 0)}", border=1, align="R")
                pdf.cell(40, 6, xarajat.get("foydalanuvchi", ""), border=1)
                pdf.ln()
            pdf.cell(70, 6, f"Kunlik xarajat jami: {data['umumiy_xarajat']} so'm", border=0, ln=True)
        else:
            pdf.cell(70, 6, "Xarajatlar yo'q", ln=True)

        pdf.ln(8)  # Bo'limlar orasini ajratish uchun

    # Umumiy hisobot
    pdf.set_font("Arial", style="B", size=9)
    pdf.cell(100, 8, txt=f"Umumiy savdo: {sum(day['umumiy_savdo'] for day in kunlik_hisobot.values())} dona", ln=True)
    pdf.cell(100, 8, txt=f"Umumiy tushum: {sum(day['umumiy_tushum']['karta'] + day['umumiy_tushum']['hisob'] + day['umumiy_tushum']['naqd'] for day in kunlik_hisobot.values())} so'm", ln=True)
    pdf.cell(100, 8, txt=f"Umumiy xarajat: {sum(day['umumiy_xarajat'] for day in kunlik_hisobot.values())} so'm", ln=True)

    # PDF faylni saqlash
    pdf.output("oylik_hisobot.pdf", "F")





async def yakuniy_savdo(message: Message):
    args = message.text.strip().split(maxsplit=1)  # Faqat mahsulot nomi va sonini qabul qilish
    if len(args) != 2:
        await message.answer("❌ Mahsulot nomi va sonini to'g'ri kiriting. Masalan: Un 10")
        return

    mahsulot, soni = args
    try:
        soni = int(soni)
        if soni <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Soni musbat butun son bo'lishi kerak!")
        return

    # Savdoni saqlash
    savdo = {
        "mahsulot": mahsulot,
        "soni": soni,
        "sana": datetime.now().strftime("%Y-%m-%d"),
    }
    database["savdolar"].append(savdo)
    save_data()

    await message.answer(f"✅ Savdo muvaffaqiyatli qo'shildi: {mahsulot} - {soni} dona")




async def kunlik_tushum(message: Message):
    args = message.text.strip().split(maxsplit=3)
    if len(args) != 3:
        await message.answer(
            "❓ Tushumlarni uch turda kiriting. Masalan: 20000 15000 10000\n"
            "Bu yerda: Karta - 20000, Hisob - 15000, Naqd - 10000."
        )
        return

    try:
        karta, hisob, naqd = map(int, args)
        if karta < 0 or hisob < 0 or naqd < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Tushumlar faqat musbat butun sonlar bo'lishi kerak!")
        return

    # Tushumlarni saqlash
    tushum = {
        "karta": karta,
        "hisob": hisob,
        "naqd": naqd,
        "sana": datetime.now().strftime("%Y-%m-%d")
    }
    database.setdefault("tushumlar", []).append(tushum)
    save_data()

    await message.answer(
        f"✅ Tushumlar qo'shildi:\n"
        f"Karta: {karta} so'm\nHisob: {hisob} so'm\nNaqd: {naqd} so'm"
    )



async def ombor(message: Message):
    if not await foydalanuvchini_tekshirish(message):
        return

    if not database["ombor"]:
        await message.answer("Ombor bo‘sh!")
    else:
        javob = "Ombordagi mahsulotlar:\n"
        for mahsulot, soni in database["ombor"].items():
            javob += f"✅ {mahsulot}: {soni} dona\n"
        await message.answer(javob)


async def qabul(message: Message):
    args = message.text.strip().split(maxsplit=1)
    if len(args) != 2:
        await message.answer("❌ Mahsulot nomi va sonini kiriting. Masalan: Un 10")
        return

    mahsulot, soni = args[0], args[1]

    try:
        soni = int(soni)
        if soni <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Soni faqat musbat butun son bo‘lishi kerak!")
        return

    database["ombor"][mahsulot] = database["ombor"].get(mahsulot, 0) + soni
    save_data()

    await message.answer(f"✅ Omborga qabul qilindi: {mahsulot} - {soni} dona")


async def chiqarish(message: Message):
    args = message.text.strip().split(maxsplit=1)
    if len(args) != 2:
        await message.answer("❌ Mahsulot nomi va sonini kiriting. Masalan: Un 2")
        return

    mahsulot, soni = args[0], args[1]


    try:
        soni = int(soni)
        if soni <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Soni faqat musbat butun son bo‘lishi kerak !")
        return

    if mahsulot not in database["ombor"] or database["ombor"][mahsulot] < soni:
        await message.answer(
            f"❌ Omborda {mahsulot} yetarli emas yoki mavjud emas! Ombordagi soni: {database['ombor'].get(mahsulot, 0)} dona."
        )
        return

    database["ombor"][mahsulot] -= soni
    if database["ombor"][mahsulot] == 0:
        del database["ombor"][mahsulot]
    save_data()

    await message.answer(f"✅ Ombordan chiqarildi: {mahsulot} - {soni} dona")


async def xarajat(message: Message):
    if not await foydalanuvchini_tekshirish(message):
        return
    
    args = message.text.strip().split(maxsplit=1)  # Xarajat matnini bo'lish
    if len(args) != 2:
        await message.answer("❓ Xarajat nomi va narxini kiriting. Masalan: Elektr 50000")
        return

    mahsulot, narxi = args
    try:
        narxi = int(narxi)
        if narxi <= 0:
            raise ValueError("Narx musbat son bo'lishi kerak.")
    except ValueError:
        await message.answer("❌ Narx faqat musbat butun son bo‘lishi kerak!")
        return

    # Xarajatni saqlash
    foydalanuvchi = message.from_user.username or "NoName"
    xarajat = {
        "mahsulot": mahsulot,
        "narxi": narxi,
        "foydalanuvchi": foydalanuvchi,
        "sana": datetime.now().strftime("%Y-%m-%d"),
    }
    database["xarajatlar"].append(xarajat)
    save_data()

    await message.answer(f"✅ Xarajat qo‘shildi:\n{mahsulot} - {narxi} so'm 👤 {foydalanuvchi}")


async def kunlik_hisobot(message: Message):
    bugun = datetime.now().strftime("%Y-%m-%d")

    # Savdolarni olish
    savdolar = [
        savdo for savdo in database["savdolar"]
        if "sana" in savdo and savdo["sana"] == bugun
    ]
    savdo_hisobot = (
        "\n".join([f"{savdo['mahsulot']} - {savdo['soni']} dona" for savdo in savdolar])
        or "Hech narsa sotilmagan."
    )

    # Tushumlarni olish
    tushumlar = [
        t for t in database.get("tushumlar", [])
        if "sana" in t and t["sana"] == bugun
    ]
    karta = sum(t.get("karta", 0) for t in tushumlar)
    hisob = sum(t.get("hisob", 0) for t in tushumlar)
    naqd = sum(t.get("naqd", 0) for t in tushumlar)
    umumiy_tushum = karta + hisob + naqd

    # Xarajatlarni olish
    xarajatlar = [
        xarajat for xarajat in database["xarajatlar"]
        if "sana" in xarajat and xarajat["sana"] == bugun
    ]
    xarajat_hisobot = (
        "\n".join([f"{x['mahsulot']} - {x['narxi']} so'm" for x in xarajatlar])
        or "Hech qanday xarajat qilinmagan."
    )
    umumiy_xarajat = sum(x.get("narxi", 0) for x in xarajatlar)

    # Hisobotni yaratish
    hisobot = (
        f"📆 Kunlik hisobot ({bugun}):\n\n"
        f"🛒 Savdolar:\n{savdo_hisobot}\n\n"
        f"💰 Tushumlar:\nKarta: {karta} so'm\nHisob: {hisob} so'm\nNaqd: {naqd} so'm\n"
        f"Umumiy tushum: {umumiy_tushum} so'm\n\n"
        f"📉 Xarajatlar:\n{xarajat_hisobot}\n"
        f"Umumiy xarajat: {umumiy_xarajat} so'm\n"
    )

    await message.answer(hisobot)



async def oylik_hisobot(message: Message):
    try:
        # PDF hisobotni yaratish
        generate_monthly_report()
        
        # PDF faylni yuklash va foydalanuvchiga jo'natish
        pdf_file = FSInputFile("oylik_hisobot.pdf")
        await message.answer_document(pdf_file, caption="📆 Oylik hisobot PDF")
    except Exception as e:
        # Agar xatolik yuz bersa, foydalanuvchiga xabar berish
        await message.answer(f"❌ Hisobotni yaratishda xatolik yuz berdi: {e}")


# Foydalanuvchi holatini saqlash uchun lug‘at
user_states = {}

async def tozalash(message: Message):
    user_id = message.from_user.id
    if not await foydalanuvchini_tekshirish(message):
        return

    # Foydalanuvchi holatini tozalash holatiga o‘zgartirish
    user_states[user_id] = {"tozalash": True}
    await message.answer("❗Ro‘yxatni tozalash uchun parolni qaytadan kiriting:")

async def handle_message(message: Message):
    user_id = message.from_user.id

    # Foydalanuvchi holatini tekshirish
    if user_states.get(user_id, {}).get("tozalash"):
        if message.text == ADMIN_PASSWORD:
            database.clear()
            save_data()
            user_states[user_id]["tozalash"] = False
            await message.answer("✅ Barcha ma'lumotlar o‘chirildi!")
        else:
            await message.answer("❌ Parol noto‘g‘ri! Qaytadan urinib ko‘ring.")
    else:
        await message.answer("Noma'lum buyruq!")


async def main():
    load_data()
    bot = Bot(token="8198692446:AAE062mioUGN8xHpycUandU0BvP6NOntXFI")
    dp = Dispatcher()

    # Komanda buyruqlarni ro'yxatdan o'tkazish
    dp.message.register(start_command, Command(commands=["start"]))
    dp.message.register(parol_tekshirish)
    dp.message.register(oylik_hisobot, Command(commands=["oylik_hisobot"]))
    dp.message.register(xarajat, Command(commands=["xarajat"]))
    dp.message.register(kunlik_tushum, Command(commands=["kunlik_tushum"]))
    dp.message.register(yakuniy_savdo, Command(commands=["yakuniy_savdo"]))
    dp.message.register(ombor, Command(commands=["ombor"]))
    dp.message.register(qabul, Command(commands=["qabul"]))
    dp.message.register(chiqarish, Command(commands=["chiqarish"]))
    dp.message.register(kunlik_hisobot, Command(commands=["kunlik_hisobot"]))
    dp.message.register(tozalash, Command(commands=["tozalash"]))
    dp.message.register(foydalanuvchilar, Command(commands=["foydalanuvchilar"]))
    dp.message.register(foydalanuvchilarni_tozalash, Command(commands=["foydalanuvchilarni_tozalash"]))
    dp.message.register(tugmalar_ishlovchi)  # Tugmalarni boshqaruvchi

    # Eskirgan yangilanishlarni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)

    # Botni boshlash
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

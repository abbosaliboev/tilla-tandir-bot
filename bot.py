import json
from fpdf import FPDF
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Global variables
ADMIN_PASSWORD = "Abbos"
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
async def foydalanuvchini_tekshirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in ruxsat_etilgan_foydalanuvchilar:
        return True
    await update.message.reply_text("Avval /start bosing va parolni kiriting.")
    return False

# `/start` buyrug‘i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in ruxsat_etilgan_foydalanuvchilar:
        javob = (
            "Buyruqlar ro‘yxati:\n"
            "/yakuniy_savdo - Yakuniy savdo\n"
            "/ombor - Ombordagi mahsulotlar\n"
            "/qabul - Omborga mahsulot qabul qilish\n"
            "/chiqarish - Ombordan mahsulot chiqarish\n"
            "/kunlik_hisobot - Kunlik hisobot\n"
            "/oylik_hisobot - Oylik hisobot\n"
            "/xarajat - Xarajatni kiritish\n"
            "/foydalanuvchilar - Foydalanuvchilar ro‘yxati\n"
            "/foydalanuvchilarni_tozalash - Barcha foydalanuvchilarni o‘chirish\n"
            "/foydalanuvchini_ochirish - Foydalanuvchini o‘chirish (ID bilan)\n"
        )
        await update.message.reply_text(javob)
    else:
        await update.message.reply_text("🔑 Parolni kiriting:")

# Parolni tekshirish
async def parol_tekshirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name or "Ismsiz"
    username = update.message.from_user.username or "Username yo'q"

    if user_id in ruxsat_etilgan_foydalanuvchilar:
        await update.message.reply_text("❌ Noto‘g‘ri buyruq!\n Buyruqlar ro‘yxati uchun /start ni bosing.")
    else:
        if update.message.text == ADMIN_PASSWORD:
            # Foydalanuvchi ma'lumotlarini qo‘shish
            ruxsat_etilgan_foydalanuvchilar[user_id] = {"first_name": first_name, "username": username}
            await update.message.reply_text("✅ Parol to‘g‘ri! Endi tizimga kirdingiz.")
            # Buyruqlarni ko‘rsatish uchun /start funksiyasini chaqirish
            await start(update, context)
        else:
            await update.message.reply_text("❌ Parol noto‘g‘ri! Qaytadan urinib ko‘ring.")

# Foydalanuvchilar ro‘yxatini ko‘rsatish
async def foydalanuvchilar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):  # Foydalanuvchini tekshirish
        return

    if ruxsat_etilgan_foydalanuvchilar:
        javob = "✅ Ruxsat etilgan foydalanuvchilar ro‘yxati:\n"
        for user_id, info in ruxsat_etilgan_foydalanuvchilar.items():
            ism = info["first_name"]
            username = f"@{info['username']}" if info["username"] != "Username yo'q" else "Username yo‘q"
            javob += f"👤 {ism} ({username})\n"
        await update.message.reply_text(javob)
    else:
        await update.message.reply_text("❗ Ruxsat etilgan foydalanuvchilar yo‘q.")

# Foydalanuvchilar ro‘yxatini tozalash
async def foydalanuvchilarni_tozalash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ruxsat_etilgan_foydalanuvchilar:
        await update.message.reply_text("Siz tizimga kirmagansiz!")
        return

    ruxsat_etilgan_foydalanuvchilar.clear()
    await update.message.reply_text("✅ Barcha foydalanuvchilar o‘chirildi!")

# Foydalanuvchini o‘chirish
async def foydalanuvchini_ochirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ruxsat_etilgan_foydalanuvchilar:
        await update.message.reply_text("Siz tizimga kirmagansiz!")
        return

    args = context.args
    if len(args) != 1:
        await update.message.reply_text("❗ Foydalanish: /foydalanuvchini_ochirish [user_id]")
        return

    target_id = int(args[0])
    if target_id in ruxsat_etilgan_foydalanuvchilar:
        del ruxsat_etilgan_foydalanuvchilar[target_id]
        await update.message.reply_text(f"✅ Foydalanuvchi ID: {target_id} muvaffaqiyatli o‘chirildi.")
    else:
        await update.message.reply_text(f"❗ Foydalanuvchi ID: {target_id} topilmadi.")

def generate_monthly_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    # Hisobot uchun oyning nomi va yili
    oy = datetime.now().strftime("%Y-%m")
    yil_va_oy = datetime.now().strftime("%Y yil, %B")

    # Hisobot sarlavhasi
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(200, 6, txt=f"Oylik Hisobot ({yil_va_oy})", ln=True, align="C")
    pdf.ln(6)

    # Ma'lumotlarni yig'ish
    savdolar = [savdo for savdo in database["savdolar"] if savdo["sana"].startswith(oy)]
    xarajatlar = [xarajat for xarajat in database["xarajatlar"] if xarajat["sana"].startswith(oy)]

    # Sanalar bo‘yicha savdolarni va xarajatlarni guruhlash
    kunlik_hisobot = {}
    for savdo in savdolar:
        sana = savdo["sana"]
        if sana not in kunlik_hisobot:
            kunlik_hisobot[sana] = {"savdolar": [], "xarajatlar": [], "umumiy_savdo": 0, "umumiy_xarajat": 0}
        kunlik_hisobot[sana]["savdolar"].append(savdo)
        kunlik_hisobot[sana]["umumiy_savdo"] += savdo["narxi"] * savdo["soni"]

    for xarajat in xarajatlar:
        sana = xarajat["sana"]
        if sana not in kunlik_hisobot:
            kunlik_hisobot[sana] = {"savdolar": [], "xarajatlar": [], "umumiy_savdo": 0, "umumiy_xarajat": 0}
        kunlik_hisobot[sana]["xarajatlar"].append(xarajat)
        kunlik_hisobot[sana]["umumiy_xarajat"] += xarajat["narxi"]

    # Umumiy oylik daromad va xarajat
    umumiy_daromad = sum(day["umumiy_savdo"] for day in kunlik_hisobot.values())
    umumiy_xarajat = sum(day["umumiy_xarajat"] for day in kunlik_hisobot.values())

    # Tablitsa yaratish
    pdf.set_font("Arial", style="B", size=8)
    pdf.cell(200, 5, txt="Kunlik Hisobotlar:", ln=True)
    pdf.set_font("Arial", size=7)

    for sana, data in sorted(kunlik_hisobot.items()):
        # Sana
        pdf.set_font("Arial", style="B", size=7)
        pdf.cell(200, 5, txt=f"Sana: {sana}", ln=True)
        pdf.set_font("Arial", size=7)

        # Savdolar jadvali
        pdf.cell(60, 5, txt="Savdolar:", ln=True)
        pdf.cell(50, 5, txt="Mahsulot", border=1, align="C")
        pdf.cell(20, 5, txt="Soni", border=1, align="C")
        pdf.cell(30, 5, txt="Narxi (won)", border=1, align="C")
        pdf.ln()
        for savdo in data["savdolar"]:
            pdf.cell(50, 5, txt=savdo["mahsulot"], border=1)
            pdf.cell(20, 5, txt=str(savdo["soni"]), border=1, align="R")
            pdf.cell(30, 5, txt=f"{int(savdo['narxi'])} won", border=1, align="R")
            pdf.ln()

        # Umumiy savdolar
        pdf.cell(100, 5, txt="Kunlik umumiy savdo:", border=0, align="R")
        pdf.cell(30, 5, txt=f"{int(data['umumiy_savdo'])} won", border=1, align="R")
        pdf.ln(6)

        # Xarajatlar jadvali
        pdf.cell(60, 5, txt="Xarajatlar:", ln=True)
        pdf.cell(50, 5, txt="Mahsulot", border=1, align="C")
        pdf.cell(30, 5, txt="Narxi (won)", border=1, align="C")
        pdf.cell(40, 5, txt="Ism", border=1, align="C")
        pdf.ln()
        for xarajat in data["xarajatlar"]:
            pdf.cell(50, 5, txt=xarajat["mahsulot"], border=1)
            pdf.cell(30, 5, txt=f"{int(xarajat['narxi'])} won", border=1, align="R")
            pdf.cell(40, 5, txt=xarajat["foydalanuvchi"], border=1)
            pdf.ln()

        # Umumiy xarajatlar
        pdf.cell(100, 5, txt="Kunlik umumiy xarajat:", border=0, align="R")
        pdf.cell(30, 5, txt=f"{int(data['umumiy_xarajat'])} won", border=1, align="R")
        pdf.ln(10)

    # Umumiy oylik daromad va xarajat
    pdf.set_font("Arial", style="B", size=8)
    pdf.cell(100, 5, txt=f"Umumiy oylik daromad: {int(umumiy_daromad)} won", ln=True)
    pdf.cell(100, 5, txt=f"Umumiy oylik xarajat: {int(umumiy_xarajat)} won", ln=True)

    # Faylni saqlash
    pdf.output("oylik_hisobot.pdf")
    
async def yakuniy_savdo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):
        return
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Misol: /yakuniy_savdo [mahsulot_nomi] [soni] [narxi]")
        return
    mahsulot, soni, narxi = args
    savdo = {"mahsulot": mahsulot, "soni": int(soni), "narxi": int(narxi), "sana": datetime.now().strftime("%Y-%m-%d")}
    database["savdolar"].append(savdo)
    save_data()
    await update.message.reply_text(f"✅ Yakuniy savdo qo‘shildi: \n{mahsulot} - {soni} dona - {int(narxi)} won")

async def ombor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):
        return
    args = context.args
    if not database["ombor"]:
        await update.message.reply_text("Ombor bo‘sh!")
    else:
        javob = "Ombordagi mahsulotlar:\n"
        for mahsulot, soni in database["ombor"].items():
            javob += f"✅ {mahsulot}: {soni} dona\n"
        await update.message.reply_text(javob)

async def qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Misol: /qabul [mahsulot_nomi] [soni]")
        return
    mahsulot, soni = args
    database["ombor"][mahsulot] = database["ombor"].get(mahsulot, 0) + int(soni)
    save_data()
    await update.message.reply_text(f"✅ Omborga qabul qilindi: \n{mahsulot} - {soni} dona")

async def chiqarish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Misol: /chiqarish [mahsulot_nomi] [soni]")
        return
    mahsulot, soni = args
    if mahsulot not in database["ombor"] or database["ombor"][mahsulot] < int(soni):
        await update.message.reply_text("Omborda yetarli mahsulot yo‘q!")
    else:
        database["ombor"][mahsulot] -= int(soni)
        if database["ombor"][mahsulot] == 0:
            del database["ombor"][mahsulot]
        save_data()
        await update.message.reply_text(f"✅ Ombordan chiqarildi: \n{mahsulot} - {soni} dona")

async def xarajat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Misol: /xarajat [mahsulot_nomi] [narxi]")
        return
    mahsulot, narxi = args
    foydalanuvchi = update.message.from_user.username or "NoName"
    xarajat = {
        "mahsulot": mahsulot,
        "narxi": int(narxi),
        "foydalanuvchi": foydalanuvchi,
        "sana": datetime.now().strftime("%Y-%m-%d"),
    }
    database["xarajatlar"].append(xarajat)
    save_data()
    await update.message.reply_text(f"✅ Xarajat qo‘shildi: \n{mahsulot} - {int(narxi)} won 👤 {foydalanuvchi}")

async def kunlik_hisobot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):
        return

    bugun = datetime.now().strftime("%Y-%m-%d")
    savdolar = [savdo for savdo in database["savdolar"] if savdo["sana"] == bugun]
    xarajatlar = [xarajat for xarajat in database["xarajatlar"] if xarajat["sana"] == bugun]

    # Savdolarni birlashtirish
    guruhlangan_savdolar = {}
    for savdo in savdolar:
        mahsulot = savdo["mahsulot"]
        if mahsulot not in guruhlangan_savdolar:
            guruhlangan_savdolar[mahsulot] = {"soni": 0, "narxi": 0}
        guruhlangan_savdolar[mahsulot]["soni"] += savdo["soni"]
        guruhlangan_savdolar[mahsulot]["narxi"] += savdo["narxi"]

    # Xarajatlarni birlashtirish
    guruhlangan_xarajatlar = {}
    for xarajat in xarajatlar:
        mahsulot = xarajat["mahsulot"]
        if mahsulot not in guruhlangan_xarajatlar:
            guruhlangan_xarajatlar[mahsulot] = {"narxi": 0, "foydalanuvchilar": set()}
        guruhlangan_xarajatlar[mahsulot]["narxi"] += xarajat["narxi"]
        guruhlangan_xarajatlar[mahsulot]["foydalanuvchilar"].add(xarajat["foydalanuvchi"])

    # Umumiy daromad va xarajat
    umumiy_daromad = sum(item["narxi"] for item in guruhlangan_savdolar.values())
    umumiy_xarajat = sum(item["narxi"] for item in guruhlangan_xarajatlar.values())

    # Hisobotni yaratish
    savdo_hisobot = "\n".join(
        [f"{mahsulot} - {data['soni']} dona - {int(data['narxi'])} won" for mahsulot, data in guruhlangan_savdolar.items()]
    )
    xarajat_hisobot = "\n".join(
        [
            f"{mahsulot} - {int(data['narxi'])} won 👤 {', '.join(data['foydalanuvchilar'])}"
            for mahsulot, data in guruhlangan_xarajatlar.items()
        ]
    )

    hisobot = f"📆 Kunlik hisobot ({bugun}):\n\n"
    hisobot += "Savdolar:\n" + (savdo_hisobot or "Hech narsa sotilmagan.") + "\n\n"
    hisobot += "Xarajatlar:\n" + (xarajat_hisobot or "Hech qanday xarajat qilinmagan.") + "\n\n"
    hisobot += f"🟢 Umumiy daromad: {int(umumiy_daromad)} won\n"
    hisobot += f"🔴 Umumiy xarajat: {int(umumiy_xarajat)} won\n"

    await update.message.reply_text(hisobot)

async def oylik_hisobot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):
        return

    generate_monthly_report()
    
    try:
        with open("oylik_hisobot.pdf", "rb") as pdf_file:
            await update.message.reply_document(pdf_file, filename="Oylik_Hisobot.pdf")
    except Exception as e:
        await update.message.reply_text(f"PDF faylni yuborishda xatolik: {e}")

async def tozalash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await foydalanuvchini_tekshirish(update, context):
        return
    await update.message.reply_text("❗Ro‘yxatni tozalash uchun parolni qaytadan kiriting:")
    context.user_data["tozalash"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("tozalash"):
        if update.message.text == ADMIN_PASSWORD:
            database.clear()
            save_data()
            context.user_data["tozalash"] = False
            await update.message.reply_text("✅ Barcha ma'lumotlar o‘chirildi!")
        else:
            await update.message.reply_text("❌ Parol noto‘g‘ri!")
    else:
        await update.message.reply_text("Noma'lum buyruq!")

# Application setup
def main():
    load_data()
    app = ApplicationBuilder().token("8198692446:AAE062mioUGN8xHpycUandU0BvP6NOntXFI").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, parol_tekshirish))
    app.add_handler(CommandHandler("yakuniy_savdo", yakuniy_savdo))
    app.add_handler(CommandHandler("ombor", ombor))
    app.add_handler(CommandHandler("qabul", qabul))
    app.add_handler(CommandHandler("chiqarish", chiqarish))
    app.add_handler(CommandHandler("kunlik_hisobot", kunlik_hisobot))
    app.add_handler(CommandHandler("oylik_hisobot", oylik_hisobot))
    app.add_handler(CommandHandler("xarajat", xarajat))
    app.add_handler(CommandHandler("tozalash", tozalash))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("foydalanuvchilar", foydalanuvchilar))
    app.add_handler(CommandHandler("foydalanuvchilarni_tozalash", foydalanuvchilarni_tozalash))
    app.add_handler(CommandHandler("foydalanuvchini_ochirish", foydalanuvchini_ochirish))

    app.run_polling()

if __name__ == "__main__":
    main()
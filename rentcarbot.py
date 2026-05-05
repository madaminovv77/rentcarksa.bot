#!/usr/bin/env python3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes, filters

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

LANG, MENU, SELECT_TRIP_TYPE, SELECT_CAR, SELECT_DAYS, GET_NAME, GET_PHONE, GET_DATE, CONFIRM = range(9)
CARS = {
    "malibu_1": {"name": "Chevrolet Malibu 2023 (1)", "emoji": "🏎", "seats": 5, "transmission": "Automatic", "fuel": "Petrol", "city_price": 180, "outside_km_price": 2.5, "min_km": 100, "available": True},
    "malibu_2": {"name": "Chevrolet Malibu 2023 (2)", "emoji": "🏎", "seats": 5, "transmission": "Automatic", "fuel": "Petrol", "city_price": 180, "outside_km_price": 2.5, "min_km": 100, "available": True},
    "santa_fe": {"name": "Hyundai Santa Fe 2023", "emoji": "🚙", "seats": 7, "transmission": "Automatic", "fuel": "Petrol", "city_price": 220, "outside_km_price": 3.0, "min_km": 100, "available": True},
    "karnival_1": {"name": "Kia Carnival 2023 (1)", "emoji": "🚐", "seats": 8, "transmission": "Automatic", "fuel": "Petrol", "city_price": 260, "outside_km_price": 3.5, "min_km": 100, "available": True},
    "karnival_2": {"name": "Kia Carnival 2023 (2)", "emoji": "🚐", "seats": 8, "transmission": "Automatic", "fuel": "Petrol", "city_price": 260, "outside_km_price": 3.5, "min_km": 100, "available": True},
}
TEXTS = {
    "uz": {"welcome": "👋 Xush kelibsiz!\n\n🚗 *Saudi Rent Car*!", "menu_rent": "🚗 Mashina ijarasi", "menu_prices": "💰 Narxlar", "menu_contact": "📞 Boglanish", "menu_about": "ℹ️ Haqimizda", "choose_trip": "🗺 Qaysi yonalish?", "city": "🏙 Shahar ichida", "outside": "🛣 Shahar tashqarisi", "choose_car": "🚗 Mashinani tanlang:", "choose_days": "📅 Necha kun?", "enter_name": "👤 Ismingizni kiriting:", "enter_phone": "📱 Telefon:", "enter_date": "📅 Sana:", "confirm_title": "📋 *Buyurtma*", "car_label": "🚗 Mashina", "trip_label": "🗺 Yonalish", "days_label": "📅 Muddat", "price_label": "💰 Jami", "name_label": "👤 Ism", "phone_label": "📱 Tel", "date_label": "📆 Sana", "confirm_q": "Tasdiqlaysizmi?", "yes": "✅ Ha", "no": "❌ Yoq", "order_ok": "✅ *Qabul qilindi!* 🙏", "order_cancel": "❌ Bekor. /start", "back": "🔙 Orqaga", "days_suffix": " kun", "change_lang": "🌐 Til"},
    "ru": {"welcome": "👋 Добро пожаловать!\n\n🚗 *Saudi Rent Car*!", "menu_rent": "🚗 Аренда авто", "menu_prices": "💰 Цены", "menu_contact": "📞 Контакты", "menu_about": "ℹ️ О нас", "choose_trip": "🗺 Куда?", "city": "🏙 По городу", "outside": "🛣 За городом", "choose_car": "🚗 Выберите авто:", "choose_days": "📅 Сколько дней?", "enter_name": "👤 Ваше имя:", "enter_phone": "📱 Телефон:", "enter_date": "📅 Дата:", "confirm_title": "📋 *Заказ*", "car_label": "🚗 Авто", "trip_label": "🗺 Маршрут", "days_label": "📅 Срок", "price_label": "💰 Итого", "name_label": "👤 Имя", "phone_label": "📱 Тел", "date_label": "📆 Дата", "confirm_q": "Подтвердить?", "yes": "✅ Да", "no": "❌ Нет", "order_ok": "✅ *Принято!* 🙏", "order_cancel": "❌ Отменено. /start", "back": "🔙 Назад", "days_suffix": " дн.", "change_lang": "🌐 Язык"},
    "en": {"welcome": "👋 Welcome!\n\n🚗 *Saudi Rent Car*!", "menu_rent": "🚗 Rent a Car", "menu_prices": "💰 Prices", "menu_contact": "📞 Contact", "menu_about": "ℹ️ About", "choose_trip": "🗺 Where?", "city": "🏙 Within city", "outside": "🛣 Outside city", "choose_car": "🚗 Choose car:", "choose_days": "📅 How many days?", "enter_name": "👤 Your name:", "enter_phone": "📱 Phone:", "enter_date": "📅 Date:", "confirm_title": "📋 *Order*", "car_label": "🚗 Car", "trip_label": "🗺 Route", "days_label": "📅 Days", "price_label": "💰 Total", "name_label": "👤 Name", "phone_label": "📱 Phone", "date_label": "📆 Date", "confirm_q": "Confirm?", "yes": "✅ Yes", "no": "❌ No", "order_ok": "✅ *Received!* 🙏", "order_cancel": "❌ Cancelled. /start", "back": "🔙 Back", "days_suffix": " days", "change_lang": "🌐 Language"},
    "ar": {"welcome": "👋 مرحباً!\n\n🚗 *Saudi Rent Car*!", "menu_rent": "🚗 استئجار", "menu_prices": "💰 الأسعار", "menu_contact": "📞 اتصل", "menu_about": "ℹ️ من نحن", "choose_trip": "🗺 إلى أين؟", "city": "🏙 داخل المدينة", "outside": "🛣 خارج المدينة", "choose_car": "🚗 اختر:", "choose_days": "📅 كم يوماً؟", "enter_name": "👤 اسمك:", "enter_phone": "📱 هاتف:", "enter_date": "📅 تاريخ:", "confirm_title": "📋 *الطلب*", "car_label": "🚗 السيارة", "trip_label": "🗺 المسار", "days_label": "📅 المدة", "price_label": "💰 المجموع", "name_label": "👤 الاسم", "phone_label": "📱 هاتف", "date_label": "📆 التاريخ", "confirm_q": "تأكيد؟", "yes": "✅ نعم", "no": "❌ لا", "order_ok": "✅ *تم!* 🙏", "order_cancel": "❌ إلغاء. /start", "back": "🔙 رجوع", "days_suffix": " أيام", "change_lang": "🌐 اللغة"},
}

def t(lang, key):
    return TEXTS.get(lang, TEXTS["en"]).get(key, "")

def lang_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"), InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")], [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"), InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]])

def menu_keyboard(lang):
    return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"menu_rent"), callback_data="menu_rent")], [InlineKeyboardButton(t(lang,"menu_prices"), callback_data="menu_prices")], [InlineKeyboardButton(t(lang,"menu_contact"), callback_data="menu_contact")], [InlineKeyboardButton(t(lang,"menu_about"), callback_data="menu_about")], [InlineKeyboardButton(t(lang,"change_lang"), callback_data="change_lang")]])

def trip_type_keyboard(lang):
    return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"city"), callback_data="trip_city")], [InlineKeyboardButton(t(lang,"outside"), callback_data="trip_outside")], [InlineKeyboardButton(t(lang,"back"), callback_data="back_menu")]])

def cars_keyboard(lang, trip_type):
    rows = []
    for car_id, car in CARS.items():
        price_str = f"{car['city_price']} SAR/day" if trip_type=="city" else f"{car['outside_km_price']} SAR/km"
        cb = f"car_{car_id}" if car["available"] else "car_unavail"
        rows.append([InlineKeyboardButton(f"{'✅' if car['available'] else '❌'} {car['emoji']} {car['name']} | {price_str}", callback_data=cb)])
    rows.append([InlineKeyboardButton(t(lang,"back"), callback_data="back_trip")])
    return InlineKeyboardMarkup(rows)

def days_keyboard(lang, car_id):
    return InlineKeyboardMarkup([[InlineKeyboardButton("1", callback_data=f"days_1_{car_id}"), InlineKeyboardButton("2", callback_data=f"days_2_{car_id}"), InlineKeyboardButton("3", callback_data=f"days_3_{car_id}")], [InlineKeyboardButton("5", callback_data=f"days_5_{car_id}"), InlineKeyboardButton("7", callback_data=f"days_7_{car_id}"), InlineKeyboardButton("10", callback_data=f"days_10_{car_id}")], [InlineKeyboardButton("14", callback_data=f"days_14_{car_id}"), InlineKeyboardButton("30", callback_data=f"days_30_{car_id}")], [InlineKeyboardButton(t(lang,"back"), callback_data="back_cars")]])

def confirm_keyboard(lang):
    return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"yes"), callback_data="confirm_yes"), InlineKeyboardButton(t(lang,"no"), callback_data="confirm_no")]])
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    msg = update.message or update.callback_query.message
    await msg.reply_text("🌐 Choose language / Tilni tanlang / Выберите язык / اختر اللغة:", reply_markup=lang_keyboard())
    return LANG

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang
    await query.edit_message_text(t(lang,"welcome"), parse_mode="Markdown", reply_markup=menu_keyboard(lang))
    return MENU

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang","en")
    if query.data == "menu_rent":
        await query.edit_message_text(t(lang,"choose_trip"), reply_markup=trip_type_keyboard(lang))
        return SELECT_TRIP_TYPE
    elif query.data == "menu_prices":
        text = "💰 *Prices*\n\n🏙 *City (per day)*\n"
        for car in CARS.values():
            text += f"{car['emoji']} {car['name']}: {car['city_price']} SAR\n"
        text += "\n🛣 *Outside city (per km)*\n"
        for car in CARS.values():
            text += f"{car['emoji']} {car['name']}: {car['outside_km_price']} SAR/km\n"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"back"), callback_data="back_menu")]]))
        return MENU
    elif query.data == "menu_contact":
        await query.edit_message_text("📞 *Contact*\n\n📱 +966 50 123 4567\n📍 Riyadh, Saudi Arabia\n🕐 07:00-23:00\n📨 @saudirentcar", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"back"), callback_data="back_menu")]]))
        return MENU
    elif query.data == "menu_about":
        await query.edit_message_text("ℹ️ *Saudi Rent Car*\n\n✅ Modern fleet\n✅ 24/7 support\n✅ Insurance included\n✅ City & intercity", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"back"), callback_data="back_menu")]]))
        return MENU
    elif query.data == "back_menu":
        await query.edit_message_text(t(lang,"welcome"), parse_mode="Markdown", reply_markup=menu_keyboard(lang))
        return MENU
    elif query.data == "change_lang":
        await query.edit_message_text("🌐 Choose language:", reply_markup=lang_keyboard())
        return LANG
    return MENU
async def select_trip_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang","en")
    if query.data == "back_menu":
        await query.edit_message_text(t(lang,"welcome"), parse_mode="Markdown", reply_markup=menu_keyboard(lang))
        return MENU
    trip_type = query.data.replace("trip_","")
    context.user_data["trip_type"] = trip_type
    await query.edit_message_text(t(lang,"choose_car"), reply_markup=cars_keyboard(lang, trip_type))
    return SELECT_CAR

async def select_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang","en")
    trip_type = context.user_data.get("trip_type","city")
    if query.data == "car_unavail":
        await query.answer("❌ Not available", show_alert=True)
        return SELECT_CAR
    if query.data == "back_trip":
        await query.edit_message_text(t(lang,"choose_trip"), reply_markup=trip_type_keyboard(lang))
        return SELECT_TRIP_TYPE
    car_id = query.data.replace("car_","")
    car = CARS.get(car_id)
    if not car:
        return SELECT_CAR
    context.user_data["car_id"] = car_id
    if trip_type == "city":
        price_info = f"💰 {car['city_price']} SAR/day"
    else:
        price_info = f"💰 {car['outside_km_price']} SAR/km (min {car['min_km']} km)"
    text = f"{car['emoji']} *{car['name']}*\n\n💺 {car['seats']} seats\n⚙️ {car['transmission']} | ⛽ {car['fuel']}\n{price_info}\n\n{t(lang,'choose_days')}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=days_keyboard(lang, car_id))
    return SELECT_DAYS

async def select_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang","en")
    trip_type = context.user_data.get("trip_type","city")
    if query.data == "back_cars":
        await query.edit_message_text(t(lang,"choose_car"), reply_markup=cars_keyboard(lang, trip_type))
        return SELECT_CAR
    parts = query.data.split("_")
    days = int(parts[1])
    car_id = parts[2]
    car = CARS[car_id]
    context.user_data["days"] = days
    context.user_data["car_id"] = car_id
    if trip_type == "city":
        discount = 0.20 if days>=30 else 0.10 if days>=7 else 0
        total = car["city_price"] * days * (1-discount)
        context.user_data["price_display"] = f"{round(total,2)} SAR"
        context.user_data["discount"] = discount
    else:
        context.user_data["price_display"] = f"{car['outside_km_price']} SAR/km (min {car['min_km']} km)"
        context.user_data["discount"] = 0
    await query.edit_message_text(t(lang,"enter_name"))
    return GET_NAME
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang","en")
    context.user_data["name"] = update.message.text
    await update.message.reply_text(t(lang,"enter_phone"))
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang","en")
    context.user_data["phone"] = update.message.text
    await update.message.reply_text(t(lang,"enter_date"))
    return GET_DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang","en")
    context.user_data["date"] = update.message.text
    d = context.user_data
    car = CARS[d["car_id"]]
    trip_label = t(lang,"city") if d["trip_type"]=="city" else t(lang,"outside")
    discount_line = f"\n🎁 -{int(d['discount']*100)}%" if d.get("discount",0)>0 else ""
    summary = f"{t(lang,'confirm_title')}\n\n{t(lang,'car_label')}: {car['emoji']} {car['name']}\n{t(lang,'trip_label')}: {trip_label}\n{t(lang,'days_label')}: {d['days']}{t(lang,'days_suffix')}{discount_line}\n{t(lang,'price_label')}: {d['price_display']}\n{t(lang,'name_label')}: {d['name']}\n{t(lang,'phone_label')}: {d['phone']}\n{t(lang,'date_label')}: {d['date']}\n\n{t(lang,'confirm_q')}"
    await update.message.reply_text(summary, parse_mode="Markdown", reply_markup=confirm_keyboard(lang))
    return CONFIRM

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang","en")
    if query.data == "confirm_no":
        await query.edit_message_text(t(lang,"order_cancel"))
        return ConversationHandler.END
    d = context.user_data
    car = CARS[d["car_id"]]
    user = update.effective_user
    trip_en = "City" if d["trip_type"]=="city" else "Outside city"
    await query.edit_message_text(t(lang,"order_ok"), parse_mode="Markdown")
    admin_msg = f"🔔 *NEW ORDER*\n\n👤 [{user.first_name}](tg://user?id={user.id})\n🆔 `{user.id}`\n🌐 {lang.upper()}\n🚗 {car['emoji']} {car['name']}\n🗺 {trip_en}\n📅 {d['days']} days\n💰 {d['price_display']}\n👤 {d['name']}\n📱 {d['phone']}\n📆 {d['date']}"
    try:
        await query.get_bot().send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Admin error: {e}")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang","en")
    await update.message.reply_text(t(lang,"order_cancel"))
    context.user_data.clear()
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [CallbackQueryHandler(select_language, pattern="^lang_")],
            MENU: [CallbackQueryHandler(handle_menu)],
            SELECT_TRIP_TYPE: [CallbackQueryHandler(select_trip_type)],
            SELECT_CAR: [CallbackQueryHandler(select_car)],
            SELECT_DAYS: [CallbackQueryHandler(select_days)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            CONFIRM: [CallbackQueryHandler(confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
        allow_reentry=True,
    )
    app.add_handler(conv)
    print("🚗 Saudi Rent Car Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

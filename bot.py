# bot.py  (compatible with python-telegram-bot==20.5)
import os
import asyncio
import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes,
    CallbackQueryHandler, filters
)
import datetime

# ===== CONFIG (edit or set as env vars) =====
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8293803625:AAFk3eQuYQo7ru7EjmfYp6YSXpq9_5y0Pc0"
CHANNEL_USERNAME = os.getenv("CHANNEL_ID") or "@betting_Bot_somalia"
PROMO_CODE = "ABAANA777"

# ADMIN: username only (no @). You provided link https://t.me/affiliate_sub_Id
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME") or "affiliate_sub_Id"

# Payment numbers (example)
PAYMENT_METHODS = {
    "EVC": "615823680",
    "Waafi": "615823680",
    "eDahab": "625823680",
    "Premier": "615823680"
}

# For tips
TEAMS = ["Team A", "Team B", "Team C", "Team D", "Team E"]
ICONS = ["⚽", "🔥", "💰", "🏆", "🎯"]

DB_FILE = "data.db"

# ===== Database helpers =====
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vip_users (
            username TEXT PRIMARY KEY,
            added_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            chat_id INTEGER,
            message_id INTEGER,
            text TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_vip(username):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO vip_users (username, added_at) VALUES (?, datetime('now'))", (username,))
    conn.commit()
    conn.close()

def is_vip(username):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM vip_users WHERE username = ?", (username,))
    r = cur.fetchone()
    conn.close()
    return bool(r)

def add_pending(user_id, username, chat_id, message_id, text):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pending (user_id, username, chat_id, message_id, text, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
        (user_id, username, chat_id, message_id, text)
    )
    pid = cur.lastrowid
    conn.commit()
    conn.close()
    return pid

def get_pending(pending_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, username, chat_id, message_id, text FROM pending WHERE id = ?", (pending_id,))
    r = cur.fetchone()
    conn.close()
    return r

def delete_pending(pending_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM pending WHERE id = ?", (pending_id,))
    conn.commit()
    conn.close()

# ===== Helpers UI =====
def make_approve_keyboard(pending_id):
    buttons = [
        InlineKeyboardButton("✅ Ogolaasho", callback_data=f"approve:{pending_id}"),
        InlineKeyboardButton("❌ Diid", callback_data=f"reject:{pending_id}")
    ]
    return InlineKeyboardMarkup([buttons])

def check_payment_text(content: str) -> bool:
    """Heuristic: if content contains a known payment number AND '10' or 'abdulkadir' -> accept."""
    if not content:
        return False
    txt = content.lower()
    for num in PAYMENT_METHODS.values():
        if num in txt:
            if "10" in txt or "abdulkadir" in txt or "$10" in txt or "10$" in txt:
                return True
            # accept if name present
            if "abdulkadir" in txt:
                return True
    return False

# ===== Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 🤖\nKu soo dhawoow bot-ka. /vip si aad u aragto sida loo bixiyo VIP ($10)."
    )

async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = []
    for name in PAYMENT_METHODS.keys():
        kb.append([InlineKeyboardButton(name, callback_data=f"paybtn:{name}")])
    markup = InlineKeyboardMarkup(kb)
    await update.message.reply_text(
        "Dooro habka payment ka:",
        reply_markup=markup
    )

# when user clicks payment method button -> show instructions (DM or in chat)
async def payment_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data  # paybtn:EVC
    method = data.split(":",1)[1]
    number = PAYMENT_METHODS.get(method, "N/A")
    msg = (
        f"Habka: {method}\nNumber: {number}\n\n"
        "Talaabooyinka:\n"
        "1) Ku wareeji $10 lambarkan.\n"
        "2) Kadib soo dir halkan screenshot ama qoraal (caption) muujinaya number iyo magacaaga.\n"
        "Magaca bixiyaha: Abdulkadir mohamed mohamud\n\n"
        f"Haddii aad su'aal qabto la xiriir admin: @{ADMIN_USERNAME}"
    )
    await q.message.reply_text(msg)

# handle any text or photo as payment proof
async def payment_proof_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = msg.from_user
    username = (user.username or user.first_name).replace("@","")
    text = ""
    if msg.text:
        text = msg.text
    if msg.caption:
        text = (text + " " + msg.caption) if text else msg.caption

    # Try automatic heuristic
    if check_payment_text(text.lower()):
        add_vip(username)
        await msg.reply_text(f"✅ @{username}, waxaad si otomaatig ah u noqotay VIP. Waad ku mahadsan tahay bixinta $10.")
        # notify admin
        try:
            admin_chat = ("@" + ADMIN_USERNAME) if not ADMIN_USERNAME.startswith("@") else ADMIN_USERNAME
            await context.bot.send_message(chat_id=admin_chat, text=f"Auto-approved VIP: @{username}\nSample: {text[:300]}")
        except Exception:
            pass
        return

    # Not auto -> create pending and forward to admin with approve/reject buttons
    pending_id = add_pending(user.id, username, msg.chat.id, msg.message_id, (text or "")[:1000])
    admin_chat = ("@" + ADMIN_USERNAME) if not ADMIN_USERNAME.startswith("@") else ADMIN_USERNAME

    # Forward original message (if possible) so admin sees image/text
    try:
        await context.bot.forward_message(chat_id=admin_chat, from_chat_id=msg.chat.id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=admin_chat,
                                       text=f"Manual verification needed for @{username}. Pending ID: {pending_id}",
                                       reply_markup=make_approve_keyboard(pending_id))
    except Exception:
        # fallback: send text + approve buttons
        await context.bot.send_message(chat_id=admin_chat,
                                       text=f"Manual verification needed for @{username}.\nMessage: {text[:500]}\nPending ID: {pending_id}",
                                       reply_markup=make_approve_keyboard(pending_id))

    await msg.reply_text("Cadeyntaada waan helnay. Admin ayaa baar doona oo kuu soo sheegi doona.")

# admin clicks approve/reject
async def approve_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    caller = (query.from_user.username or "").replace("@","")
    if caller.lower() != ADMIN_USERNAME.lower():
        await query.edit_message_text("❌ Kaliya admin ayaa ogolaan kara baddhankan.")
        return

    data = query.data  # "approve:123" or "reject:123"
    try:
        action, pid_str = data.split(":",1)
        pid = int(pid_str)
    except Exception:
        await query.edit_message_text("❌ Data invalid.")
        return

    pending = get_pending(pid)
    if not pending:
        await query.edit_message_text("❌ Pending request lama helin (ama hore loo shaqeeyey).")
        return

    _, user_id, username, chat_id, message_id, text = pending
    username = username.replace("@","")

    if action == "approve":
        add_vip(username)
        delete_pending(pid)
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"🎉 @{username}, admin ayaa ku xaqiijiyey — waxaad hadda tahay VIP! ✅")
        except Exception:
            pass
        await query.edit_message_text(f"✅ @{username} waa laga ogolaaday VIP by @{caller}.")
        # notify admin (confirmation)
        try:
            admin_chat = ("@" + ADMIN_USERNAME) if not ADMIN_USERNAME.startswith("@") else ADMIN_USERNAME
            if admin_chat != ("@" + caller):
                await context.bot.send_message(chat_id=admin_chat, text=f"Admin @{caller} ayaa @{username} VIP ka dhigay.")
        except Exception:
            pass
    else:  # reject
        delete_pending(pid)
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ @{username}, cadeyntaada lama aqbalin. Fadlan isku day mar kale ama la xiriir admin.")
        except Exception:
            pass
        await query.edit_message_text(f"❌ @{username} waa la diiday (by @{caller}).")

# admin manual add
async def addvip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    actor = update.message.from_user.username or ""
    if actor.lower() != ADMIN_USERNAME.lower():
        await update.message.reply_text("❌ Kaliya admin ayaa isticmaali kara.")
        return
    if not context.args:
        await update.message.reply_text("Isticmaal: /addvip username")
        return
    new_v = context.args[0].replace("@","")
    add_vip(new_v)
    await update.message.reply_text(f"✅ @{new_v} waa lagu daray VIP (manual).")

# VIP check and viptips
async def myvip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = (update.message.from_user.username or update.message.from_user.first_name).replace("@","")
    if is_vip(username):
        await update.message.reply_text("🎉 Waxaad tahay VIP! Ku qor /viptips si aad u hesho 10 VIP tips.")
    else:
        await update.message.reply_text("Ma tihid VIP. Haddii aad rabto qor /vip si aad u aragto payment options.")

async def viptips_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = (update.message.from_user.username or "").replace("@","")
    if not is_vip(username):
        await update.message.reply_text("❌ Ma tihid VIP.")
        return
    tips = []
    for i in range(10):
        tips.append(f"{random.choice(ICONS)} VIP Tip {i+1}: {random.choice(TEAMS)} @ {round(random.uniform(1.5,3.5),2)}")
    await update.message.reply_text("\n".join(tips) + f"\n\n💡 Promo: {PROMO_CODE}")

# ===== Scheduler (simple channel posts) =====
async def scheduler(app):
    while True:
        now = datetime.datetime.now()
        hour, minute = now.hour, now.minute
        if (hour, minute) in [(9, 0), (15, 0), (21, 0)]:
            tips = []
            for i in range(7):
                tips.append(f"{random.choice(ICONS)} Tip {i+1}: {random.choice(TEAMS)} @ {round(random.uniform(1.5,3.5),2)}")
            await app.bot.send_message(chat_id=CHANNEL_USERNAME, text="🔥 Free Tips\n\n" + "\n".join(tips) + f"\n\nPromo: {PROMO_CODE}")
            await asyncio.sleep(60)
        if hour == 23 and minute == 59:
            await app.bot.send_message(chat_id=CHANNEL_USERNAME, text="🏆 Maanta natiijooyinka ayaa la soo gudbin doonaa (demo).")
            await asyncio.sleep(60)
        await asyncio.sleep(30)

# ===== Main =====
async def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vip", vip_command))
    app.add_handler(CommandHandler("myvip", myvip_cmd))
    app.add_handler(CommandHandler("viptips", viptips_cmd))
    app.add_handler(CommandHandler("addvip", addvip_cmd))
    app.add_handler(CallbackQueryHandler(approve_reject_callback, pattern=r"^(approve|reject):"))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT | filters.CAPTION, payment_proof_handler))

    asyncio.create_task(scheduler(app))

    print("✅ Bot-ka waa online!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

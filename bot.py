import os
import html
import random
import string
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("tempmail-bot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@bkcd_gc")
CHANNEL_URL = os.environ.get("CHANNEL_URL", "https://t.me/bkcd_gc")
DEVELOPER = "𝑫 𝑨 𝑹 𝑲 𝑵 𝑬 𝑿 𝑨"
API = "https://api.mail.tm"

# user_id -> {"address":..., "password":..., "token":...}
SESSIONS: dict[int, dict] = {}


# ---------- tiny web server so Render Web Service stays alive ----------
class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, *args):
        pass


def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Health).serve_forever()


# ---------- helpers ----------
def rand(n=10):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


async def is_joined(bot, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ("member", "administrator", "creator")
    except Exception as e:
        log.warning("join check failed: %s", e)
        return False


def join_markup():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📢 Channel Join Karo", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ Joined, Verify", callback_data="verify")],
        ]
    )


def menu_markup():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📧 New Email", callback_data="new")],
            [
                InlineKeyboardButton("📥 Inbox", callback_data="inbox"),
                InlineKeyboardButton("🗑 Delete", callback_data="delete"),
            ],
        ]
    )


async def gate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if await is_joined(context.bot, user.id):
        return True
    text = (
        "⚠️ <b>Bot use karne ke liye pehle channel join karna padega.</b>\n\n"
        f"Join karo: {CHANNEL_URL}\nPhir <b>Verify</b> dabao."
    )
    if update.callback_query:
        await update.callback_query.message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=join_markup()
        )
    else:
        await update.effective_message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=join_markup()
        )
    return False


async def create_account() -> dict:
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(f"{API}/domains")
        r.raise_for_status()
        domain = r.json()["hydra:member"][0]["domain"]
        address = f"{rand(10)}@{domain}"
        password = rand(14)
        r = await c.post(f"{API}/accounts", json={"address": address, "password": password})
        r.raise_for_status()
        r = await c.post(f"{API}/token", json={"address": address, "password": password})
        r.raise_for_status()
        return {"address": address, "password": password, "token": r.json()["token"]}


async def api_get(session: dict, path: str):
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(f"{API}{path}", headers={"Authorization": f"Bearer {session['token']}"})
        r.raise_for_status()
        return r.json()


# ---------- handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await gate(update, context):
        return
    name = html.escape(update.effective_user.first_name or "User")
    await update.message.reply_text(
        f"👋 Hello <b>{name}</b>!\n\n"
        "Main ek <b>Temp Mail Maker Bot</b> hoon. Ek click me temporary email "
        "banao aur OTP / verification mail yahin receive karo.\n\n"
        f"👨‍💻 Developer: <b>{DEVELOPER}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=menu_markup(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    if data == "verify":
        if await is_joined(context.bot, uid):
            await q.message.reply_text(
                "✅ Verified! Ab bot use kar sakte ho.", reply_markup=menu_markup()
            )
        else:
            await q.message.reply_text(
                "❌ Aapne abhi channel join nahi kiya.", reply_markup=join_markup()
            )
        return

    if not await gate(update, context):
        return

    if data == "new":
        try:
            SESSIONS[uid] = await create_account()
        except Exception as e:
            log.error("create failed: %s", e)
            await q.message.reply_text("⚠️ Email banane me error aaya, thodi der baad try karo.")
            return
        await q.message.reply_text(
            f"✅ <b>Aapka Temp Email:</b>\n<code>{SESSIONS[uid]['address']}</code>\n\n"
            "Isko kisi site par use karo, phir 📥 Inbox dabao.",
            parse_mode=ParseMode.HTML,
            reply_markup=menu_markup(),
        )

    elif data == "inbox":
        s = SESSIONS.get(uid)
        if not s:
            await q.message.reply_text("Pehle 📧 New Email banao.", reply_markup=menu_markup())
            return
        try:
            msgs = (await api_get(s, "/messages"))["hydra:member"]
        except Exception as e:
            log.error("inbox failed: %s", e)
            await q.message.reply_text("⚠️ Inbox load nahi hua, dobara try karo.")
            return
        if not msgs:
            await q.message.reply_text(
                f"📭 Inbox khali hai.\n<code>{s['address']}</code>",
                parse_mode=ParseMode.HTML,
                reply_markup=menu_markup(),
            )
            return
        rows = []
        for m in msgs[:10]:
            sender = m["from"].get("address", "?")
            subj = (m.get("subject") or "(no subject)")[:35]
            rows.append([InlineKeyboardButton(f"{sender[:18]} | {subj}", callback_data=f"read:{m['id']}")])
        rows.append([InlineKeyboardButton("🔄 Refresh", callback_data="inbox")])
        await q.message.reply_text(
            f"📥 <b>Inbox</b> ({len(msgs)})\n<code>{s['address']}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(rows),
        )

    elif data.startswith("read:"):
        s = SESSIONS.get(uid)
        if not s:
            return
        try:
            m = await api_get(s, f"/messages/{data[5:]}")
        except Exception:
            await q.message.reply_text("⚠️ Mail open nahi hua.")
            return
        body = html.escape((m.get("text") or m.get("intro") or "(empty)")[:3500])
        await q.message.reply_text(
            f"📨 <b>From:</b> {html.escape(m['from'].get('address', '?'))}\n"
            f"<b>Subject:</b> {html.escape(m.get('subject') or '')}\n\n{body}",
            parse_mode=ParseMode.HTML,
            reply_markup=menu_markup(),
        )

    elif data == "delete":
        SESSIONS.pop(uid, None)
        await q.message.reply_text("🗑 Email delete ho gaya.", reply_markup=menu_markup())


def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    log.info("Bot started | Developer: %s", DEVELOPER)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
  

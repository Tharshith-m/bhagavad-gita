
import os
import random
import logging
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from . import database, models
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()  

# === Config ===

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
user_id_str = os.getenv("TELEGRAM_USER_ID")
if not user_id_str:
    raise ValueError("❌ TELEGRAM_USER_ID is missing in .env file")
USER_ID = int(user_id_str)
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# === DB helper ===
def get_random_slokam():
    db: Session = database.SessionLocal()
    count = db.query(models.Slokam).count()
    if count == 0:
        return "No slokams found in DB."
    offset = random.randint(0, count - 1)
    slokam = db.query(models.Slokam).offset(offset).first()
    return (
        f"📖 Chapter {slokam.chapter}, Verse {slokam.verse}\n\n"
        f"{slokam.verse_text}\n\n"
        f"🌍 {slokam.translation}\n\n"
        f"🪔 {slokam.bhavam}"
    )


# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌸 Hare Krishna! You will now receive daily Bhagavad Gita slokams."
    )


async def send_daily_slokam(context: ContextTypes.DEFAULT_TYPE):
    """JobQueue callback to send slokam"""
    slokam_text = get_random_slokam()
    await context.bot.send_message(chat_id=USER_ID, text=slokam_text)


# === Main ===
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))

    # Use JobQueue (no APScheduler needed)
    job_queue = application.job_queue

    if TEST_MODE:
        job_queue.run_repeating(send_daily_slokam, interval=60, first=5)
        logger.info("✅ TEST MODE: sending slokam every 60s")
    else:
        job_queue.run_daily(send_daily_slokam, time=time(hour=10, minute=0))
        logger.info("📅 PROD MODE: sending slokam daily at 10:00")

    # Start bot
    application.run_polling()


if __name__ == "__main__":
    main()

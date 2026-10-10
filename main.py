from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import (
    BOT_TOKEN,
    ROCKET,
    URL_CRYPTO,
    URL_CURRENCY,
    about_message,
    build_currency_message,
    build_crypto_message,
    build_single_asset_message,
    fetch_html,
    fetch_single_asset,
    find_slug,
    help_message,
    parse_currencies,
    parse_cryptos,
    welcome_message,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

LOADING_CURRENCY = (
    f"{ROCKET} *در حال دریافت نرخ‌های لحظه‌ای...*\n\n"
    "`▰▰▰▱▱▱▱▱▱▱` 30%\n"
    "`▰▰▰▰▰▰▱▱▱▱` 60%\n"
    "`▰▰▰▰▰▰▰▰▰▰` 100%"
)

LOADING_CRYPTO = (
    f"{ROCKET} *در حال دریافت ارزهای دیجیتال...*\n\n"
    "`▰▰▰▱▱▱▱▱▱▱` 30%\n"
    "`▰▰▰▰▰▰▱▱▱▱` 60%\n"
    "`▰▰▰▰▰▰▰▰▰▰` 100%"
)

LOADING_SINGLE = f"{ROCKET} *در حال دریافت قیمت...*\n\n`▰▰▰▰▰▱▱▱▱▱`"


async def _safe_delete(message) -> None:
    try:
        await message.delete()
    except Exception:
        pass


async def _safe_edit(message, text: str) -> None:
    try:
        await message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.warning("Edit failed: %s", e)


async def _safe_send(bot, chat_id: int, text: str) -> None:
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.warning("Send failed: %s", e)


async def send_currency_list(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    wait_msg = await context.bot.send_message(
        chat_id=chat_id, text=LOADING_CURRENCY, parse_mode=ParseMode.MARKDOWN
    )
    try:
        html = await fetch_html(URL_CURRENCY)
        data = parse_currencies(html)
    except Exception as e:
        await _safe_edit(wait_msg, f"❌ Error: `{e}`")
        return
    if not data:
        await _safe_edit(wait_msg, "❌ No data received.")
        return
    text = build_currency_message(data)
    await _safe_edit(wait_msg, text)


async def send_crypto_list(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    wait_msg = await context.bot.send_message(
        chat_id=chat_id, text=LOADING_CRYPTO, parse_mode=ParseMode.MARKDOWN
    )
    try:
        html = await fetch_html(URL_CRYPTO)
        data = parse_cryptos(html)
    except Exception as e:
        await _safe_edit(wait_msg, f"❌ Error: `{e}`")
        return
    if not data:
        await _safe_edit(wait_msg, "❌ No data received.")
        return
    text = build_crypto_message(data)
    await _safe_edit(wait_msg, text)


async def send_single_asset(
    chat_id: int, slug: str, context: ContextTypes.DEFAULT_TYPE
) -> None:
    wait_msg = await context.bot.send_message(
        chat_id=chat_id, text=LOADING_SINGLE, parse_mode=ParseMode.MARKDOWN
    )
    result = await fetch_single_asset(slug)
    if not result or "error" in result:
        err = result.get("error", "unknown") if result else "unknown"
        await _safe_edit(wait_msg, f"❌ Error: `{err}`")
        return
    await _safe_edit(wait_msg, build_single_asset_message(result))


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    first_name = (user.first_name if user else None) or "دوست عزیز"

    keyboard = [
        [
            InlineKeyboardButton("💱  لیست ارزها", callback_data="list_currency"),
            InlineKeyboardButton("🪙  لیست کریپتو", callback_data="list_crypto"),
        ],
        [
            InlineKeyboardButton("🇺🇸  دلار", callback_data="single_price_dollar_rl"),
            InlineKeyboardButton("🇪🇺  یورو", callback_data="single_price_eur"),
        ],
        [
            InlineKeyboardButton("₿  بیت کوین", callback_data="single_crypto-bitcoin"),
            InlineKeyboardButton("⚡  ترون", callback_data="single_crypto-tron"),
        ],
        [
            InlineKeyboardButton("❓  راهنما", callback_data="help"),
            InlineKeyboardButton("👑  درباره", callback_data="about"),
        ],
    ]

    await update.message.reply_text(
        welcome_message(first_name),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(help_message(), parse_mode=ParseMode.MARKDOWN)


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_currency_list(update.effective_chat.id, context)


async def cmd_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_crypto_list(update.effective_chat.id, context)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data == "list_currency":
        await send_currency_list(chat_id, context)
    elif data == "list_crypto":
        await send_crypto_list(chat_id, context)
    elif data == "help":
        await _safe_send(context.bot, chat_id, help_message())
    elif data == "about":
        await _safe_send(context.bot, chat_id, about_message())
    elif data.startswith("single_"):
        await send_single_asset(chat_id, data.replace("single_", ""), context)


CURRENCY_KEYWORDS = ("لیست ارز", "لیست قیمت ارز", "currency", "ارزها", "نرخ ارز")
CRYPTO_KEYWORDS = ("لیست کریپتو", "لیست ارز دیجیتال", "crypto", "کریپتو", "رمزارز", "ارز دیجیتال")
HELP_KEYWORDS = ("راهنما", "help", "کمک")
ABOUT_KEYWORDS = ("درباره", "about")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    t = update.message.text.strip()
    tl = t.lower()
    chat_id = update.effective_chat.id

    if any(k in tl for k in CURRENCY_KEYWORDS):
        await send_currency_list(chat_id, context)
        return
    if any(k in tl for k in CRYPTO_KEYWORDS):
        await send_crypto_list(chat_id, context)
        return
    if any(k in tl for k in HELP_KEYWORDS):
        await _safe_send(context.bot, chat_id, help_message())
        return
    if any(k in tl for k in ABOUT_KEYWORDS):
        await _safe_send(context.bot, chat_id, about_message())
        return
    if "لیست" in tl:
        await send_currency_list(chat_id, context)
        return

    slug = find_slug(tl)
    if slug:
        await send_single_asset(chat_id, slug, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception:", exc_info=context.error)


def main() -> None:
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .build()
    )
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("crypto", cmd_crypto))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)
    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()

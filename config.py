from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "25"))
MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "3800"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")

URL_CURRENCY = "https://www.tgju.org/currency"
URL_CRYPTO = "https://www.tgju.org/crypto"
URL_PROFILE = "https://www.tgju.org/profile/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 15; Pixel 9) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
}

DIVIDER_THICK = "▬" * 26
DIVIDER_THIN = "━" * 26
DIVIDER_DOT = "· " * 16
DIVIDER_STAR = "✦ " * 16

DIAMOND = "◆"
SPARKLE = "✨"
FIRE = "🔥"
CROWN = "👑"
ROCKET = "🚀"
STAR = "⭐"
LIGHTNING = "⚡"
GEM = "💎"
HEART = "💖"
WAVE = "👋"
SMILE = "😊"
BOW = "🙇"
CHART_UP = "📈"
CHART_DOWN = "📉"
CHART_FLAT = "➖"
MONEY = "💰"
BANK = "🏦"
GLOBE = "🌐"
CLOCK = "🕐"
LINK = "🔗"
SEARCH = "🔍"
CHECK = "✅"
CROSS = "❌"
WARNING = "⚠️"

CURRENCY_ICONS = {
    "دلار": "🇺🇸", "یورو": "🇪🇺", "پوند انگلیس": "🇬🇧",
    "درهم امارات": "🇦🇪", "لیر ترکیه": "🇹🇷", "فرانک سوئیس": "🇨🇭",
    "یوان چین": "🇨🇳", "ین ژاپن": "🇯🇵", "وون کره جنوبی": "🇰🇷",
    "دلار کانادا": "🇨🇦", "دلار استرالیا": "🇦🇺", "دلار نیوزیلند": "🇳🇿",
    "دلار سنگاپور": "🇸🇬", "روپیه هند": "🇮🇳", "روپیه پاکستان": "🇵🇰",
    "دینار عراق": "🇮🇶", "پوند سوریه": "🇸🇾", "افغانی": "🇦🇫",
    "کرون دانمارک": "🇩🇰", "کرون سوئد": "🇸🇪", "کرون نروژ": "🇳🇴",
    "ریال عربستان": "🇸🇦", "ریال قطر": "🇶🇦", "ریال عمان": "🇴🇲",
    "دینار کویت": "🇰🇼", "دینار بحرین": "🇧🇭", "رینگیت مالزی": "🇲🇾",
    "بات تایلند": "🇹🇭", "دلار هنگ کنگ": "🇭🇰", "روبل روسیه": "🇷🇺",
    "منات آذربایجان": "🇦🇿", "درام ارمنستان": "🇦🇲", "لاری گرجستان": "🇬🇪",
    "سوم قرقیزستان": "🇰🇬", "سامانی تاجیکستان": "🇹🇯", "منات ترکمنستان": "🇹🇲",
}

CRYPTO_ICONS = {
    "بیت کوین": "₿", "اتریوم": "Ξ", "تتر": "💵", "ریپل": "💧",
    "بایننس کوین": "🟡", "سولانا": "◎", "کاردانو": "🔵", "دوج کوین": "🐕",
    "شیبا اینو": "🐶", "لایت کوین": "Ł", "مونرو": "🔒", "پولکا دات": "⚪",
    "آوالانچ": "🔺", "چین لینک": "🔗", "یونی سواپ": "🦄", "استلار": "⭐",
    "ترون": "⚡", "پپه": "🐸", "تتر گلد": "🥇", "پکس گلد": "🥇",
    "بیت کوین کش": "💚", "اتریوم کلاسیک": "💠", "دش": "🔷", "زیکش": "🛡",
    "نئو": "🟢", "کازماز": "⚛", "فایل کوین": "📁", "الروند": "🔶",
    "سندباکس": "🏖", "تزوس": "🌐", "فانتوم": "👻", "گالا": "🎮",
    "پنکیک سواپ": "🥞", "ایاس": "⚡", "فلو": "🌊", "لوپرینگ": "🔁",
    "بیت تورنت": "🌀", "ماکر": "🏛", "ویوز": "🌊", "دیکرید": "🔐",
    "کوانت": "🎯", "هدرا": "🎩", "سویی": "💧", "آپتوس": "🅰",
    "اینترنت کامپیوتر": "🌍", "نير پروتکل": "🔵", "تون کوین": "💎",
    "رندر": "🎨", "تائو": "🧠", "آربیتروم": "🔷", "اوپتیمیزم": "🔴",
    "کوانتوم": "⚡", "استیم": "💠", "تراست ولت": "🛡", "سیاکوین": "💾",
    "کومپاند": "🏦", "اسنیکس": "⚙", "کرونوس": "🦁", "میم کور": "😂",
    "اتنا": "🌿", "میدنایت": "🌙", "لایتر": "🔥",
}

ASSET_ALIASES = {
    "دلار": "price_dollar_rl", "dollar": "price_dollar_rl", "usd": "price_dollar_rl",
    "یورو": "price_eur", "euro": "price_eur", "eur": "price_eur",
    "پوند": "price_gbp", "pound": "price_gbp", "gbp": "price_gbp",
    "درهم": "price_aed", "aed": "price_aed",
    "لیر": "price_try", "try": "price_try",
    "یوان": "price_cny", "cny": "price_cny",
    "ین": "price_jpy", "jpy": "price_jpy",
    "روبل": "price_rub", "rub": "price_rub",
    "دینار عراق": "price_iqd", "iqd": "price_iqd",
    "افغانی": "price_afn", "afn": "price_afn",
    "ریال عربستان": "price_sar", "sar": "price_sar",
    "ریال قطر": "price_qar", "qar": "price_qar",
    "دینار کویت": "price_kwd", "kwd": "price_kwd",
    "کرون سوئد": "price_sek", "sek": "price_sek",
    "کرون نروژ": "price_nok", "nok": "price_nok",
    "دلار کانادا": "price_cad", "cad": "price_cad",
    "دلار استرالیا": "price_aud", "aud": "price_aud",
    "ترون": "crypto-tron", "tron": "crypto-tron", "trx": "crypto-tron",
    "بیت کوین": "crypto-bitcoin", "bitcoin": "crypto-bitcoin", "btc": "crypto-bitcoin",
    "اتریوم": "crypto-ethereum", "ethereum": "crypto-ethereum", "eth": "crypto-ethereum",
    "تتر": "crypto-tether", "tether": "crypto-tether", "usdt": "crypto-tether",
    "ریپل": "crypto-ripple", "ripple": "crypto-ripple", "xrp": "crypto-ripple",
    "بایننس": "crypto-bnb", "bnb": "crypto-bnb",
    "سولانا": "crypto-solana", "solana": "crypto-solana", "sol": "crypto-solana",
    "کاردانو": "crypto-cardano", "cardano": "crypto-cardano", "ada": "crypto-cardano",
    "دوج": "crypto-dogecoin", "dogecoin": "crypto-dogecoin", "doge": "crypto-dogecoin",
    "شیبا": "crypto-shiba-inu", "shiba": "crypto-shiba-inu", "shib": "crypto-shiba-inu",
    "لایت کوین": "crypto-litecoin", "litecoin": "crypto-litecoin", "ltc": "crypto-litecoin",
    "مونرو": "crypto-monero", "monero": "crypto-monero", "xmr": "crypto-monero",
    "پولکادات": "crypto-polkadot-new", "polkadot": "crypto-polkadot-new", "dot": "crypto-polkadot-new",
    "آوالانچ": "crypto-avalanche", "avalanche": "crypto-avalanche", "avax": "crypto-avalanche",
    "چین لینک": "crypto-chainlink", "chainlink": "crypto-chainlink", "link": "crypto-chainlink",
    "یونی سواپ": "crypto-uniswap", "uniswap": "crypto-uniswap", "uni": "crypto-uniswap",
    "استلار": "crypto-stellar", "stellar": "crypto-stellar", "xlm": "crypto-stellar",
    "پپه": "crypto-pepe", "pepe": "crypto-pepe",
    "بیت کوین کش": "crypto-bitcoin-cash", "bch": "crypto-bitcoin-cash",
    "اتریوم کلاسیک": "crypto-ethereum-classic", "etc": "crypto-ethereum-classic",
    "دش": "crypto-dash", "dash": "crypto-dash",
    "زیکش": "crypto-zcash", "zcash": "crypto-zcash", "zec": "crypto-zcash",
    "نئو": "crypto-neo", "neo": "crypto-neo",
    "کازماز": "crypto-cosmos", "cosmos": "crypto-cosmos", "atom": "crypto-cosmos",
    "فایل کوین": "crypto-filecoin", "filecoin": "crypto-filecoin", "fil": "crypto-filecoin",
    "الروند": "crypto-elrond", "elrond": "crypto-elrond", "egld": "crypto-elrond",
    "سندباکس": "crypto-the-sandbox", "sandbox": "crypto-the-sandbox", "sand": "crypto-the-sandbox",
    "تزوس": "crypto-tezos", "tezos": "crypto-tezos", "xtz": "crypto-tezos",
    "فانتوم": "crypto-fantom", "fantom": "crypto-fantom", "ftm": "crypto-fantom",
    "گالا": "crypto-gala", "gala": "crypto-gala",
    "پنکیک": "crypto-pancakeswap", "pancakeswap": "crypto-pancakeswap", "cake": "crypto-pancakeswap",
    "ایاس": "crypto-eos", "eos": "crypto-eos",
    "فلو": "crypto-flow", "flow": "crypto-flow",
    "لوپرینگ": "crypto-loopring", "loopring": "crypto-loopring", "lrc": "crypto-loopring",
    "بیت تورنت": "crypto-bittorrent", "bittorrent": "crypto-bittorrent", "btt": "crypto-bittorrent",
    "ماکر": "crypto-maker", "maker": "crypto-maker", "mkr": "crypto-maker",
    "ویوز": "crypto-waves", "waves": "crypto-waves",
    "دیکرید": "crypto-decred", "decred": "crypto-decred", "dcr": "crypto-decred",
    "کوانت": "crypto-quant", "quant": "crypto-quant", "qnt": "crypto-quant",
    "هدرا": "crypto-hedera", "hedera": "crypto-hedera", "hbar": "crypto-hedera",
    "سویی": "crypto-sui", "sui": "crypto-sui",
    "آپتوس": "crypto-aptos", "aptos": "crypto-aptos", "apt": "crypto-aptos",
    "اینترنت کامپیوتر": "crypto-internet-computer", "icp": "crypto-internet-computer",
    "نير": "crypto-near-protocol", "near": "crypto-near-protocol",
    "تون کوین": "crypto-toncoin", "toncoin": "crypto-toncoin", "ton": "crypto-toncoin",
    "رندر": "crypto-render", "render": "crypto-render",
    "تائو": "crypto-bittensor", "bittensor": "crypto-bittensor", "tao": "crypto-bittensor",
    "آربیتروم": "crypto-arbitrum", "arbitrum": "crypto-arbitrum", "arb": "crypto-arbitrum",
    "اوپتیمیزم": "crypto-optimism", "optimism": "crypto-optimism", "op": "crypto-optimism",
    "کوانتوم": "crypto-qtum", "qtum": "crypto-qtum",
    "استیم": "crypto-steem", "steem": "crypto-steem",
    "تراست ولت": "crypto-trust-wallet", "twt": "crypto-trust-wallet",
    "سیاکوین": "crypto-siacoin", "siacoin": "crypto-siacoin", "sc": "crypto-siacoin",
    "کومپاند": "crypto-compound", "compound": "crypto-compound", "comp": "crypto-compound",
    "اسنیکس": "crypto-synthetix", "synthetix": "crypto-synthetix", "snx": "crypto-synthetix",
    "کرونوس": "crypto-cronos", "cronos": "crypto-cronos", "cro": "crypto-cronos",
    "اتنا": "crypto-ethena", "ethena": "crypto-ethena", "ena": "crypto-ethena",
}


def time_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d  %H:%M:%S")


def get_currency_icon(name: str) -> str:
    for key, icon in CURRENCY_ICONS.items():
        if key in name:
            return icon
    return "💱"


def get_crypto_icon(name: str) -> str:
    for key, icon in CRYPTO_ICONS.items():
        if key in name:
            return icon
    return "🪙"


def get_trend_emoji(change_str: str) -> str:
    if not change_str or change_str == "-":
        return CHART_FLAT
    try:
        m = re.search(r"\(([\d.\-]+)%\)", change_str)
        if m:
            pct = float(m.group(1))
            if pct > 0.5:
                return CHART_UP
            if pct < -0.5:
                return CHART_DOWN
    except (ValueError, AttributeError):
        pass
    s = str(change_str).strip()
    if s.startswith("-"):
        return CHART_DOWN
    if any(c.isdigit() for c in s):
        return CHART_UP
    return CHART_FLAT


def get_hero_emoji(rank: int) -> str:
    if rank == 1:
        return CROWN
    if rank == 2:
        return "🥈"
    if rank == 3:
        return "🥉"
    if rank <= 10:
        return FIRE
    return SPARKLE


def find_slug(text: str) -> str | None:
    t = text.strip().lower()
    if t in ASSET_ALIASES:
        return ASSET_ALIASES[t]
    for key, slug in ASSET_ALIASES.items():
        if key in t:
            return slug
    return None


def _to_toman(price_str: str) -> str:
    if not price_str or price_str in ("-", "نامشخص"):
        return price_str
    try:
        digits = "".join(c for c in price_str if c.isdigit())
        if not digits:
            return price_str
        toman = int(digits) // 10
        return f"{toman:,}"
    except Exception:
        return price_str


async def fetch_html(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    connector = aiohttp.TCPConnector(limit=10, ssl=False)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        async with session.get(url, headers=HEADERS) as response:
            response.raise_for_status()
            return await response.text()


def parse_currencies(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    results: list[dict[str, str]] = []
    for table in soup.select("table.market-table"):
        for row in table.select("tbody > tr"):
            try:
                th = row.find("th")
                if not th:
                    continue
                flag = th.find("span")
                if flag:
                    flag.decompose()
                name = th.get_text(strip=True)
                tds = row.find_all("td")
                if len(tds) < 5:
                    continue
                results.append({
                    "name": name,
                    "price": tds[0].get_text(strip=True),
                    "change": tds[1].get_text(strip=True),
                    "low": tds[2].get_text(strip=True),
                    "high": tds[3].get_text(strip=True),
                    "time": tds[4].get_text(strip=True),
                })
            except Exception:
                continue
    return results


def parse_cryptos(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    results: list[dict[str, str]] = []
    table = soup.select_one("table.tgcss-table-auto")
    if not table:
        return results
    for row in table.select("tbody > tr"):
        try:
            tds = row.find_all("td")
            if len(tds) < 8:
                continue
            name_cell = tds[1]
            name_div = name_cell.find("div", class_="tgcss-text-base")
            name = name_div.get_text(strip=True) if name_div else name_cell.get_text(strip=True)
            results.append({
                "name": name,
                "symbol": tds[2].get_text(strip=True),
                "price_tether": tds[3].get_text(strip=True),
                "price_rial": tds[4].get_text(strip=True),
                "change_tether": tds[5].get_text(strip=True),
                "change_percent": tds[6].get_text(strip=True),
                "market_cap": tds[7].get_text(strip=True),
                "slug": row.get("data-market-nameslug", ""),
            })
        except Exception:
            continue
    return results


async def fetch_single_asset(slug: str) -> dict[str, Any]:
    url = URL_PROFILE + slug
    try:
        html = await fetch_html(url)
    except Exception as e:
        return {"error": str(e)}

    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else slug
    title = title.split("|")[0].strip()

    price = None
    price_el = soup.select_one('span[data-col="info.last_trade.PDrCotVal"]')
    if price_el:
        price = price_el.get_text(strip=True)

    change_percent = "-"
    change_pct_el = soup.select_one('span[data-col="info.last_trade.last_change_percentage"]')
    if change_pct_el:
        change_percent = change_pct_el.get_text(strip=True)

    data: dict[str, Any] = {
        "title": title, "price": price or "نامشخص",
        "change_percent": change_percent,
        "yesterday_price": "-", "yesterday_change": "-",
        "yesterday_dp": "-", "open": "-", "high": "-", "low": "-",
        "max_daily_tolerance": "-", "max_daily_tolerance_pct": "-",
        "slug": slug, "url": url,
    }

    for table in soup.select("table.table"):
        for row in table.select("tbody tr"):
            tds = row.find_all("td")
            if len(tds) < 2:
                continue
            label = tds[0].get_text(strip=True)
            value = tds[1].get_text(strip=True)
            if "بالاترین قیمت روز" in label:
                data["high"] = value
            elif "پایین" in label and "قیمت روز" in label:
                data["low"] = value
            elif "نرخ بازگشایی" in label:
                data["open"] = value
            elif "نرخ روز گذشته" in label:
                data["yesterday_price"] = value
            elif "درصد تغییر نسبت به روز گذشته" in label:
                data["yesterday_dp"] = value
            elif "میزان تغییر نسبت به روز گذشته" in label:
                data["yesterday_change"] = value
            elif "بیشترین مقدار نوسان روز" in label:
                data["max_daily_tolerance"] = value
            elif "درصد بیشترین نوسان روز" in label:
                data["max_daily_tolerance_pct"] = value

    if not data["price"] or data["price"] == "نامشخص":
        text = soup.get_text()
        m = re.search(r"نرخ فعلی[:\s]*([\d,]+)", text)
        if m:
            data["price"] = m.group(1)

    return data


def welcome_message(first_name: str) -> str:
    return (
        f"╔══════════════════════════════╗\n"
        f"║  {WAVE}  *سلام {first_name} عزیز!*  {SMILE}\n"
        f"╚══════════════════════════════╝\n\n"
        f"{HEART}  خوش اومدی به *ربات قیمت لحظه‌ای*!\n\n"
        f"{DIVIDER_STAR}\n\n"
        f"{GEM}  *من می‌تونم بهت کمک کنم:*\n\n"
        f"╭──────────────────────────────╮\n"
        f"│  💱  نرخ لحظه‌ای ارزها (تومان)\n"
        f"│  🪙  قیمت ارزهای دیجیتال\n"
        f"│  📊  بیشترین و کمترین قیمت\n"
        f"│  📈  روند بازار\n"
        f"│  ⚡  پاسخ سریع و دقیق\n"
        f"╰──────────────────────────────╯\n\n"
        f"{DIVIDER_DOT}\n\n"
        f"{LIGHTNING}  *دستورات سریع:*\n\n"
        f"  {STAR}  `لیست ارز`\n"
        f"  {STAR}  `لیست کریپتو`\n"
        f"  {STAR}  `راهنما`\n\n"
        f"{SEARCH}  *جستجوی مستقیم:*\n\n"
        f"  🇺🇸  `دلار`      |  ₿  `بیت کوین`\n"
        f"  🇪🇺  `یورو`      |  Ξ  `اتریوم`\n"
        f"  🇬🇧  `پوند`      |  ⚡  `ترون`\n\n"
        f"{DIVIDER_DOT}\n\n"
        f"{BOW}  فقط اسمش رو بنویس، بقیه‌اش با من!  {HEART}\n\n"
        f"{DIVIDER_STAR}\n"
        f"{GEM}  *شبکه اطلاع‌رسانی طلا و ارز*  {GEM}\n"
        f"{STAR}  tgju.org  {STAR}"
    )


def help_message() -> str:
    return (
        f"╔══════════════════════════════╗\n"
        f"║  {CROWN}  *راهنمای کامل ربات*  {CROWN}\n"
        f"╚══════════════════════════════╝\n\n"
        f"{DIVIDER_STAR}\n\n"
        f"{GEM}  *۱. دریافت لیست کامل:*\n\n"
        f"╭──────────────────────────────╮\n"
        f"│  {LIGHTNING}  `لیست ارز`\n"
        f"│       └─ نرخ همه ارزهای آزاد\n"
        f"│\n"
        f"│  {STAR}  `لیست کریپتو`\n"
        f"│       └─ لیست ارزهای دیجیتال\n"
        f"╰──────────────────────────────╯\n\n"
        f"{GEM}  *۲. جستجوی قیمت ارز:*\n\n"
        f"╭──────────────────────────────╮\n"
        f"│  🇺🇸  `دلار`     |  `dollar`\n"
        f"│  🇪🇺  `یورو`     |  `euro`\n"
        f"│  🇬🇧  `پوند`     |  `pound`\n"
        f"│  🇹🇷  `لیر`      |  `try`\n"
        f"╰──────────────────────────────╯\n\n"
        f"{GEM}  *۳. جستجوی کریپتو:*\n\n"
        f"╭──────────────────────────────╮\n"
        f"│  ₿  `بیت کوین`  |  `bitcoin`\n"
        f"│  Ξ  `اتریوم`    |  `ethereum`\n"
        f"│  💵  `تتر`       |  `tether`\n"
        f"│  ⚡  `ترون`      |  `tron`\n"
        f"╰──────────────────────────────╯\n\n"
        f"{DIVIDER_DOT}\n\n"
        f"{HEART}  *نکته:* فقط کافیه اسمش رو بنویسی!\n\n"
        f"{DIVIDER_STAR}\n"
        f"{GEM}  *شبکه اطلاع‌رسانی طلا و ارز*  {GEM}\n"
        f"{STAR}  tgju.org  {STAR}"
    )


def about_message() -> str:
    return (
        f"╔══════════════════════════════╗\n"
        f"║  {GEM}  *درباره ربات*  {GEM}\n"
        f"╚══════════════════════════════╝\n\n"
        f"{ROCKET}  *ربات قیمت‌های لحظه‌ای (تومان)*\n\n"
        f"{DIVIDER_STAR}\n\n"
        f"{STAR}  *امکانات:*\n\n"
        f"╭──────────────────────────────╮\n"
        f"│  💱  نرخ ارزهای آزاد\n"
        f"│  🪙  ارزهای دیجیتال\n"
        f"│  📊  تغییرات روزانه\n"
        f"│  📈  روند قیمتی\n"
        f"│  ⚡  سرعت بالا\n"
        f"│  🎨  طراحی زیبا\n"
        f"╰──────────────────────────────╯\n\n"
        f"{DIVIDER_STAR}\n\n"
        f"{HEART}  *ساخته شده با عشق برای شما*  {HEART}\n\n"
        f"{GEM}  *شبکه اطلاع‌رسانی طلا و ارز*  {GEM}\n"
        f"{STAR}  tgju.org  {STAR}"
    )


def build_currency_message(data: list[dict[str, str]]) -> str:
    header = (
        f"{LIGHTNING} *نرخ لحظه‌ای ارزها (تومان)* {LIGHTNING}\n"
        f"{CLOCK} `{time_stamp()}`\n"
        f"📊 تعداد: *{len(data)}* | 🏦 بازار: *آزاد*\n"
        f"{DIVIDER_THIN}\n"
    )
    lines = []
    for i, d in enumerate(data, 1):
        icon = get_currency_icon(d["name"])
        trend = get_trend_emoji(d["change"])
        price = _to_toman(d["price"])
        low = _to_toman(d["low"])
        high = _to_toman(d["high"])
        lines.append(
            f"`{i:>2}.` {icon} *{d['name']}*\n"
            f"     {MONEY} `{price}`  {trend} `{d['change']}`\n"
            f"     🔻 `{low}`  🔺 `{high}`\n"
        )
    return header + "".join(lines) + (
        f"{DIVIDER_THIN}\n"
        f"{GEM} *شبکه اطلاع‌رسانی طلا و ارز* {GEM}\n"
        f"{STAR} tgju.org {STAR}"
    )


def build_crypto_message(data: list[dict[str, str]]) -> str:
    header = (
        f"🪙 *بازار ارزهای دیجیتال* 🪙\n"
        f"{CLOCK} `{time_stamp()}`\n"
        f"📊 تعداد: *{len(data)}* | 🌐 بازار: *جهانی*\n"
        f"{DIVIDER_THIN}\n"
    )
    lines = []
    for i, d in enumerate(data, 1):
        icon = get_crypto_icon(d["name"])
        trend = get_trend_emoji(d["change_percent"])
        rial = _to_toman(d["price_rial"])
        lines.append(
            f"`{i:>2}.` {icon} *{d['name']}* `{d['symbol']}`\n"
            f"     💰 `{d['price_tether']}`  💵 `{rial}` تومان\n"
            f"     {trend} `{d['change_tether']}` ({d['change_percent']})\n"
            f"     🏦 `{d['market_cap']}`\n"
        )
    return header + "".join(lines) + (
        f"{DIVIDER_THIN}\n"
        f"{GEM} *شبکه اطلاع‌رسانی طلا و ارز* {GEM}\n"
        f"{STAR} tgju.org {STAR}"
    )


def build_single_asset_message(r: dict[str, Any]) -> str:
    is_crypto = "crypto" in r["slug"]
    icon = get_crypto_icon(r["title"]) if is_crypto else get_currency_icon(r["title"])
    trend = get_trend_emoji(r["change_percent"])

    price = _to_toman(r["price"])

    text = (
        f"╔══════════════════════════════╗\n"
        f"║  {icon}   *{r['title']}*   {icon}\n"
        f"╚══════════════════════════════╝\n\n"
        f"╭──────────────────────────────╮\n"
        f"│  {GEM}  *قیمت لحظه‌ای (تومان)*  {GEM}\n"
        f"│  {DIVIDER_THIN}\n"
        f"│  {MONEY}  `{price}`\n"
        f"│  {trend}  تغییر:  `{r['change_percent']}`\n"
        f"╰──────────────────────────────╯\n\n"
    )

    rows = []
    if r["open"] != "-":
        rows.append(f"│  🔓 بازگشایی   :  `{_to_toman(r['open'])}`")
    if r["high"] != "-":
        rows.append(f"│  🔺 بیشترین    :  `{_to_toman(r['high'])}`")
    if r["low"] != "-":
        rows.append(f"│  🔻 کمترین     :  `{_to_toman(r['low'])}`")
    if r["yesterday_price"] != "-":
        rows.append(f"│  📅 دیروز      :  `{_to_toman(r['yesterday_price'])}`")
    if r["yesterday_change"] != "-":
        rows.append(f"│  📊 تغییر دیروز:  `{_to_toman(r['yesterday_change'])}`")
    if r["yesterday_dp"] != "-":
        rows.append(f"│  📈 درصد دیروز :  `{r['yesterday_dp']}`")
    if r["max_daily_tolerance"] != "-":
        rows.append(f"│  ⚡ نوسان روز  :  `{_to_toman(r['max_daily_tolerance'])}`")
    if r["max_daily_tolerance_pct"] != "-":
        rows.append(f"│  🎯 درصد نوسان :  `{r['max_daily_tolerance_pct']}`")

    if rows:
        text += (
            f"╭──────────────────────────────╮\n"
            f"│  📊 *اطلاعات تکمیلی*\n"
            f"│  {DIVIDER_THIN}\n"
            + "\n".join(rows) + "\n"
            f"╰──────────────────────────────╯\n\n"
        )

    text += (
        f"┌──────────────────────────────┐\n"
        f"│  {LINK} [مشاهده پروفایل کامل]({r['url']})\n"
        f"└──────────────────────────────┘\n\n"
        f"{DIVIDER_THIN}\n"
        f"{GEM}  *شبکه اطلاع‌رسانی طلا و ارز*  {GEM}\n"
        f"{STAR}  tgju.org  {STAR}"
    )
    return text

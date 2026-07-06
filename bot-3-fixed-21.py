import requests
import time
import json
import os
import random
from datetime import datetime, timedelta, timezone

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")           ""
BASE_URL       = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
PROVIDER_TOKEN = "WALLET-OK6HEWN7IPAA2YKC"

BOT_USERNAME = "IRANI_MEMBER_BOT"
ADMIN_IDS    = [324157864]
DATA_FILE    = "bot_data.json"

SVCLABEL = {
    "bale_view_single": "بازدید تکی بله",
    "bale_reaction":    "ری‌اکشن بله",
    "rubika_view":      "بازدید تکی روبیکا",
    "eitaa_view":       "بازدید ایتا",
    "bale_member":      "ممبر بله",
    "rubika_member":    "ممبر روبیکا",
    "eitaa_member":     "ممبر ایتا",
    "rubika_follower":  "فالوور روبیکا",
}

SVC_PLATFORM = {
    "bale_view_single": "bale",
    "bale_reaction":    "bale",
    "rubika_view":      "rubika",
    "eitaa_view":       "eitaa",
    "bale_member":      "bale",
    "rubika_member":    "rubika",
    "eitaa_member":     "eitaa",
    "rubika_follower":  "rubika",
}

ALL_SVC_KEYS = list(SVCLABEL.keys())

# سرویس‌های فروش سکه
COIN_SERVICES = {
    "coin_bale_channel":    {"label": "فروش سکه کانال | بله 🔵",    "price_per_1053": 30000, "min": 200, "max": 3000, "enabled": True},
    "coin_bale_group":      {"label": "فروش سکه گروه | بله 🔵",      "price_per_1053": 25000, "min": 200, "max": 3000, "enabled": True},
    "coin_rubika_channel":  {"label": "فروش سکه کانال | روبیکا 🔴",  "price_per_1053": 35000, "min": 200, "max": 3000, "enabled": True},
    "coin_rubika_group":    {"label": "فروش سکه گروه | روبیکا 🔴",   "price_per_1053": 25000, "min": 200, "max": 3000, "enabled": True},
    "coin_rubika_like":     {"label": "فروش سکه لایک | روبیکا 🔴",   "price_per_1053": 15000, "min": 200, "max": 3000, "enabled": True},
    "coin_rubika_follower": {"label": "فروش سکه فالوور | روبیکا 🔴", "price_per_1053": 15000, "min": 200, "max": 3000, "enabled": True},
    "coin_eitaa_channel":   {"label": "فروش سکه کانال | ایتا 🟢",   "price_per_1053": 15000, "min": 200, "max": 3000, "enabled": True},
    "coin_eitaa_group":     {"label": "فروش سکه گروه | ایتا 🟢",    "price_per_1053": 15000, "min": 200, "max": 3000, "enabled": True},
}

# شماره واریز سکه (ثابت در کد)
COIN_PHONE_NUMBER = "09014285820"

# ══════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════
def default_data():
    return {
        "settings": {
            "forced_join":      True,
            "channel":          "@IRANI_MEMBER",
            "channel_link":     "https://ble.ir/IRANI_MEMBER",
            "bot_active":       True,
            "bale_view_single": {"enabled": True, "min": 500,   "max": 3000,  "price_per_1000": 25200,  "stock": 999999},
            "bale_reaction":    {"enabled": True, "min": 100,   "max": 1000,  "price_per_1000": 25200,  "stock": 999999},
            "rubika_view":      {"enabled": True, "min": 100,   "max": 50000, "price_per_1000": 25200,  "stock": 999999},
            "eitaa_view":       {"enabled": True, "min": 100,   "max": 10000, "price_per_1000": 56000,  "stock": 999999},
            "bale_member":      {"enabled": True, "min": 100,   "max": 10000, "price_per_1000": 288000, "stock": 999999},
            "rubika_member":    {"enabled": True, "min": 100,   "max": 20000, "price_per_1000": 480000, "stock": 999999},
            "eitaa_member":     {"enabled": True, "min": 100,   "max": 10000, "price_per_1000": 372000, "stock": 999999},
            "rubika_follower":  {"enabled": True, "min": 100,   "max": 20000, "price_per_1000": 216000, "stock": 999999},
            "coin_services":    COIN_SERVICES,
            "coin_card_number": "",  # شماره کارت ادمین برای کارت به کارت
            "design_price":     12000,  # قیمت طراحی عکس
            "forced_join_price_per_hour": 5000,  # قیمت هر ساعت جوین اجباری
            "fj_free_refs_per_hour": 3,           # تعداد زیرمجموعه برای هر ساعت رایگان
            "fj_free_hours_per_batch": 1,          # ساعت رایگان به ازای هر دسته زیرمجموعه
        },
        "stats": {
            "total_users": 0, "total_orders": 0,
            "total_revenue": 0, "daily_stats": {}
        },
        "users":          {},
        "orders":         [],
        "coin_orders":    [],
        "design_orders":  [],
        "forced_join_orders": [],
        "forced_join_channels": [],
        "tickets":        {},
        "pledges":        {},
        "discount_codes": {},
        "ticket_counter": 0,
        "order_counter":  0,
        "coin_order_counter":        0,
        "design_order_counter":      0,
        "forced_join_order_counter": 0,
    }

def migrate_data(data):
    defaults = default_data()
    for k, v in defaults.items():
        if k not in data:
            data[k] = v
    for svc_key, svc_default in defaults["settings"].items():
        if svc_key not in data["settings"]:
            data["settings"][svc_key] = svc_default
        elif isinstance(svc_default, dict):
            for field, field_default in svc_default.items():
                if field not in data["settings"][svc_key]:
                    data["settings"][svc_key][field] = field_default
    # migrate coin_services
    if "coin_services" not in data["settings"]:
        data["settings"]["coin_services"] = COIN_SERVICES
    else:
        for k, v in COIN_SERVICES.items():
            if k not in data["settings"]["coin_services"]:
                data["settings"]["coin_services"][k] = v
            else:
                for f, fv in v.items():
                    if f not in data["settings"]["coin_services"][k]:
                        data["settings"]["coin_services"][k][f] = fv
    if "coin_card_number" not in data["settings"]:
        data["settings"]["coin_card_number"] = ""
    if "coin_orders" not in data:
        data["coin_orders"] = []
    if "coin_order_counter" not in data:
        data["coin_order_counter"] = 0
    if "design_orders" not in data:
        data["design_orders"] = []
    if "design_order_counter" not in data:
        data["design_order_counter"] = 0
    if "design_price" not in data["settings"]:
        data["settings"]["design_price"] = 12000
    if "forced_join_orders" not in data:
        data["forced_join_orders"] = []
    if "forced_join_channels" not in data:
        data["forced_join_channels"] = []
    if "discount_codes" not in data:
        data["discount_codes"] = {}
    if "bot_active" not in data["settings"]:
        data["settings"]["bot_active"] = True
    if "pledges" not in data:
        data["pledges"] = {}
    for u in data.get("users", {}).values():
        if "last_spin"             not in u: u["last_spin"]             = ""
        if "active_discount_code"  not in u: u["active_discount_code"]  = ""
        if "spam_warnings"         not in u: u["spam_warnings"]         = 0
        if "referred_by"           not in u: u["referred_by"]           = None
    if "forced_join_order_counter" not in data:
        data["forced_join_order_counter"] = 0
    if "forced_join_price_per_hour" not in data["settings"]:
        data["settings"]["forced_join_price_per_hour"] = 5000
    if "fj_free_refs_per_hour" not in data["settings"]:
        data["settings"]["fj_free_refs_per_hour"] = 3
    if "fj_free_hours_per_batch" not in data["settings"]:
        data["settings"]["fj_free_hours_per_batch"] = 1
    # migrate referral fields on all users
    for u in data.get("users", {}).values():
        if "referred_by"   not in u: u["referred_by"]   = None
        if "referrals"     not in u: u["referrals"]     = []
        if "fj_free_used_hours" not in u: u["fj_free_used_hours"] = 0
    return data

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            return migrate_data(d)
        except:
            pass
    return default_data()

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════
def is_admin(chat_id):
    return int(chat_id) in ADMIN_IDS

def register_user(data, chat_id, uinfo=None):
    uid = str(chat_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "chat_id":     chat_id,
            "first_seen":  datetime.now().isoformat(),
            "last_seen":   datetime.now().isoformat(),
            "orders":      0,
            "total_spent": 0,
            "blocked":     False,
            "username":    (uinfo or {}).get("username", ""),
            "first_name":  (uinfo or {}).get("first_name", ""),
            "referred_by": None,
            "referrals":   [],
            "fj_free_used_hours": 0,
        }
        data["stats"]["total_users"] += 1
    else:
        data["users"][uid]["last_seen"] = datetime.now().isoformat()
        if uinfo:
            data["users"][uid]["username"]   = uinfo.get("username",   data["users"][uid].get("username", ""))
            data["users"][uid]["first_name"] = uinfo.get("first_name", data["users"][uid].get("first_name", ""))
    save_data(data)

def check_membership(chat_id):
    data = load_data()

    # ── چک کانال اصلی ──────────────────────────────────
    if data["settings"]["forced_join"]:
        try:
            r = requests.get(
                f"{BASE_URL}/getChatMember",
                params={"chat_id": data["settings"]["channel"], "user_id": chat_id},
                timeout=10
            ).json()
            if r.get("ok"):
                if r["result"].get("status", "") not in ["member", "administrator", "creator"]:
                    return False
            else:
                return False
        except Exception as e:
            print(f"check_membership main error: {e}")
            return False

    # ── چک کانال‌های جوین اجباری فعال ─────────────────
    active_fj = get_active_fj_channels(data)
    for ch in active_fj:
        link = ch.get("link", "")
        if not link:
            continue
        try:
            r = requests.get(
                f"{BASE_URL}/getChatMember",
                params={"chat_id": link, "user_id": chat_id},
                timeout=10
            ).json()
            if r.get("ok"):
                status = r["result"].get("status", "")
                if status not in ["member", "administrator", "creator"]:
                    return False
            else:
                # API خطا داد = نمی‌دونیم عضوه یا نه → بلاک کن
                return False
        except Exception as e:
            return False  # خطای شبکه → بلاک کن

    return True

def get_unjoined_fj_channels(chat_id, data):
    """لیست کانال‌هایی که کاربر هنوز عضو نشده"""
    missing = []
    if data["settings"]["forced_join"]:
        try:
            r = requests.get(
                f"{BASE_URL}/getChatMember",
                params={"chat_id": data["settings"]["channel"], "user_id": chat_id},
                timeout=10
            ).json()
            if r.get("ok"):
                if r["result"].get("status", "") not in ["member", "administrator", "creator"]:
                    missing.append({"link": data["settings"]["channel"], "url": data["settings"]["channel_link"], "label": "📢 کانال اصلی"})
            else:
                missing.append({"link": data["settings"]["channel"], "url": data["settings"]["channel_link"], "label": "📢 کانال اصلی"})
        except:
            pass
    for ch in get_active_fj_channels(data):
        link = ch.get("link", "")
        if not link:
            continue
        try:
            r = requests.get(
                f"{BASE_URL}/getChatMember",
                params={"chat_id": link, "user_id": chat_id},
                timeout=10
            ).json()
            if r.get("ok"):
                if r["result"].get("status", "") not in ["member", "administrator", "creator"]:
                    url = link if link.startswith("http") else f"https://ble.ir/{link.lstrip('@')}"
                    missing.append({"link": link, "url": url, "label": f"📢 {link}"})
        except:
            pass
    return missing

def get_iran_now():
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    return utc_now + timedelta(hours=3, minutes=30)

def get_active_fj_channels(data):
    """برگرداندن لیست کانال‌های جوین اجباری فعال و منقضی نشده"""
    iran_now = get_iran_now()
    now_str  = iran_now.strftime("%Y-%m-%d %H:%M")
    active   = []
    all_ch   = data.get("forced_join_channels", [])
    for ch in all_ch:
        a        = ch.get("active", False)
        end_time = ch.get("end_time", "")
        if not a:
            continue
        if not end_time:
            continue
        if end_time <= now_str:
            continue
        active.append(ch)
    return active

def check_bot_is_admin(link):
    """
    True  = ربات ادمینه
    False = ربات ادمین نیست (API جواب داد ولی ربات در لیست نبود)
    None  = خطای API یا نمی‌دونیم
    """
    if not link:
        return None
    try:
        r = requests.get(
            f"{BASE_URL}/getChatAdministrators",
            params={"chat_id": link},
            timeout=10
        ).json()
        if r.get("ok"):
            for admin in r.get("result", []):
                u = admin.get("user", {})
                if u.get("is_bot") and u.get("username", "").lower() == BOT_USERNAME.lower():
                    return True
            return False  # API جواب درست داد ولی ربات نبود
        return None  # API خطا داد
    except Exception as e:
        print(f"check_bot_is_admin error: {e}")
        return None  # خطای شبکه

def check_fj_channels_health(data):
    """بررسی دوره‌ای: فقط انقضای کانال‌های FJ"""
    changed  = False
    iran_now = get_iran_now()
    now_str  = iran_now.strftime("%Y-%m-%d %H:%M")

    for ch in data.get("forced_join_channels", []):
        if not ch.get("active", False):
            continue
        oid      = ch.get("order_id", "")
        end_time = ch.get("end_time", "")
        if end_time and end_time <= now_str:
            ch["active"] = False
            changed      = True
            for o in data.get("forced_join_orders", []):
                if o["id"] == oid and o.get("status") == "active":
                    o["status"] = "done"
                    send(o["user_id"],
                        f"*⏰ جوین اجباری کانال شما به پایان رسید.\n\n"
                        f"🆔 {oid}\n🔗 {ch['link']}\n\n"
                        f"ممنون از خرید شما! 🙏*"
                    )
    if changed:
        save_data(data)

def validate_bale_link(link):
    link = link.strip()
    if link.startswith("@") and len(link) > 1:
        return True
    for p in ["https://ble.ir/", "http://ble.ir/", "ble.ir/"]:
        if link.startswith(p) and len(link) > len(p):
            return True
    return False

def validate_rubika_link(link):
    link = link.strip()
    if link.startswith("@") and len(link) > 1:
        return True
    for p in ["https://rubika.ir/", "http://rubika.ir/", "rubika.ir/"]:
        if link.startswith(p) and len(link) > len(p):
            return True
    return False

def validate_eitaa_link(link):
    link = link.strip()
    if link.startswith("@") and len(link) > 1:
        return True
    for p in ["https://eitaa.com/", "http://eitaa.com/", "eitaa.com/"]:
        if link.startswith(p) and len(link) > len(p):
            return True
    return False

def gregorian_to_jalali(gy, gm, gd):
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    gy2 = gy - 1600; gm2 = gm - 1; gd2 = gd - 1
    g_day_no = 365*gy2 + (gy2+3)//4 - (gy2+99)//100 + (gy2+399)//400
    for i in range(gm2): g_day_no += g_days_in_month[i]
    if gm2 > 1 and ((gy%4==0 and gy%100!=0) or (gy%400==0)): g_day_no += 1
    g_day_no += gd2
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053; j_day_no %= 12053
    jy = 979 + 33*j_np + 4*(j_day_no//1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no-1)//365; j_day_no = (j_day_no-1)%365
    for i in range(11):
        if j_day_no < j_days_in_month[i]:
            jm = i+1; jd = j_day_no+1; break
        j_day_no -= j_days_in_month[i]
    else:
        jm = 12; jd = j_day_no+1
    return jy, jm, jd

def now_jalali_str():
    utc_now  = datetime.now(timezone.utc).replace(tzinfo=None)
    iran_now = utc_now + timedelta(hours=3, minutes=30)
    jy, jm, jd = gregorian_to_jalali(iran_now.year, iran_now.month, iran_now.day)
    return f"{jy:04d}/{jm:02d}/{jd:02d} - {iran_now.strftime('%H:%M:%S')}"

def mask_user_id(chat_id):
    s = str(chat_id); n = len(s)
    if n <= 4: return "*" * n
    vs = max(2, (n-4)//2); ve = n-vs-4
    if ve < 2: ve=2; vs=n-ve-4
    if vs < 1: vs=1
    ml = n-vs-ve
    if ml < 1: ml=1
    return s[:vs] + ("*"*ml) + s[n-ve:]

def send(chat_id, text, markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if markup:
        payload["reply_markup"] = markup
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print(f"send error: {e}")

def send_photo(chat_id, photo, caption="", markup=None):
    payload = {"chat_id": chat_id, "photo": photo, "caption": caption, "parse_mode": "Markdown"}
    if markup:
        payload["reply_markup"] = markup
    try:
        requests.post(f"{BASE_URL}/sendPhoto", json=payload, timeout=15)
    except Exception as e:
        print(f"send_photo error: {e}")

def forward_photo(chat_id, from_chat_id, message_id):
    try:
        requests.post(f"{BASE_URL}/forwardMessage", json={
            "chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id
        }, timeout=10)
    except Exception as e:
        print(f"forward error: {e}")

def kb(*rows):
    return {"keyboard": [[{"text": t} for t in row] for row in rows], "resize_keyboard": True}

BACK_BTN      = kb(["🔙 بازگشت"])
BACK_BTN_USER = kb(["🔙 بازگشت به منوی اصلی 🏠"])

# ══════════════════════════════════════════
#  JOIN / START
# ══════════════════════════════════════════
def _build_join_buttons(chat_id, data):
    """ساخت دکمه‌های اینلاین برای همه کانال‌هایی که کاربر باید عضو بشه"""
    buttons = []
    # کانال اصلی
    if data["settings"]["forced_join"]:
        buttons.append([{
            "text": "📢 عضویت در کانال اصلی",
            "url":  data["settings"]["channel_link"]
        }])
    # کانال‌های جوین اجباری فعال
    for ch in get_active_fj_channels(data):
        link = ch.get("link", "")
        if not link:
            continue
        url = link if link.startswith("http") else f"https://ble.ir/{link.lstrip('@')}"
        buttons.append([{
            "text": f"📢 جوین اجباری | {link}",
            "url":  url
        }])
    # دکمه تأیید
    buttons.append([{"text": "✅ تأیید عضویت", "callback_data": "check_join"}])
    return buttons

def send_join_required(chat_id):
    data    = load_data()
    buttons = _build_join_buttons(chat_id, data)
    active_fj = get_active_fj_channels(data)
    if active_fj:
        extra = f"\n\n📢 همچنین باید در {len(active_fj)} کانال جوین اجباری زیر عضو شوی:"
        for ch in active_fj:
            extra += f"\n🔹 {ch.get('link', '')}"
    else:
        extra = ""
    send(chat_id,
        f"*✨ برای استفاده از ربات باید عضو شوی!\n\n"
        f"👇 روی دکمه‌های زیر کلیک کن و عضو شو، سپس تأیید را بزن:{extra}\n\n"
        f"✅ بعد از عضویت دکمه تأیید را بزن! 🚀*",
        {"inline_keyboard": buttons}
    )

def send_not_joined(chat_id):
    data    = load_data()
    buttons = _build_join_buttons(chat_id, data)
    active_fj = get_active_fj_channels(data)
    if active_fj:
        extra = f"\n\n📢 همچنین باید در {len(active_fj)} کانال جوین اجباری عضو باشی:"
        for ch in active_fj:
            extra += f"\n🔸 {ch.get('link', '')}"
    else:
        extra = ""
    send(chat_id,
        f"*⚠️ هنوز در همه کانال‌ها عضو نشدی!\n\n"
        f"👇 روی دکمه‌های زیر کلیک کن:{extra}\n\n"
        f"بعد از عضویت دکمه تأیید را بزن! ✨*",
        {"inline_keyboard": buttons}
    )

def send_start(chat_id):
    send(chat_id,
        "*🌈 سلام سلام! به ربات افزایش ممبر | بازدید ایران خوش اومدی! 🌈🎉\n\n"
        "چه خوب که اینجایی 😍💖\n\n"
        "اینجا قراره با یه عالمه انرژی خوب،\n"
        "ممبر و بازدید رو سریع، راحت و جذاب تجربه کنی 🚀🔥\n\n"
        "💫 چرا اینجا؟\n\n"
        "🌟 سریع و آسان\n\n"
        "🌟 شاد و کاربرپسند\n\n"
        "🌟 پشتیبانی همیشه همراه\n\n"
        "🌟 مناسب برای رشد بهتر و بیشتر\n\n"
        "🚀 برای شروع همین الان وارد شو:\n\n"
        "🔗 @IRANI_MEMBER\n\n"
        "💌 پشتیبانی مهربون و پاسخ‌گو:\n\n"
        "🆔 @ARKA_SUPPORT_IR\n\n"
        "🌸✨ منتظر یه تجربه عالی و پرانرژی باش! ✨🌸\n\n"
        "با ما، رشدت شیرین‌تره 🍭💎\n\n"
        "👇 از دکمه‌های زیر برای دسترسی به خدمات ربات استفاده کنید:*",
        kb(
            ["سفارش بازدید 👁️", "سفارش ممبر 👥", "🛍 فروش سکه"],
            ["🎨 طراحی عکس حرفه‌ای", "📱 ثبت جوین اجباری"],
            ["👥 زیرمجموعه‌گیری", "🧩 سرگرمی‌ها", "🎡 گردونه روزانه"],
            ["حساب کاربری 👤", "پیگیری سفارش 🔎", "قوانین ⚖️"],
            ["📞 پشتیبانی"]
        )
    )

# ══════════════════════════════════════════
#  حساب کاربری
# ══════════════════════════════════════════
def send_account(chat_id):
    data    = load_data()
    uid     = str(chat_id)
    u       = data["users"].get(uid, {})
    name    = u.get("first_name", "نامشخص")
    uname   = u.get("username", "")
    uname_display = f"@{uname}" if uname else "ندارد"
    total   = u.get("orders", 0)
    done    = sum(1 for o in data["orders"] if str(o.get("user_id")) == uid and o.get("status") == "done")
    pending = sum(1 for o in data["orders"] if str(o.get("user_id")) == uid and o.get("status") == "pending")
    coin_total   = sum(1 for o in data["coin_orders"] if str(o.get("user_id")) == uid)
    design_total = sum(1 for o in data.get("design_orders", []) if str(o.get("user_id")) == uid)
    refs         = len(u.get("referrals", []))
    warnings     = u.get("spam_warnings", 0)

    # دکمه‌های اینلاین copy
    inline_btns = []
    if uname:
        inline_btns.append([{"text": f"📋 کپی یوزرنیم | @{uname}", "copy_text": {"text": f"@{uname}"}}])
    inline_btns.append([{"text": f"📋 کپی آیدی عددی | {chat_id}", "copy_text": {"text": str(chat_id)}}])

    send(chat_id,
        f"*👤 حساب کاربری\n"
        f"━━━━━━━━━━━━\n\n"
        f"🆔 شناسه کاربری: `{chat_id}`\n"
        f"👤 نام: {name}\n"
        f"🔗 نام کاربری: {uname_display}\n\n"
        f"📦 آمار سفارش‌ها\n"
        f"📋 کل سفارش‌ها: {total}\n"
        f"⏳ در حال انجام: {pending}\n"
        f"✅ تکمیل شده: {done}\n"
        f"🪙 فروش سکه: {coin_total}\n"
        f"🎨 طراحی عکس: {design_total}\n"
        f"👥 زیرمجموعه‌ها: {refs} نفر\n"
        f"⚠️ اخطار اسپم: {warnings}/3*",
        {"inline_keyboard": inline_btns}
    )
    send(chat_id, "👇", BACK_BTN_USER)

# ══════════════════════════════════════════
#  پیگیری سفارش
# ══════════════════════════════════════════
def send_tracking(chat_id):
    data   = load_data()
    uid    = str(chat_id)
    orders = [o for o in data["orders"] if str(o.get("user_id")) == uid]
    coin_orders = [o for o in data["coin_orders"] if str(o.get("user_id")) == uid]
    design_orders = [o for o in data.get("design_orders", []) if str(o.get("user_id")) == uid]
    fj_orders     = [o for o in data.get("forced_join_orders", []) if str(o.get("user_id")) == uid]
    if not orders and not coin_orders and not design_orders and not fj_orders:
        send(chat_id, "*📋 شما هنوز هیچ سفارشی ثبت نکرده‌اید.*", BACK_BTN_USER)
        return
    if orders:
        send(chat_id, f"*🔎 پیگیری سفارش‌ها | {len(orders)} سفارش*")
        for o in reversed(orders[-10:]):
            st = o.get("status", "")
            if st == "done":       st_icon = "✅ تکمیل شده"
            elif st == "pending":  st_icon = "⏳ در حال انجام"
            elif st == "pending_payment": st_icon = "💳 در انتظار پرداخت"
            else:                  st_icon = "❓ نامشخص"
            date_str = o.get("date", "")[:10]
            send(chat_id,
                f"*🆔 {o.get('id', '?')}\n"
                f"📦 {o.get('service', '?')}\n"
                f"🔢 تعداد: {o.get('amount', 0):,}\n"
                f"💰 مبلغ: {o.get('price', 0):,} تومان\n"
                f"🔗 لینک: {o.get('link', '?')}\n"
                f"📅 تاریخ: {date_str}\n"
                f"وضعیت: {st_icon}*"
            )
    if coin_orders:
        send(chat_id, f"*🪙 سفارشات فروش سکه | {len(coin_orders)} سفارش*")
        for o in reversed(coin_orders[-10:]):
            st = o.get("status", "pending")
            if st == "approved":  st_icon = "✅ تأیید شده"
            elif st == "rejected": st_icon = "❌ رد شده"
            else:                  st_icon = "⏳ در انتظار بررسی"
            send(chat_id,
                f"*🆔 {o.get('id', '?')}\n"
                f"📦 {o.get('service_label', '?')}\n"
                f"🪙 تعداد: {o.get('amount', 0):,} سکه\n"
                f"💰 مبلغ: {o.get('price', 0):,} تومان\n"
                f"📱 شماره: {o.get('phone', '?')}\n"
                f"📅 تاریخ: {o.get('date', '')[:10]}\n"
                f"وضعیت: {st_icon}*"
            )
    if design_orders:
        send(chat_id, f"*🎨 سفارشات طراحی عکس | {len(design_orders)} سفارش*")
        for o in reversed(design_orders[-10:]):
            st = o.get("status", "pending")
            if st == "done":      st_icon = "✅ تحویل داده شده"
            elif st == "rejected": st_icon = "❌ رد شده"
            else:                  st_icon = "⏳ در حال انجام"
            send(chat_id,
                f"*🆔 {o.get('id', '?')}\n"
                f"🎨 طراحی عکس حرفه‌ای\n"
                f"💰 مبلغ: {o.get('price', 0):,} تومان\n"
                f"📅 تاریخ: {o.get('date', '')[:10]}\n"
                f"وضعیت: {st_icon}*"
            )
    if fj_orders:
        send(chat_id, f"*📱 سفارشات جوین اجباری | {len(fj_orders)} سفارش*")
        for o in reversed(fj_orders[-10:]):
            st = o.get("status", "pending")
            if st == "active":    st_icon = f"✅ فعال | پایان: {o.get('end_time', '')}"
            elif st == "done":    st_icon = "🏁 تمام شده"
            elif st == "rejected":st_icon = "❌ رد شده"
            else:                 st_icon = "⏳ در انتظار بررسی"
            send(chat_id,
                f"*🆔 {o.get('id', '?')}\n"
                f"⏳ {o.get('hours', 0)} ساعت\n"
                f"🔗 {o.get('link', '?')}\n"
                f"💰 {o.get('price', 0):,} تومان\n"
                f"📅 {o.get('date', '')[:10]}\n"
                f"وضعیت: {st_icon}*"
            )
    send(chat_id, "*👆 لیست سفارش‌های شما*", BACK_BTN_USER)

# ══════════════════════════════════════════
#  قوانین
# ══════════════════════════════════════════
def send_rules(chat_id):
    send(chat_id,
        "*━━━━━━━━━━━━━━━━━━\n"
        "⚖️ قوانین و ضوابط استفاده از ربات «افزایش ممبر | بازدید ایران»\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "استفاده از خدمات این ربات به منزله‌ی تایید کامل تمامی موارد زیر می‌باشد. لطفاً پیش از ثبت سفارش، با دقت مطالعه کنید:\n\n"
        "📍 بخش اول: مسئولیت کاربر\n"
        "🔹 دقت در اطلاعات: مسئولیت صحت تمامی اطلاعات وارد شده (لینک، آیدی، تعداد و پلتفرم) بر عهده کاربر است.\n"
        "🔹 فرمت صحیح: ثبت سفارش با لینک‌های نامعتبر یا فرمت اشتباه، مسئولیت خود کاربر است.\n\n"
        "⚠️ بخش دوم: سیاست‌های مهم\n"
        "🚫 عدم بازگشت وجه: با توجه به ماهیت دیجیتالی خدمات، به هیچ عنوان امکان استرداد یا بازگشت وجه پس از ثبت سفارش وجود ندارد.\n"
        "🚫 ماهیت سرویس: توجه داشته باشید که برخی خدمات صرفاً جهت بهبود آمار و نمایش هستند.\n\n"
        "💡 توصیه نهایی:\n"
        "برای دریافت بهترین نتیجه، همیشه ابتدا با مقادیر کم تست کنید. 🚀\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🆘 نیاز به کمک دارید؟\n"
        "ارتباط با پشتیبانی: @ARKA_SUPPORT_IR\n"
        "━━━━━━━━━━━━━━━━━━*",
        BACK_BTN_USER
    )

# ══════════════════════════════════════════
#  سیستم تیکت پشتیبانی
# ══════════════════════════════════════════
def get_user_open_ticket(data, chat_id):
    uid = str(chat_id)
    for tid, t in data["tickets"].items():
        if str(t.get("user_id")) == uid and t.get("status") == "open":
            return tid, t
    return None, None

def create_ticket(data, chat_id, first_msg, uinfo=None):
    data["ticket_counter"] = data.get("ticket_counter", 0) + 1
    tid   = f"TKT{data['ticket_counter']}"
    name  = (uinfo or {}).get("first_name", "کاربر")
    uname = (uinfo or {}).get("username", "")
    data["tickets"][tid] = {
        "id":       tid,
        "user_id":  chat_id,
        "name":     name,
        "username": uname,
        "status":   "open",
        "created":  datetime.now().isoformat(),
        "messages": [{"from": "user", "text": first_msg, "time": datetime.now().isoformat()}]
    }
    save_data(data)
    return tid

def send_support_menu(chat_id):
    data   = load_data()
    tid, t = get_user_open_ticket(data, chat_id)
    if tid:
        send(chat_id,
            f"*📞 پشتیبانی\n\n"
            f"شما یک گفتگوی باز دارید: #{tid}\n\n"
            f"پیام خود را ارسال کنید تا پشتیبان پاسخ دهد.*",
            kb(["❌ بستن تیکت", "🔙 بازگشت به منوی اصلی 🏠"])
        )
    else:
        send(chat_id,
            "*📞 پشتیبانی\n\n"
            "پیام خود را بنویسید تا گفتگو با پشتیبان شروع شود.\n\n"
            "💡 سوال، مشکل یا درخواست خود را ارسال کنید:*",
            kb(["🔙 بازگشت به منوی اصلی 🏠"])
        )

def handle_support_message(chat_id, text, data, states, uinfo=None):
    uid = str(chat_id)
    if text == "❌ بستن تیکت":
        tid, t = get_user_open_ticket(data, chat_id)
        if tid:
            data["tickets"][tid]["status"] = "closed"
            save_data(data)
            states.pop(uid, None)
            send(chat_id, f"*✅ گفتگو #{tid} بسته شد.*", BACK_BTN_USER)
            for aid in ADMIN_IDS:
                send(aid, f"*🔴 تیکت #{tid} توسط کاربر بسته شد.*")
        else:
            states.pop(uid, None)
            send(chat_id, "*هیچ گفتگوی بازی وجود ندارد.*", BACK_BTN_USER)
        return

    tid, t = get_user_open_ticket(data, chat_id)
    if not tid:
        tid       = create_ticket(data, chat_id, text, uinfo)
        uname     = (uinfo or {}).get("username", "")
        uname_str = f"@{uname}" if uname else str(chat_id)
        name      = (uinfo or {}).get("first_name", "کاربر")
        send(chat_id,
            f"*✅ گفتگو #{tid} شروع شد!\n\n"
            f"پشتیبان پیام شما را دریافت کرد و به زودی پاسخ می‌دهد.*",
            kb(["❌ بستن تیکت", "🔙 بازگشت به منوی اصلی 🏠"])
        )
        for aid in ADMIN_IDS:
            send(aid,
                f"*🎫 گفتگوی جدید #{tid}\n\n"
                f"👤 {name} ({uname_str})\n"
                f"🆔 آیدی: {chat_id}\n\n"
                f"💬 پیام:\n{text}*",
                {"inline_keyboard": [
                    [{"text": f"↩️ پاسخ به #{tid}", "callback_data": f"reply_ticket|{tid}"}],
                    [{"text": f"🔴 بستن #{tid}",    "callback_data": f"close_ticket|{tid}"}]
                ]}
            )
    else:
        t["messages"].append({"from": "user", "text": text, "time": datetime.now().isoformat()})
        save_data(data)
        send(chat_id, "*✅ پیام ارسال شد. منتظر پاسخ باشید.*",
             kb(["❌ بستن تیکت", "🔙 بازگشت به منوی اصلی 🏠"]))
        uname     = t.get("username", "")
        uname_str = f"@{uname}" if uname else str(chat_id)
        for aid in ADMIN_IDS:
            send(aid,
                f"*💬 پیام جدید در #{tid}\n\n"
                f"👤 {t.get('name', 'کاربر')} ({uname_str})\n\n"
                f"📩 پیام:\n{text}*",
                {"inline_keyboard": [
                    [{"text": f"↩️ پاسخ به #{tid}", "callback_data": f"reply_ticket|{tid}"}],
                    [{"text": f"🔴 بستن #{tid}",    "callback_data": f"close_ticket|{tid}"}]
                ]}
            )

def admin_reply_to_ticket(admin_chat_id, tid, reply_text, data):
    t = data["tickets"].get(tid)
    if not t:
        send(admin_chat_id, f"*⚠️ تیکت #{tid} یافت نشد.*")
        return
    if t.get("status") == "closed":
        send(admin_chat_id, f"*⚠️ تیکت #{tid} بسته است.*")
        return
    t["messages"].append({"from": "admin", "text": reply_text, "time": datetime.now().isoformat()})
    save_data(data)
    user_id = t.get("user_id")
    send(user_id,
        f"*📩 پاسخ پشتیبانی - گفتگو #{tid}\n\n"
        f"━━━━━━━━━━━━\n\n"
        f"{reply_text}\n\n"
        f"━━━━━━━━━━━━\n"
        f"می‌توانید پاسخ دهید یا گفتگو را ببندید.*",
        kb(["❌ بستن تیکت", "🔙 بازگشت به منوی اصلی 🏠"])
    )
    send(admin_chat_id,
        f"*✅ پاسخ به #{tid} ارسال شد.*",
        {"inline_keyboard": [
            [{"text": f"↩️ پاسخ دیگر به #{tid}", "callback_data": f"reply_ticket|{tid}"}],
            [{"text": f"🔴 بستن #{tid}",          "callback_data": f"close_ticket|{tid}"}]
        ]}
    )

# ══════════════════════════════════════════
#  فروش سکه - جریان کاربر
# ══════════════════════════════════════════
def coin_service_key_from_text(text):
    MAP = {
        "🔵 فروش سکه کانال | بله 🚀":       "coin_bale_channel",
        "🔵 فروش سکه گروه | بله 🚀":         "coin_bale_group",
        "🔴 فروش سکه کانال | روبیکا ⚡️":    "coin_rubika_channel",
        "🔴 فروش سکه گروه | روبیکا ⚡️":     "coin_rubika_group",
        "🔴 فروش سکه لایک | روبیکا ⚡️":     "coin_rubika_like",
        "🔴 فروش سکه فالوور | روبیکا ⚡️":   "coin_rubika_follower",
        "🟢 فروش سکه کانال | ایتا ☕️":      "coin_eitaa_channel",
        "🟢 فروش سکه گروه | ایتا ☕️":       "coin_eitaa_group",
    }
    return MAP.get(text)

def send_coin_platform(chat_id):
    send(chat_id,
        "*🛍 فروش سکه 💰\n\n"
        "━━━━━━━━━━━━\n\n"
        "خب رفیق! لطفاً پلتفرم مورد نظرت رو انتخاب کن: 👇🌈*",
        kb(
            ["🔵 فروش سکه | بله 🚀"],
            ["🔴 فروش سکه | روبیکا ⚡️"],
            ["🟢 فروش سکه | ایتا ☕️"],
            ["🔙 بازگشت به منوی اصلی 🏠"]
        )
    )

def send_coin_bale_menu(chat_id):
    data = load_data()
    cs   = data["settings"]["coin_services"]
    def info(k):
        s = cs.get(k, {})
        return f"{s.get('price_per_1053', 0):,} تومان / 1053 سکه"
    send(chat_id,
        f"*🔵 فروش سکه | بله 🚀\n\n"
        f"کانال: {info('coin_bale_channel')}\n"
        f"گروه: {info('coin_bale_group')}\n\n"
        f"یک گزینه را انتخاب کنید:*",
        kb(
            ["🔵 فروش سکه کانال | بله 🚀", "🔵 فروش سکه گروه | بله 🚀"],
            ["🔙 بازگشت"]
        )
    )

def send_coin_rubika_menu(chat_id):
    data = load_data()
    cs   = data["settings"]["coin_services"]
    def info(k):
        s = cs.get(k, {})
        return f"{s.get('price_per_1053', 0):,} تومان / 1053 سکه"
    send(chat_id,
        f"*🔴 فروش سکه | روبیکا ⚡️\n\n"
        f"کانال: {info('coin_rubika_channel')}\n"
        f"گروه: {info('coin_rubika_group')}\n"
        f"لایک: {info('coin_rubika_like')}\n"
        f"فالوور: {info('coin_rubika_follower')}\n\n"
        f"یک گزینه را انتخاب کنید:*",
        kb(
            ["🔴 فروش سکه کانال | روبیکا ⚡️", "🔴 فروش سکه گروه | روبیکا ⚡️"],
            ["🔴 فروش سکه لایک | روبیکا ⚡️", "🔴 فروش سکه فالوور | روبیکا ⚡️"],
            ["🔙 بازگشت"]
        )
    )

def send_coin_eitaa_menu(chat_id):
    data = load_data()
    cs   = data["settings"]["coin_services"]
    def info(k):
        s = cs.get(k, {})
        return f"{s.get('price_per_1053', 0):,} تومان / 1053 سکه"
    send(chat_id,
        f"*🟢 فروش سکه | ایتا ☕️\n\n"
        f"کانال: {info('coin_eitaa_channel')}\n"
        f"گروه: {info('coin_eitaa_group')}\n\n"
        f"یک گزینه را انتخاب کنید:*",
        kb(
            ["🟢 فروش سکه کانال | ایتا ☕️", "🟢 فروش سکه گروه | ایتا ☕️"],
            ["🔙 بازگشت"]
        )
    )

def start_coin_order(chat_id, svc_key, data, states):
    cs  = data["settings"]["coin_services"]
    svc = cs.get(svc_key, {})
    if not svc.get("enabled", True):
        send(chat_id, "*⚠️ این سرویس موقتاً غیرفعال است.*")
        return
    mn  = svc.get("min", 200)
    mx  = svc.get("max", 3000)
    p   = svc.get("price_per_1053", 0)
    states[str(chat_id)] = f"coin_qty|{svc_key}"
    send(chat_id,
        f"*⚜️ فروش سکه ⚜️\n\n"
        f"✨ ویژه: بسته به نیاز شما، از {mn:,} تا {mx:,} سکه به فروش بگذارید.\n\n"
        f"💰 قیمت هر 1053 سکه: {p//1000} هزار تومان!\n\n"
        f"🚀 پیشنهاد ویژه: 1053 سکه را با {p:,} تومان به فروش بگذارید!\n\n"
        f"📌 مرحله 1 از 4\n\n"
        f"💐 لطفاً تعداد سکه دلخواه خود را وارد نمایید:*",
        BACK_BTN_USER
    )

def calc_coin_price(qty, price_per_1053):
    return int(qty * price_per_1053 / 1053)

# ══════════════════════════════════════════
#  طراحی عکس حرفه‌ای
# ══════════════════════════════════════════
def send_design_start(chat_id):
    data  = load_data()
    price = data["settings"].get("design_price", 12000)
    send(chat_id,
        f"*🎨 طراحی عکس حرفه‌ای\n\n"
        f"━━━━━━━━━━━━\n\n"
        f"✨ با تیم طراحی ما، عکس دلخواهت رو به بهترین شکل ممکن بساز!\n\n"
        f"💰 قیمت: {price:,} تومان به ازای هر عکس\n\n"
        f"📌 مرحله 1 از 3\n\n"
        f"🆔 آیدی بله خود را جهت دریافت عکس وارد کنید:\n\n"
        f"مثال: @username یا شماره موبایل*",
        BACK_BTN_USER
    )

def send_design_invoice(chat_id, bale_id, description):
    data  = load_data()
    price = data["settings"].get("design_price", 12000)
    data["design_order_counter"] = data.get("design_order_counter", 0) + 1
    oid   = data["design_order_counter"]
    order_id = f"DSN{oid}"
    data["design_orders"].append({
        "id":          order_id,
        "user_id":     chat_id,
        "bale_id":     bale_id,
        "description": description,
        "price":       price,
        "status":      "pending_payment",
        "date":        datetime.now().isoformat()
    })
    save_data(data)
    result = requests.post(f"{BASE_URL}/sendInvoice", json={
        "chat_id":        chat_id,
        "title":          "🎨 طراحی عکس حرفه‌ای",
        "description":    f"🎨 طراحی عکس\n🆔 آیدی دریافت: {bale_id}\n📝 توضیحات: {description[:100]}\n🔖 سفارش: {order_id}",
        "payload":        f"design_{oid}",
        "provider_token": PROVIDER_TOKEN,
        "currency":       "IRR",
        "prices":         [{"label": "طراحی عکس حرفه‌ای", "amount": price * 10}],
        "start_parameter": "pay"
    }, timeout=15).json()
    if not result.get("ok"):
        send(chat_id, "*❌ خطا در ارسال فاکتور! با پشتیبانی تماس بگیرید: @ARKA_SUPPORT_IR*")

def register_design_payment(chat_id, payload):
    data = load_data()
    order_num = None
    try:
        order_num = int(payload.replace("design_", ""))
    except:
        pass
    target = None
    for o in data["design_orders"]:
        if o["id"] == f"DSN{order_num}" and o["user_id"] == chat_id and o["status"] == "pending_payment":
            target = o; break
    if not target:
        for o in reversed(data["design_orders"]):
            if o["user_id"] == chat_id and o["status"] == "pending_payment":
                target = o; break
    if target:
        target["status"] = "pending"
        today = get_today()
        data["stats"]["total_orders"]  += 1
        data["stats"]["total_revenue"] += target["price"]
        uid = str(chat_id)
        if uid in data["users"]:
            data["users"][uid]["orders"]      = data["users"][uid].get("orders", 0) + 1
            data["users"][uid]["total_spent"] = data["users"][uid].get("total_spent", 0) + target["price"]
        if today not in data["stats"]["daily_stats"]:
            data["stats"]["daily_stats"][today] = {"orders": 0, "revenue": 0}
        data["stats"]["daily_stats"][today]["orders"]  += 1
        data["stats"]["daily_stats"][today]["revenue"] += target["price"]
        save_data(data)
        send(chat_id,
            f"*🎉 پرداخت موفق! سفارش طراحی ثبت شد!\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"🆔 شماره سفارش: {target['id']}\n"
            f"🎨 سرویس: طراحی عکس حرفه‌ای\n"
            f"🆔 آیدی دریافت: {target['bale_id']}\n"
            f"💰 مبلغ: {target['price']:,} تومان\n\n"
            f"⏳ سفارش در حال پردازش است.\n"
            f"📸 عکس طراحی شده به آیدی شما ارسال خواهد شد.\n"
            f"💌 پشتیبانی: @ARKA_SUPPORT_IR*"
        )
        uinfo_name = data["users"].get(str(chat_id), {}).get("first_name", "")
        uinfo_un   = data["users"].get(str(chat_id), {}).get("username", "")
        un_str     = f"@{uinfo_un}" if uinfo_un else str(chat_id)
        for aid in ADMIN_IDS:
            send(aid,
                f"*🎨 سفارش طراحی جدید!\n\n"
                f"🆔 {target['id']}\n"
                f"👤 {uinfo_name} ({un_str}) | آیدی: {chat_id}\n"
                f"🆔 آیدی دریافت: {target['bale_id']}\n"
                f"💰 {target['price']:,} تومان\n\n"
                f"📝 توضیحات:\n{target['description']}*",
                {"inline_keyboard": [
                    [{"text": "✅ تکمیل سفارش", "callback_data": f"complete_design|{target['id']}"}],
                    [{"text": "❌ رد سفارش",     "callback_data": f"reject_design|{target['id']}"}]
                ]}
            )
    else:
        send(chat_id, "*✅ پرداخت انجام شد!\n\n⏳ سفارش طراحی در حال پردازش است.\n💌 @ARKA_SUPPORT_IR*")

def complete_design_order(order_id, data):
    target = next((o for o in data["design_orders"] if o["id"] == order_id), None)
    if not target:
        return False, "سفارش یافت نشد."
    if target["status"] == "done":
        return False, "این سفارش قبلاً تکمیل شده."
    target["status"] = "done"
    save_data(data)
    send(target["user_id"],
        f"*✅ سفارش طراحی عکس شما تکمیل شد!\n\n"
        f"🆔 {target['id']}\n"
        f"🎨 عکس طراحی شده به آیدی {target['bale_id']} ارسال شد.\n\n"
        f"ممنون از اعتمادت! 💖\n"
        f"📞 پشتیبانی: @ARKA_SUPPORT_IR*"
    )
    return True, target

def reject_design_order(order_id, data):
    target = next((o for o in data["design_orders"] if o["id"] == order_id), None)
    if not target:
        return False, "سفارش یافت نشد."
    target["status"] = "rejected"
    save_data(data)
    send(target["user_id"],
        f"*❌ متأسفانه سفارش طراحی شما رد شد.\n\n"
        f"🆔 {target['id']}\n\n"
        f"برای اطلاعات بیشتر با پشتیبانی تماس بگیرید:\n"
        f"📞 @ARKA_SUPPORT_IR*"
    )
    return True, target

# ══════════════════════════════════════════
#  جوین اجباری
# ══════════════════════════════════════════
FJ_PRICES = {1:5000, 2:10000, 3:15000, 4:20000, 5:25000,
             6:30000, 7:35000, 8:40000, 9:45000, 10:50000}

def send_forced_join_menu(chat_id):
    data  = load_data()
    pph   = data["settings"].get("forced_join_price_per_hour", 5000)
    lines = "\n".join([f"⏳ {h} ساعته | 💰 {h*pph:,} تومان" for h in range(1, 11)])
    send(chat_id,
        f"*📱 ثبت جوین اجباری\n\n"
        f"🔥 تعرفه‌های ویژه «جوین اجباری ایران» 🔥\n\n"
        f"برای رشد کانالت، زمان رو انتخاب کن و بترکون! 🚀\n\n"
        f"{lines}\n\n"
        f"━━━━━━━━━━━━\n"
        f"🔢 تعداد ساعت موردنظر را وارد کنید (۱ تا ۱۰):*",
        BACK_BTN_USER
    )

# ══════════════════════════════════════════
#  بازی‌ها / Games
# ══════════════════════════════════════════
GAME_WORDS = [
    "خانه","کتاب","درخت","آسمان","زمین","ماهی","پرنده","گربه",
    "مدرسه","پارک","بازار","آتش","باد","برف","باران","ستاره",
    "ماه","خورشید","ابر","کوه","رودخانه","دریا","جنگل","شهر",
    "نان","برنج","چای","قهوه","کفش","لباس","کیف","ساعت",
    "ماشین","قطار","موتور","پنجره","میز","صندلی","تخت","دیوار",
    "گل","برگ","میوه","سیب","موز","انگور","هندوانه","توت"
]

def send_games_menu(chat_id):
    send(chat_id,
        "*🧩 سرگرمی‌ها\n\n"
        "به بخش بازی‌ها خوش آمدی! 🎮\n\n"
        "یک بازی انتخاب کن و بزن بریم:*",
        kb(
            ["🎲 تاس بازی",        "🔢 حدس عدد"],
            ["🔤 حدس کلمه",        "🪨 سنگ کاغذ قیچی"],
            ["🧮 محاسبه سریع"],
            ["🔙 بازگشت به منوی اصلی 🏠"]
        )
    )

# ── تاس ───────────────────────────────────────────────────────
def start_dice_game(chat_id):
    states[str(chat_id)] = "game_dice|0|0|1"
    send(chat_id,
        "*🎲 تاس بازی!\n\n"
        "تو و ربات هر دور یه تاس می‌اندازید.\n"
        "عدد بالاتر برنده‌ست — بهترین ۲ از ۳ قهرمانه! 🏆*",
        {"inline_keyboard": [[{"text": "🎲 بینداز تاس!", "callback_data": "game_dice_roll"}]]}
    )

def process_dice_roll(chat_id):
    uid   = str(chat_id)
    state = states.get(uid, "")
    parts = state.split("|")
    if len(parts) != 4: return
    _, uw, bw, rnd = parts
    uw, bw, rnd = int(uw), int(bw), int(rnd)
    ur = random.randint(1, 6)
    br = random.randint(1, 6)
    faces = ["","⚀","⚁","⚂","⚃","⚄","⚅"]
    if ur > br:   uw += 1; res = f"🎉 بردی! {faces[ur]} > {faces[br]}"
    elif br > ur: bw += 1; res = f"😅 باختی! {faces[ur]} < {faces[br]}"
    else:                   res = f"🤝 مساوی! {faces[ur]} = {faces[br]}"
    if uw == 2:
        states.pop(uid, None)
        send(chat_id, f"*{res}\n\n🏆 قهرمان شدی! امتیاز: {uw}-{bw}*",
             kb(["🎲 بازی مجدد", "🔙 بازگشت به منوی اصلی 🏠"])); return
    if bw == 2:
        states.pop(uid, None)
        send(chat_id, f"*{res}\n\n💔 ربات برنده شد! امتیاز: {uw}-{bw}*",
             kb(["🎲 بازی مجدد", "🔙 بازگشت به منوی اصلی 🏠"])); return
    rnd += 1
    states[uid] = f"game_dice|{uw}|{bw}|{rnd}"
    send(chat_id, f"*{res}\n\nامتیاز: تو {uw} | ربات {bw}\nدور {rnd}:*",
         {"inline_keyboard": [[{"text": "🎲 بینداز تاس!", "callback_data": "game_dice_roll"}]]})

# ── حدس عدد ──────────────────────────────────────────────────
def send_number_game_menu(chat_id):
    send(chat_id,
        "*🔢 حدس عدد\n\n"
        "یک عدد رو حدس بزن!\n"
        "بعد از هر حدس می‌گم بزرگتره یا کوچیکتره.\n\n"
        "سطح رو انتخاب کن:*",
        kb(
            ["🟢 آسان (۱-۲۰، ۷ شانس)"],
            ["🟡 متوسط (۱-۵۰، ۶ شانس)"],
            ["🔴 سخت (۱-۱۰۰، ۵ شانس)"],
            ["🔙 بازگشت"]
        )
    )

def start_number_game(chat_id, level):
    cfg = {"easy": (1,20,7,"آسان"), "medium": (1,50,6,"متوسط"), "hard": (1,100,5,"سخت")}
    mn, mx, att, label = cfg[level]
    secret = random.randint(mn, mx)
    states[str(chat_id)] = f"game_number|{secret}|{att}|{mn}|{mx}"
    send(chat_id,
        f"*🔢 سطح {label}\n\n"
        f"یه عدد بین {mn} تا {mx} انتخاب کردم!\n"
        f"🎯 {att} شانس داری.\n\nعددت رو بفرست:*",
        BACK_BTN_USER
    )

def process_number_guess(chat_id, text):
    uid   = str(chat_id)
    parts = states.get(uid, "").split("|")
    if len(parts) != 5: return
    _, secret, att, mn, mx = parts
    secret, att, mn, mx = int(secret), int(att), int(mn), int(mx)
    try:    guess = int(text.strip())
    except: send(chat_id, "*⚠️ فقط عدد بفرست!*"); return
    if guess < mn or guess > mx:
        send(chat_id, f"*⚠️ عدد باید بین {mn} تا {mx} باشه!*"); return
    att -= 1
    if guess == secret:
        states.pop(uid, None)
        send(chat_id, f"*🎉 آفرین! عدد {secret} بود! 🏆*",
             kb(["🔢 بازی مجدد", "🔙 بازگشت به منوی اصلی 🏠"])); return
    if att <= 0:
        states.pop(uid, None)
        send(chat_id, f"*💔 تموم شد! عدد {secret} بود!*",
             kb(["🔢 بازی مجدد", "🔙 بازگشت به منوی اصلی 🏠"])); return
    hint = "🔼 بزرگتره!" if secret > guess else "🔽 کوچیکتره!"
    states[uid] = f"game_number|{secret}|{att}|{mn}|{mx}"
    send(chat_id, f"*{hint}\n\n🎯 {att} شانس باقی مونده.*")

# ── حدس کلمه ─────────────────────────────────────────────────
def start_word_game(chat_id):
    word = random.choice(GAME_WORDS)
    states[str(chat_id)] = f"game_word|{word}||0"
    _show_word(chat_id, word, set(), 0)

def _show_word(chat_id, word, guessed, wrong_count):
    MAX_WRONG = 6
    display = " ".join([c if c in guessed else "_" for c in word])
    wrongs  = [c for c in guessed if c not in word]
    hearts  = "❤️" * (MAX_WRONG - wrong_count) + "🖤" * wrong_count
    send(chat_id,
        f"*🔤 حدس کلمه\n\n"
        f"{hearts}\n\n"
        f"کلمه: {display}\n"
        f"حروف اشتباه: {' '.join(wrongs) if wrongs else '—'}\n\n"
        f"یک حرف فارسی بفرست:*"
    )

def process_word_guess(chat_id, text):
    MAX_WRONG = 6
    uid   = str(chat_id)
    parts = states.get(uid, "").split("|")
    if len(parts) != 4: return
    _, word, gs, wrong_count = parts
    wrong_count = int(wrong_count)
    guessed     = set(gs) if gs else set()
    letter      = text.strip()
    if len(letter) != 1:
        send(chat_id, "*⚠️ فقط یک حرف بفرست!*"); return
    if letter in guessed:
        send(chat_id, f"*⚠️ «{letter}» رو قبلاً گفتی!*"); return
    guessed.add(letter)
    if letter not in word: wrong_count += 1
    states[uid] = f"game_word|{word}|{''.join(guessed)}|{wrong_count}"
    if all(c in guessed for c in word):
        states.pop(uid, None)
        send(chat_id, f"*🎉 آفرین! کلمه «{word}» رو پیدا کردی! 🏆*",
             kb(["🔤 بازی مجدد", "🔙 بازگشت به منوی اصلی 🏠"])); return
    if wrong_count >= MAX_WRONG:
        states.pop(uid, None)
        send(chat_id, f"*💔 تموم شد! کلمه «{word}» بود!*",
             kb(["🔤 بازی مجدد", "🔙 بازگشت به منوی اصلی 🏠"])); return
    _show_word(chat_id, word, guessed, wrong_count)

# ── سنگ کاغذ قیچی ────────────────────────────────────────────
def send_rps_game(chat_id):
    states[str(chat_id)] = "game_rps|0|0|1"
    _send_rps(chat_id, 0, 0, 1)

def _send_rps(chat_id, uw, bw, rnd):
    send(chat_id,
        f"*🪨 سنگ کاغذ قیچی\n\nامتیاز: تو {uw} | ربات {bw}\nدور {rnd} از ۳:*",
        {"inline_keyboard": [[
            {"text": "🪨",  "callback_data": "rps|rock"},
            {"text": "📄", "callback_data": "rps|paper"},
            {"text": "✂️", "callback_data": "rps|scissors"}
        ]]}
    )

def process_rps(chat_id, choice):
    uid   = str(chat_id)
    parts = states.get(uid, "").split("|")
    if len(parts) != 4: return
    _, uw, bw, rnd = parts
    uw, bw, rnd = int(uw), int(bw), int(rnd)
    bc    = random.choice(["rock","paper","scissors"])
    icons = {"rock":"🪨 سنگ","paper":"📄 کاغذ","scissors":"✂️ قیچی"}
    wins  = {("rock","scissors"),("paper","rock"),("scissors","paper")}
    if choice == bc:         res = "🤝 مساوی!"
    elif (choice,bc) in wins: uw += 1; res = "🎉 بردی!"
    else:                     bw += 1; res = "😅 باختی!"
    msg = f"*تو: {icons[choice]} | ربات: {icons[bc]}\n{res}*"
    if uw == 2:
        states.pop(uid, None)
        send(chat_id, f"{msg}\n\n*🏆 قهرمان شدی! {uw}-{bw}*",
             kb(["🪨 بازی مجدد","🔙 بازگشت به منوی اصلی 🏠"])); return
    if bw == 2:
        states.pop(uid, None)
        send(chat_id, f"{msg}\n\n*💔 ربات برنده شد! {uw}-{bw}*",
             kb(["🪨 بازی مجدد","🔙 بازگشت به منوی اصلی 🏠"])); return
    rnd += 1
    states[uid] = f"game_rps|{uw}|{bw}|{rnd}"
    send(chat_id, msg)
    _send_rps(chat_id, uw, bw, rnd)

# ── محاسبه سریع ───────────────────────────────────────────────
def _gen_math():
    op = random.choice(["+","-","×"])
    if op == "+":
        a,b = random.randint(1,50), random.randint(1,50)
        return f"{a} + {b}", a+b
    elif op == "-":
        a,b = random.randint(10,99), random.randint(1,10)
        return f"{a} - {b}", a-b
    else:
        a,b = random.randint(2,12), random.randint(2,12)
        return f"{a} × {b}", a*b

def start_math_game(chat_id):
    q,a = _gen_math()
    states[str(chat_id)] = f"game_math|{a}|0|1"
    send(chat_id,
        f"*🧮 محاسبه سریع\n\n"
        f"۱۰ سوال داری — هر جواب درست ۱ امتیاز!\n\n"
        f"سوال ۱/۱۰:\n{q} = ؟*",
        BACK_BTN_USER
    )

def process_math(chat_id, text):
    uid   = str(chat_id)
    parts = states.get(uid,"").split("|")
    if len(parts) != 4: return
    _, correct, score, qnum = parts
    correct, score, qnum = int(correct), int(score), int(qnum)
    try:    ans = int(text.strip())
    except: send(chat_id, "*⚠️ فقط عدد بفرست!*"); return
    fb = "✅ آفرین!" if ans == correct else f"❌ اشتباه! جواب {correct} بود."
    if ans == correct: score += 1
    if qnum >= 10:
        states.pop(uid, None)
        stars = "⭐" * (score // 2) or "—"
        send(chat_id, f"*{fb}\n\n🏁 بازی تموم شد!\nامتیاز: {score}/۱۰ {stars}*",
             kb(["🧮 بازی مجدد","🔙 بازگشت به منوی اصلی 🏠"])); return
    q,a = _gen_math()
    qnum += 1
    states[uid] = f"game_math|{a}|{score}|{qnum}"
    send(chat_id, f"*{fb}\n\nسوال {qnum}/۱۰:\n{q} = ؟\n\nامتیاز: {score}*")

# ══════════════════════════════════════════
#  گردونه تخفیف روزانه
# ══════════════════════════════════════════
import string as _string

def get_iran_today():
    return get_iran_now().strftime("%Y-%m-%d")

def _generate_code(data):
    while True:
        code = "ARKA-" + "".join(random.choices(_string.ascii_uppercase + _string.digits, k=6))
        if code not in data.get("discount_codes", {}):
            return code

def send_spin_wheel(chat_id):
    data  = load_data()
    uid   = str(chat_id)
    u     = data["users"].get(uid, {})
    today = get_iran_today()

    # قبلاً امروز چرخوندی؟
    if u.get("last_spin") == today:
        ac = u.get("active_discount_code", "")
        if ac and ac in data["discount_codes"] and not data["discount_codes"][ac].get("used"):
            dc = data["discount_codes"][ac]
            send(chat_id,
                f"*🎡 امروز گردونه زدی!\n\n"
                f"کد تخفیف فعالت:\n"
                f"🎟️ `{ac}`\n"
                f"💰 {dc['percent']}٪ تخفیف\n\n"
                f"موقع خرید ازش استفاده کن!*",
                {"inline_keyboard": [[{"text": f"📋 کپی کد تخفیف", "copy_text": {"text": ac}}]]}
            )
            send(chat_id, "👇", BACK_BTN_USER)
        else:
            send(chat_id,
                "*🎡 امروز گردونه زدی!\n\nفردا بعد از ۱۲ شب دوباره بیا! 🌙*",
                BACK_BTN_USER
            )
        return

    # کد تخفیف استفاده نشده از قبل داری؟
    ac = u.get("active_discount_code", "")
    if ac and ac in data["discount_codes"] and not data["discount_codes"][ac].get("used"):
        dc = data["discount_codes"][ac]
        send(chat_id,
            f"*⚠️ کد تخفیف قبلیت رو هنوز استفاده نکردی!\n\n"
            f"🎟️ کد: `{ac}`\n"
            f"💰 {dc['percent']}٪ تخفیف\n\n"
            f"اول این کد رو موقع خرید استفاده کن، بعد گردونه بزن.*",
            {"inline_keyboard": [[{"text": "📋 کپی کد", "copy_text": {"text": ac}}]]}
        )
        send(chat_id, "👇", BACK_BTN_USER)
        return

    # بزن بریم!
    percent = random.randint(1, 10)
    code    = _generate_code(data)
    data["discount_codes"][code] = {
        "user_id":   chat_id,
        "percent":   percent,
        "created":   today,
        "used":      False,
        "used_date": None,
        "used_order": None
    }
    data["users"][uid]["last_spin"]            = today
    data["users"][uid]["active_discount_code"] = code
    save_data(data)

    # انیمیشن چرخش
    slices = ["🟥1%","🟧2%","🟨3%","🟩4%","🟦5%","🟪6%","⬛7%","🟫8%","⬜9%","🔴10%"]
    send(chat_id, f"*🎡 گردونه در حال چرخش...\n\n{'  '.join(slices)}*")
    time.sleep(1)
    send(chat_id,
        f"*🎉 تبریک! {percent}٪ تخفیف گرفتی!\n\n"
        f"━━━━━━━━━━━━\n"
        f"🎟️ کد تخفیف: `{code}`\n"
        f"💰 {percent}٪ تخفیف برای یک خرید\n"
        f"⚠️ تا استفاده نکردی نمی‌تونی دوباره بزنی\n"
        f"━━━━━━━━━━━━\n\n"
        f"موقع خرید کدت رو وارد کن! 🛒*",
        {"inline_keyboard": [[{"text": "📋 کپی کد تخفیف", "copy_text": {"text": code}}]]}
    )
    send(chat_id, "👇", BACK_BTN_USER)

def check_and_apply_discount(chat_id, code, price):
    """اعتبارسنجی کد تخفیف. برمی‌گردونه (percent, discounted_price) یا (0, price)"""
    data = load_data()
    code = code.strip().upper()
    dc   = data["discount_codes"].get(code)
    if not dc:
        return None, price, "❌ کد تخفیف معتبر نیست."
    if dc.get("used"):
        return None, price, "❌ این کد قبلاً استفاده شده."
    if str(dc.get("user_id")) != str(chat_id):
        return None, price, "❌ این کد متعلق به شما نیست."
    percent         = dc["percent"]
    discounted      = int(price * (100 - percent) / 100)
    return percent, discounted, f"✅ کد معتبر! {percent}٪ تخفیف اعمال شد."

def use_discount_code(code, order_id):
    """کد رو استفاده‌شده علامت‌گذاری کن"""
    data = load_data()
    if code in data["discount_codes"]:
        data["discount_codes"][code]["used"]       = True
        data["discount_codes"][code]["used_date"]  = get_iran_today()
        data["discount_codes"][code]["used_order"] = order_id
        uid = str(data["discount_codes"][code]["user_id"])
        if uid in data["users"]:
            data["users"][uid]["active_discount_code"] = ""
        save_data(data)

def send_referral_menu(chat_id):
    data  = load_data()
    uid   = str(chat_id)
    u     = data["users"].get(uid, {})
    refs  = u.get("referrals", [])
    used  = u.get("fj_free_used_hours", 0)
    refs_per = data["settings"].get("fj_free_refs_per_hour", 3)
    hrs_per  = data["settings"].get("fj_free_hours_per_batch", 1)
    total_earned = (len(refs) // refs_per) * hrs_per
    available    = total_earned - used
    ref_link = f"https://ble.ir/{BOT_USERNAME}?start={chat_id}"
    send(chat_id,
        f"*👥 زیرمجموعه‌گیری\n\n"
        f"━━━━━━━━━━━━\n\n"
        f"🎁 با دعوت دوستان، جوین اجباری رایگان بگیر!\n\n"
        f"📌 قانون:\n"
        f"هر *{refs_per} زیرمجموعه* = *{hrs_per} ساعت* جوین اجباری رایگان\n\n"
        f"━━━━━━━━━━━━\n\n"
        f"👥 زیرمجموعه‌های تو: *{len(refs)} نفر*\n"
        f"⏳ ساعت رایگان کسب‌شده: *{total_earned} ساعت*\n"
        f"✅ ساعت رایگان باقی‌مانده: *{available} ساعت*\n\n"
        f"━━━━━━━━━━━━\n\n"
        f"🔗 لینک اختصاصی تو:\n"
        f"`{ref_link}`\n\n"
        f"👇 دکمه زیر را بزن تا لینک کپی شود:*",
        {"inline_keyboard": [
            [{"text": "📋 رونوشت پیوند زیرمجموعه‌گیری", "copy_text": {"text": ref_link}}],
            [{"text": "🔙 بازگشت به منوی اصلی 🏠", "callback_data": "go_home"}]
        ]}
    )

def send_fj_free_menu(chat_id):
    data  = load_data()
    uid   = str(chat_id)
    u     = data["users"].get(uid, {})
    refs  = u.get("referrals", [])
    used  = u.get("fj_free_used_hours", 0)
    refs_per = data["settings"].get("fj_free_refs_per_hour", 3)
    hrs_per  = data["settings"].get("fj_free_hours_per_batch", 1)
    total_earned = (len(refs) // refs_per) * hrs_per
    available    = total_earned - used
    if available <= 0:
        needed = refs_per - (len(refs) % refs_per)
        send(chat_id,
            f"*🎁 جوین اجباری رایگان\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"⚠️ ساعت رایگانی برای استفاده نداری!\n\n"
            f"👥 زیرمجموعه‌های تو: {len(refs)} نفر\n"
            f"📌 برای ساعت بعدی: *{needed} زیرمجموعه* دیگر لازم داری\n\n"
            f"👇 لینکت رو بفرست و دوستانت رو دعوت کن:*",
            BACK_BTN_USER
        )
        return
    send(chat_id,
        f"*🎁 جوین اجباری رایگان\n\n"
        f"━━━━━━━━━━━━\n\n"
        f"✅ ساعت رایگان باقی‌مانده: *{available} ساعت*\n\n"
        f"⏳ چند ساعت جوین اجباری رایگان می‌خوای؟\n"
        f"(حداکثر {available} ساعت)*",
        BACK_BTN_USER
    )

def send_forced_join_menu(chat_id):
    data  = load_data()
    pph   = data["settings"].get("forced_join_price_per_hour", 5000)
    lines = "\n".join([f"⏳ {h} ساعته | 💰 {h*pph:,} تومان" for h in range(1, 11)])
    send(chat_id,
        f"*📱 ثبت جوین اجباری\n\n"
        f"🔥 تعرفه‌های ویژه «جوین اجباری ایران» 🔥\n\n"
        f"برای رشد کانالت، زمان رو انتخاب کن و بترکون! 🚀\n\n"
        f"{lines}\n\n"
        f"━━━━━━━━━━━━\n"
        f"🔢 تعداد ساعت موردنظر را وارد کنید (۱ تا ۱۰):*",
        kb(
            ["🎁 جوین اجباری رایگان"],
            ["🔙 بازگشت به منوی اصلی 🏠"]
        )
    )
    data  = load_data()
    pph   = data["settings"].get("forced_join_price_per_hour", 5000)
    price = hours * pph
    data["forced_join_order_counter"] = data.get("forced_join_order_counter", 0) + 1
    oid   = data["forced_join_order_counter"]
    order_id = f"FJ{oid}"
    data["forced_join_orders"].append({
        "id":      order_id,
        "user_id": chat_id,
        "hours":   hours,
        "link":    link,
        "price":   price,
        "status":  "pending_payment",
        "date":    datetime.now().isoformat(),
        "end_time": ""
    })
    save_data(data)
    result = requests.post(f"{BASE_URL}/sendInvoice", json={
        "chat_id":        chat_id,
        "title":          f"📱 جوین اجباری {hours} ساعته",
        "description":    f"📱 جوین اجباری\n⏳ مدت: {hours} ساعت\n🔗 لینک: {link}\n🔖 سفارش: {order_id}",
        "photo_url":      "https://i.postimg.cc/TPZvJb24/9c952dff-0225-4ee4-a6c8-856abce59e5f.png",
        "provider_token": PROVIDER_TOKEN,
        "currency":       "IRR",
        "prices":         [{"label": f"جوین اجباری {hours} ساعته", "amount": price * 10}],
        "start_parameter": "pay"
    }, timeout=15).json()
    if not result.get("ok"):
        err = result.get("description", "نامشخص")
        send(chat_id, f"*❌ خطا در ارسال فاکتور!\n\n🔴 {err}\n\nبا پشتیبانی تماس بگیرید: @ARKA_SUPPORT_IR*")

def register_fj_payment(chat_id, payload):
    data = load_data()
    order_num = None
    try:
        order_num = int(payload.replace("fj_", ""))
    except:
        pass
    target = None
    for o in data["forced_join_orders"]:
        if o["id"] == f"FJ{order_num}" and o["user_id"] == chat_id and o["status"] == "pending_payment":
            target = o; break
    if not target:
        for o in reversed(data["forced_join_orders"]):
            if o["user_id"] == chat_id and o["status"] == "pending_payment":
                target = o; break
    if target:
        target["status"] = "pending"
        today = get_today()
        data["stats"]["total_orders"]  += 1
        data["stats"]["total_revenue"] += target["price"]
        uid = str(chat_id)
        if uid in data["users"]:
            data["users"][uid]["orders"]      = data["users"][uid].get("orders", 0) + 1
            data["users"][uid]["total_spent"] = data["users"][uid].get("total_spent", 0) + target["price"]
        if today not in data["stats"]["daily_stats"]:
            data["stats"]["daily_stats"][today] = {"orders": 0, "revenue": 0}
        data["stats"]["daily_stats"][today]["orders"]  += 1
        data["stats"]["daily_stats"][today]["revenue"] += target["price"]
        save_data(data)
        send(chat_id,
            f"*🎉 پرداخت موفق! سفارش جوین اجباری ثبت شد!\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"🆔 شماره سفارش: {target['id']}\n"
            f"⏳ مدت: {target['hours']} ساعت\n"
            f"🔗 لینک: {target['link']}\n"
            f"💰 مبلغ: {target['price']:,} تومان\n\n"
            f"⏳ سفارش در حال بررسی است.\n"
            f"💌 پشتیبانی: @ARKA_SUPPORT_IR*"
        )
        uname = data["users"].get(str(chat_id), {}).get("username", "")
        un_str = f"@{uname}" if uname else str(chat_id)
        for aid in ADMIN_IDS:
            send(aid,
                f"*📱 سفارش جوین اجباری جدید!\n\n"
                f"🆔 {target['id']}\n"
                f"👤 {un_str} | آیدی: {chat_id}\n"
                f"⏳ مدت: {target['hours']} ساعت\n"
                f"🔗 لینک: {target['link']}\n"
                f"💰 {target['price']:,} تومان*",
                {"inline_keyboard": [
                    [{"text": "✅ تأیید و ثبت کانال", "callback_data": f"approve_fj|{target['id']}"}],
                    [{"text": "❌ رد سفارش",          "callback_data": f"reject_fj|{target['id']}"}]
                ]}
            )
    else:
        send(chat_id, "*✅ پرداخت انجام شد!\n\n⏳ سفارش جوین اجباری در حال پردازش است.\n💌 @ARKA_SUPPORT_IR*")

# ══════════════════════════════════════════
#  ORDER (ممبر/بازدید)
# ══════════════════════════════════════════
def send_platform(chat_id):
    send(chat_id,
        "*👁️ بزن بریم برای رشد! سفارش بازدید شروع شد… 🚀✨\n\n"
        "━━━━━━━━━━━━\n\n"
        "خب رفیق! حالا وقتشه که مشخص کنیم قراره کجا رو بترکونیم! 😍💥\n\n"
        "لطفاً پلتفرم مورد نظرت رو انتخاب کن تا با سرعت جت شروع کنیم: 👇🌈*",
        kb(
            ["🔵 سفارش بازدید | بله 🚀"],
            ["🔴 سفارش بازدید | روبیکا ⚡️"],
            ["🟢 سفارش بازدید | ایتا ☕️"],
            ["🔙 بازگشت به منوی اصلی 🏠"]
        )
    )

def send_bale_services(chat_id):
    data = load_data()
    s    = data["settings"]
    rows = []
    if s["bale_view_single"]["enabled"]:
        rows.append(["بازدید تکی 👁️"])
    if s["bale_reaction"]["enabled"]:
        rows.append(["ری‌اکشن بله ❤️"])
    rows.append(["🔙 بازگشت به منوی اصلی 🏠"])
    send(chat_id,
        "*✨ بزن بریم برای شروع! چه نوع سرویسی می‌خوای؟ ✨\n\n"
        "━━━━━━━━━━━━\n\n"
        "🔹 بازدید تکی 🎯 | (فقط برای یک پست خاص که خودت انتخاب می‌کنی)\n\n"
        "🔹 ری‌اکشن بله ❤️ | (به پست‌هات با کلی ری‌اکشن و عشق برس!)\n\n"
        "👇 یکی رو انتخاب کن تا شروع کنیم:*",
        kb(*rows)
    )

def send_member_platform(chat_id):
    send(chat_id,
        "*👥 بزن بریم برای رشد! سفارش ممبر شروع شد… 🚀✨\n\n"
        "━━━━━━━━━━━━\n\n"
        "خب رفیق! لطفاً پلتفرم مورد نظرت رو انتخاب کن: 👇🌈*",
        kb(
            ["🔵 سفارش ممبر | بله 🚀"],
            ["🔴 سفارش ممبر | روبیکا ⚡️"],
            ["🟢 سفارش ممبر | ایتا ☕️"],
            ["🟣 سفارش فالوور | روبیکا 🔥"],
            ["🔙 بازگشت به منوی اصلی 🏠"]
        )
    )

def send_service_info(chat_id, key):
    data = load_data()
    s    = data["settings"][key]
    INFO = {
        "bale_view_single": ("👁️", "افزایش سین برای پست دلخواه کانال بله", "بازدید",
            "✅ - فقط برای کانال‌ها و پست‌های بله\n👁️ - نوع: بازدید/سین پست\n⚡ - زمان انجام: آنی\n🛡️ - ریزش: ندارد یا بسیار کم"),
        "bale_reaction":    ("❤️", "افزایش ری‌اکشن برای پست‌های بله", "ری‌اکشن",
            "✅ - فقط برای کانال‌ها و پست‌های بله\n❤️ - ری‌اکشن روی پست\n⚡ - زمان انجام: آنی\n🛡️ - ریزش: ندارد یا بسیار کم"),
        "rubika_view":      ("👁️", "افزایش سین برای پست دلخواه کانال روبیکا", "بازدید",
            "✅ - مخصوص روبیکا/روبینو\n🇮🇷 - کیفیت: ایرانی\n⚡ - زمان انجام: سریع\n↘️ - ریزش: ممکن است داشته باشد"),
        "eitaa_view":       ("👁️", "افزایش سین (بازدید) پست کانال ایتا", "بازدید",
            "✅ - مخصوص ایتا\n🇮🇷 - کیفیت: ایرانی\n⚡ - زمان انجام: سریع\n↘️ - ریزش: ممکن است داشته باشد"),
        "bale_member":      ("👥", "افزایش عضو کانال بله", "ممبر",
            "✅ - فقط برای کانال‌های بله\n🇮🇷 - کیفیت: اجباری ایرانی\n👁️ - بازدید: پایین\n⚡ - زمان انجام: آنی\n↘️ - ریزش: دارد"),
        "rubika_member":    ("👥", "افزایش عضو (ممبر) کانال روبیکا", "ممبر",
            "✅ - مخصوص روبیکا/روبینو\n🇮🇷 - کیفیت: ایرانی\n⚡ - زمان انجام: سریع\n↘️ - ریزش: ممکن است داشته باشد"),
        "eitaa_member":     ("👥", "افزایش عضو (ممبر) کانال ایتا", "ممبر",
            "✅ - مخصوص ایتا\n🇮🇷 - کیفیت: ایرانی\n⚡ - زمان انجام: سریع\n↘️ - ریزش: ممکن است داشته باشد"),
        "rubika_follower":  ("👥", "افزایش فالوور روبیکا (روبینو)", "فالوور",
            "✅ - مخصوص روبیکا/روبینو\n🇮🇷 - کیفیت: ایرانی\n⚡ - زمان انجام: سریع\n↘️ - ریزش: ممکن است داشته باشد"),
    }
    icon, title, unit, notes = INFO.get(key, ("📦", key, "عدد", ""))
    send(chat_id,
        f"*{icon} {title}\n"
        f"• حداقل: {s['min']:,}  |  حداکثر: {s['max']:,}\n"
        f"• قیمت هر ۱۰۰۰ {unit}: {s['price_per_1000']:,} تومان\n\n"
        f"📌 نکات\n{notes}\n\n"
        f"⚠️ در هر بار سفارش از {s['min']:,} تا {s['max']:,} {unit} می‌توانید ثبت کنید\n\n"
        f"🔢 تعداد {unit} موردنظر را ارسال کنید:*",
        BACK_BTN_USER
    )

def check_stock_and_start(chat_id, key, data, states):
    s = data["settings"].get(key, {})
    if not s.get("enabled", True):
        send(chat_id, "*⚠️ این سرویس موقتاً غیرفعال است.*")
        return
    stock = s.get("stock", 999999)
    if stock <= 0:
        send(chat_id, "*⚠️ موجودی این سرویس تمام شده. لطفاً بعداً مراجعه کنید.*")
        return
    states[str(chat_id)] = f"order_qty|{key}"
    send_service_info(chat_id, key)

def send_invoice(chat_id, key, qty, price, link, discount_code=""):
    data = load_data()
    data["order_counter"] = data.get("order_counter", 0) + 1
    oid  = data["order_counter"]
    data["orders"].append({
        "id":             f"ORK{oid}",
        "user_id":        chat_id,
        "service":        SVCLABEL[key],
        "key":            key,
        "amount":         qty,
        "price":          price,
        "link":           link,
        "status":         "pending_payment",
        "discount_code":  discount_code,
        "date":           datetime.now().isoformat()
    })
    save_data(data)
    desc = f"📦 سرویس: {SVCLABEL[key]}\n🔢 تعداد: {qty:,}\n🔗 لینک: {link}\n🆔 سفارش: ORK{oid}"
    if discount_code:
        pct = data["discount_codes"].get(discount_code, {}).get("percent", 0)
        desc += f"\n🎟️ تخفیف: {pct}٪ ({discount_code})"
    result = requests.post(f"{BASE_URL}/sendInvoice", json={
        "chat_id":        chat_id,
        "title":          f"🛒 {SVCLABEL[key]}",
        "description":    desc,
        "photo_url":      "https://i.postimg.cc/TPZvJb24/9c952dff-0225-4ee4-a6c8-856abce59e5f.png",
        "payload":        f"order_{oid}",
        "provider_token": PROVIDER_TOKEN,
        "currency":       "IRR",
        "prices":         [{"label": SVCLABEL[key], "amount": price * 10}],
        "start_parameter": "pay"
    }, timeout=15).json()
    if not result.get("ok"):
        err = result.get("description", "نامشخص")
        send(chat_id, f"*❌ خطا در ارسال فاکتور!\n\n🔴 {err}\n\nبا پشتیبانی تماس بگیرید: @ARKA_SUPPORT_IR*")

def register_successful_order(chat_id, payload):
    data      = load_data()
    order_num = None
    try:
        order_num = int(payload.replace("order_", ""))
    except:
        pass
    target = None
    for o in data["orders"]:
        if o["id"] == f"ORK{order_num}" and o["user_id"] == chat_id and o["status"] == "pending_payment":
            target = o
            break
    if not target:
        for o in reversed(data["orders"]):
            if o["user_id"] == chat_id and o["status"] == "pending_payment":
                target = o
                break
    if target:
        target["status"] = "pending"
        today = get_today()
        data["stats"]["total_orders"]  += 1
        data["stats"]["total_revenue"] += target["price"]
        uid = str(chat_id)
        if uid in data["users"]:
            data["users"][uid]["orders"]      = data["users"][uid].get("orders", 0) + 1
            data["users"][uid]["total_spent"] = data["users"][uid].get("total_spent", 0) + target["price"]
        if today not in data["stats"]["daily_stats"]:
            data["stats"]["daily_stats"][today] = {"orders": 0, "revenue": 0}
        data["stats"]["daily_stats"][today]["orders"]  += 1
        data["stats"]["daily_stats"][today]["revenue"] += target["price"]
        key = target.get("key", "")
        if key in data["settings"] and isinstance(data["settings"][key], dict):
            cur = data["settings"][key].get("stock", 999999)
            data["settings"][key]["stock"] = max(0, cur - target["amount"])
        # کد تخفیف رو مارک کن
        dc_code = target.get("discount_code", "")
        if dc_code and dc_code in data["discount_codes"]:
            data["discount_codes"][dc_code]["used"]       = True
            data["discount_codes"][dc_code]["used_date"]  = today
            data["discount_codes"][dc_code]["used_order"] = target["id"]
            if uid in data["users"]:
                data["users"][uid]["active_discount_code"] = ""
        save_data(data)
        send(chat_id,
            f"*🎉 پرداخت موفق! سفارش ثبت شد!\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"🆔 شماره سفارش: {target['id']}\n"
            f"📦 سرویس: {target['service']}\n"
            f"🔢 تعداد: {target['amount']:,}\n"
            f"🔗 لینک: {target['link']}\n"
            f"💰 مبلغ: {target['price']:,} تومان\n\n"
            f"⏳ سفارش در حال پردازش است.\n"
            f"💌 پشتیبانی: @ARKA_SUPPORT_IR*"
        )
        for aid in ADMIN_IDS:
            try:
                send(aid,
                    f"*🔔 سفارش جدید!\n\n"
                    f"🆔 {target['id']} | 👤 {chat_id}\n"
                    f"📦 {target['service']} | {target['amount']:,}\n"
                    f"🔗 {target['link']}\n"
                    f"💰 {target['price']:,} تومان*",
                    {"inline_keyboard": [[{"text": "✅ تکمیل سفارش", "callback_data": f"complete|{target['id']}"}]]}
                )
            except:
                pass
    else:
        send(chat_id, "*✅ پرداخت انجام شد!\n\n⏳ سفارش در حال پردازش است.\n💌 @ARKA_SUPPORT_IR*")

def complete_order(order_id):
    data   = load_data()
    target = next((o for o in data["orders"] if o["id"] == order_id), None)
    if not target:
        return False, "سفارش یافت نشد."
    if target["status"] == "done":
        return False, "این سفارش قبلاً تکمیل شده."
    # آپدیت آمار (فقط اگر قبلاً در register_successful_order حساب نشده)
    # register_successful_order آمار رو موقع پرداخت ثبت می‌کنه، پس اینجا دوباره اضافه نمی‌کنیم
    target["status"]       = "done"
    target["completed_at"] = datetime.now().isoformat()
    save_data(data)
    # ارسال به کانال
    masked     = mask_user_id(target["user_id"])
    jalali_now = now_jalali_str()
    channel    = data["settings"]["channel"]
    try:
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id":    channel,
            "text":       f"*✅ گزارش خرید #موفق\n\n"
                          f"📋 اطلاعات سفارش:\n"
                          f"📦 نام سرویس: {target['service']}\n"
                          f"🔢 مقدار: {target['amount']:,}\n"
                          f"💰 قیمت: {target['price']:,} تومان\n"
                          f"👤 شناسه مشتری: {masked}\n"
                          f"🕒 زمان خرید: {jalali_now}*",
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": [[{"text": "ربات ممبر | بازدید ایران 🚀", "url": f"https://ble.ir/{BOT_USERNAME}"}]]}
        }, timeout=10)
    except Exception as e:
        print(f"complete_order channel send error: {e}")
    # اطلاع به کاربر
    try:
        send(target["user_id"],
            f"*✅ سفارش شما تکمیل شد!\n\n"
            f"🆔 {target['id']}\n"
            f"📦 {target['service']}\n"
            f"🔢 {target['amount']:,}\n"
            f"🔗 {target['link']}\n\n"
            f"ممنون از خرید شما 🙏*"
        )
    except Exception as e:
        print(f"complete_order user notify error: {e}")
    return True, target

# ══════════════════════════════════════════
#  ADMIN LOOKUP MAPS
# ══════════════════════════════════════════
PRICE_MAP = {
    "ap_price_bale_view":       ("bale_view_single", "بازدید بله"),
    "ap_price_reaction":        ("bale_reaction",    "ری‌اکشن"),
    "ap_price_rubika_view":     ("rubika_view",      "بازدید روبیکا"),
    "ap_price_eitaa_view":      ("eitaa_view",       "بازدید ایتا"),
    "ap_price_bale_member":     ("bale_member",      "ممبر بله"),
    "ap_price_rubika_member":   ("rubika_member",    "ممبر روبیکا"),
    "ap_price_eitaa_member":    ("eitaa_member",     "ممبر ایتا"),
    "ap_price_rubika_follower": ("rubika_follower",  "فالوور روبیکا"),
}
MM_MAP = {
    "ap_mm_bale_view":       "bale_view_single",
    "ap_mm_reaction":        "bale_reaction",
    "ap_mm_rubika_view":     "rubika_view",
    "ap_mm_eitaa_view":      "eitaa_view",
    "ap_mm_bale_member":     "bale_member",
    "ap_mm_rubika_member":   "rubika_member",
    "ap_mm_eitaa_member":    "eitaa_member",
    "ap_mm_rubika_follower": "rubika_follower",
}
STOCK_MAP = {
    "ap_stock_bale_view":       "bale_view_single",
    "ap_stock_reaction":        "bale_reaction",
    "ap_stock_rubika_view":     "rubika_view",
    "ap_stock_eitaa_view":      "eitaa_view",
    "ap_stock_bale_member":     "bale_member",
    "ap_stock_rubika_member":   "rubika_member",
    "ap_stock_eitaa_member":    "eitaa_member",
    "ap_stock_rubika_follower": "rubika_follower",
}
TOGGLE_MAP = {
    "👁️ بازدید بله روشن/خاموش":     ("bale_view_single", "بازدید بله"),
    "❤️ ری‌اکشن روشن/خاموش":        ("bale_reaction",    "ری‌اکشن"),
    "🔴 بازدید روبیکا روشن/خاموش":  ("rubika_view",      "بازدید روبیکا"),
    "🟢 بازدید ایتا روشن/خاموش":    ("eitaa_view",       "بازدید ایتا"),
    "🔵 ممبر بله روشن/خاموش":        ("bale_member",      "ممبر بله"),
    "🔴 ممبر روبیکا روشن/خاموش":    ("rubika_member",    "ممبر روبیکا"),
    "🟢 ممبر ایتا روشن/خاموش":      ("eitaa_member",     "ممبر ایتا"),
    "🟣 فالوور روبیکا روشن/خاموش":  ("rubika_follower",  "فالوور روبیکا"),
}
MM_BTNS = {
    "🔢 بازدید بله":     "ap_mm_bale_view",
    "🔢 ری‌اکشن":        "ap_mm_reaction",
    "🔢 بازدید روبیکا":  "ap_mm_rubika_view",
    "🔢 بازدید ایتا":    "ap_mm_eitaa_view",
    "🔢 ممبر بله":        "ap_mm_bale_member",
    "🔢 ممبر روبیکا":    "ap_mm_rubika_member",
    "🔢 ممبر ایتا":      "ap_mm_eitaa_member",
    "🔢 فالوور روبیکا":  "ap_mm_rubika_follower",
}
PRICE_BTNS = {
    "💰 نرخ بازدید بله":     "ap_price_bale_view",
    "💰 نرخ ری‌اکشن":        "ap_price_reaction",
    "💰 نرخ بازدید روبیکا":  "ap_price_rubika_view",
    "💰 نرخ بازدید ایتا":    "ap_price_eitaa_view",
    "💰 نرخ ممبر بله":        "ap_price_bale_member",
    "💰 نرخ ممبر روبیکا":    "ap_price_rubika_member",
    "💰 نرخ ممبر ایتا":      "ap_price_eitaa_member",
    "💰 نرخ فالوور روبیکا":  "ap_price_rubika_follower",
}
STOCK_BTNS = {
    "📦 موجودی بازدید بله":     "ap_stock_bale_view",
    "📦 موجودی ری‌اکشن":        "ap_stock_reaction",
    "📦 موجودی بازدید روبیکا":  "ap_stock_rubika_view",
    "📦 موجودی بازدید ایتا":    "ap_stock_eitaa_view",
    "📦 موجودی ممبر بله":        "ap_stock_bale_member",
    "📦 موجودی ممبر روبیکا":    "ap_stock_rubika_member",
    "📦 موجودی ممبر ایتا":      "ap_stock_eitaa_member",
    "📦 موجودی فالوور روبیکا":  "ap_stock_rubika_follower",
}

# ──────────────────────────────────────────────
#  نگاشت‌های فروش سکه برای ادمین
# ──────────────────────────────────────────────
COIN_PRICE_BTNS = {
    "💰 نرخ سکه کانال بله":       "coin_bale_channel",
    "💰 نرخ سکه گروه بله":         "coin_bale_group",
    "💰 نرخ سکه کانال روبیکا":    "coin_rubika_channel",
    "💰 نرخ سکه گروه روبیکا":     "coin_rubika_group",
    "💰 نرخ سکه لایک روبیکا":     "coin_rubika_like",
    "💰 نرخ سکه فالوور روبیکا":   "coin_rubika_follower",
    "💰 نرخ سکه کانال ایتا":      "coin_eitaa_channel",
    "💰 نرخ سکه گروه ایتا":       "coin_eitaa_group",
}
COIN_MM_BTNS = {
    "🔢 حداقل/حداکثر سکه کانال بله":     "coin_bale_channel",
    "🔢 حداقل/حداکثر سکه گروه بله":       "coin_bale_group",
    "🔢 حداقل/حداکثر سکه کانال روبیکا":  "coin_rubika_channel",
    "🔢 حداقل/حداکثر سکه گروه روبیکا":   "coin_rubika_group",
    "🔢 حداقل/حداکثر سکه لایک روبیکا":   "coin_rubika_like",
    "🔢 حداقل/حداکثر سکه فالوور روبیکا": "coin_rubika_follower",
    "🔢 حداقل/حداکثر سکه کانال ایتا":    "coin_eitaa_channel",
    "🔢 حداقل/حداکثر سکه گروه ایتا":     "coin_eitaa_group",
}
COIN_TOGGLE_BTNS = {
    "🔵 سکه کانال بله روشن/خاموش":       "coin_bale_channel",
    "🔵 سکه گروه بله روشن/خاموش":         "coin_bale_group",
    "🔴 سکه کانال روبیکا روشن/خاموش":    "coin_rubika_channel",
    "🔴 سکه گروه روبیکا روشن/خاموش":     "coin_rubika_group",
    "🔴 سکه لایک روبیکا روشن/خاموش":     "coin_rubika_like",
    "🔴 سکه فالوور روبیکا روشن/خاموش":   "coin_rubika_follower",
    "🟢 سکه کانال ایتا روشن/خاموش":      "coin_eitaa_channel",
    "🟢 سکه گروه ایتا روشن/خاموش":       "coin_eitaa_group",
}

# ══════════════════════════════════════════
#  ADMIN PANEL
# ══════════════════════════════════════════
def send_admin_panel(chat_id):
    data   = load_data()
    s      = data["settings"]
    st     = data["stats"]
    td     = st["daily_stats"].get(get_today(), {})
    open_t = sum(1 for t in data["tickets"].values() if t.get("status") == "open")
    closed_t = sum(1 for t in data["tickets"].values() if t.get("status") == "closed")
    pend_coin   = sum(1 for o in data["coin_orders"] if o.get("status") == "pending")
    pend_design = sum(1 for o in data.get("design_orders", []) if o.get("status") == "pending")
    pend_fj     = sum(1 for o in data.get("forced_join_orders", []) if o.get("status") == "pending")
    active_fj   = sum(1 for o in data.get("forced_join_channels", []) if o.get("active", False))
    send(chat_id,
        f"*🔧 پنل مدیریت ربات آرکا\n\n"
        f"━━━━━━━━━━━━\n"
        f"👥 کاربران: {st['total_users']:,}  |  📦 سفارشات: {st['total_orders']:,}\n"
        f"💰 درآمد کل: {st['total_revenue']:,} تومان\n"
        f"📅 امروز: {td.get('orders', 0):,} سفارش | {td.get('revenue', 0):,} تومان\n"
        f"🎫 تیکت باز: {open_t} | بسته: {closed_t}\n"
        f"🪙 سفارشات سکه در انتظار: {pend_coin}\n"
        f"🎨 سفارشات طراحی در انتظار: {pend_design}\n"
        f"📱 جوین اجباری در انتظار: {pend_fj} | فعال: {active_fj}\n"
        f"🔒 جوین اجباری: {'✅' if s['forced_join'] else '❌'}\n"
        f"🤖 وضعیت ربات: {'✅ فعال' if s.get('bot_active', True) else '🔴 غیرفعال'}\n"
        f"━━━━━━━━━━━━\n\n"
        f"👇 یک بخش را انتخاب کنید:*",
        kb(
            ["📊 آمار و گزارشات", "📦 مدیریت سفارشات", "⚙️ مدیریت خدمات"],
            ["💰 نرخ و قیمت‌ها", "📦 مدیریت موجودی", "👥 مدیریت کاربران"],
            ["📨 پیام همگانی", "🔒 جوین اجباری", "📢 تنظیمات کانال"],
            ["🪙 مدیریت فروش سکه", "🎨 مدیریت طراحی عکس"],
            ["📱 مدیریت جوین اجباری"],
            ["🗑️ پاک‌سازی تاریخچه"],
            ["🎫 تیکت‌های باز", "🔴 تیکت‌های بسته"],
            ["🤖 وضعیت ربات", "🎡 مدیریت تخفیف‌ها"],
            ["🏠 خروج از پنل ادمین"]
        )
    )

def send_open_tickets(chat_id, data):
    tickets = [(tid, t) for tid, t in data["tickets"].items() if t.get("status") == "open"]
    if not tickets:
        send(chat_id, "*هیچ تیکت باز فعالی وجود ندارد.*", BACK_BTN)
        return
    send(chat_id, f"*🎫 تیکت‌های باز: {len(tickets)} مورد*")
    for tid, t in tickets[-20:]:
        uname_str = f"@{t['username']}" if t.get("username") else str(t.get("user_id", ""))
        last_msg  = t["messages"][-1]["text"][:80] if t.get("messages") else "-"
        send(chat_id,
            f"*🎫 #{tid} | {t.get('name', '?')} ({uname_str})\n"
            f"💬 {len(t.get('messages', []))} پیام | آخرین: {last_msg}*",
            {"inline_keyboard": [
                [{"text": f"↩️ پاسخ به #{tid}", "callback_data": f"reply_ticket|{tid}"}],
                [{"text": f"🔴 بستن #{tid}",    "callback_data": f"close_ticket|{tid}"}]
            ]}
        )
    send(chat_id, "*👆 تیکت‌های باز*", kb(["🗑️ ریست تیکت‌های باز", "🔙 بازگشت"]))

def send_closed_tickets(chat_id, data):
    tickets = [(tid, t) for tid, t in data["tickets"].items() if t.get("status") == "closed"]
    if not tickets:
        send(chat_id, "*هیچ تیکت بسته‌ای وجود ندارد.*", BACK_BTN)
        return
    send(chat_id, f"*🔴 تیکت‌های بسته: {len(tickets)} مورد*")
    for tid, t in tickets[-20:]:
        uname_str = f"@{t['username']}" if t.get("username") else str(t.get("user_id", ""))
        send(chat_id,
            f"*🔴 #{tid} | {t.get('name', '?')} ({uname_str}) | {len(t.get('messages', []))} پیام*"
        )
    send(chat_id, "*👆 تیکت‌های بسته*", kb(["🗑️ ریست تیکت‌های بسته", "🔙 بازگشت"]))

# ──────────────────────────────────────────────
#  پنل مدیریت فروش سکه
# ──────────────────────────────────────────────
def send_coin_admin_panel(chat_id, data):
    cs = data["settings"]["coin_services"]
    def st(k): return "✅" if cs.get(k, {}).get("enabled", True) else "❌"
    def p(k):  return f"{cs.get(k, {}).get('price_per_1053', 0):,}"
    def mm(k): return f"{cs.get(k, {}).get('min', 200):,}-{cs.get(k, {}).get('max', 3000):,}"
    pend = sum(1 for o in data["coin_orders"] if o.get("status") == "pending")
    appr = sum(1 for o in data["coin_orders"] if o.get("status") == "approved")
    rej  = sum(1 for o in data["coin_orders"] if o.get("status") == "rejected")
    card = data["settings"].get("coin_card_number", "تنظیم نشده")
    send(chat_id,
        f"*🪙 مدیریت فروش سکه\n\n"
        f"━━━━━━━━━━━━\n"
        f"⏳ در انتظار: {pend} | ✅ تأیید: {appr} | ❌ رد: {rej}\n"
        f"💳 شماره کارت: {card}\n"
        f"━━━━━━━━━━━━\n\n"
        f"🔵بله کانال:{st('coin_bale_channel')} {p('coin_bale_channel')}ت | {mm('coin_bale_channel')}\n"
        f"🔵بله گروه:{st('coin_bale_group')} {p('coin_bale_group')}ت\n"
        f"🔴روبیکا کانال:{st('coin_rubika_channel')} {p('coin_rubika_channel')}ت\n"
        f"🔴روبیکا گروه:{st('coin_rubika_group')} {p('coin_rubika_group')}ت\n"
        f"🔴روبیکا لایک:{st('coin_rubika_like')} {p('coin_rubika_like')}ت\n"
        f"🔴روبیکا فالوور:{st('coin_rubika_follower')} {p('coin_rubika_follower')}ت\n"
        f"🟢ایتا کانال:{st('coin_eitaa_channel')} {p('coin_eitaa_channel')}ت\n"
        f"🟢ایتا گروه:{st('coin_eitaa_group')} {p('coin_eitaa_group')}ت*",
        kb(
            ["⏳ سفارشات سکه در انتظار", "✅ سفارشات سکه تأیید شده"],
            ["❌ سفارشات سکه رد شده"],
            ["💰 تغییر نرخ سکه", "🔢 تغییر حداقل/حداکثر سکه"],
            ["🔛 روشن/خاموش سرویس‌های سکه"],
            ["💳 تنظیم شماره کارت ادمین"],
            ["🔙 بازگشت"]
        )
    )

def send_pending_coin_orders(chat_id, data):
    orders = [o for o in data["coin_orders"] if o.get("status") == "pending"]
    if not orders:
        send(chat_id, "*هیچ سفارش سکه در انتظاری وجود ندارد.*", BACK_BTN)
        return
    send(chat_id, f"*⏳ سفارشات سکه در انتظار: {len(orders)}*")
    for o in reversed(orders[-15:]):
        pay_type = "پاکت هدیه" if o.get("payment_type") == "gift" else "کارت به کارت"
        send(chat_id,
            f"*🆔 {o.get('id', '?')}\n"
            f"👤 کاربر: {o.get('user_id', '?')}\n"
            f"📦 {o.get('service_label', '?')}\n"
            f"🪙 {o.get('amount', 0):,} سکه\n"
            f"💰 {o.get('price', 0):,} تومان\n"
            f"📱 {o.get('phone', '?')}\n"
            f"💳 روش: {pay_type}\n"
            f"📋 اطلاعات: {o.get('payment_info', '?')}*",
            {"inline_keyboard": [
                [
                    {"text": f"✅ تأیید {o['id']}", "callback_data": f"approve_coin|{o['id']}"},
                    {"text": f"❌ رد {o['id']}",    "callback_data": f"reject_coin|{o['id']}"}
                ],
                [{"text": f"📤 ارسال به کانال", "callback_data": f"channel_coin|{o['id']}"}]
            ]}
        )
    send(chat_id, "*👆 پایان لیست*", BACK_BTN)

def approve_coin_order(order_id, data):
    for o in data["coin_orders"]:
        if o["id"] == order_id:
            o["status"] = "approved"
            save_data(data)
            # اطلاع به کاربر
            send(o["user_id"],
                f"*✅ سفارش فروش سکه شما تأیید شد!\n\n"
                f"━━━━━━━━━━━━\n"
                f"🆔 {o['id']}\n"
                f"📦 {o.get('service_label', '')}\n"
                f"🪙 {o.get('amount', 0):,} سکه\n"
                f"💰 {o.get('price', 0):,} تومان\n"
                f"━━━━━━━━━━━━\n"
                f"مبلغ به زودی واریز خواهد شد.\n"
                f"📞 پشتیبانی: @ARKA_SUPPORT_IR*"
            )
            return True, o
    return False, None

def reject_coin_order(order_id, data):
    for o in data["coin_orders"]:
        if o["id"] == order_id:
            o["status"] = "rejected"
            save_data(data)
            send(o["user_id"],
                f"*❌ متأسفانه سفارش فروش سکه شما رد شد.\n\n"
                f"🆔 {o['id']}\n"
                f"📦 {o.get('service_label', '')}\n"
                f"🪙 {o.get('amount', 0):,} سکه\n\n"
                f"برای اطلاعات بیشتر با پشتیبانی تماس بگیرید:\n"
                f"📞 @ARKA_SUPPORT_IR*"
            )
            return True, o
    return False, None

def channel_coin_order(order_id, data):
    for o in data["coin_orders"]:
        if o["id"] == order_id:
            channel    = data["settings"]["channel"]
            masked     = mask_user_id(o["user_id"])
            jalali_now = now_jalali_str()
            pay_type   = "پاکت هدیه" if o.get("payment_type") == "gift" else "کارت به کارت"
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id":    channel,
                "text":       f"*✅ گزارش خرید #موفق\n\n"
                              f"📋 اطلاعات سفارش:\n"
                              f"📦 نام سرویس: {o.get('service_label', 'فروش سکه')}\n"
                              f"🔢 مقدار: {o.get('amount', 0):,} سکه\n"
                              f"💰 قیمت: {o.get('price', 0):,} تومان\n"
                              f"👤 شناسه مشتری: {masked}\n"
                              f"🕒 زمان خرید: {jalali_now}*",
                "parse_mode": "Markdown",
                "reply_markup": {"inline_keyboard": [[{"text": "ربات فروش سکه 🪙", "url": f"https://ble.ir/{BOT_USERNAME}"}]]}
            }, timeout=10)
            return True
    return False

# ══════════════════════════════════════════
#  ADMIN HANDLER
# ══════════════════════════════════════════
def handle_admin(chat_id, text, data, states):
    uid   = str(chat_id)
    state = states.get(uid, "")

    if text in ("/cancel", "🔙 بازگشت"):
        states[uid] = "admin"
        send_admin_panel(chat_id)
        return
    if text == "🏠 خروج از پنل ادمین":
        states.pop(uid, None)
        send_start(chat_id)
        return

    # ─ قیمت جوین اجباری ─────────────────────────────────
    if state == "ap_fj_refs_per_hour":
        try:
            val = int(text.strip())
            assert val > 0
            data["settings"]["fj_free_refs_per_hour"] = val
            save_data(data)
            states[uid] = "admin"
            send(chat_id, f"*✅ هر {val} زیرمجموعه = ۱ ساعت رایگان.*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فقط عدد صحیح مثبت وارد کنید.*", BACK_BTN)
        return

    if state == "ap_fj_hours_per_batch":
        try:
            val = int(text.strip())
            assert val > 0
            data["settings"]["fj_free_hours_per_batch"] = val
            save_data(data)
            states[uid] = "admin"
            send(chat_id, f"*✅ هر دسته = {val} ساعت رایگان.*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فقط عدد صحیح مثبت وارد کنید.*", BACK_BTN)
        return

    # ─ قیمت جوین اجباری ─────────────────────────────────
    if state == "ap_fj_price":
        try:
            price = int(text.replace(",", "").strip())
            data["settings"]["forced_join_price_per_hour"] = price
            save_data(data)
            states[uid] = "admin"
            send(chat_id, f"*✅ قیمت جوین → {price:,} تومان/ساعت*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فقط عدد ارسال کنید.*", BACK_BTN)
        return

    # ─ ثبت کانال جوین جدید توسط ادمین ─────────────────
    if state == "ap_fj_add_link":
        states[uid] = f"ap_fj_add_hours|{text.strip()}"
        send(chat_id,
            f"*🔗 لینک: {text.strip()}\n\n"
            f"⏳ چند ساعت جوین اجباری باشد؟\n"
            f"(فقط عدد بزنید، مثال: 24)*",
            BACK_BTN
        )
        return

    if state.startswith("ap_fj_add_hours|"):
        link = state.split("|", 1)[1]
        try:
            hours    = int(text.strip())
            assert hours > 0
        except:
            send(chat_id, "*⚠️ فقط عدد صحیح وارد کنید (مثال: 24)*", BACK_BTN)
            return
        iran_now   = get_iran_now()
        end_dt     = iran_now + timedelta(hours=hours)
        end_time   = end_dt.strftime("%Y-%m-%d %H:%M")
        start_time = iran_now.strftime("%Y-%m-%d %H:%M")
        if "forced_join_channels" not in data:
            data["forced_join_channels"] = []
        data["forced_join_order_counter"] = data.get("forced_join_order_counter", 0) + 1
        cid = f"FJC{data['forced_join_order_counter']}"
        data["forced_join_channels"].append({
            "order_id":   cid,
            "link":       link,
            "start_time": start_time,
            "end_time":   end_time,
            "active":     True,
            "added_by":   "admin",
            "date":       datetime.now().isoformat()
        })
        save_data(data)
        states[uid] = "admin"
        send(chat_id,
            f"*✅ کانال {link} ثبت شد.\n\n"
            f"🟢 شروع: {start_time}\n"
            f"🔴 پایان: {end_time} ({hours} ساعت)*",
            BACK_BTN
        )
        return

    # ─ قیمت طراحی عکس ───────────────────────────────────
    if state == "ap_design_price":
        try:
            price = int(text.replace(",", "").strip())
            data["settings"]["design_price"] = price
            save_data(data)
            states[uid] = "admin"
            send(chat_id, f"*✅ قیمت طراحی → {price:,} تومان*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فقط عدد ارسال کنید.*", BACK_BTN)
        return

    # ─ پاسخ به تیکت ─────────────────────────────────────
    if state.startswith("ap_reply_ticket|"):
        tid = state.split("|", 1)[1]
        admin_reply_to_ticket(chat_id, tid, text, data)
        states[uid] = "admin"
        return

    # ─ قیمت سرویس عادی ──────────────────────────────────
    if state in PRICE_MAP:
        key, label = PRICE_MAP[state]
        try:
            price = int(text.replace(",", "").strip())
            data["settings"][key]["price_per_1000"] = price
            save_data(data)
            states[uid] = "admin"
            send(chat_id, f"*✅ نرخ {label} → {price:,} تومان*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فقط عدد ارسال کنید.*", BACK_BTN)
        return

    # ─ min/max سرویس عادی ────────────────────────────────
    if state in MM_MAP:
        key = MM_MAP[state]
        try:
            parts = text.strip().split()
            mn, mx = int(parts[0]), int(parts[1])
            assert mn < mx
            data["settings"][key]["min"] = mn
            data["settings"][key]["max"] = mx
            save_data(data)
            states[uid] = "admin"
            send(chat_id, f"*✅ {mn:,} تا {mx:,}*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فرمت اشتباه. مثال: 100 5000*", BACK_BTN)
        return

    # ─ موجودی سرویس عادی ────────────────────────────────
    if state in STOCK_MAP:
        key = STOCK_MAP[state]
        try:
            val   = text.strip()
            stock = 999999 if val in ("0", "نامحدود", "-") else int(val.replace(",", ""))
            data["settings"][key]["stock"] = stock
            save_data(data)
            states[uid] = "admin"
            disp = "نامحدود" if stock >= 999999 else f"{stock:,}"
            send(chat_id, f"*✅ موجودی {SVCLABEL.get(key, key)} → {disp}*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فقط عدد. برای نامحدود: 0*", BACK_BTN)
        return

    # ─ قیمت فروش سکه ─────────────────────────────────────
    if state.startswith("ap_coin_price|"):
        svc_key = state.split("|", 1)[1]
        try:
            price = int(text.replace(",", "").strip())
            data["settings"]["coin_services"][svc_key]["price_per_1053"] = price
            save_data(data)
            states[uid] = "admin"
            lbl = data["settings"]["coin_services"][svc_key].get("label", svc_key)
            send(chat_id, f"*✅ نرخ {lbl} → {price:,} تومان*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فقط عدد ارسال کنید.*", BACK_BTN)
        return

    # ─ min/max فروش سکه ──────────────────────────────────
    if state.startswith("ap_coin_mm|"):
        svc_key = state.split("|", 1)[1]
        try:
            parts = text.strip().split()
            mn, mx = int(parts[0]), int(parts[1])
            assert mn < mx
            data["settings"]["coin_services"][svc_key]["min"] = mn
            data["settings"]["coin_services"][svc_key]["max"] = mx
            save_data(data)
            states[uid] = "admin"
            send(chat_id, f"*✅ {mn:,} تا {mx:,} سکه*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ فرمت اشتباه. مثال: 200 3000*", BACK_BTN)
        return

    # ─ شماره کارت ادمین ─────────────────────────────────
    if state == "ap_coin_card":
        card = text.strip().replace("-", "").replace(" ", "")
        if len(card) != 16 or not card.isdigit():
            send(chat_id, "*⚠️ شماره کارت باید ۱۶ رقم باشد.*", BACK_BTN)
            return
        data["settings"]["coin_card_number"] = card
        save_data(data)
        states[uid] = "admin"
        send(chat_id, f"*✅ شماره کارت → {card}*", BACK_BTN)
        return

    # ─ سایر state ها ─────────────────────────────────────
    if state == "ap_set_channel":
        ch = text.strip()
        if not ch.startswith("@"):
            send(chat_id, "*⚠️ با @ شروع شود.*", BACK_BTN)
            return
        data["settings"]["channel"] = ch
        save_data(data)
        states[uid] = "admin"
        send(chat_id, f"*✅ کانال → {ch}*", BACK_BTN)
        return

    if state == "ap_set_link":
        data["settings"]["channel_link"] = text.strip()
        save_data(data)
        states[uid] = "admin"
        send(chat_id, "*✅ لینک کانال به‌روز شد.*", BACK_BTN)
        return

    if state == "ap_broadcast":
        if text == "❌ لغو":
            states[uid] = "admin"
            states.pop(f"bc_pending_{uid}", None)
            send_admin_panel(chat_id)
            return
        # پیام متنی
        ok = fail = 0
        for u in data["users"].values():
            cid = u.get("chat_id")
            if not cid or int(cid) <= 0:
                continue
            try:
                send(cid, text)
                ok += 1
                time.sleep(0.05)
            except:
                fail += 1
        states[uid] = "admin"
        send(chat_id, f"*📨 پیام متنی ارسال شد.\n✅ {ok}\n❌ {fail}*", BACK_BTN)
        return

    if state == "ap_block":
        try:
            t = str(int(text.strip()))
            if t in data["users"]:
                data["users"][t]["blocked"] = True
                save_data(data)
                send(chat_id, f"*✅ {t} مسدود شد.*", BACK_BTN)
            else:
                send(chat_id, "*⚠️ کاربر یافت نشد.*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ آیدی اشتباه.*", BACK_BTN)
        states[uid] = "admin"
        return

    if state == "ap_unblock":
        try:
            t = str(int(text.strip()))
            if t in data["users"]:
                data["users"][t]["blocked"] = False
                save_data(data)
                send(chat_id, f"*✅ {t} رفع مسدودیت شد.*", BACK_BTN)
            else:
                send(chat_id, "*⚠️ کاربر یافت نشد.*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ آیدی اشتباه.*", BACK_BTN)
        states[uid] = "admin"
        return

    if state == "ap_search":
        try:
            t = str(int(text.strip()))
            u = data["users"].get(t)
            if u:
                send(chat_id,
                    f"*🔍 {t}:\n"
                    f"👤 {u.get('first_name', '?')} | @{u.get('username', 'ندارد')}\n"
                    f"📅 {u.get('first_seen', '')[:10]}\n"
                    f"📦 {u.get('orders', 0)} سفارش | {u.get('total_spent', 0):,} تومان\n"
                    f"🚫 {'مسدود' if u.get('blocked') else 'فعال'}*", BACK_BTN)
            else:
                send(chat_id, "*⚠️ یافت نشد.*", BACK_BTN)
        except:
            send(chat_id, "*⚠️ آیدی اشتباه.*", BACK_BTN)
        states[uid] = "admin"
        return

    # ══════════════════════════════════════════
    #  منوهای پنل
    # ══════════════════════════════════════════
    if text == "📊 آمار و گزارشات":
        send(chat_id, "*📊 آمار*",
             kb(["📊 آمار کلی", "📅 آمار امروز"],
                ["📊 آمار هفتگی", "📊 آمار ماهانه"],
                ["🔄 ریست آمار امروز"],
                ["🔙 بازگشت"]))
        return

    if text == "📦 مدیریت سفارشات":
        send(chat_id, "*📦 سفارشات*",
             kb(["⏳ سفارش‌های فعال"],
                ["✅ سفارش‌های تکمیل‌شده"],
                ["📋 ۱۰ سفارش آخر", "📤 خروجی کامل آمار"],
                ["🔙 بازگشت"]))
        return

    if text == "⚙️ مدیریت خدمات":
        s = data["settings"]
        def st(k): return "✅" if s[k]["enabled"] else "❌"
        send(chat_id,
            f"*⚙️ خدمات\n\n"
            f"👁️بله:{st('bale_view_single')} ❤️ری‌اکشن:{st('bale_reaction')}\n"
            f"🔴روبیکا:{st('rubika_view')} 🟢ایتا:{st('eitaa_view')}\n"
            f"🔵ممبر بله:{st('bale_member')} 🔴ممبر روبیکا:{st('rubika_member')}\n"
            f"🟢ممبر ایتا:{st('eitaa_member')} 🟣فالوور:{st('rubika_follower')}*",
            kb(
                ["👁️ بازدید بله روشن/خاموش",     "❤️ ری‌اکشن روشن/خاموش"],
                ["🔴 بازدید روبیکا روشن/خاموش",  "🟢 بازدید ایتا روشن/خاموش"],
                ["🔵 ممبر بله روشن/خاموش",        "🔴 ممبر روبیکا روشن/خاموش"],
                ["🟢 ممبر ایتا روشن/خاموش",      "🟣 فالوور روبیکا روشن/خاموش"],
                ["🔢 تغییر حداقل/حداکثر"],
                ["🔙 بازگشت"]
            ))
        return

    if text == "💰 نرخ و قیمت‌ها":
        s = data["settings"]
        def p(k): return f"{s[k]['price_per_1000']:,}"
        send(chat_id,
            f"*💰 نرخ‌ها (تومان/۱۰۰۰)\n\n"
            f"👁️بازدید بله:{p('bale_view_single')}\n❤️ری‌اکشن:{p('bale_reaction')}\n"
            f"🔴بازدید روبیکا:{p('rubika_view')}\n🟢بازدید ایتا:{p('eitaa_view')}\n"
            f"🔵ممبر بله:{p('bale_member')}\n🔴ممبر روبیکا:{p('rubika_member')}\n"
            f"🟢ممبر ایتا:{p('eitaa_member')}\n🟣فالوور:{p('rubika_follower')}*",
            kb(
                ["💰 نرخ بازدید بله",     "💰 نرخ ری‌اکشن"],
                ["💰 نرخ بازدید روبیکا",  "💰 نرخ بازدید ایتا"],
                ["💰 نرخ ممبر بله",        "💰 نرخ ممبر روبیکا"],
                ["💰 نرخ ممبر ایتا",       "💰 نرخ فالوور روبیکا"],
                ["🔙 بازگشت"]
            ))
        return

    if text == "📦 مدیریت موجودی":
        s = data["settings"]
        def stk(k):
            v = s[k].get("stock", 999999)
            return "نامحدود" if v >= 999999 else f"{v:,}"
        send(chat_id,
            f"*📦 موجودی\n\n"
            f"👁️بازدید بله:{stk('bale_view_single')}\n❤️ری‌اکشن:{stk('bale_reaction')}\n"
            f"🔴بازدید روبیکا:{stk('rubika_view')}\n🟢بازدید ایتا:{stk('eitaa_view')}\n"
            f"🔵ممبر بله:{stk('bale_member')}\n🔴ممبر روبیکا:{stk('rubika_member')}\n"
            f"🟢ممبر ایتا:{stk('eitaa_member')}\n🟣فالوور:{stk('rubika_follower')}*",
            kb(
                ["📦 موجودی بازدید بله",     "📦 موجودی ری‌اکشن"],
                ["📦 موجودی بازدید روبیکا",  "📦 موجودی بازدید ایتا"],
                ["📦 موجودی ممبر بله",        "📦 موجودی ممبر روبیکا"],
                ["📦 موجودی ممبر ایتا",       "📦 موجودی فالوور روبیکا"],
                ["♾️ نامحدود همه سرویس‌ها"],
                ["🔙 بازگشت"]
            ))
        return

    if text == "🪙 مدیریت فروش سکه":
        states[uid] = "admin_coin"
        send_coin_admin_panel(chat_id, data)
        return

    if text == "🎨 مدیریت طراحی عکس":
        price    = data["settings"].get("design_price", 12000)
        pend     = sum(1 for o in data.get("design_orders", []) if o.get("status") == "pending")
        done     = sum(1 for o in data.get("design_orders", []) if o.get("status") == "done")
        rejected = sum(1 for o in data.get("design_orders", []) if o.get("status") == "rejected")
        send(chat_id,
            f"*🎨 مدیریت طراحی عکس\n\n"
            f"💰 قیمت فعلی: {price:,} تومان\n"
            f"⏳ در انتظار: {pend} | ✅ تکمیل: {done} | ❌ رد: {rejected}*",
            kb(
                ["⏳ سفارشات طراحی در انتظار"],
                ["✅ سفارشات طراحی تکمیل‌شده", "❌ سفارشات طراحی رد شده"],
                ["💰 تغییر قیمت طراحی"],
                ["🔙 بازگشت"]
            )
        )
        return

    if text == "⏳ سفارشات طراحی در انتظار":
        orders = [o for o in data.get("design_orders", []) if o.get("status") == "pending"]
        if not orders:
            send(chat_id, "*هیچ سفارش طراحی در انتظاری وجود ندارد.*", BACK_BTN)
            return
        send(chat_id, f"*🎨 سفارشات طراحی در انتظار: {len(orders)}*")
        for o in reversed(orders[-15:]):
            send(chat_id,
                f"*🆔 {o.get('id', '?')}\n"
                f"👤 کاربر: {o.get('user_id', '?')}\n"
                f"🆔 آیدی دریافت: {o.get('bale_id', '?')}\n"
                f"💰 {o.get('price', 0):,} تومان\n"
                f"📝 توضیحات:\n{o.get('description', '?')[:200]}*",
                {"inline_keyboard": [
                    [
                        {"text": f"✅ تکمیل {o['id']}", "callback_data": f"complete_design|{o['id']}"},
                        {"text": f"❌ رد {o['id']}",    "callback_data": f"reject_design|{o['id']}"}
                    ]
                ]}
            )
        send(chat_id, "*👆 پایان لیست*", BACK_BTN)
        return

    if text == "✅ سفارشات طراحی تکمیل‌شده":
        orders = [o for o in data.get("design_orders", []) if o.get("status") == "done"]
        if not orders:
            send(chat_id, "*هیچ سفارش تکمیل‌شده‌ای وجود ندارد.*", BACK_BTN); return
        send(chat_id, f"*✅ سفارشات تکمیل شده: {len(orders)}*")
        for o in reversed(orders[-10:]):
            send(chat_id, f"*🆔{o['id']} | 👤{o.get('user_id','')} | {o.get('bale_id','')} | {o.get('price',0):,}ت*")
        send(chat_id, "*👆*", BACK_BTN)
        return

    if text == "❌ سفارشات طراحی رد شده":
        orders = [o for o in data.get("design_orders", []) if o.get("status") == "rejected"]
        if not orders:
            send(chat_id, "*هیچ سفارش رد شده‌ای وجود ندارد.*", BACK_BTN); return
        send(chat_id, f"*❌ سفارشات رد شده: {len(orders)}*")
        for o in reversed(orders[-10:]):
            send(chat_id, f"*🆔{o['id']} | 👤{o.get('user_id','')} | {o.get('bale_id','')}*")
        send(chat_id, "*👆*", BACK_BTN)
        return

    if text == "💰 تغییر قیمت طراحی":
        cur = data["settings"].get("design_price", 12000)
        states[uid] = "ap_design_price"
        send(chat_id, f"*💰 قیمت فعلی: {cur:,} تومان\n\nقیمت جدید:*", BACK_BTN)
        return

    if text == "⏳ سفارشات سکه در انتظار":
        send_pending_coin_orders(chat_id, data)
        return

    if text == "✅ سفارشات سکه تأیید شده":
        orders = [o for o in data["coin_orders"] if o.get("status") == "approved"]
        if not orders:
            send(chat_id, "*هیچ سفارش تأیید شده‌ای وجود ندارد.*", BACK_BTN)
            return
        send(chat_id, f"*✅ سفارشات تأیید شده: {len(orders)}*")
        for o in reversed(orders[-10:]):
            send(chat_id, f"*🆔{o['id']} | {o.get('service_label', '')} | {o.get('amount', 0):,}🪙 | {o.get('price', 0):,}ت*")
        send(chat_id, "*👆*", BACK_BTN)
        return

    if text == "❌ سفارشات سکه رد شده":
        orders = [o for o in data["coin_orders"] if o.get("status") == "rejected"]
        if not orders:
            send(chat_id, "*هیچ سفارش رد شده‌ای وجود ندارد.*", BACK_BTN)
            return
        send(chat_id, f"*❌ سفارشات رد شده: {len(orders)}*")
        for o in reversed(orders[-10:]):
            send(chat_id, f"*🆔{o['id']} | {o.get('service_label', '')} | {o.get('amount', 0):,}🪙*")
        send(chat_id, "*👆*", BACK_BTN)
        return

    if text == "💰 تغییر نرخ سکه":
        cs = data["settings"]["coin_services"]
        def p(k): return f"{cs.get(k, {}).get('price_per_1053', 0):,}"
        send(chat_id,
            f"*💰 نرخ فروش سکه (تومان/۱۰۵۳)\n\n"
            f"🔵کانال بله:{p('coin_bale_channel')}\n🔵گروه بله:{p('coin_bale_group')}\n"
            f"🔴کانال روبیکا:{p('coin_rubika_channel')}\n🔴گروه روبیکا:{p('coin_rubika_group')}\n"
            f"🔴لایک روبیکا:{p('coin_rubika_like')}\n🔴فالوور روبیکا:{p('coin_rubika_follower')}\n"
            f"🟢کانال ایتا:{p('coin_eitaa_channel')}\n🟢گروه ایتا:{p('coin_eitaa_group')}*",
            kb(
                ["💰 نرخ سکه کانال بله",    "💰 نرخ سکه گروه بله"],
                ["💰 نرخ سکه کانال روبیکا",  "💰 نرخ سکه گروه روبیکا"],
                ["💰 نرخ سکه لایک روبیکا",   "💰 نرخ سکه فالوور روبیکا"],
                ["💰 نرخ سکه کانال ایتا",    "💰 نرخ سکه گروه ایتا"],
                ["🔙 بازگشت"]
            ))
        return

    if text == "🔢 تغییر حداقل/حداکثر سکه":
        cs = data["settings"]["coin_services"]
        def mm(k): return f"{cs.get(k, {}).get('min', 200):,}-{cs.get(k, {}).get('max', 3000):,}"
        send(chat_id,
            f"*🔢 حداقل/حداکثر سکه\n\n"
            f"🔵کانال بله:{mm('coin_bale_channel')}\n🔵گروه بله:{mm('coin_bale_group')}\n"
            f"🔴کانال روبیکا:{mm('coin_rubika_channel')}\n🔴گروه روبیکا:{mm('coin_rubika_group')}\n"
            f"🔴لایک روبیکا:{mm('coin_rubika_like')}\n🔴فالوور روبیکا:{mm('coin_rubika_follower')}\n"
            f"🟢کانال ایتا:{mm('coin_eitaa_channel')}\n🟢گروه ایتا:{mm('coin_eitaa_group')}*",
            kb(
                ["🔢 حداقل/حداکثر سکه کانال بله",    "🔢 حداقل/حداکثر سکه گروه بله"],
                ["🔢 حداقل/حداکثر سکه کانال روبیکا",  "🔢 حداقل/حداکثر سکه گروه روبیکا"],
                ["🔢 حداقل/حداکثر سکه لایک روبیکا",   "🔢 حداقل/حداکثر سکه فالوور روبیکا"],
                ["🔢 حداقل/حداکثر سکه کانال ایتا",    "🔢 حداقل/حداکثر سکه گروه ایتا"],
                ["🔙 بازگشت"]
            ))
        return

    if text == "🔛 روشن/خاموش سرویس‌های سکه":
        cs = data["settings"]["coin_services"]
        def st(k): return "✅" if cs.get(k, {}).get("enabled", True) else "❌"
        send(chat_id,
            f"*🔛 وضعیت سرویس‌های سکه\n\n"
            f"🔵کانال بله:{st('coin_bale_channel')} 🔵گروه بله:{st('coin_bale_group')}\n"
            f"🔴کانال روبیکا:{st('coin_rubika_channel')} 🔴گروه روبیکا:{st('coin_rubika_group')}\n"
            f"🔴لایک روبیکا:{st('coin_rubika_like')} 🔴فالوور روبیکا:{st('coin_rubika_follower')}\n"
            f"🟢کانال ایتا:{st('coin_eitaa_channel')} 🟢گروه ایتا:{st('coin_eitaa_group')}*",
            kb(
                ["🔵 سکه کانال بله روشن/خاموش",    "🔵 سکه گروه بله روشن/خاموش"],
                ["🔴 سکه کانال روبیکا روشن/خاموش",  "🔴 سکه گروه روبیکا روشن/خاموش"],
                ["🔴 سکه لایک روبیکا روشن/خاموش",   "🔴 سکه فالوور روبیکا روشن/خاموش"],
                ["🟢 سکه کانال ایتا روشن/خاموش",    "🟢 سکه گروه ایتا روشن/خاموش"],
                ["🔙 بازگشت"]
            ))
        return

    if text == "💳 تنظیم شماره کارت ادمین":
        cur = data["settings"].get("coin_card_number", "تنظیم نشده")
        states[uid] = "ap_coin_card"
        send(chat_id, f"*💳 شماره کارت فعلی: {cur}\n\nشماره کارت جدید (۱۶ رقم):*", BACK_BTN)
        return

    if text == "📱 مدیریت جوین اجباری":
        pph     = data["settings"].get("forced_join_price_per_hour", 5000)
        rph     = data["settings"].get("fj_free_refs_per_hour", 3)
        hpb     = data["settings"].get("fj_free_hours_per_batch", 1)
        pend    = sum(1 for o in data.get("forced_join_orders", []) if o.get("status") == "pending")
        active  = [c for c in data.get("forced_join_channels", []) if c.get("active", False)]
        send(chat_id,
            f"*📱 مدیریت جوین اجباری\n\n"
            f"💰 قیمت هر ساعت: {pph:,} تومان\n"
            f"👥 زیرمجموعه رایگان: هر {rph} نفر = {hpb} ساعت\n"
            f"⏳ در انتظار تأیید: {pend}\n"
            f"✅ کانال‌های فعال: {len(active)}*",
            kb(
                ["⏳ سفارشات جوین در انتظار"],
                ["📋 کانال‌های فعال جوین", "➕ ثبت کانال جوین جدید"],
                ["💰 تغییر قیمت هر ساعت جوین"],
                ["👥 تنظیمات زیرمجموعه‌گیری"],
                ["🔄 ریست کانال‌های FJ"],
                ["🔙 بازگشت"]
            )
        )
        return

    if text == "⏳ سفارشات جوین در انتظار":
        orders = [o for o in data.get("forced_join_orders", []) if o.get("status") == "pending"]
        if not orders:
            send(chat_id, "*هیچ سفارش جوین اجباری در انتظاری وجود ندارد.*", BACK_BTN); return
        send(chat_id, f"*⏳ سفارشات جوین در انتظار: {len(orders)}*")
        for o in reversed(orders[-15:]):
            send(chat_id,
                f"*🆔 {o.get('id', '?')}\n"
                f"👤 کاربر: {o.get('user_id', '?')}\n"
                f"⏳ {o.get('hours', 0)} ساعت\n"
                f"🔗 {o.get('link', '?')}\n"
                f"💰 {o.get('price', 0):,} تومان*",
                {"inline_keyboard": [
                    [
                        {"text": f"✅ تأیید {o['id']}", "callback_data": f"approve_fj|{o['id']}"},
                        {"text": f"❌ رد {o['id']}",    "callback_data": f"reject_fj|{o['id']}"}
                    ]
                ]}
            )
        send(chat_id, "*👆 پایان لیست*", BACK_BTN)
        return

    if text == "🔄 ریست کانال‌های FJ":
        iran_now = get_iran_now()
        now_str  = iran_now.strftime("%Y-%m-%d %H:%M")
        fixed = 0
        for ch in data.get("forced_join_channels", []):
            end_time = ch.get("end_time", "")
            if end_time and end_time > now_str:
                ch["active"] = True
                fixed += 1
        save_data(data)
        send(chat_id, f"*✅ {fixed} کانال فعال شد.*", BACK_BTN)
        return
        channels = [c for c in data.get("forced_join_channels", []) if c.get("active", False)]
        if not channels:
            send(chat_id, "*هیچ کانال فعالی وجود ندارد.*", BACK_BTN); return
        send(chat_id, f"*📋 کانال‌های فعال جوین اجباری: {len(channels)}*")
        for c in channels:
            send(chat_id,
                f"*🆔 {c.get('order_id', '?')}\n"
                f"🔗 {c.get('link', '?')}\n"
                f"⏰ پایان: {c.get('end_time', '?')}*",
                {"inline_keyboard": [[
                    {"text": f"🗑️ حذف {c['order_id']}", "callback_data": f"remove_fj_channel|{c['order_id']}"}
                ]]}
            )
        send(chat_id, "*👆*", BACK_BTN)
        return

    if text == "➕ ثبت کانال جوین جدید":
        states[uid] = "ap_fj_add_link"
        send(chat_id, "*🔗 لینک کانال را وارد کنید:*", BACK_BTN)
        return

    if text == "💰 تغییر قیمت هر ساعت جوین":
        cur = data["settings"].get("forced_join_price_per_hour", 5000)
        states[uid] = "ap_fj_price"
        send(chat_id, f"*💰 قیمت فعلی: {cur:,} تومان/ساعت\n\nقیمت جدید:*", BACK_BTN)
        return

    if text == "👥 تنظیمات زیرمجموعه‌گیری":
        rph = data["settings"].get("fj_free_refs_per_hour", 3)
        hpb = data["settings"].get("fj_free_hours_per_batch", 1)
        send(chat_id,
            f"*👥 تنظیمات زیرمجموعه‌گیری\n\n"
            f"📌 قانون فعلی:\n"
            f"هر *{rph} زیرمجموعه* = *{hpb} ساعت* جوین اجباری رایگان*",
            kb(
                ["🔢 تعداد زیرمجموعه برای هر ساعت"],
                ["⏳ ساعت رایگان به ازای هر دسته"],
                ["🔙 بازگشت"]
            )
        )
        return

    if text == "🔢 تعداد زیرمجموعه برای هر ساعت":
        cur = data["settings"].get("fj_free_refs_per_hour", 3)
        states[uid] = "ap_fj_refs_per_hour"
        send(chat_id, f"*📌 فعلی: {cur} زیرمجموعه برای هر ساعت\n\nتعداد جدید:*", BACK_BTN)
        return

    if text == "⏳ ساعت رایگان به ازای هر دسته":
        cur = data["settings"].get("fj_free_hours_per_batch", 1)
        states[uid] = "ap_fj_hours_per_batch"
        send(chat_id, f"*📌 فعلی: {cur} ساعت به ازای هر دسته\n\nساعت جدید:*", BACK_BTN)
        return
        send(chat_id, "*🗑️ پاک‌سازی\n\n⚠️ برگشت‌پذیر نیست!*",
             kb(["🗑️ پاک کردن همه سفارشات"],
                ["🗑️ پاک کردن سفارشات تکمیل‌شده"],
                ["🗑️ پاک کردن آمار روزانه"],
                ["🗑️ پاک سفارشات سکه", "🗑️ پاک سفارشات طراحی"],
                ["🗑️ ریست کامل (همه چیز)"],
                ["🔙 بازگشت"]))
        return

    if text == "🎫 تیکت‌های باز":
        send_open_tickets(chat_id, data)
        return
    if text == "🔴 تیکت‌های بسته":
        send_closed_tickets(chat_id, data)
        return

    if text == "👥 مدیریت کاربران":
        bc      = sum(1 for u in data["users"].values() if u.get("blocked"))
        warns   = sum(1 for u in data["users"].values() if u.get("spam_warnings", 0) > 0)
        pledges = len(data.get("pledges", {}))
        send(chat_id,
            f"*👥 کاربران: {len(data['users']):,} | مسدود: {bc}\n"
            f"⚠️ دارای اخطار اسپم: {warns} | 📋 تعهدها: {pledges}*",
            kb(
                ["🚫 مسدود کردن کاربر", "✅ رفع مسدودیت"],
                ["📵 لیست کاربران مسدود", "🔍 جستجوی کاربر"],
                ["⚠️ مدیریت اخطار اسپم", "📋 مشاهده تعهدها"],
                ["🔙 بازگشت"]
            )
        )
        return

    if text == "⚠️ مدیریت اخطار اسپم":
        warned = [(wuid, wu) for wuid, wu in data["users"].items() if wu.get("spam_warnings", 0) > 0]
        if not warned:
            send(chat_id, "*هیچ کاربری اخطار اسپم ندارد.*", BACK_BTN)
            return
        msg = f"*⚠️ کاربران دارای اخطار ({len(warned)} نفر):\n\n"
        for wuid, wu in warned[:30]:
            msg += f"🆔 {wuid} | {wu.get('first_name','?')} | اخطار: {wu.get('spam_warnings',0)}/3\n"
        msg += "*"
        send(chat_id, msg, kb(["🗑️ پاک کردن همه اخطارها", "🔙 بازگشت"]))
        return

    if text == "🗑️ پاک کردن همه اخطارها":
        cnt = 0
        for u in data["users"].values():
            if u.get("spam_warnings", 0) > 0:
                u["spam_warnings"] = 0
                cnt += 1
        save_data(data)
        _spam_tracker.clear()
        send(chat_id, f"*✅ اخطار {cnt} کاربر پاک شد.*", BACK_BTN)
        return

    if text == "📋 مشاهده تعهدها":
        pledges = data.get("pledges", {})
        if not pledges:
            send(chat_id, "*هیچ تعهدی ثبت نشده.*", BACK_BTN)
            return
        msg = f"*📋 تعهدها ({len(pledges)} مورد):\n\n"
        for puid, p in list(pledges.items())[-20:]:
            msg += (
                f"👤 {p.get('first_name','?')} | @{p.get('username','')}\n"
                f"🆔 {puid} | 📱 {p.get('phone','?')}\n"
                f"📅 {p.get('date','')[:16]}\n\n"
            )
        if len(msg) > 3900:
            msg = msg[:3890] + "\n...*"
        else:
            msg += "*"
        send(chat_id, msg, kb(["🗑️ پاک کردن تعهدها", "🔙 بازگشت"]))
        return

    if text == "🗑️ پاک کردن تعهدها":
        data["pledges"] = {}
        save_data(data)
        send(chat_id, "*✅ همه تعهدها پاک شد.*", BACK_BTN)
        return

    if text == "📢 تنظیمات کانال":
        send(chat_id, "*📢 تنظیمات کانال*",
             kb(["📢 تغییر آیدی کانال", "📌 تغییر لینک کانال"],
                ["🔙 بازگشت"]))
        return

    if text == "🤖 وضعیت ربات":
        cur = data["settings"].get("bot_active", True)
        send(chat_id,
            f"*🤖 وضعیت ربات\n\nوضعیت فعلی: {'✅ فعال' if cur else '🔴 غیرفعال'}*",
            kb(["✅ فعال‌سازی ربات", "🔴 غیرفعال‌سازی ربات"], ["🔙 بازگشت"])
        )
        return

    if text == "🎡 مدیریت تخفیف‌ها":
        codes = data.get("discount_codes", {})
        total = len(codes)
        used  = sum(1 for c in codes.values() if c.get("used"))
        unused= total - used
        msg   = f"*🎡 مدیریت کدهای تخفیف\n\n📊 کل: {total} | استفاده‌شده: {used} | فعال: {unused}\n\n"
        for code, dc in list(codes.items())[-20:]:
            status = "✅ استفاده‌شده" if dc.get("used") else "🟢 فعال"
            msg += f"🎟️ {code} | {dc['percent']}٪ | 👤{dc['user_id']} | {status}\n"
        msg += "*"
        if len(msg) > 4000: msg = msg[:3990] + "...*"
        send(chat_id, msg, kb(["🗑️ پاک کردن کدهای استفاده‌شده", "🗑️ پاک کردن همه کدها", "🔙 بازگشت"]))
        return

    if text == "🗑️ پاک کردن کدهای استفاده‌شده":
        before = len(data.get("discount_codes", {}))
        data["discount_codes"] = {k: v for k, v in data.get("discount_codes", {}).items() if not v.get("used")}
        save_data(data)
        send(chat_id, f"*✅ {before - len(data['discount_codes'])} کد پاک شد.*", BACK_BTN)
        return

    if text == "🗑️ پاک کردن همه کدها":
        data["discount_codes"] = {}
        save_data(data)
        send(chat_id, "*✅ همه کدهای تخفیف پاک شد.*", BACK_BTN)
        return

    if text == "✅ فعال‌سازی ربات":
        data["settings"]["bot_active"] = True
        save_data(data)
        send(chat_id, "*✅ ربات فعال شد. کاربران می‌توانند استفاده کنند.*", BACK_BTN)
        return

    if text == "🔴 غیرفعال‌سازی ربات":
        data["settings"]["bot_active"] = False
        save_data(data)
        send(chat_id, "*🔴 ربات غیرفعال شد. کاربران پیام غیرفعال بودن می‌گیرند.*", BACK_BTN)
        return
        cur = data["settings"]["forced_join"]
        data["settings"]["forced_join"] = not cur
        save_data(data)
        send(chat_id, f"*🔒 {'✅ فعال شد' if not cur else '❌ غیرفعال شد'}*", BACK_BTN)
        return

    if text == "📨 پیام همگانی":
        states[uid] = "ap_broadcast"
        send(chat_id,
            "*📨 پیام همگانی\n\n"
            "متن، تصویر، گیف، استیکر یا فایل ارسال کنید:*",
            kb(["❌ لغو"])
        )
        return

    # ─ پاک‌سازی ─────────────────────────────────────────
    if text == "🗑️ پاک کردن همه سفارشات":
        data["orders"] = []
        data["stats"]["total_orders"]  = 0
        data["stats"]["total_revenue"] = 0
        save_data(data)
        send(chat_id, "*✅ همه سفارشات پاک شد.*", BACK_BTN)
        return
    if text == "🗑️ پاک کردن سفارشات تکمیل‌شده":
        before = len(data["orders"])
        data["orders"] = [o for o in data["orders"] if o.get("status") != "done"]
        save_data(data)
        send(chat_id, f"*✅ {before - len(data['orders'])} سفارش پاک شد.*", BACK_BTN)
        return
    if text == "🗑️ پاک کردن آمار روزانه":
        data["stats"]["daily_stats"] = {}
        save_data(data)
        send(chat_id, "*✅ آمار روزانه پاک شد.*", BACK_BTN)
        return
    if text == "🗑️ پاک سفارشات سکه":
        data["coin_orders"] = []
        save_data(data)
        send(chat_id, "*✅ سفارشات سکه پاک شد.*", BACK_BTN)
        return
    if text == "🗑️ پاک سفارشات طراحی":
        data["design_orders"] = []
        save_data(data)
        send(chat_id, "*✅ سفارشات طراحی پاک شد.*", BACK_BTN)
        return
    if text == "🗑️ ریست کامل (همه چیز)":
        nd = default_data()
        nd["settings"] = data["settings"]
        save_data(nd)
        send(chat_id, "*✅ ریست کامل. تنظیمات حفظ شد.*", BACK_BTN)
        return

    # ─ تیکت‌ها ──────────────────────────────────────────
    if text == "🗑️ ریست تیکت‌های باز":
        data["tickets"] = {tid: t for tid, t in data["tickets"].items() if t.get("status") != "open"}
        save_data(data)
        send(chat_id, "*✅ تیکت‌های باز پاک شد.*", BACK_BTN)
        return
    if text == "🗑️ ریست تیکت‌های بسته":
        data["tickets"] = {tid: t for tid, t in data["tickets"].items() if t.get("status") != "closed"}
        save_data(data)
        send(chat_id, "*✅ تیکت‌های بسته پاک شد.*", BACK_BTN)
        return

    # ─ آمار ─────────────────────────────────────────────
    if text == "📊 آمار کلی":
        st = data["stats"]
        coin_total = len(data.get("coin_orders", []))
        send(chat_id, f"*📊:\n👥 {st['total_users']:,}\n📦 {st['total_orders']:,}\n💰 {st['total_revenue']:,} تومان\n🪙 سفارشات سکه: {coin_total}*", BACK_BTN)
        return
    if text == "📅 آمار امروز":
        td = data["stats"]["daily_stats"].get(get_today(), {})
        send(chat_id, f"*📅 امروز:\n📦 {td.get('orders', 0):,}\n💵 {td.get('revenue', 0):,} تومان*", BACK_BTN)
        return
    if text == "📊 آمار هفتگی":
        to = tr = 0
        for i in range(7):
            d = data["stats"]["daily_stats"].get((datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), {})
            to += d.get("orders", 0); tr += d.get("revenue", 0)
        send(chat_id, f"*📊 ۷ روز:\n📦 {to:,}\n💰 {tr:,} تومان*", BACK_BTN)
        return
    if text == "📊 آمار ماهانه":
        month = datetime.now().strftime("%Y-%m")
        to = tr = 0
        for day, d in data["stats"]["daily_stats"].items():
            if day.startswith(month):
                to += d.get("orders", 0); tr += d.get("revenue", 0)
        send(chat_id, f"*📊 این ماه:\n📦 {to:,}\n💰 {tr:,} تومان*", BACK_BTN)
        return
    if text == "🔄 ریست آمار امروز":
        data["stats"]["daily_stats"][get_today()] = {"orders": 0, "revenue": 0}
        save_data(data)
        send(chat_id, "*✅ آمار امروز ریست شد.*", BACK_BTN)
        return

    # ─ سفارشات ──────────────────────────────────────────
    def _olist(lst, title, show_btn):
        if not lst:
            send(chat_id, f"*{title}: خالی*", BACK_BTN)
            return
        # همه رو در یک پیام خلاصه کن
        msg = f"*{title}: {len(lst)} مورد\n\n"
        for o in lst[-20:]:
            st  = o.get("status", "")
            lbl = "💳" if st == "pending_payment" else ("🔄" if st == "pending" else "✅")
            msg += (
                f"{lbl} {o.get('id','?')} | 👤{o.get('user_id','?')}\n"
                f"   📦{o.get('service','?')} | {o.get('amount',0):,} | {o.get('price',0):,}t\n"
            )
        msg += "*"
        # اگر پیام خیلی بلند شد برش
        if len(msg) > 4000:
            msg = msg[:3990] + "...*"
        send(chat_id, msg, BACK_BTN)
        # دکمه‌های تکمیل فقط برای pending - هر کدوم جداگانه
        if show_btn:
            for o in lst[-20:]:
                if o.get("status") == "pending":
                    send(chat_id,
                        f"*✅ تکمیل سفارش {o['id']}؟*",
                        {"inline_keyboard": [[{"text": f"✅ تکمیل {o['id']}", "callback_data": f"complete|{o['id']}"}]]}
                    )

    if text == "⏳ سفارش‌های فعال":
        _olist([o for o in data["orders"] if o.get("status") in ("pending", "pending_payment")], "⏳ فعال", True)
        return
    if text == "✅ سفارش‌های تکمیل‌شده":
        _olist([o for o in data["orders"] if o.get("status") == "done"], "✅ تکمیل‌شده", False)
        return
    if text == "📋 ۱۰ سفارش آخر":
        lst = data["orders"][-10:]
        if not lst:
            send(chat_id, "*خالی*", BACK_BTN); return
        msg = "*📋 ۱۰ سفارش آخر:\n\n"
        for o in reversed(lst):
            msg += f"🆔{o.get('id', '?')}|{o.get('service', '?')}|{o.get('amount', 0):,}|{o.get('price', 0):,}t|{o.get('status', '?')}\n"
        send(chat_id, msg + "*", BACK_BTN)
        return
    if text == "📤 خروجی کامل آمار":
        st  = data["stats"]
        msg = f"*📤 آمار:\n👥{st['total_users']:,}\n📦{st['total_orders']:,}\n💰{st['total_revenue']:,}t\n\n۷روز:\n"
        for i in range(7):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            d   = st["daily_stats"].get(day, {})
            msg += f"{day}:{d.get('orders', 0)}|{d.get('revenue', 0):,}t\n"
        send(chat_id, msg + "*", BACK_BTN)
        return

    # ─ toggle خدمات ─────────────────────────────────────
    if text in TOGGLE_MAP:
        key, label = TOGGLE_MAP[text]
        cur = data["settings"][key]["enabled"]
        data["settings"][key]["enabled"] = not cur
        save_data(data)
        send(chat_id, f"*{label} {'✅ فعال' if not cur else '❌ غیرفعال'} شد.*", BACK_BTN)
        return

    if text == "🔢 تغییر حداقل/حداکثر":
        s = data["settings"]
        def mm(k): return f"{s[k]['min']:,}-{s[k]['max']:,}"
        send(chat_id,
            f"*🔢 حداقل/حداکثر\n\n"
            f"👁️بازدید بله:{mm('bale_view_single')}\n❤️ری‌اکشن:{mm('bale_reaction')}\n"
            f"🔴بازدید روبیکا:{mm('rubika_view')}\n🟢بازدید ایتا:{mm('eitaa_view')}\n"
            f"🔵ممبر بله:{mm('bale_member')}\n🔴ممبر روبیکا:{mm('rubika_member')}\n"
            f"🟢ممبر ایتا:{mm('eitaa_member')}\n🟣فالوور:{mm('rubika_follower')}*",
            kb(
                ["🔢 بازدید بله",    "🔢 ری‌اکشن"],
                ["🔢 بازدید روبیکا", "🔢 بازدید ایتا"],
                ["🔢 ممبر بله",       "🔢 ممبر روبیکا"],
                ["🔢 ممبر ایتا",      "🔢 فالوور روبیکا"],
                ["🔙 بازگشت"]
            ))
        return

    if text in MM_BTNS:
        st_key  = MM_BTNS[text]
        svc_key = MM_MAP[st_key]
        states[uid] = st_key
        s = data["settings"][svc_key]
        send(chat_id, f"*فعلی: {s['min']:,} تا {s['max']:,}\nحداقل و حداکثر جدید (مثال: 100 5000):*", BACK_BTN)
        return

    if text in PRICE_BTNS:
        st_key  = PRICE_BTNS[text]
        svc_key = PRICE_MAP[st_key][0]
        states[uid] = st_key
        send(chat_id, f"*نرخ فعلی: {data['settings'][svc_key]['price_per_1000']:,} تومان\nنرخ جدید:*", BACK_BTN)
        return

    if text in STOCK_BTNS:
        st_key  = STOCK_BTNS[text]
        svc_key = STOCK_MAP[st_key]
        states[uid] = st_key
        cur = data["settings"][svc_key].get("stock", 999999)
        send(chat_id,
            f"*موجودی {SVCLABEL.get(svc_key, svc_key)}: {'نامحدود' if cur >= 999999 else f'{cur:,}'}\n\nموجودی جدید (0=نامحدود):*",
            BACK_BTN)
        return

    if text == "♾️ نامحدود همه سرویس‌ها":
        for k in ALL_SVC_KEYS:
            data["settings"][k]["stock"] = 999999
        save_data(data)
        send(chat_id, "*✅ همه موجودی‌ها نامحدود شد.*", BACK_BTN)
        return

    # ─ toggle سکه ────────────────────────────────────────
    if text in COIN_TOGGLE_BTNS:
        svc_key = COIN_TOGGLE_BTNS[text]
        cur = data["settings"]["coin_services"][svc_key].get("enabled", True)
        data["settings"]["coin_services"][svc_key]["enabled"] = not cur
        save_data(data)
        lbl = data["settings"]["coin_services"][svc_key].get("label", svc_key)
        send(chat_id, f"*{lbl} {'✅ فعال' if not cur else '❌ غیرفعال'} شد.*", BACK_BTN)
        return

    if text in COIN_PRICE_BTNS:
        svc_key = COIN_PRICE_BTNS[text]
        states[uid] = f"ap_coin_price|{svc_key}"
        cur = data["settings"]["coin_services"][svc_key].get("price_per_1053", 0)
        lbl = data["settings"]["coin_services"][svc_key].get("label", svc_key)
        send(chat_id, f"*{lbl}\nنرخ فعلی: {cur:,} تومان\n\nنرخ جدید (تومان برای 1053 سکه):*", BACK_BTN)
        return

    if text in COIN_MM_BTNS:
        svc_key = COIN_MM_BTNS[text]
        states[uid] = f"ap_coin_mm|{svc_key}"
        cs  = data["settings"]["coin_services"][svc_key]
        lbl = cs.get("label", svc_key)
        send(chat_id, f"*{lbl}\nفعلی: {cs.get('min', 200):,} تا {cs.get('max', 3000):,}\n\nحداقل و حداکثر جدید (مثال: 200 3000):*", BACK_BTN)
        return

    # ─ کاربران ──────────────────────────────────────────
    if text == "🚫 مسدود کردن کاربر":
        states[uid] = "ap_block"
        send(chat_id, "*آیدی عددی:*", BACK_BTN)
        return
    if text == "✅ رفع مسدودیت":
        states[uid] = "ap_unblock"
        send(chat_id, "*آیدی عددی:*", BACK_BTN)
        return
    if text == "🔍 جستجوی کاربر":
        states[uid] = "ap_search"
        send(chat_id, "*آیدی عددی:*", BACK_BTN)
        return
    if text == "📵 لیست کاربران مسدود":
        bl = [(u, v) for u, v in data["users"].items() if v.get("blocked")]
        if not bl:
            send(chat_id, "*هیچ کاربر مسدودی نیست.*", BACK_BTN)
            return
        msg = f"*📵 مسدود ({len(bl)}):\n\n"
        for u, v in bl[:30]:
            msg += f"🆔{u}|{v.get('first_name', '?')}\n"
        send(chat_id, msg + "*", BACK_BTN)
        return

    # ─ کانال ────────────────────────────────────────────
    if text == "📢 تغییر آیدی کانال":
        states[uid] = "ap_set_channel"
        send(chat_id, f"*کانال فعلی: {data['settings']['channel']}\n\nجدید (@channel):*", BACK_BTN)
        return
    if text == "📌 تغییر لینک کانال":
        states[uid] = "ap_set_link"
        send(chat_id, f"*لینک فعلی: {data['settings']['channel_link']}\n\nجدید:*", BACK_BTN)
        return

    send_admin_panel(chat_id)

# ══════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════
def broadcast_media(admin_id, method, payload_key, file_id, caption=""):
    """پخش media به همه کاربران"""
    data = load_data()
    ok = fail = 0
    for u in data["users"].values():
        cid = u.get("chat_id")
        if not cid or int(cid) <= 0:
            continue
        try:
            body = {"chat_id": cid, payload_key: file_id, "parse_mode": "Markdown"}
            if caption:
                body["caption"] = caption
            requests.post(f"{BASE_URL}/{method}", json=body, timeout=10)
            ok += 1
            time.sleep(0.05)
        except:
            fail += 1
    send(admin_id, f"*📨 ارسال شد.\n✅ {ok}\n❌ {fail}*", BACK_BTN)


last_update_id = 0
states         = {}
_spam_tracker  = {}   # {uid: {'count': int, 'window': float}}

MAX_MSGS_PER_WINDOW = 5    # حداکثر پیام در بازه
SPAM_WINDOW_SECS    = 3    # بازه زمانی (ثانیه)
MAX_WARNINGS        = 3    # تعداد اخطار قبل از مسدودی

def check_spam(chat_id, msg_date):
    """بررسی اسپم با استفاده از timestamp خود پیام (نه زمان پردازش)"""
    uid = str(chat_id)
    if uid not in _spam_tracker:
        _spam_tracker[uid] = []
    # فقط پیام‌های درون بازه زمانی رو نگه دار
    _spam_tracker[uid] = [t for t in _spam_tracker[uid] if msg_date - t < SPAM_WINDOW_SECS]
    _spam_tracker[uid].append(msg_date)
    return len(_spam_tracker[uid]) > MAX_MSGS_PER_WINDOW

SVC_KEYS_TEXT = {
    "بازدید تکی 👁️":  "bale_view_single",
    "ری‌اکشن بله ❤️": "bale_reaction",
}
BTN_TO_SVC = {
    "🔴 سفارش بازدید | روبیکا ⚡️": "rubika_view",
    "🟢 سفارش بازدید | ایتا ☕️":   "eitaa_view",
    "🔵 سفارش ممبر | بله 🚀":       "bale_member",
    "🔴 سفارش ممبر | روبیکا ⚡️":   "rubika_member",
    "🟢 سفارش ممبر | ایتا ☕️":     "eitaa_member",
    "🟣 سفارش فالوور | روبیکا 🔥":  "rubika_follower",
}

COIN_LEAF_TEXTS = list(coin_service_key_from_text.__globals__["COIN_SERVICES"].keys()) if False else [
    "🔵 فروش سکه کانال | بله 🚀", "🔵 فروش سکه گروه | بله 🚀",
    "🔴 فروش سکه کانال | روبیکا ⚡️", "🔴 فروش سکه گروه | روبیکا ⚡️",
    "🔴 فروش سکه لایک | روبیکا ⚡️", "🔴 فروش سکه فالوور | روبیکا ⚡️",
    "🟢 فروش سکه کانال | ایتا ☕️", "🟢 فروش سکه گروه | ایتا ☕️",
]

print("===================================")
print("🤖 ربات فروش ممبر آرکا استارت شد")
print("===================================")

try:
    _me = requests.get(f"{BASE_URL}/getMe", timeout=10).json()
    if _me.get("ok") and _me["result"].get("username"):
        BOT_USERNAME = _me["result"]["username"]
        print(f"✅ یوزرنیم: @{BOT_USERNAME}")
except Exception as e:
    print(f"⚠️ یوزرنیم: {e}")

_fj_last_check = 0  # تایمر برای چک دوره‌ای هر ۶۰ ثانیه

while True:
    try:
        # ── بررسی دوره‌ای کانال‌های جوین اجباری هر ۶۰ ثانیه ──
        _now_ts = time.time()
        if _now_ts - _fj_last_check >= 60:
            _fj_last_check = _now_ts
            _hdata = load_data()
            check_fj_channels_health(_hdata)

        resp   = requests.get(f"{BASE_URL}/getUpdates",
                              params={"offset": last_update_id + 1, "timeout": 25}, timeout=30)
        result = resp.json()
        if not isinstance(result, dict) or not result.get("ok"):
            time.sleep(2); continue
        updates = result.get("result", [])
        if not isinstance(updates, list):
            time.sleep(2); continue

        for upd in updates:
            try:
                last_update_id = upd["update_id"]
                data = load_data()

                # ── Pre-checkout ─────────────────────────
                if "pre_checkout_query" in upd:
                    pcq = upd["pre_checkout_query"]
                    requests.post(f"{BASE_URL}/answerPreCheckoutQuery",
                                  json={"pre_checkout_query_id": pcq["id"], "ok": True}, timeout=10)
                    continue

                # ── Callback ─────────────────────────────
                if "callback_query" in upd:
                    cb      = upd["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    cb_data = cb.get("data", "")
                    requests.post(f"{BASE_URL}/answerCallbackQuery",
                                  json={"callback_query_id": cb["id"]}, timeout=5)

                    if cb_data == "check_join":
                        if check_membership(chat_id):
                            register_user(data, chat_id)
                            send_start(chat_id)
                        else:
                            send_not_joined(chat_id)

                    elif cb_data == "go_home":
                        states.pop(str(chat_id), None)
                        send_start(chat_id)

                    elif cb_data.startswith("use_discount|"):
                        choice   = cb_data.split("|")[1]
                        uid_cb   = str(chat_id)
                        st_cb    = states.get(uid_cb, "")
                        if not st_cb.startswith("order_discount|"):
                            send(chat_id, "*⚠️ خطا - دوباره سفارش بده.*")
                            continue
                        parts_cb = st_cb.split("|")
                        key_cb   = parts_cb[1]
                        qty_cb   = int(parts_cb[2])
                        price_cb = int(parts_cb[3])
                        link_cb  = parts_cb[4]
                        code_cb  = parts_cb[5]
                        states.pop(uid_cb, None)
                        if choice == "yes":
                            dc_cb   = data["discount_codes"].get(code_cb, {})
                            pct     = dc_cb.get("percent", 0)
                            new_p   = int(price_cb * (100 - pct) / 100)
                            send(chat_id, f"*✅ {pct}٪ تخفیف اعمال شد!\n💰 {price_cb:,} ← {new_p:,} تومان*")
                            send_invoice(chat_id, key_cb, qty_cb, new_p, link_cb, discount_code=code_cb)
                        else:
                            send_invoice(chat_id, key_cb, qty_cb, price_cb, link_cb)

                    elif cb_data == "game_dice_roll":
                        if states.get(str(chat_id), "").startswith("game_dice|"):
                            process_dice_roll(chat_id)
                        else:
                            start_dice_game(chat_id)

                    elif cb_data.startswith("rps|"):
                        if states.get(str(chat_id), "").startswith("game_rps|"):
                            process_rps(chat_id, cb_data.split("|")[1])
                        else:
                            send_rps_game(chat_id)

                    elif cb_data == "cancel_order":
                        states.pop(str(chat_id), None)
                        states.pop(f"coin_pending_{chat_id}", None)
                        send(chat_id, "*❌ سفارش لغو شد.*")
                        send_start(chat_id)

                    elif cb_data.startswith("fj_check_admin_free|"):
                        parts_cb = cb_data.split("|")
                        hours_cb = int(parts_cb[1])
                        link_cb  = "|".join(parts_cb[2:])
                        send(chat_id, "*⏳ در حال بررسی...*")
                        admin_result = check_bot_is_admin(link_cb)
                        if admin_result is True:
                            uid_cb = str(chat_id)
                            d2 = load_data()
                            u2 = d2["users"].get(uid_cb, {})
                            u2["fj_free_used_hours"] = u2.get("fj_free_used_hours", 0) + hours_cb
                            d2["forced_join_order_counter"] = d2.get("forced_join_order_counter", 0) + 1
                            oid2 = f"FJ{d2['forced_join_order_counter']}"
                            d2["forced_join_orders"].append({
                                "id": oid2, "user_id": chat_id, "hours": hours_cb,
                                "link": link_cb, "price": 0, "status": "pending",
                                "free": True, "date": datetime.now().isoformat(), "end_time": ""
                            })
                            save_data(d2)
                            states.pop(str(chat_id), None)
                            send(chat_id,
                                f"*✅ سفارش جوین اجباری رایگان ثبت شد!\n\n"
                                f"🆔 {oid2}\n🔗 {link_cb}\n⏳ {hours_cb} ساعت\n💰 رایگان 🎁\n\n"
                                f"⏳ منتظر تأیید ادمین باشید.*"
                            )
                            for aid in ADMIN_IDS:
                                send(aid,
                                    f"*🎁 سفارش جوین اجباری رایگان!\n\n"
                                    f"🆔 {oid2}\n👤 {chat_id}\n🔗 {link_cb}\n⏳ {hours_cb} ساعت*",
                                    {"inline_keyboard": [[{"text": "✅ تأیید و فعال کردن", "callback_data": f"approve_fj|{oid2}"}]]}
                                )
                        elif admin_result is None:
                            send(chat_id, "*⚠️ خطای شبکه. دوباره تلاش کنید.*",
                                {"inline_keyboard": [[{"text": "🔄 دوباره", "callback_data": cb_data}], [{"text": "❌ انصراف", "callback_data": "cancel_order"}]]})
                        else:
                            send(chat_id, f"*❌ ربات هنوز ادمین نیست!\n🔗 {link_cb}*",
                                {"inline_keyboard": [[{"text": "✅ ادمین کردم", "callback_data": cb_data}], [{"text": "❌ انصراف", "callback_data": "cancel_order"}]]})

                    elif cb_data.startswith("fj_check_admin|"):
                        parts_cb = cb_data.split("|")
                        hours_cb = int(parts_cb[1])
                        price_cb = int(parts_cb[2])
                        link_cb  = "|".join(parts_cb[3:])
                        send(chat_id, "*⏳ در حال بررسی ادمین بودن ربات...*")
                        admin_result = check_bot_is_admin(link_cb)
                        if admin_result is True:
                            states.pop(str(chat_id), None)
                            send(chat_id,
                                f"*✅ ربات ادمین است! لینک ثبت شد.\n\n"
                                f"📱 جوین اجباری: {hours_cb} ساعت\n"
                                f"🔗 {link_cb}\n"
                                f"💰 {price_cb:,} تومان\n\n"
                                f"فاکتور پرداخت ارسال می‌شود...*"
                            )
                            send_fj_invoice(chat_id, hours_cb, link_cb)
                        elif admin_result is None:
                            send(chat_id,
                                f"*⚠️ خطا در بررسی ادمین!\n\n"
                                f"لطفاً دوباره تلاش کنید.*",
                                {"inline_keyboard": [
                                    [{"text": "🔄 دوباره چک کن", "callback_data": f"fj_check_admin|{hours_cb}|{price_cb}|{link_cb}"}],
                                    [{"text": "❌ انصراف", "callback_data": "cancel_order"}]
                                ]}
                            )
                        else:
                            send(chat_id,
                                f"*❌ ربات هنوز ادمین کانال نیست!\n\n"
                                f"🔗 {link_cb}\n\n"
                                f"لطفاً @{BOT_USERNAME} را به عنوان ادمین اضافه کنید و دوباره تلاش کنید.*",
                                {"inline_keyboard": [
                                    [{"text": "✅ ادمین کردم، دوباره چک کن", "callback_data": f"fj_check_admin|{hours_cb}|{price_cb}|{link_cb}"}],
                                    [{"text": "❌ انصراف", "callback_data": "cancel_order"}]
                                ]}
                            )

                    elif cb_data.startswith("complete|"):
                        if not is_admin(chat_id): continue
                        oid     = cb_data.split("|", 1)[1]
                        ok, res = complete_order(oid)
                        send(chat_id, f"*{'✅ تکمیل شد.' if ok else '⚠️ ' + str(res)}*")

                    elif cb_data.startswith("approve_fj|"):
                        if not is_admin(chat_id): continue
                        oid = cb_data.split("|", 1)[1]
                        target = next((o for o in data["forced_join_orders"] if o["id"] == oid), None)
                        if target:
                            if target.get("status") == "active":
                                send(chat_id, f"*⚠️ سفارش {oid} قبلاً فعال شده است.*")
                            else:
                                iran_now   = get_iran_now()
                                hours      = target.get("hours", 1)
                                end_dt     = iran_now + timedelta(hours=hours)
                                end_time   = end_dt.strftime("%Y-%m-%d %H:%M")
                                start_time = iran_now.strftime("%Y-%m-%d %H:%M")
                                target["status"]     = "active"
                                target["end_time"]   = end_time
                                target["start_time"] = start_time
                                if "forced_join_channels" not in data:
                                    data["forced_join_channels"] = []
                                data["forced_join_channels"] = [
                                    c for c in data["forced_join_channels"]
                                    if c.get("order_id") != oid
                                ]
                                data["forced_join_channels"].append({
                                    "order_id":   oid,
                                    "link":       target["link"],
                                    "start_time": start_time,
                                    "end_time":   end_time,
                                    "active":     True,
                                    "date":       datetime.now().isoformat()
                                })
                                save_data(data)
                                send(chat_id,
                                    f"*✅ سفارش {oid} تأیید و کانال فعال شد!\n\n"
                                    f"🔗 {target['link']}\n"
                                    f"⏳ مدت: {hours} ساعت\n"
                                    f"🟢 شروع: {start_time}\n"
                                    f"🔴 پایان: {end_time}*"
                                )
                                send(target["user_id"],
                                    f"*✅ سفارش جوین اجباری شما تأیید شد!\n\n"
                                    f"🆔 {oid}\n"
                                    f"🔗 {target['link']}\n"
                                    f"⏳ {hours} ساعت\n"
                                    f"🟢 شروع: {start_time}\n"
                                    f"🔴 پایان: {end_time}\n\n"
                                    f"کانال شما در جوین اجباری فعال شد. 🚀\n\n"
                                    f"⚠️ توجه: اگر ربات را از ادمینی کانال خارج کنید، سفارش لغو می‌شود و وجه عودت داده نمی‌شود.*"
                                )
                        else:
                            send(chat_id, f"*⚠️ سفارش {oid} یافت نشد.*")

                    elif cb_data.startswith("reject_fj|"):
                        if not is_admin(chat_id): continue
                        oid    = cb_data.split("|", 1)[1]
                        target = next((o for o in data["forced_join_orders"] if o["id"] == oid), None)
                        if target:
                            target["status"] = "rejected"
                            save_data(data)
                            send(chat_id, f"*❌ سفارش {oid} رد شد.*")
                            send(target["user_id"],
                                f"*❌ سفارش جوین اجباری شما رد شد.\n\n"
                                f"🆔 {oid}\n"
                                f"📞 پشتیبانی: @ARKA_SUPPORT_IR*"
                            )
                        else:
                            send(chat_id, f"*⚠️ سفارش {oid} یافت نشد.*")

                    elif cb_data.startswith("remove_fj_channel|"):
                        if not is_admin(chat_id): continue
                        oid = cb_data.split("|", 1)[1]
                        data["forced_join_channels"] = [
                            c for c in data.get("forced_join_channels", [])
                            if c.get("order_id") != oid
                        ]
                        save_data(data)
                        send(chat_id, f"*✅ کانال {oid} حذف شد.*")

                    elif cb_data.startswith("complete_design|"):
                        if not is_admin(chat_id): continue
                        oid    = cb_data.split("|", 1)[1]
                        ok, res = complete_design_order(oid, data)
                        send(chat_id, f"*{'✅ سفارش طراحی تکمیل شد.' if ok else '⚠️ ' + str(res)}*")

                    elif cb_data.startswith("reject_design|"):
                        if not is_admin(chat_id): continue
                        oid    = cb_data.split("|", 1)[1]
                        ok, res = reject_design_order(oid, data)
                        send(chat_id, f"*{'❌ سفارش طراحی رد شد.' if ok else '⚠️ ' + str(res)}*")

                    elif cb_data.startswith("approve_coin|"):
                        if not is_admin(chat_id): continue
                        oid    = cb_data.split("|", 1)[1]
                        ok, o  = approve_coin_order(oid, data)
                        if ok:
                            send(chat_id, f"*✅ سفارش {oid} تأیید شد.*")
                        else:
                            send(chat_id, f"*⚠️ سفارش {oid} یافت نشد.*")

                    elif cb_data.startswith("reject_coin|"):
                        if not is_admin(chat_id): continue
                        oid    = cb_data.split("|", 1)[1]
                        ok, o  = reject_coin_order(oid, data)
                        if ok:
                            send(chat_id, f"*❌ سفارش {oid} رد شد.*")
                        else:
                            send(chat_id, f"*⚠️ سفارش {oid} یافت نشد.*")

                    elif cb_data.startswith("channel_coin|"):
                        if not is_admin(chat_id): continue
                        oid = cb_data.split("|", 1)[1]
                        ok  = channel_coin_order(oid, data)
                        send(chat_id, f"*{'✅ به کانال ارسال شد.' if ok else '⚠️ سفارش یافت نشد.'}*")

                    elif cb_data.startswith("coin_pay|"):
                        # کاربر پاکت هدیه یا کارت به کارت انتخاب کرد
                        # فرمت: coin_pay|gift|oid  یا  coin_pay|card|oid
                        parts    = cb_data.split("|")
                        pay_type = parts[1]
                        oid      = parts[2]
                        uid_s    = str(chat_id)
                        # پیدا کردن سفارش در states
                        # اطلاعات سفارش در state نگه داشته شده
                        coin_state = states.get(f"coin_pending_{chat_id}", {})
                        if not coin_state:
                            send(chat_id, "*⚠️ سفارش یافت نشد. دوباره شروع کنید.*", BACK_BTN_USER)
                            continue
                        if pay_type == "gift":
                            states[uid_s] = f"coin_gift_id|{json.dumps(coin_state)}"
                            send(chat_id,
                                f"*🎁 روش پرداخت: پاکت هدیه\n\n"
                                f"📌 مرحله 3 از 4\n\n"
                                f"لطفاً آیدی بله خود را وارد کنید تا پاکت سکه ارسال شود:\n\n"
                                f"مثال: @username یا 09123456789*",
                                BACK_BTN_USER
                            )
                        else:  # card
                            mn_card = 1000
                            if coin_state.get("amount", 0) < mn_card:
                                send(chat_id,
                                    f"*⚠️ حداقل واریز به صورت کارت به کارت {mn_card} سکه است.\n\n"
                                    f"تعداد سکه انتخابی شما {coin_state.get('amount', 0)} سکه می‌باشد.\n"
                                    f"لطفاً روش پاکت هدیه را انتخاب کنید یا تعداد بیشتری سکه انتخاب کنید.*",
                                    BACK_BTN_USER
                                )
                                states.pop(f"coin_pending_{chat_id}", None)
                                continue
                            states[uid_s] = f"coin_card_num|{json.dumps(coin_state)}"
                            send(chat_id,
                                f"*💳 روش پرداخت: کارت به کارت\n\n"
                                f"📌 مرحله 3 از 4\n\n"
                                f"لطفاً شماره کارت خود را وارد کنید (۱۶ رقم):\n\n"
                                f"مثال: 6037991234567890*",
                                BACK_BTN_USER
                            )

                    elif cb_data.startswith("coin_screenshot|"):
                        # کاربر روی دکمه ارسال اسکرین شات زد
                        oid   = cb_data.split("|", 1)[1]
                        uid_s = str(chat_id)
                        states[uid_s] = f"coin_screenshot|{oid}"
                        send(chat_id,
                            "*📸 لطفاً اسکرین شات رسید واریز سکه را ارسال کنید.\n\n"
                            "⚠️ فقط تصویر ارسال شود.*",
                            BACK_BTN_USER
                        )

                    elif cb_data.startswith("reply_ticket|"):
                        if not is_admin(chat_id): continue
                        tid = cb_data.split("|", 1)[1]
                        t   = data["tickets"].get(tid)
                        if not t:
                            send(chat_id, "*⚠️ تیکت یافت نشد.*"); continue
                        if t.get("status") == "closed":
                            send(chat_id, f"*⚠️ تیکت #{tid} بسته است.*"); continue
                        states[str(chat_id)] = f"ap_reply_ticket|{tid}"
                        history = ""
                        for m in t.get("messages", [])[-5:]:
                            sender   = "👤 کاربر" if m["from"] == "user" else "🛡️ ادمین"
                            history += f"{sender}: {m['text'][:100]}\n"
                        send(chat_id,
                            f"*↩️ پاسخ به تیکت #{tid}\n\n"
                            f"📝 آخرین پیام‌ها:\n{history}\n\n"
                            f"پاسخ خود را ارسال کنید:*",
                            kb(["🔙 بازگشت"])
                        )

                    elif cb_data.startswith("close_ticket|"):
                        if not is_admin(chat_id): continue
                        tid = cb_data.split("|", 1)[1]
                        t   = data["tickets"].get(tid)
                        if t:
                            t["status"] = "closed"
                            save_data(data)
                            send(chat_id, f"*✅ تیکت #{tid} بسته شد.*")
                            try:
                                send(t["user_id"],
                                    f"*🔴 گفتگوی #{tid} توسط پشتیبانی بسته شد.\n\n"
                                    f"برای مشکل جدید می‌توانید دوباره پیام بدید.*",
                                    BACK_BTN_USER
                                )
                                states.pop(str(t["user_id"]), None)
                            except: pass
                        else:
                            send(chat_id, "*⚠️ تیکت یافت نشد.*")
                    continue

                # ── Message ──────────────────────────────
                if "message" not in upd:
                    continue
                msg     = upd["message"]
                chat_id = msg["chat"]["id"]
                uid     = str(chat_id)
                uinfo   = msg.get("from", {})

                # ── پخش media ادمین ──────────────────────────
                if is_admin(chat_id) and states.get(uid) == "ap_broadcast":
                    caption = (msg.get("caption") or "").strip()
                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                        broadcast_media(chat_id, "sendPhoto", "photo", file_id, caption)
                        states[uid] = "admin"
                        continue
                    if "animation" in msg:
                        broadcast_media(chat_id, "sendAnimation", "animation", msg["animation"]["file_id"], caption)
                        states[uid] = "admin"
                        continue
                    if "sticker" in msg:
                        broadcast_media(chat_id, "sendSticker", "sticker", msg["sticker"]["file_id"])
                        states[uid] = "admin"
                        continue
                    if "document" in msg:
                        broadcast_media(chat_id, "sendDocument", "document", msg["document"]["file_id"], caption)
                        states[uid] = "admin"
                        continue
                    if "video" in msg:
                        broadcast_media(chat_id, "sendVideo", "video", msg["video"]["file_id"], caption)
                        states[uid] = "admin"
                        continue

                if "successful_payment" in msg:
                    payload = msg["successful_payment"].get("invoice_payload", "")
                    if payload.startswith("design_"):
                        register_design_payment(chat_id, payload)
                    elif payload.startswith("fj_"):
                        register_fj_payment(chat_id, payload)
                    else:
                        register_successful_order(chat_id, payload)
                    states.pop(uid, None)
                    continue

                if "contact" in msg:
                    contact = msg["contact"]
                    phone   = contact.get("phone_number", "")
                    fname   = contact.get("first_name", "")
                    data2 = load_data()
                    data2["pledges"][uid] = {
                        "chat_id":    chat_id,
                        "phone":      phone,
                        "first_name": fname,
                        "username":   uinfo.get("username", ""),
                        "date":       datetime.now().isoformat(),
                        "reason":     "spam_block"
                    }
                    if uid in data2["users"]:
                        data2["users"][uid]["blocked"]       = False
                        data2["users"][uid]["spam_warnings"] = 0
                    save_data(data2)
                    _spam_tracker.pop(uid, None)
                    send(chat_id,
                        f"*✅ شماره تلفن ثبت شد و مسدودیت برداشته شد.\n\n"
                        f"📱 {phone}\n\n"
                        f"تعهد می‌دهید که قوانین ربات را رعایت کنید.\n"
                        f"در صورت تخلف مجدد، حساب شما برای همیشه مسدود می‌شود.*",
                        BACK_BTN_USER
                    )
                    for aid in ADMIN_IDS:
                        send(aid,
                            f"*📋 تعهد جدید\n\n"
                            f"👤 {fname} | @{uinfo.get('username','')}\n"
                            f"🆔 {chat_id}\n"
                            f"📱 {phone}\n"
                            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
                        )
                    continue

                # ── بررسی عکس (اسکرین شات) ──────────────
                cur_state = states.get(uid, "")
                if "photo" in msg:
                    if cur_state.startswith("coin_screenshot|"):
                        oid        = cur_state.split("|", 1)[1]
                        photo_id   = msg["photo"][-1]["file_id"]
                        # پیدا کردن سفارش
                        coin_order = next((o for o in data["coin_orders"] if o["id"] == oid), None)
                        if coin_order:
                            coin_order["screenshot"] = photo_id
                            coin_order["status"]     = "pending"
                            save_data(data)
                            states.pop(uid, None)
                            send(chat_id,
                                f"*✅ سفارش فروش سکه ثبت شد!\n\n"
                                f"━━━━━━━━━━━━\n"
                                f"🆔 {coin_order['id']}\n"
                                f"📦 {coin_order.get('service_label', '')}\n"
                                f"🪙 {coin_order.get('amount', 0):,} سکه\n"
                                f"💰 {coin_order.get('price', 0):,} تومان\n"
                                f"━━━━━━━━━━━━\n"
                                f"⏳ سفارش در حال بررسی است.\n"
                                f"📞 پشتیبانی: @ARKA_SUPPORT_IR*",
                                BACK_BTN_USER
                            )
                            pay_type = "پاکت هدیه" if coin_order.get("payment_type") == "gift" else "کارت به کارت"
                            for aid in ADMIN_IDS:
                                send(aid,
                                    f"*🪙 سفارش فروش سکه جدید!\n\n"
                                    f"🆔 {coin_order['id']}\n"
                                    f"👤 کاربر: {chat_id}\n"
                                    f"📦 {coin_order.get('service_label', '')}\n"
                                    f"🪙 {coin_order.get('amount', 0):,} سکه\n"
                                    f"💰 {coin_order.get('price', 0):,} تومان\n"
                                    f"📱 شماره: {coin_order.get('phone', '')}\n"
                                    f"💳 روش: {pay_type}\n"
                                    f"📋 اطلاعات: {coin_order.get('payment_info', '')}*",
                                    {"inline_keyboard": [
                                        [
                                            {"text": f"✅ تأیید", "callback_data": f"approve_coin|{oid}"},
                                            {"text": f"❌ رد",    "callback_data": f"reject_coin|{oid}"}
                                        ],
                                        [{"text": "📤 ارسال به کانال", "callback_data": f"channel_coin|{oid}"}]
                                    ]}
                                )
                                # forward عکس به ادمین
                                forward_photo(aid, chat_id, msg["message_id"])
                        else:
                            send(chat_id, "*⚠️ سفارش یافت نشد.*", BACK_BTN_USER)
                        continue
                    # اگر عکس فرستاد ولی در state اسکرین شات نبود
                    continue

                text = msg.get("text", "").strip()
                if not text:
                    # اگر پیام غیر متنی و غیر عکس بود
                    if cur_state.startswith("coin_screenshot|"):
                        send(chat_id, "*⚠️ لطفاً فقط تصویر ارسال کنید.*")
                    continue

                is_brand_new = uid not in data["users"]
                register_user(data, chat_id, uinfo)

                if data["users"].get(uid, {}).get("blocked"):
                    send(chat_id, "*⛔ دسترسی شما مسدود شده است.*")
                    continue

                # چک وضعیت ربات
                if not data["settings"].get("bot_active", True) and not is_admin(chat_id):
                    send(chat_id, "*🔴 ربات در حال حاضر غیرفعال است.\n\nلطفاً بعداً مراجعه کنید. 🙏*")
                    continue

                # ── ضد اسپم ────────────────────────────────────────
                msg_date = msg.get("date", int(time.time()))
                if not is_admin(chat_id) and check_spam(chat_id, msg_date):
                    data["users"][uid]["spam_warnings"] = data["users"][uid].get("spam_warnings", 0) + 1
                    warns = data["users"][uid]["spam_warnings"]
                    if warns >= MAX_WARNINGS:
                        data["users"][uid]["blocked"] = True
                        save_data(data)
                        send(chat_id,
                            f"*🚫 حساب شما به دلیل ارسال پیام‌های زیاد مسدود شد!\n\n"
                            f"برای رفع مسدودیت، شماره تلفن خود را ارسال کنید.*",
                            {"keyboard": [[{"text": "📱 ارسال شماره تلفن برای رفع مسدودیت", "request_contact": True}]],
                             "resize_keyboard": True, "one_time_keyboard": True}
                        )
                    else:
                        save_data(data)
                        send(chat_id,
                            f"*⚠️ اخطار {warns}/{MAX_WARNINGS}: ارسال پیام زیاد!\n\n"
                            f"پس از {MAX_WARNINGS} اخطار حساب شما مسدود می‌شود.*"
                        )
                    continue

                if text == "/admin":
                    if is_admin(chat_id):
                        states[uid] = "admin"
                        send_admin_panel(chat_id)
                    continue

                cur_state = states.get(uid, "")
                if cur_state == "admin" or cur_state.startswith("ap_") or cur_state == "admin_coin":
                    handle_admin(chat_id, text, data, states)
                    continue

                # ── ثبت referral قبل از check_membership ──────────────
                # کاربر جدیدی که از لینک دعوت اومده باید قبل از هر چیز ثبت بشه
                if is_brand_new and text.startswith("/start "):
                    parts_start = text.split(" ", 1)
                    ref_id = parts_start[1].strip()
                    if ref_id.isdigit() and ref_id != uid:
                        data = load_data()
                        ref_user = data["users"].get(ref_id)
                        if ref_user is not None and data["users"].get(uid, {}).get("referred_by") is None:
                            data["users"][uid]["referred_by"] = int(ref_id)
                            if uid not in [str(r) for r in data["users"][ref_id].get("referrals", [])]:
                                data["users"][ref_id].setdefault("referrals", []).append(chat_id)
                            refs_per     = data["settings"].get("fj_free_refs_per_hour", 3)
                            hrs_per      = data["settings"].get("fj_free_hours_per_batch", 1)
                            new_count    = len(data["users"][ref_id]["referrals"])
                            save_data(data)
                            used         = data["users"][ref_id].get("fj_free_used_hours", 0)
                            total_earned = (new_count // refs_per) * hrs_per
                            avail        = total_earned - used
                            send(int(ref_id),
                                f"*🎉 یک زیرمجموعه جدید برات اومد!\n\n"
                                f"👤 زیرمجموعه‌های کل: {new_count} نفر\n"
                                f"⏳ ساعت رایگان باقی‌مانده: {avail} ساعت\n\n"
                                f"هر {refs_per} زیرمجموعه = {hrs_per} ساعت جوین اجباری رایگان 🎁*"
                            )

                if not check_membership(chat_id):
                    send_join_required(chat_id)
                    continue

                if text.startswith("/start"):
                    states.pop(uid, None)
                    states.pop(f"coin_pending_{chat_id}", None)
                    send_start(chat_id)
                    continue

                if text in ("🔙 بازگشت به منوی اصلی 🏠", "🏠 بازگشت"):
                    states.pop(uid, None)
                    states.pop(f"coin_pending_{chat_id}", None)
                    send_start(chat_id)
                    continue

                if text == "🔙 بازگشت":
                    cur_b = states.get(uid, "")
                    if cur_b in ("coin_bale", "coin_rubika", "coin_eitaa"):
                        states[uid] = "coin_platform"
                        send_coin_platform(chat_id)
                    else:
                        states.pop(uid, None)
                        states.pop(f"coin_pending_{chat_id}", None)
                        send_start(chat_id)
                    continue

                # ─ منوی اصلی ─────────────────────────────
                if text == "سفارش بازدید 👁️":
                    states.pop(uid, None)
                    send_platform(chat_id)
                    continue
                if text == "سفارش ممبر 👥":
                    states.pop(uid, None)
                    send_member_platform(chat_id)
                    continue
                if text == "حساب کاربری 👤":
                    send_account(chat_id)
                    continue
                if text == "پیگیری سفارش 🔎":
                    send_tracking(chat_id)
                    continue
                if text == "قوانین ⚖️":
                    send_rules(chat_id)
                    continue
                if text == "📞 پشتیبانی":
                    states[uid] = "support"
                    send_support_menu(chat_id)
                    continue

                if text == "🛍 فروش سکه":
                    states[uid] = "coin_platform"
                    send_coin_platform(chat_id)
                    continue

                if text == "🎨 طراحی عکس حرفه‌ای":
                    states[uid] = "design_bale_id"
                    send_design_start(chat_id)
                    continue

                if text == "👥 زیرمجموعه‌گیری":
                    send_referral_menu(chat_id)
                    continue

                if text == "🧩 سرگرمی‌ها":
                    states.pop(uid, None)
                    send_games_menu(chat_id)
                    continue

                if text == "🎡 گردونه روزانه":
                    states.pop(uid, None)
                    send_spin_wheel(chat_id)
                    continue

                # ── بازی‌ها ──────────────────────────────────────
                if text == "🎲 تاس بازی" or text == "🎲 بازی مجدد":
                    start_dice_game(chat_id); continue
                if text == "🔢 حدس عدد" or text == "🔢 بازی مجدد":
                    send_number_game_menu(chat_id); continue
                if text == "🟢 آسان (۱-۲۰، ۷ شانس)":
                    start_number_game(chat_id, "easy"); continue
                if text == "🟡 متوسط (۱-۵۰، ۶ شانس)":
                    start_number_game(chat_id, "medium"); continue
                if text == "🔴 سخت (۱-۱۰۰، ۵ شانس)":
                    start_number_game(chat_id, "hard"); continue
                if text == "🔤 حدس کلمه" or text == "🔤 بازی مجدد":
                    start_word_game(chat_id); continue
                if text == "🪨 سنگ کاغذ قیچی" or text == "🪨 بازی مجدد":
                    send_rps_game(chat_id); continue
                if text == "🧮 محاسبه سریع" or text == "🧮 بازی مجدد":
                    start_math_game(chat_id); continue

                if text == "📱 ثبت جوین اجباری":
                    states[uid] = "fj_hours"
                    send_forced_join_menu(chat_id)
                    continue

                if text == "🎁 جوین اجباری رایگان":
                    states[uid] = "fj_free_hours"
                    send_fj_free_menu(chat_id)
                    continue

                # ─ فروش سکه زیرمنو ──────────────────────
                if text == "🔵 فروش سکه | بله 🚀":
                    states[uid] = "coin_bale"
                    send_coin_bale_menu(chat_id)
                    continue
                if text == "🔴 فروش سکه | روبیکا ⚡️":
                    states[uid] = "coin_rubika"
                    send_coin_rubika_menu(chat_id)
                    continue
                if text == "🟢 فروش سکه | ایتا ☕️":
                    states[uid] = "coin_eitaa"
                    send_coin_eitaa_menu(chat_id)
                    continue

                # ─ سرویس سکه انتخاب شد ─────────────────
                svc_key = coin_service_key_from_text(text)
                if svc_key:
                    start_coin_order(chat_id, svc_key, data, states)
                    continue

                # ─ جریان سفارش سکه ──────────────────────
                if cur_state.startswith("coin_qty|"):
                    svc_key = cur_state.split("|")[1]
                    cs_svc  = data["settings"]["coin_services"].get(svc_key, {})
                    mn      = cs_svc.get("min", 200)
                    mx      = cs_svc.get("max", 3000)
                    price_p = cs_svc.get("price_per_1053", 0)
                    try:
                        qty = int(text.replace(",", "").strip())
                    except:
                        send(chat_id, "*⚠️ لطفاً فقط عدد وارد کنید.*")
                        continue
                    if qty < mn:
                        send(chat_id, f"*⚠️ حداقل تعداد {mn:,} سکه می‌باشد.*")
                        continue
                    if qty > mx:
                        send(chat_id, f"*⚠️ حداکثر تعداد {mx:,} سکه می‌باشد.*")
                        continue
                    price = calc_coin_price(qty, price_p)
                    states[uid] = f"coin_phone|{svc_key}|{qty}|{price}"
                    send(chat_id,
                        f"*✅ تعداد {qty:,} سکه | مبلغ: {price:,} تومان\n\n"
                        f"📱 شماره تلفن خود را وارد کنید:\n\n"
                        f"📌 مرحله 2 از 4*",
                        BACK_BTN_USER
                    )
                    continue

                if cur_state.startswith("coin_phone|"):
                    parts    = cur_state.split("|")
                    svc_key  = parts[1]
                    qty      = int(parts[2])
                    price    = int(parts[3])
                    phone    = text.strip()
                    if not phone.isdigit() or len(phone) != 11:
                        send(chat_id, "*⚠️ شماره تلفن نامعتبر است!\nشماره باید ۱۱ رقم باشد.\nمثال: 09123456789*")
                        continue
                    if not phone.startswith("09"):
                        send(chat_id, "*⚠️ شماره تلفن باید با 09 شروع شود.\nمثال: 09123456789\nشماره را فقط به انگلیسی وارد کنید.*")
                        continue
                    # نمایش پیش‌نمایش
                    svc_label = data["settings"]["coin_services"].get(svc_key, {}).get("label", svc_key)
                    # ذخیره اطلاعات موقت
                    coin_pending = {
                        "svc_key":     svc_key,
                        "svc_label":   svc_label,
                        "amount":      qty,
                        "price":       price,
                        "phone":       phone,
                        "user_id":     chat_id,
                    }
                    states[f"coin_pending_{chat_id}"] = coin_pending
                    states[uid] = "coin_preview"
                    # تولید شناسه سفارش موقت
                    data["coin_order_counter"] = data.get("coin_order_counter", 0) + 1
                    temp_oid = f"CSK{data['coin_order_counter']}"
                    save_data(data)
                    coin_pending["temp_oid"] = temp_oid
                    states[f"coin_pending_{chat_id}"] = coin_pending
                    send(chat_id,
                        f"*🧾 پیش‌نمایش\n"
                        f"━━━━━━━━━━━━\n\n"
                        f"📦 نام سرویس: {svc_label}\n"
                        f"✴️ تعداد: {qty:,} سکه\n"
                        f"💵 مبلغ قابل پرداخت: {price:,} تومان\n"
                        f"📱 مقصد واریز سکه: {phone}\n\n"
                        f"✅️ اکنون اگر اطلاعات درست است دکمه مورد نظر را انتخاب نمایید!*",
                        {"inline_keyboard": [
                            [
                                {"text": "🎁 دریافت پاکت هدیه",  "callback_data": f"coin_pay|gift|{temp_oid}"},
                                {"text": "💳 دریافت کارت به کارت", "callback_data": f"coin_pay|card|{temp_oid}"}
                            ],
                            [{"text": "🔙 بازگشت", "callback_data": "cancel_order"}]
                        ]}
                    )
                    continue

                # ─ آیدی پاکت هدیه ───────────────────────
                if cur_state.startswith("coin_gift_id|"):
                    try:
                        coin_info = json.loads(cur_state.split("|", 1)[1])
                    except:
                        coin_info = states.get(f"coin_pending_{chat_id}", {})
                    bale_id   = text.strip()
                    coin_info["payment_type"] = "gift"
                    coin_info["payment_info"] = bale_id
                    # ثبت سفارش
                    oid = coin_info.get("temp_oid", f"CSK?")
                    data["coin_orders"].append({
                        "id":           oid,
                        "user_id":      chat_id,
                        "service_key":  coin_info.get("svc_key", ""),
                        "service_label": coin_info.get("svc_label", ""),
                        "amount":       coin_info.get("amount", 0),
                        "price":        coin_info.get("price", 0),
                        "phone":        coin_info.get("phone", ""),
                        "payment_type": "gift",
                        "payment_info": bale_id,
                        "status":       "awaiting_screenshot",
                        "date":         datetime.now().isoformat()
                    })
                    save_data(data)
                    states.pop(f"coin_pending_{chat_id}", None)
                    states[uid] = f"coin_screenshot|{oid}"
                    send(chat_id,
                        f"*✅️ اطلاعات ثبت شد.\n"
                        f"━━━━━━━━━━━━\n\n"
                        f"📦 نام سرویس: {coin_info.get('svc_label', '')}\n"
                        f"✴️ تعداد: {coin_info.get('amount', 0):,} سکه\n"
                        f"💵 مبلغ قابل دریافت: {coin_info.get('price', 0):,} تومان\n"
                        f"📱 مبدأ واریز سکه: {coin_info.get('phone', '')}\n\n"
                        f"━━━━━━━━━━━━\n"
                        f"📞 شماره تلفنی که باید سکه به آن واریز شود:\n"
                        f"{COIN_PHONE_NUMBER}\n\n"
                        f"━━━━━━━━━━━━\n\n"
                        f"📌 مرحله 4 از 4 - ارسال اسکرین شات\n\n"
                        f"⚠️ لطفاً پس از واریز سکه به شماره {COIN_PHONE_NUMBER}\n"
                        f"🎁 یک اسکرین شات از واریز سکه ارسال کنید.\n\n"
                        f"✅️ روی دکمه ارسال اسکرین شات کلیک کرده و تصویر را ارسال کنید.*",
                        {"inline_keyboard": [
                            [{"text": "📸 ارسال اسکرین شات", "callback_data": f"coin_screenshot|{oid}"}],
                            [{"text": "🔙 بازگشت به منوی اصلی 🏠", "callback_data": "cancel_order"}]
                        ]}
                    )
                    continue

                # ─ شماره کارت کاربر ─────────────────────
                if cur_state.startswith("coin_card_num|"):
                    try:
                        coin_info = json.loads(cur_state.split("|", 1)[1])
                    except:
                        coin_info = states.get(f"coin_pending_{chat_id}", {})
                    card_num = text.strip().replace("-", "").replace(" ", "")
                    if not card_num.isdigit() or len(card_num) != 16:
                        send(chat_id, "*⚠️ شماره کارت باید ۱۶ رقم باشد.\nمثال: 6037991234567890*")
                        continue
                    coin_info["payment_type"] = "card"
                    coin_info["payment_info"] = card_num
                    oid = coin_info.get("temp_oid", f"CSK?")
                    data["coin_orders"].append({
                        "id":           oid,
                        "user_id":      chat_id,
                        "service_key":  coin_info.get("svc_key", ""),
                        "service_label": coin_info.get("svc_label", ""),
                        "amount":       coin_info.get("amount", 0),
                        "price":        coin_info.get("price", 0),
                        "phone":        coin_info.get("phone", ""),
                        "payment_type": "card",
                        "payment_info": card_num,
                        "status":       "awaiting_screenshot",
                        "date":         datetime.now().isoformat()
                    })
                    save_data(data)
                    states.pop(f"coin_pending_{chat_id}", None)
                    states[uid] = f"coin_screenshot|{oid}"
                    admin_card = data["settings"].get("coin_card_number", "تنظیم نشده")
                    send(chat_id,
                        f"*✅️ اطلاعات ثبت شد.\n"
                        f"━━━━━━━━━━━━\n\n"
                        f"📦 نام سرویس: {coin_info.get('svc_label', '')}\n"
                        f"✴️ تعداد: {coin_info.get('amount', 0):,} سکه\n"
                        f"💵 مبلغ قابل دریافت: {coin_info.get('price', 0):,} تومان\n"
                        f"📱 مبدأ واریز سکه: {coin_info.get('phone', '')}\n\n"
                        f"━━━━━━━━━━━━\n"
                        f"📞 شماره تلفنی که باید سکه به آن واریز شود:\n"
                        f"{COIN_PHONE_NUMBER}\n\n"
                        f"━━━━━━━━━━━━\n\n"
                        f"📌 مرحله 4 از 4 - ارسال اسکرین شات\n\n"
                        f"⚠️ لطفاً پس از واریز سکه به شماره {COIN_PHONE_NUMBER}\n"
                        f"📸 یک اسکرین شات از واریز سکه ارسال کنید.\n\n"
                        f"✅️ روی دکمه ارسال اسکرین شات کلیک کرده و تصویر را ارسال کنید.*",
                        {"inline_keyboard": [
                            [{"text": "📸 ارسال اسکرین شات", "callback_data": f"coin_screenshot|{oid}"}],
                            [{"text": "🔙 بازگشت به منوی اصلی 🏠", "callback_data": "cancel_order"}]
                        ]}
                    )
                    continue

                # ─ اگر در state اسکرین شات بود ولی متن فرستاد
                if cur_state.startswith("coin_screenshot|"):
                    send(chat_id, "*⚠️ لطفاً فقط تصویر ارسال کنید.*")
                    continue

                # ─ بازدید بله زیرمنو ─────────────────────
                if text == "🔵 سفارش بازدید | بله 🚀":
                    send_bale_services(chat_id)
                    continue

                # ─ سرویس مستقیم (ممبر/بازدید) ───────────
                if text in BTN_TO_SVC:
                    check_stock_and_start(chat_id, BTN_TO_SVC[text], data, states)
                    continue

                if text in SVC_KEYS_TEXT:
                    check_stock_and_start(chat_id, SVC_KEYS_TEXT[text], data, states)
                    continue

                # ─ پشتیبانی ──────────────────────────────
                if text == "❌ بستن تیکت":
                    handle_support_message(chat_id, text, data, states, uinfo)
                    continue

                cur_state = states.get(uid, "")
                if cur_state == "support":
                    handle_support_message(chat_id, text, data, states, uinfo)
                    continue

                tid, t = get_user_open_ticket(data, chat_id)
                if tid:
                    handle_support_message(chat_id, text, data, states, uinfo)
                    continue

                # ─ جریان جوین اجباری ─────────────────────
                # ── state های بازی ──────────────────────────────
                if cur_state.startswith("game_number|"):
                    process_number_guess(chat_id, text); continue
                if cur_state.startswith("game_word|"):
                    process_word_guess(chat_id, text); continue
                if cur_state.startswith("game_math|"):
                    process_math(chat_id, text); continue

                if cur_state == "fj_free_hours":
                    uid_str = uid
                    u = data["users"].get(uid_str, {})
                    refs_per = data["settings"].get("fj_free_refs_per_hour", 3)
                    hrs_per  = data["settings"].get("fj_free_hours_per_batch", 1)
                    refs     = u.get("referrals", [])
                    used     = u.get("fj_free_used_hours", 0)
                    available = (len(refs) // refs_per) * hrs_per - used
                    if available <= 0:
                        send(chat_id, "*⚠️ ساعت رایگانی نداری!*", BACK_BTN_USER)
                        states.pop(uid, None)
                        continue
                    try:
                        hours = int(text.strip())
                    except:
                        send(chat_id, "*⚠️ لطفاً فقط عدد وارد کنید.*")
                        continue
                    if hours < 1:
                        send(chat_id, "*⚠️ حداقل ۱ ساعت وارد کنید.*")
                        continue
                    if hours > available:
                        send(chat_id, f"*⚠️ ساعت رایگان باقی‌مانده فقط {available} ساعت است.*")
                        continue
                    states[uid] = f"fj_free_link|{hours}"
                    send(chat_id,
                        f"*✅ {hours} ساعت جوین اجباری رایگان\n\n"
                        f"🔗 لینک کانال خود را وارد کنید:\n"
                        f"مثال: https://ble.ir/channel یا @username*",
                        BACK_BTN_USER
                    )
                    continue

                if cur_state.startswith("fj_free_link|"):
                    hours = int(cur_state.split("|")[1])
                    link  = text.strip()
                    if len(link) < 2:
                        send(chat_id, "*⚠️ لینک معتبر نیست.*")
                        continue
                    send(chat_id, "*⏳ در حال بررسی ادمین بودن ربات...*")
                    admin_result = check_bot_is_admin(link)
                    if admin_result is None:
                        send(chat_id, "*⚠️ خطا در بررسی. دوباره لینک را ارسال کنید.*")
                        continue
                    if admin_result is not True:
                        send(chat_id,
                            f"*⚠️ ربات باید ادمین کانال شما باشد!\n\n"
                            f"🔗 {link}\n\n"
                            f"ابتدا @{BOT_USERNAME} را ادمین کنید، سپس دوباره لینک را بفرستید.*",
                            {"inline_keyboard": [
                                [{"text": "✅ ادمین کردم، چک کن", "callback_data": f"fj_check_admin_free|{hours}|{link}"}],
                                [{"text": "❌ انصراف", "callback_data": "cancel_order"}]
                            ]}
                        )
                        continue
                    # ثبت سفارش رایگان
                    u = data["users"].get(uid, {})
                    u["fj_free_used_hours"] = u.get("fj_free_used_hours", 0) + hours
                    data["forced_join_order_counter"] = data.get("forced_join_order_counter", 0) + 1
                    oid = f"FJ{data['forced_join_order_counter']}"
                    data["forced_join_orders"].append({
                        "id": oid, "user_id": chat_id, "hours": hours,
                        "link": link, "price": 0, "status": "pending",
                        "free": True, "date": datetime.now().isoformat(), "end_time": ""
                    })
                    save_data(data)
                    states.pop(uid, None)
                    send(chat_id,
                        f"*✅ سفارش جوین اجباری رایگان ثبت شد!\n\n"
                        f"🆔 {oid}\n🔗 {link}\n⏳ {hours} ساعت\n💰 رایگان 🎁\n\n"
                        f"⏳ منتظر تأیید ادمین باشید.*"
                    )
                    for aid in ADMIN_IDS:
                        send(aid,
                            f"*🎁 سفارش جوین اجباری رایگان!\n\n"
                            f"🆔 {oid}\n👤 {chat_id}\n🔗 {link}\n⏳ {hours} ساعت*",
                            {"inline_keyboard": [[{"text": "✅ تأیید و فعال کردن", "callback_data": f"approve_fj|{oid}"}]]}
                        )
                    continue

                if cur_state == "fj_hours":
                    try:
                        hours = int(text.strip())
                    except:
                        send(chat_id, "*⚠️ لطفاً فقط عدد وارد کنید (۱ تا ۱۰).*")
                        continue
                    if hours < 1 or hours > 10:
                        send(chat_id, "*⚠️ تعداد ساعت باید بین ۱ تا ۱۰ باشد.*")
                        continue
                    pph   = data["settings"].get("forced_join_price_per_hour", 5000)
                    price = hours * pph
                    states[uid] = f"fj_link|{hours}|{price}"
                    send(chat_id,
                        f"*✅ {hours} ساعت | {price:,} تومان\n\n"
                        f"🔗 لینک کانال خود را وارد کنید:\n\n"
                        f"مثال: https://ble.ir/channel یا @username*",
                        BACK_BTN_USER
                    )
                    continue

                if cur_state.startswith("fj_link|"):
                    parts = cur_state.split("|")
                    hours = int(parts[1])
                    price = int(parts[2])
                    link  = text.strip()
                    if len(link) < 2:
                        send(chat_id, "*⚠️ لینک معتبر نیست.*")
                        continue
                    # چک کردن ادمین بودن ربات
                    send(chat_id, "*⏳ در حال بررسی ادمین بودن ربات در کانال شما...*")
                    admin_result = check_bot_is_admin(link)
                    if admin_result is None:
                        send(chat_id,
                            f"*⚠️ خطا در بررسی ادمین! لطفاً دوباره لینک را ارسال کنید.*"
                        )
                        continue
                    if admin_result is not True:
                        states[uid] = f"fj_waiting_admin|{hours}|{price}|{link}"
                        send(chat_id,
                            f"*⚠️ ربات باید ادمین کانال شما باشد!\n\n"
                            f"🔗 کانال: {link}\n\n"
                            f"📌 مراحل افزودن ادمین:\n"
                            f"1️⃣ وارد کانال خود شوید\n"
                            f"2️⃣ روی نام کانال کلیک کنید\n"
                            f"3️⃣ ادمین‌ها را باز کنید\n"
                            f"4️⃣ ربات @{BOT_USERNAME} را اضافه کنید\n"
                            f"5️⃣ بعد از افزودن، دکمه زیر را بزنید\n\n"
                            f"⚠️ توجه: اگر ربات ادمین نباشد، سفارش ثبت نمی‌شود!\n"
                            f"اگر در حین سرویس ربات را از ادمینی خارج کنید، سفارش لغو می‌شود و وجه عودت داده نمی‌شود.*",
                            {"inline_keyboard": [
                                [{"text": "✅ ربات را ادمین کردم، چک کن", "callback_data": f"fj_check_admin|{hours}|{price}|{link}"}],
                                [{"text": "❌ انصراف", "callback_data": "cancel_order"}]
                            ]}
                        )
                        continue
                    states.pop(uid, None)
                    send(chat_id,
                        f"*✅ ربات ادمین است! لینک ثبت شد.\n\n"
                        f"📱 جوین اجباری: {hours} ساعت\n"
                        f"🔗 {link}\n"
                        f"💰 {price:,} تومان\n\n"
                        f"فاکتور پرداخت ارسال می‌شود...*"
                    )
                    send_fj_invoice(chat_id, hours, link)
                    continue

                # ─ جریان طراحی عکس ──────────────────────
                if cur_state == "design_bale_id":
                    bale_id = text.strip()
                    if len(bale_id) < 2:
                        send(chat_id, "*⚠️ آیدی وارد شده معتبر نیست. دوباره امتحان کنید.*")
                        continue
                    states[uid] = f"design_desc|{bale_id}"
                    send(chat_id,
                        f"*✅ آیدی ثبت شد: {bale_id}\n\n"
                        f"📌 مرحله 2 از 3\n\n"
                        f"📝 توضیحات کامل عکس موردنظر را ارسال کنید:\n\n"
                        f"• چه عکسی می‌خواهید؟\n"
                        f"• رنگ، سبک، محتوا\n"
                        f"• هر جزئیاتی که لازم است*",
                        BACK_BTN_USER
                    )
                    continue

                if cur_state.startswith("design_desc|"):
                    bale_id     = cur_state.split("|", 1)[1]
                    description = text.strip()
                    if len(description) < 10:
                        send(chat_id, "*⚠️ لطفاً توضیحات کامل‌تری ارسال کنید (حداقل ۱۰ کاراکتر).*")
                        continue
                    states.pop(uid, None)
                    price = data["settings"].get("design_price", 12000)
                    send(chat_id,
                        f"*📌 مرحله 3 از 3 - پرداخت\n\n"
                        f"🎨 سرویس: طراحی عکس حرفه‌ای\n"
                        f"🆔 آیدی دریافت: {bale_id}\n"
                        f"💰 مبلغ: {price:,} تومان\n\n"
                        f"✅ فاکتور پرداخت ارسال می‌شود...*"
                    )
                    send_design_invoice(chat_id, bale_id, description)
                    continue

                # ─ تعداد سفارش (ممبر/بازدید) ─────────────
                if cur_state.startswith("order_qty|"):
                    key = cur_state.split("|")[1]
                    s   = data["settings"][key]
                    try:
                        qty = int(text.replace(",", "").strip())
                    except:
                        send(chat_id, "*⚠️ فقط عدد ارسال کنید.*")
                        continue
                    if qty < s["min"]:
                        send(chat_id, f"*⚠️ حداقل {s['min']:,} می‌باشد.*")
                        continue
                    if qty > s["max"]:
                        send(chat_id, f"*⚠️ حداکثر {s['max']:,} می‌باشد.*")
                        continue
                    stock = s.get("stock", 999999)
                    if stock < qty:
                        send(chat_id, f"*⚠️ موجودی ربات {stock:,} عدد هست. عدد کمتری وارد کنید.*")
                        continue
                    price = int(qty * s["price_per_1000"] / 1000)
                    states[uid] = f"order_link|{key}|{qty}|{price}"
                    platform = SVC_PLATFORM.get(key, "bale")
                    if platform == "rubika":
                        hint = "🔗 لینک روبیکا:\n• https://rubika.ir/channel\n• @username"
                    elif platform == "eitaa":
                        hint = "🔗 لینک ایتا:\n• https://eitaa.com/channel\n• @username"
                    else:
                        hint = "🔗 لینک بله:\n• https://ble.ir/channel\n• @username"
                    send(chat_id, f"*✅ تعداد {qty:,} | مبلغ {price:,} تومان\n\n{hint}*", BACK_BTN_USER)
                    continue

                # ─ لینک سفارش ────────────────────────────
                if cur_state.startswith("order_link|"):
                    parts    = cur_state.split("|")
                    key      = parts[1]
                    qty      = int(parts[2])
                    price    = int(parts[3])
                    link     = text.strip()
                    platform = SVC_PLATFORM.get(key, "bale")
                    if platform == "rubika":
                        valid = validate_rubika_link(link)
                        err   = "*⚠️ لینک روبیکا معتبر نیست!\n• https://rubika.ir/channel\n• @username*"
                    elif platform == "eitaa":
                        valid = validate_eitaa_link(link)
                        err   = "*⚠️ لینک ایتا معتبر نیست!\n• https://eitaa.com/channel\n• @username*"
                    else:
                        valid = validate_bale_link(link)
                        err   = "*⚠️ لینک بله معتبر نیست!\n• https://ble.ir/channel\n• @username*"
                    if not valid:
                        send(chat_id, err)
                        continue
                    # چک کد تخفیف
                    u_obj = data["users"].get(uid, {})
                    ac    = u_obj.get("active_discount_code", "")
                    if ac and ac in data["discount_codes"] and not data["discount_codes"][ac].get("used"):
                        dc = data["discount_codes"][ac]
                        states[uid] = f"order_discount|{key}|{qty}|{price}|{link}|{ac}"
                        send(chat_id,
                            f"*🎟️ کد تخفیف {dc['percent']}٪ داری!\n\n"
                            f"کد: {ac}\n"
                            f"💰 مبلغ فعلی: {price:,} تومان\n"
                            f"💸 بعد از تخفیف: {int(price*(100-dc['percent'])/100):,} تومان\n\n"
                            f"می‌خوای استفاده کنی؟*",
                            {"inline_keyboard": [
                                [{"text": "✅ بله، تخفیف بزن!", "callback_data": f"use_discount|yes"}],
                                [{"text": "❌ نه، همین قیمت", "callback_data": f"use_discount|no"}]
                            ]}
                        )
                        continue
                    states.pop(uid, None)
                    send_invoice(chat_id, key, qty, price, link)
                    continue

                # ─ fallback ───────────────────────────────
                send(chat_id, "*👇 از دکمه‌های منو استفاده کنید:*",
                     kb(["سفارش بازدید 👁️", "سفارش ممبر 👥", "🛍 فروش سکه"],
                        ["🎨 طراحی عکس حرفه‌ای", "📱 ثبت جوین اجباری"],
                        ["حساب کاربری 👤", "پیگیری سفارش 🔎", "قوانین ⚖️"],
                        ["📞 پشتیبانی"]))

            except Exception as ie:
                print(f"inner error: {ie}")
                continue

        time.sleep(0.1)

    except Exception as e:
        print(f"ERROR: {e}")
        time.sleep(3)

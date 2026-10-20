import os
import json
import requests
import datetime
import time
import threading
import sys
from telebot import TeleBot, types

# ==============================================================
#      SYSTEM ARCHITECTURE & CORE DESIGNED FOR: TANVEER        
# ==============================================================
BOT_TOKEN = "8789734130:AAGaEfI5DMeXNBTxLcIUHO1UyQj9d_5e7iQ"
OWNER_ID = 8879326948

# Autolike API Configurations
API_1_URL = "https://220like-api.vercel.app/like?uid={uid}&server_name={region}"
API_2_URL = "https://likeselling-api.vercel.app/like?uid={uid}&server_name={region}&key={key}"
API_KEY = "Narayan"
# ==============================================================

bot = TeleBot(BOT_TOKEN, parse_mode="HTML")
DATA_FILE = "autolike_data.json"
EXPORT_FILE = "active_uids_list.txt"
execution_lock = threading.Lock()
last_executed_record = None

def export_uids_file():
    try:
        os.makedirs("autolike_data", exist_ok=True)
        export_path = os.path.join("autolike_data", EXPORT_FILE)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write("=== ACTIVE AUTOLIKE UIDS REPORT ===\n\n")
            for uid, data in db.get("uids", {}).items():
                f.write(f"UID: {uid}\n")
                f.write(f"Region: {data.get('region')}\n")
                f.write(f"Days Left: {data.get('days')}\n")
                f.write(f"Remaining Likes: {data.get('days', 0) * 220}\n")
                f.write(f"Expire Date: {data.get('expire_date')}\n")
                f.write(f"Telegram: {data.get('tg_id')}\n")
                f.write(f"Paused: {data.get('paused', False)}\n")
                f.write("-" * 30 + "\n")
    except Exception as e:
        print(f"[!] File export error: {e}")

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if "like_command_status" not in data:
                    data["like_command_status"] = "ON"
                if "active_api" not in data:
                    data["active_api"] = 2
                if "banned_users" not in data:
                    data["banned_users"] = []
                if "lockdown" not in data:
                    data["lockdown"] = False
                if "api_timeout" not in data:
                    data["api_timeout"] = 25
                export_uids_file()
                return data
        except Exception as e:
            print(f"[!] Error loading data: {e}")
    default_data = {
        "admins": [],
        "groups": [],
        "uids": {},
        "banned_users": [],
        "lockdown": False,
        "limit": 100,
        "total_likes_given": 0,
        "auto_time": "04:00",
        "bot_status": "ON",
        "like_command_status": "ON",
        "active_api": 2,
        "api_timeout": 25
    }
    return default_data

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        export_uids_file()
    except Exception as e:
        print(f"[!] Error saving data: {e}")

db = load_data()

# Font Customization System
def sc(text):
    text = str(text)
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    small  = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ0123456789"
    return text.translate(str.maketrans(normal, small))

# Custom Emojis & Aesthetic Decorators Map
CE_GUN      = '<tg-emoji emoji-id="5303040006347046717">⚡</tg-emoji>'
CE_JUICE    = '<tg-emoji emoji-id="5303548912726982102">🧃</tg-emoji>'
CE_ALERT    = '<tg-emoji emoji-id="6154631793787015439">🚨</tg-emoji>'
CE_TIME     = '<tg-emoji emoji-id="6154603635981423575">⏳</tg-emoji>'
CE_STAR     = '<tg-emoji emoji-id="5267394977540889773">✨</tg-emoji>'
CE_MUTE     = '<tg-emoji emoji-id="5870619152829386951">🔒</tg-emoji>'
CE_CLIP     = '<tg-emoji emoji-id="6154729229415093721">📂</tg-emoji>'
CE_GIFT     = '<tg-emoji emoji-id="6154314868150243661">🎁</tg-emoji>'
CE_PIN      = '<tg-emoji emoji-id="6154635564768300782">📌</tg-emoji>'
CE_CONG     = '<tg-emoji emoji-id="5303178192624823421">🎉</tg-emoji>'
CE_CHAT     = '<tg-emoji emoji-id="5303138782004924588">💬</tg-emoji>'
CE_CROWN    = '<tg-emoji emoji-id="6154611916678369390">👑</tg-emoji>'
CE_HEART    = '<tg-emoji emoji-id="5870681447035047985">💖</tg-emoji>'
CE_BAG      = '<tg-emoji emoji-id="5278702045883292456">💎</tg-emoji>'
CE_CHECK    = '<tg-emoji emoji-id="6154718341672997377">✅</tg-emoji>'
CE_STAR2    = '<tg-emoji emoji-id="6154599104790924940">🌟</tg-emoji>'
CE_TAG      = '<tg-emoji emoji-id="6154668949549092628">🏷️</tg-emoji>'
CE_CHART    = '<tg-emoji emoji-id="4956599758044005301">📊</tg-emoji>'
CE_STAR3    = '<tg-emoji emoji-id="5267080804978151215">⭐</tg-emoji>'
CE_SWORD    = '<tg-emoji emoji-id="5463277406435422003">🗡️</tg-emoji>'
CE_FIRE     = '<tg-emoji emoji-id="5425023908233379058">🔥</tg-emoji>'
CE_SHIELD   = '<tg-emoji emoji-id="5422533038670125867">🛡️</tg-emoji>'

def send_msg(chat_id, text, reply_markup=None):
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        print(f"[!] Text send error: {e}")

def get_api_url(api_type, uid, region):
    if api_type == 1:
        return API_1_URL.format(uid=uid, region=region)
    else:
        return API_2_URL.format(uid=uid, region=region, key=API_KEY)

# Buttons Generator Functions
def get_start_buttons():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=f"✨ {sc('SLOTS')} ✨", callback_data="btn_slot")
    btn2 = types.InlineKeyboardButton(text=f"💎 {sc('PLANS')} 💎", callback_data="btn_plans")
    markup.row(btn1, btn2)
    return markup

def get_plans_buttons():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=f"⚡ {sc('7 Days - 63 INR')}", url=f"tg://user?id={OWNER_ID}")
    btn2 = types.InlineKeyboardButton(text=f"🌟 {sc('15 Days - 150 INR')}", url=f"tg://user?id={OWNER_ID}")
    btn3 = types.InlineKeyboardButton(text=f"👑 {sc('30 Days - 250 INR')}", url=f"tg://user?id={OWNER_ID}")
    btn_back = types.InlineKeyboardButton(text=f"🔙 {sc('BACK')}", callback_data="btn_back")
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn_back)
    return markup

def get_extend_button(uid):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text=f"🔄 {sc('EXTEND PLAN')}", url=f"tg://user?id={OWNER_ID}")
    markup.add(btn)
    return markup

def get_buy_owner_buttons():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text=f"🛒 {sc('BUY AUTOLIKE')}", url=f"tg://user?id={OWNER_ID}")
    btn2 = types.InlineKeyboardButton(text=f"👑 {sc('CONTACT OWNER')}", url=f"tg://user?id={OWNER_ID}")
    markup.row(btn1, btn2)
    return markup

def get_feedback_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text=f"💬 {sc('GIVE FEEDBACK')}", url=f"tg://user?id={OWNER_ID}")
    markup.add(btn)
    return markup

def get_unauthorized_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text=f"🔐 {sc('REQUEST ACCESS')}", url=f"tg://user?id={OWNER_ID}")
    markup.add(btn)
    return markup

# Security Verifications
def is_owner(uid):
    return int(uid) == int(OWNER_ID)

def is_admin(uid):
    return is_owner(uid) or int(uid) in db["admins"]

def is_group_allowed(chat_id):
    return str(chat_id) in db["groups"] or int(chat_id) == int(OWNER_ID)

def is_banned(user_id):
    return user_id in db.get("banned_users", [])

def check_command_permission(message):
    chat_type = message.chat.type
    chat_id = message.chat.id
    user_id = message.from_user.id

    if is_banned(user_id):
        send_msg(chat_id, f"{CE_MUTE} <b>🚫 YOU ARE BLACKLISTED FROM USING THIS BOT!</b>")
        return False

    if db.get("lockdown", False) and not is_owner(user_id):
        send_msg(chat_id, f"{CE_MUTE} <b>🚨 BOT IS UNDER MAINTENANCE / LOCKDOWN MODE!</b>")
        return False

    if chat_type != "private":
        if not is_group_allowed(chat_id):
            return False 
        if not is_admin(user_id):
            return False
    else:
        if not is_admin(user_id):
            text = f"╔═════════════════════════╗\n"
            text += f"   {CE_MUTE} <b>ACCESS RESTRICTED</b> {CE_MUTE}\n"
            text += f"╚═════════════════════════╝\n\n"
            text += f"{CE_ALERT} <b>You are not authorized to use this bot!</b>\n"
            text += f"{CE_STAR} <b>Contact owner to buy access or slots.</b>"
            send_msg(chat_id, text, reply_markup=get_unauthorized_button())
            return False
    return True

def sanitize_tg_text(raw_string):
    if not raw_string:
        return "Unknown Player"
    clean = str(raw_string).replace("<", "").replace(">", "").strip()
    if not clean:
        return "FF Player"
    return clean

def parse_universal_api_response(res_json):
    try:
        if not isinstance(res_json, dict):
            return "Unknown Player", 0, 0, 0
            
        p_name = "Unknown"
        name_keys = ["PlayerNickname", "name", "nickname", "PlayerName", "username"]
        for k in name_keys:
            if k in res_json and res_json[k]:
                p_name = sanitize_tg_text(str(res_json[k]))
                break
                
        given = 0
        given_keys = ["LikesGivenByAPI", "likes_given", "given", "likes", "LikesSent", "added_likes"]
        for k in given_keys:
            if k in res_json:
                try:
                    given = int(res_json[k])
                    break
                except: pass
                
        before = 0
        before_keys = ["LikesbeforeCommand", "before_likes", "old_likes", "before"]
        for k in before_keys:
            if k in res_json:
                try:
                    before = int(res_json[k])
                    break
                except: pass
                
        after = before + given
        after_keys = ["LikesafterCommand", "after_likes", "new_likes", "after", "current_likes"]
        for k in after_keys:
            if k in res_json:
                try:
                    after = int(res_json[k])
                    break
                except: pass
                
        return p_name, before, given, after
    except Exception as e:
        print(f"[!] Universal parsing error: {e}")
        return "Unknown Player", 0, 0, 0

# ==================== CALLBACK QUERY HANDLERS ====================

@bot.callback_query_handler(func=lambda call: call.data.startswith("btn_"))
def callback_handler(call):
    try:
        if is_banned(call.from_user.id):
            bot.answer_callback_query(call.id, "You are banned!", show_alert=True)
            return

        if call.data == "btn_slot":
            total_slots = len(db["uids"])
            remaining_slots = max(0, db["limit"] - total_slots)
            text = f"╔══════════════════════════╗\n"
            text += f"   {CE_STAR2} <b>AUTOLIKE SLOT STATUS</b> {CE_STAR2}\n"
            text += f"╚══════════════════════════╝\n\n"
            text += f"├ {CE_PIN} <b>Total Added UIDs :</b> <code>{total_slots}</code>\n"
            text += f"├ {CE_CHECK} <b>Remaining Slots  :</b> <code>{remaining_slots}</code>\n"
            text += f"└ {CE_CLIP} <b>Total Capacity   :</b> <code>{db['limit']}</code>\n\n"
            text += f"{CE_GIFT} <i>DM Owner to acquire slots!</i>"
            bot.answer_callback_query(call.id)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_buy_owner_buttons())
            
        elif call.data == "btn_plans":
            text = f"╔══════════════════════════╗\n"
            text += f"   {CE_GIFT} <b>PREMIUM VIP PLANS</b> {CE_GIFT}\n"
            text += f"╚══════════════════════════╝\n\n"
            text += f"⚡ <b>07 Days Plan :</b> <code>63 INR</code> (9 ₹/Day)\n"
            text += f"🌟 <b>15 Days Plan :</b> <code>150 INR</code> (10 ₹/Day)\n"
            text += f"👑 <b>30 Days Plan :</b> <code>250 INR</code> (8.3 ₹/Day)\n\n"
            text += f"{CE_FIRE} <i>Click any button below to connect with Owner!</i>"
            bot.answer_callback_query(call.id)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_plans_buttons())
            
        elif call.data == "btn_back":
            username = call.from_user.first_name
            bot_name = bot.get_me().first_name
            text = f"╔══════════════════════════╗\n"
            text += f"   {CE_CROWN} <b>WELCOME TO {bot_name.upper()}</b> {CE_CROWN}\n"
            text += f"╚══════════════════════════╝\n\n"
            text += f"👋 <i>Greetings {username}!</i>\n\n"
            text += f"├ {CE_FIRE} <b>High Speed Auto-Like Service</b>\n"
            text += f"├ {CE_TIME} <b>Daily Schedule :</b> <code>{db.get('auto_time', '04:00')} AM IST</code>\n"
            text += f"└ {CE_STAR} <b>Status Check   :</b> <code>/mystatus</code>"
            bot.answer_callback_query(call.id)
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_start_buttons())
    except Exception as e:
        print(f"Callback error: {e}")

# ==================== BOT COMMAND HANDLERS ====================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    try:
        if is_banned(message.from_user.id): return
        if message.chat.type != "private" and not is_group_allowed(message.chat.id): return
        
        username = message.from_user.first_name
        bot_name = bot.get_me().first_name
        
        text = f"╔══════════════════════════╗\n"
        text += f"   {CE_CROWN} <b>WELCOME TO {bot_name.upper()}</b> {CE_CROWN}\n"
        text += f"╚══════════════════════════╝\n\n"
        text += f"👋 <i>Greetings <b>{username}</b>!</i>\n\n"
        text += f"├ {CE_FIRE} <b>High Speed Auto-Like Engine</b>\n"
        text += f"├ {CE_TIME} <b>Daily Auto Run :</b> <code>{db.get('auto_time', '04:00')} AM IST</code>\n"
        text += f"└ {CE_CLIP} <b>Personal Status :</b> <code>/mystatus</code>\n\n"
        text += f"{CE_BAG} <b>Get instant daily likes at cheap rates!</b>"
        
        send_msg(message.chat.id, text, reply_markup=get_start_buttons())
    except Exception as e:
        print(f"Start Error: {e}")

@bot.message_handler(commands=['mystatus'])
def mystatus_cmd(message):
    try:
        if is_banned(message.from_user.id): return
        user_tg_id = str(message.from_user.id)
        found_uids = []
        
        for uid, data in db["uids"].items():
            if str(data.get("tg_id")) == user_tg_id or str(data.get("tg_id")) == f"@{message.from_user.username}":
                found_uids.append((uid, data))
                
        if not found_uids:
            send_msg(message.chat.id, f"{CE_ALERT} <b>NO ACTIVE AUTOLIKE SLOTS FOUND FOR YOUR ACCOUNT!</b>")
            return
            
        for uid, data in found_uids:
            rem_likes = data["days"] * 220
            text = f"╔══════════════════════════╗\n"
            text += f"   {CE_STAR2} <b>YOUR SUBSCRIPTION STATUS</b> {CE_STAR2}\n"
            text += f"╚══════════════════════════╝\n\n"
            text += f"├ {CE_GUN} <b>Player UID     :</b> <code>{uid}</code>\n"
            text += f"├ {CE_CHECK} <b>Added Date     :</b> {data['added_date']}\n"
            text += f"├ {CE_CLIP} <b>Expire Date    :</b> {data['expire_date']}\n"
            text += f"├ {CE_GIFT} <b>Sent So Far    :</b> {data['total_given']} Likes\n"
            text += f"├ {CE_CHART} <b>Remaining Likes:</b> {rem_likes}\n"
            text += f"├ {CE_TIME} <b>Days Left      :</b> {data['days']} Days\n"
            text += f"├ {CE_TIME} <b>Daily Execution:</b> <code>{db.get('auto_time', '04:00')} AM IST</code>\n"
            text += f"└ {CE_ALERT} <b>Active Status  :</b> {'⏸ PAUSED' if data.get('paused') else '🟢 ACTIVE'}\n\n"
            text += f"{CE_STAR} <b>Need to add more days? Click below!</b>"
            
            send_msg(message.chat.id, text, reply_markup=get_extend_button(uid))
    except Exception as e:
        print(f"MyStatus Error: {e}")

# ==================== ADVANCED ADMIN CONTROL PANEL ====================

@bot.message_handler(commands=['admin', 'help'])
def admin_cmd(message):
    try:
        if not check_command_permission(message): return
            
        current_api_num = db.get("active_api", 2)
        text = f"╔══════════════════════════════╗\n"
        text += f"   {CE_CROWN} <b>EXECUTIVE ADMIN PANEL</b> {CE_CROWN}\n"
        text += f"╚══════════════════════════════╝\n\n"
        text += f"⚙️ <b>Active API Engine  :</b> <code>API {current_api_num}</code>\n"
        text += f"⏰ <b>Scheduled Time    :</b> <code>{db.get('auto_time', '04:00')} AM IST</code>\n"
        text += f"🔒 <b>Lockdown Status   :</b> <code>{'ON 🔴' if db.get('lockdown') else 'OFF 🟢'}</code>\n\n"
        
        text += f"<b>{CE_SWORD} API CONTROL & TESTING:</b>\n"
        text += f"• <code>/checkapi1 {{region}} {{uid}}</code>\n"
        text += f"• <code>/checkapi2 {{region}} {{uid}}</code>\n"
        text += f"• <code>/setapi {{1|2}}</code> - Switch engine\n"
        text += f"• <code>/like {{region}} {{uid}}</code> - Send Likes\n"
        text += f"• <code>/vlike {{region}} {{uid}}</code> - Send V-Likes\n"
        text += f"• <code>/apistatus</code> - Test API latency\n\n"
        
        text += f"<b>{CE_PIN} UID MANAGEMENT:</b>\n"
        text += f"• <code>/autolike {{uid}} {{region}} {{days}} {{tg}}</code>\n"
        text += f"• <code>/removeuid {{uid}}</code>\n"
        text += f"• <code>/extend {{uid}} {{days}}</code>\n"
        text += f"• <code>/pause {{uid}}</code> / <code>/resume {{uid}}</code>\n"
        text += f"• <code>/resetuid {{uid}}</code> - Reset count\n"
        text += f"• <code>/searchuid {{query}}</code> - Find UID\n"
        text += f"• <code>/checklikes {{uid}}</code> | <code>/checkuid {{uid}}</code>\n"
        text += f"• <code>/alluids</code> - View full database\n\n"

        text += f"<b>{CE_CHART} SYSTEM & OPERATIONS:</b>\n"
        text += f"• <code>/status</code> - View stats\n"
        text += f"• <code>/ping</code> - Check bot latency\n"
        text += f"• <code>/runnow</code> or <code>/alllikes</code> - Force execution\n"
        text += f"• <code>/likeon</code> / <code>/likeoff</code>\n\n"
        
        if is_owner(message.from_user.id):
            text += f"<b>{CE_SHIELD} OWNER EXCLUSIVE COMMANDS:</b>\n"
            text += f"• <code>/lockdown</code> / <code>/unlockdown</code>\n"
            text += f"• <code>/banuser {{id}}</code> / <code>/unbanuser {{id}}</code>\n"
            text += f"• <code>/blacklist</code> - View banned users\n"
            text += f"• <code>/broadcast {{msg}}</code> - Global DM\n"
            text += f"• <code>/clean</code> - Clear expired UIDs\n"
            text += f"• <code>/backup</code> - Backup DB via chat\n"
            text += f"• <code>/settimeout {{sec}}</code> - Adjust timeout\n"
            text += f"• <code>/timeoff</code> / <code>/timeon</code>\n"
            text += f"• <code>/addadmin {{id}}</code> / <code>/removeadmin {{id}}</code>\n"
            text += f"• <code>/admins</code> | <code>/groups</code>\n"
            text += f"• <code>/setgroup {{id}}</code> / <code>/removegroup {{id}}</code>\n"
            text += f"• <code>/setlimit {{limit}}</code>\n"
            text += f"• <code>/settime {{hh:mm}}</code>\n"
            text += f"• <code>/notify {{user_id}} {{msg}}</code>\n"
            
        send_msg(message.chat.id, text)
    except Exception as e:
        print(f"Admin Cmd Error: {e}")

# ==================== NEW EXPANDED ADMIN COMMANDS ====================

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    if not check_command_permission(message): return
    start_t = time.time()
    msg = send_msg(message.chat.id, f"{CE_TIME} <i>Pinging server...</i>")
    end_t = time.time()
    ms = round((end_t - start_t) * 1000, 2)
    bot.edit_message_text(f"{CE_CHECK} <b>POKE PONG!</b> Latency: <code>{ms} ms</code>", message.chat.id, msg.message_id)

@bot.message_handler(commands=['lockdown'])
def lockdown_cmd(message):
    if not is_owner(message.from_user.id): return
    db["lockdown"] = True
    save_data(db)
    send_msg(message.chat.id, f"{CE_ALERT} <b>LOCKDOWN ACTIVATED! Non-owner access blocked.</b>")

@bot.message_handler(commands=['unlockdown'])
def unlockdown_cmd(message):
    if not is_owner(message.from_user.id): return
    db["lockdown"] = False
    save_data(db)
    send_msg(message.chat.id, f"{CE_CHECK} <b>LOCKDOWN DEACTIVATED! System resumed.</b>")

@bot.message_handler(commands=['banuser'])
def banuser_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        uid_to_ban = int(message.text.split()[1])
        if uid_to_ban not in db["banned_users"]:
            db["banned_users"].append(uid_to_ban)
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} User <code>{uid_to_ban}</code> has been blacklisted!")
    except Exception:
        send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/banuser {{user_id}}</code>")

@bot.message_handler(commands=['unbanuser'])
def unbanuser_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        uid_to_unban = int(message.text.split()[1])
        if uid_to_unban in db["banned_users"]:
            db["banned_users"].remove(uid_to_unban)
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} User <code>{uid_to_unban}</code> removed from blacklist!")
    except Exception:
        send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/unbanuser {{user_id}}</code>")

@bot.message_handler(commands=['blacklist'])
def blacklist_cmd(message):
    if not is_admin(message.from_user.id): return
    banned = db.get("banned_users", [])
    if not banned:
        send_msg(message.chat.id, f"{CE_CHECK} <b>No users are currently blacklisted.</b>")
        return
    text = f"{CE_MUTE} <b>BLACKLISTED USERS:</b>\n\n"
    for b in banned:
        text += f"• <code>{b}</code>\n"
    send_msg(message.chat.id, text)

@bot.message_handler(commands=['clean'])
def clean_cmd(message):
    if not is_owner(message.from_user.id): return
    removed = 0
    for uid, data in list(db["uids"].items()):
        if data.get("days", 0) <= 0:
            del db["uids"][uid]
            removed += 1
    save_data(db)
    send_msg(message.chat.id, f"{CE_CHECK} <b>Cleaned up {removed} expired UIDs from database!</b>")

@bot.message_handler(commands=['backup'])
def backup_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f:
                bot.send_document(message.chat.id, f, caption=f"{CE_CLIP} <b>Database Backup File</b>")
    except Exception as e:
        send_msg(message.chat.id, f"{CE_ALERT} Backup failed: {e}")

@bot.message_handler(commands=['resetuid'])
def resetuid_cmd(message):
    if not check_command_permission(message): return
    try:
        uid = message.text.split()[1]
        if uid in db["uids"]:
            db["uids"][uid]["total_given"] = 0
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} Total given likes reset to 0 for UID <code>{uid}</code>!")
        else:
            send_msg(message.chat.id, f"{CE_ALERT} UID not found.")
    except Exception:
        send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/resetuid {{uid}}</code>")

@bot.message_handler(commands=['searchuid'])
def searchuid_cmd(message):
    if not check_command_permission(message): return
    try:
        q = message.text.split()[1].lower()
        results = []
        for uid, data in db["uids"].items():
            if q in uid or q in str(data.get("tg_id", "")).lower():
                results.append((uid, data))
        if not results:
            send_msg(message.chat.id, f"{CE_ALERT} No matching UIDs found for query: <code>{q}</code>")
            return
        text = f"<b>🔍 SEARCH RESULTS FOR '{q}':</b>\n\n"
        for u, d in results:
            text += f"• <code>{u}</code> | TG: {d.get('tg_id')} | Days: {d.get('days')}\n"
        send_msg(message.chat.id, text)
    except Exception:
        send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/searchuid {{query}}</code>")

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/broadcast {{message}}</code>")
            return
        b_msg = parts[1]
        sent = 0
        all_targets = set()
        for d in db["uids"].values():
            if d.get("tg_id"): all_targets.add(str(d["tg_id"]))
        for t in all_targets:
            try:
                send_msg(t, f"📢 <b>GLOBAL ANNOUNCEMENT:</b>\n\n{b_msg}")
                sent += 1
            except: pass
        send_msg(message.chat.id, f"{CE_CHECK} Broadcast sent to {sent} unique users!")
    except Exception as e:
        send_msg(message.chat.id, f"Broadcast Error: {e}")

@bot.message_handler(commands=['settimeout'])
def settimeout_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        sec = int(message.text.split()[1])
        db["api_timeout"] = sec
        save_data(db)
        send_msg(message.chat.id, f"{CE_CHECK} API Request Timeout set to <code>{sec}s</code>!")
    except Exception:
        send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/settimeout {{seconds}}</code>")

@bot.message_handler(commands=['apistatus'])
def apistatus_cmd(message):
    if not check_command_permission(message): return
    timeout = db.get("api_timeout", 25)
    text = f"<b>📊 API LATENCY & HEALTH CHECK:</b>\n\n"
    
    # Test API 1
    t0 = time.time()
    try:
        res1 = requests.get(API_1_URL.format(uid="18268203963", region="ind"), timeout=timeout)
        l1 = round((time.time() - t0) * 1000, 2)
        st1 = f"🟢 OK ({l1}ms)" if res1.status_code == 200 else f"🔴 ERR ({res1.status_code})"
    except Exception as e:
        st1 = f"🔴 TIMEOUT / DOWN"

    # Test API 2
    t0 = time.time()
    try:
        res2 = requests.get(API_2_URL.format(uid="18268203963", region="ind", key=API_KEY), timeout=timeout)
        l2 = round((time.time() - t0) * 1000, 2)
        st2 = f"🟢 OK ({l2}ms)" if res2.status_code == 200 else f"🔴 ERR ({res2.status_code})"
    except Exception as e:
        st2 = f"🔴 TIMEOUT / DOWN"

    text += f"• <b>API 1 Engine :</b> {st1}\n"
    text += f"• <b>API 2 Engine :</b> {st2}\n"
    text += f"• <b>Default Timeout:</b> {timeout}s\n"
    send_msg(message.chat.id, text)

# ==================== CORE API & LIKE COMMANDS ====================

@bot.message_handler(commands=['setapi'])
def setapi_cmd(message):
    if not is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        if len(parts) < 2 or parts[1] not in ["1", "2"]:
            send_msg(message.chat.id, f"{CE_ALERT} <b>Usage:</b> <code>/setapi 1</code> or <code>/setapi 2</code>")
            return
        selected = int(parts[1])
        db["active_api"] = selected
        save_data(db)
        send_msg(message.chat.id, f"{CE_CHECK} <b>Active default engine changed to API {selected}!</b>")
    except Exception as e:
        print(f"SetAPI Error: {e}")

def perform_api_check(message, api_number):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            send_msg(message.chat.id, f"{CE_ALERT} <b>Usage:</b> <code>/checkapi{api_number} {{region}} {{uid}}</code>")
            return
        region = parts[1]
        uid = parts[2]
        timeout = db.get("api_timeout", 25)
        
        send_msg(message.chat.id, f"{CE_TIME} <b>🔍 Testing API {api_number} live response for UID <code>{uid}</code>...</b>")
        
        def async_checkapi():
            try:
                formatted_url = get_api_url(api_number, uid, region)
                res_raw = requests.get(formatted_url, timeout=timeout)
                res = res_raw.json()
                p_name, before, given, after = parse_universal_api_response(res)
                
                if given > 0:
                    text = f"{CE_CHECK} <b>API {api_number} TEST SUCCESSFUL!</b>\n\n"
                else:
                    text = f"{CE_ALERT} <b>API {api_number} RESPONDED (0 Likes Sent)</b>\n\n"
                    
                text += f"├ {CE_CROWN} <b>Player Name :</b> <b>{p_name}</b>\n"
                text += f"├ {CE_GUN} <b>Player UID  :</b> <code>{uid}</code>\n"
                text += f"├ {CE_GIFT} <b>Likes Sent  :</b> <b>{given}</b>\n"
                text += f"├ {CE_STAR2} <b>Likes Before:</b> {before}\n"
                text += f"└ {CE_CHECK} <b>Likes After :</b> {after}\n"
                
                send_msg(message.chat.id, text, reply_markup=get_buy_owner_buttons())
            except Exception as inner_ex:
                send_msg(message.chat.id, f"{CE_ALERT} <b>API {api_number} FAILED / TIMED OUT!</b>\n<code>{inner_ex}</code>")

        threading.Thread(target=async_checkapi).start()
    except Exception as e:
        print(f"CheckAPI Outer Error: {e}")

@bot.message_handler(commands=['checkapi1'])
def checkapi1_cmd(message):
    if not check_command_permission(message): return
    perform_api_check(message, 1)

@bot.message_handler(commands=['checkapi2', 'checkapi'])
def checkapi2_cmd(message):
    if not check_command_permission(message): return
    perform_api_check(message, 2)

@bot.message_handler(commands=['like'])
def user_like_cmd(message):
    if not check_command_permission(message): return
    if db.get("like_command_status", "ON") == "OFF":
        send_msg(message.chat.id, f"{CE_ALERT} <b>/like command is currently turned OFF by Admin!</b>")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 3:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜsᴀɢᴇ: /like {ʀᴇɢɪᴏɴ} {ᴜɪᴅ}"))
            return
            
        region = parts[1]
        uid = parts[2]
        api_type = db.get("active_api", 2)
        timeout = db.get("api_timeout", 25)
        
        send_msg(message.chat.id, f"{CE_TIME} <b>⚡ Processing Likes for UID <code>{uid}</code>...</b>")
        
        def async_user_like():
            try:
                formatted_url = get_api_url(api_type, uid, region)
                res_raw = requests.get(formatted_url, timeout=timeout)
                res = res_raw.json()
                p_name, before, given, after = parse_universal_api_response(res)
                
                if given > 0:
                    card_text = f"╔══════════════════════════╗\n"
                    card_text += f"   {CE_HEART} <b>AUTOLIKE SUCCESSFUL</b> {CE_HEART}\n"
                    card_text += f"╚══════════════════════════╝\n\n"
                else:
                    card_text = f"╔══════════════════════════╗\n"
                    card_text += f"   {CE_MUTE} <b>AUTOLIKE FAILED (0 LIKES)</b> {CE_MUTE}\n"
                    card_text += f"╚══════════════════════════╝\n\n"
                    
                card_text += f"├ {CE_CROWN} <b>Player Name :</b> <b>{p_name}</b>\n"
                card_text += f"├ {CE_GUN} <b>Player UID  :</b> <code>{uid}</code>\n"
                card_text += f"├ {CE_GIFT} <b>Likes Given :</b> <b>{given}</b>\n"
                card_text += f"├ {CE_STAR3} <b>Likes Before:</b> {before}\n"
                card_text += f"├ {CE_CHECK} <b>Total Likes :</b> {after}\n"
                card_text += f"└ {CE_TIME} <b>Next Auto   :</b> <code>{db.get('auto_time', '04:00')} AM IST</code>"
                    
                send_msg(message.chat.id, card_text, reply_markup=get_buy_owner_buttons())
            except Exception as inner_ex:
                send_msg(message.chat.id, f"{CE_ALERT} <b>API Error or Timeout for UID <code>{uid}</code></b>")

        threading.Thread(target=async_user_like).start()
    except Exception as e:
        print(f"User Like Error: {e}")

@bot.message_handler(commands=['vlike'])
def vlike_cmd(message):
    if not check_command_permission(message): return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("uѕαgє: /vlike {ʀᴇɢɪᴏɴ} {ᴜɪᴅ}"))
            return
        region = parts[1]
        uid = parts[2]
        api_type = db.get("active_api", 2)
        timeout = db.get("api_timeout", 25)
        
        send_msg(message.chat.id, f"{CE_TIME} <b>⚡ Processing V-Likes for UID <code>{uid}</code>...</b>")
        
        def async_vlike():
            try:
                formatted_url = get_api_url(api_type, uid, region)
                res_raw = requests.get(formatted_url, timeout=timeout)
                res = res_raw.json()
                p_name, before, given, after = parse_universal_api_response(res)
                
                text = f"╔══════════════════════════╗\n"
                text += f"   {CE_HEART} <b>V-LIKE DELIVERED</b> {CE_HEART}\n"
                text += f"╚══════════════════════════╝\n\n"
                text += f"├ {CE_CROWN} <b>Player Name :</b> <b>{p_name}</b>\n"
                text += f"├ {CE_GUN} <b>Player UID  :</b> <code>{uid}</code>\n"
                text += f"├ {CE_GIFT} <b>Likes Given :</b> <b>{given}</b>\n"
                text += f"├ {CE_STAR3} <b>Likes Before:</b> {before}\n"
                text += f"└ {CE_CHECK} <b>Total Likes :</b> {after}\n"
                
                send_msg(message.chat.id, text, reply_markup=get_buy_owner_buttons())
            except Exception as inner_ex:
                send_msg(message.chat.id, f"{CE_ALERT} <b>API Error or Timeout!</b>")

        threading.Thread(target=async_vlike).start()
    except Exception as e:
        print(f"VLike Outer Error: {e}")

@bot.message_handler(commands=['autolike'])
def autolike_cmd(message):
    if not check_command_permission(message): return
    try:
        parts = message.text.split()
        if len(parts) < 5:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜsᴀɢᴇ: /autolike {ᴜɪᴅ} {ʀᴇɢɪᴏɴ} ᴅᴀʏs {ᴛɢ_ɪᴅ_ᴏʀ_ᴜsᴇʀɴᴀᴍᴇ}"))
            return
            
        uid = parts[1]
        region = parts[2]
        days = int(parts[3])
        target_tg = parts[4]
        
        if len(db["uids"]) >= db["limit"]:
            send_msg(message.chat.id, f"{CE_ALERT} <b>DATABASE SLOTS FULL!</b>")
            return
            
        today = datetime.date.today()
        expire = today + datetime.timedelta(days=days)
        total_expected_likes = days * 220
        
        db["uids"][uid] = {
            "region": region,
            "days": days,
            "added_date": str(today),
            "expire_date": str(expire),
            "total_given": 0,
            "tg_id": target_tg,
            "paused": False
        }
        save_data(db)
        
        text = f"╔══════════════════════════╗\n"
        text += f"   {CE_CHECK} <b>AUTOLIKE ADDED</b> {CE_CHECK}\n"
        text += f"╚══════════════════════════╝\n\n"
        text += f"├ {CE_GUN} <b>Player UID     :</b> <code>{uid}</code>\n"
        text += f"├ {CE_TIME} <b>Total Days     :</b> {days} Days\n"
        text += f"├ {CE_CHART} <b>Expected Likes :</b> {total_expected_likes} (220/Day)\n"
        text += f"├ {CE_PIN} <b>Telegram User  :</b> <code>{target_tg}</code>\n"
        text += f"├ {CE_STAR} <b>Added Date     :</b> {today}\n"
        text += f"├ {CE_CLIP} <b>Expire Date    :</b> {expire}\n"
        text += f"└ {CE_TIME} <b>Daily Run Time :</b> <code>{db.get('auto_time', '04:00')} AM IST</code>\n\n"
        text += f"{CE_GIFT} <b>Thank you for choosing our service!</b>"
        
        send_msg(message.chat.id, text, reply_markup=get_buy_owner_buttons())
        
        try:
            dm_text = f"🎉 <b>YOUR AUTOLIKE SLOT HAS BEEN ACTIVATED!</b> 🎉\n\n"
            dm_text += f"├ {CE_GUN} <b>UID          :</b> <code>{uid}</code>\n"
            dm_text += f"├ {CE_TIME} <b>Days         :</b> {days}\n"
            dm_text += f"├ {CE_CHART} <b>Total Likes  :</b> {total_expected_likes}\n"
            dm_text += f"└ {CE_TIME} <b>Daily Execution Time :</b> <code>{db.get('auto_time', '04:00')} AM IST</code>"
            send_msg(target_tg, dm_text, reply_markup=get_buy_owner_buttons())
        except Exception: pass
            
    except Exception as e:
        print(f"Autolike Error: {e}")

@bot.message_handler(commands=['removeuid'])
def removeuid_cmd(message):
    if not check_command_permission(message): return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜsᴀɢᴇ: /removeuid {ᴜɪᴅ}"))
            return
        uid = parts[1]
        if uid in db["uids"]:
            tg_target = db["uids"][uid].get("tg_id")
            del db["uids"][uid]
            save_data(db)
            
            text = f"🗑️ <b>UID REMOVED FROM SYSTEM</b>\n"
            text += f"Target UID: <code>{uid}</code>"
            send_msg(message.chat.id, text, reply_markup=get_buy_owner_buttons())
            
            if tg_target:
                try:
                    send_msg(tg_target, f"{CE_ALERT} <b>Your Autolike slot for UID <code>{uid}</code> has been removed by Admin.</b>", reply_markup=get_buy_owner_buttons())
                except Exception: pass
        else:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜɪᴅ ɴᴏᴛ ғᴏᴜɴᴅ"))
    except Exception as e:
        print(f"Remove UID Error: {e}")

@bot.message_handler(commands=['extend'])
def extend_cmd(message):
    if not check_command_permission(message): return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜsᴀɢᴇ: /extend {ᴜɪᴅ} ᴅᴀʏs"))
            return
        uid = parts[1]
        days = int(parts[2])
        
        if uid in db["uids"]:
            db["uids"][uid]["days"] += days
            exp_date = datetime.datetime.strptime(db["uids"][uid]["expire_date"], "%Y-%m-%d").date()
            new_expire = exp_date + datetime.timedelta(days=days)
            db["uids"][uid]["expire_date"] = str(new_expire)
            save_data(db)
            
            tg_target = db["uids"][uid].get("tg_id")
            total_expected_likes = db["uids"][uid]["days"] * 220
            
            text = f"<b>{CE_TIME} DAYS EXTENDED SUCCESSFULLY!</b>\n\n"
            text += f"├ {CE_CHECK} <b>Added Days  :</b> {days}\n"
            text += f"├ {CE_STAR} <b>Total Days  :</b> {db['uids'][uid]['days']}\n"
            text += f"├ {CE_CHART} <b>Total Likes :</b> {total_expected_likes}\n"
            text += f"└ {CE_CLIP} <b>New Expire  :</b> {new_expire}"
            send_msg(message.chat.id, text, reply_markup=get_feedback_button())
            
            if tg_target:
                try:
                    dm_text = f"🎉 <b>YOUR AUTOLIKE HAS BEEN EXTENDED!</b>\n\n"
                    dm_text += f"├ {CE_GUN} <b>UID         :</b> <code>{uid}</code>\n"
                    dm_text += f"├ {CE_TIME} <b>Added Days  :</b> {days}\n"
                    dm_text += f"└ {CE_CLIP} <b>New Expire  :</b> {new_expire}"
                    send_msg(tg_target, dm_text, reply_markup=get_buy_owner_buttons())
                except Exception: pass
        else:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜɪᴅ ɴᴏᴛ ғᴏᴜɴᴅ"))
    except Exception as e:
        print(f"Extend Error: {e}")

@bot.message_handler(commands=['pause'])
def pause_cmd(message):
    if not check_command_permission(message): return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜsᴀɢᴇ: /pause {ᴜɪᴅ}"))
            return
        uid = parts[1]
        if uid in db["uids"]:
            db["uids"][uid]["paused"] = True
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} <b>UID <code>{uid}</code> has been PAUSED.</b>")
        else:
            send_msg(message.chat.id, f"{CE_ALERT} UID not found.")
    except Exception as e:
        print(f"Pause error: {e}")

@bot.message_handler(commands=['resume'])
def resume_cmd(message):
    if not check_command_permission(message): return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜsᴀɢᴇ: /resume {ᴜɪᴅ}"))
            return
        uid = parts[1]
        if uid in db["uids"]:
            db["uids"][uid]["paused"] = False
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} <b>UID <code>{uid}</code> has been RESUMED.</b>")
        else:
            send_msg(message.chat.id, f"{CE_ALERT} UID not found.")
    except Exception as e:
        print(f"Resume error: {e}")

@bot.message_handler(commands=['checklikes', 'checkuid'])
def checklikes_cmd(message):
    if not check_command_permission(message): return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜsᴀɢᴇ: /checkuid {ᴜɪᴅ}"))
            return
        uid = parts[1]
        if uid in db["uids"]:
            data = db["uids"][uid]
            total_expected_likes = data["days"] * 220
            text = f"╔══════════════════════════╗\n"
            text += f"   {CE_CHART} <b>UID DATABASE REPORT</b> {CE_CHART}\n"
            text += f"╚══════════════════════════╝\n\n"
            text += f"├ {CE_GUN} <b>UID          :</b> <code>{uid}</code>\n"
            text += f"├ {CE_HEART} <b>Likes Sent   :</b> <b>{data['total_given']}</b>\n"
            text += f"├ {CE_TIME} <b>Days Left    :</b> <b>{data['days']} Days</b>\n"
            text += f"├ {CE_CHART} <b>Total Target :</b> {total_expected_likes} Likes\n"
            text += f"├ {CE_CLIP} <b>Expire Date  :</b> {data['expire_date']}\n"
            text += f"├ {CE_PIN} <b>Telegram User:</b> <code>{data.get('tg_id', 'N/A')}</code>\n"
            text += f"└ {CE_CHECK} <b>Added Date   :</b> {data['added_date']}"
            send_msg(message.chat.id, text)
        else:
            send_msg(message.chat.id, f"{CE_ALERT} " + sc("ᴜɪᴅ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ sʏsᴛᴇᴍ"))
    except Exception as e:
        print(f"CheckLikes error: {e}")

@bot.message_handler(commands=['alluids'])
def alluids_cmd(message):
    if not check_command_permission(message): return
    try:
        if not db["uids"]:
            send_msg(message.chat.id, f"{CE_ALERT} <b>DATABASE IS EMPTY!</b>")
            return
        
        text = f"<b>{CE_PIN} REGISTERED UIDS DATABASE ({len(db['uids'])} Total):</b>\n\n"
        serial_no = 1
        for uid, data in db["uids"].items():
            tg_target = data.get('tg_id', 'N/A')
            status_str = "⏸ PAUSED" if data.get("paused") else "🟢 ACTIVE"
            text += f"<b>{serial_no}.</b> <code>{uid}</code> | {tg_target}\n"
            text += f"   ├ Days: {data['days']} | Status: {status_str}\n"
            text += f"   └ Expire: {data['expire_date']}\n\n"
            serial_no += 1
            if len(text) > 3800:
                send_msg(message.chat.id, text)
                text = ""
        if text:
            send_msg(message.chat.id, text)
    except Exception as e:
        print(f"AllUIDs Error: {e}")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    try:
        if not check_command_permission(message): return
        total_uid = len(db["uids"])
        active_uid_count = len([u for u, d in db["uids"].items() if not d.get("paused") and d["days"] > 0])
        remaining_slots = max(0, db["limit"] - total_uid)
        
        text = f"╔══════════════════════════╗\n"
        text += f"   {CE_STAR2} <b>BOT SYSTEM STATS</b> {CE_STAR2}\n"
        text += f"╚══════════════════════════╝\n\n"
        text += f"├ {CE_PIN} <b>Active Slots     :</b> {active_uid_count}/{total_uid}\n"
        text += f"├ {CE_CLIP} <b>Total Limit      :</b> {db['limit']}\n"
        text += f"├ {CE_CHECK} <b>Slots Available  :</b> {remaining_slots}\n"
        text += f"├ {CE_ALERT} <b>Bot Engine       :</b> {db['bot_status']}\n"
        text += f"├ {CE_TAG} <b>Default API      :</b> API {db.get('active_api', 2)}\n"
        text += f"├ {CE_TAG} <b>/like Command    :</b> {db.get('like_command_status', 'ON')}\n"
        text += f"├ {CE_TIME} <b>Auto Time        :</b> {db.get('auto_time', '04:00')} AM IST\n"
        text += f"└ {CE_HEART} <b>Total Likes Sent :</b> {db['total_likes_given']}\n"
        send_msg(message.chat.id, text)
    except Exception as e:
        print(f"Status Error: {e}")

# ==================== AUTOMATED CORE ENGINE ====================

def run_likes_process(chat_id_context=None):
    if not execution_lock.acquire(blocking=False):
        if chat_id_context:
            send_msg(chat_id_context, f"{CE_ALERT} <b>AUTOLIKE PROCESS IS ALREADY RUNNING! PLEASE WAIT.</b>")
        return

    try:
        if not db["uids"]:
            if chat_id_context:
                send_msg(chat_id_context, f"{CE_ALERT} <b>DATABASE IS EMPTY!</b>")
            return
        
        success_list = []
        failed_list = []
        skipped_list = []
        total_run_likes = 0
        api_type = db.get("active_api", 2)
        timeout = db.get("api_timeout", 25)
        
        targets = list(db["groups"])
        if not targets:
            targets = [str(OWNER_ID)]
        if chat_id_context and str(chat_id_context) not in targets:
            targets.append(str(chat_id_context))
            
        total_processing_slots = len([u for u, d in db["uids"].items() if d["days"] > 0 and not d.get("paused")])
        start_announcement = f"🎉 <b>AUTOMATED LIKES PROCESS STARTED (API {api_type})</b> 🎉\n\n"
        start_announcement += f"├ {CE_PIN} <b>Total Registered UIDs :</b> {len(db['uids'])}\n"
        start_announcement += f"├ {CE_TIME} <b>Active Queue          :</b> {total_processing_slots}\n"
        start_announcement += f"└ {CE_JUICE} <b>Status                :</b> Processing Live..."
        
        for grp in targets:
            try: send_msg(int(grp), start_announcement)
            except: pass
            
        for uid, data in list(db["uids"].items()):
            if data.get("paused"):
                skipped_list.append((uid, "Paused by Admin"))
                continue
            if data["days"] <= 0:
                skipped_list.append((uid, "Expired / 0 Days Left"))
                continue
            
            try:
                formatted_url = get_api_url(api_type, uid, data["region"])
                res_raw = requests.get(formatted_url, timeout=timeout)
                res = res_raw.json()
                p_name, before, given, after = parse_universal_api_response(res)
                
                tg_target = data.get("tg_id")
                
                if given > 0:
                    db["uids"][uid]["days"] -= 1
                    db["uids"][uid]["total_given"] += given
                    db["total_likes_given"] += given
                    total_run_likes += given
                    success_list.append((uid, p_name, db['uids'][uid]['days']))
                    
                    card_text = f"╔══════════════════════════╗\n"
                    card_text += f"   {CE_HEART} <b>AUTOLIKE SUCCESSFUL</b> {CE_HEART}\n"
                    card_text += f"╚══════════════════════════╝\n\n"
                    card_text += f"├ {CE_CROWN} <b>Player Name :</b> <b>{p_name}</b>\n"
                    card_text += f"├ {CE_GUN} <b>Player UID  :</b> <code>{uid}</code>\n"
                    card_text += f"├ {CE_GIFT} <b>Likes Given :</b> <b>{given}</b>\n"
                    card_text += f"├ {CE_STAR3} <b>Likes Before:</b> {before}\n"
                    card_text += f"└ {CE_CHECK} <b>Total Likes :</b> {after}\n"
                    
                    if tg_target:
                        try:
                            dm_success_text = f"💖 <b>DAILY AUTOLIKE DELIVERED!</b>\n\n"
                            dm_success_text += f"├ {CE_CROWN} <b>Name :</b> {p_name}\n"
                            dm_success_text += f"├ {CE_GUN} <b>UID  :</b> <code>{uid}</code>\n"
                            dm_success_text += f"├ {CE_GIFT} <b>Sent :</b> {given} Likes\n"
                            dm_success_text += f"└ {CE_TIME} <b>Days Left :</b> {db['uids'][uid]['days']} Days"
                            send_msg(tg_target, dm_success_text, reply_markup=get_buy_owner_buttons())
                        except: pass
                else:
                    failed_list.append((uid, p_name, "0 Likes Sent"))
                    card_text = f"⚠️ <b>AUTOLIKE FAILED FOR UID <code>{uid}</code> (0 Likes)</b>"

                for grp in targets:
                    send_msg(int(grp), card_text, reply_markup=get_buy_owner_buttons())
                    time.sleep(1)
                        
            except Exception as e:
                print(f"API Loop Exception for {uid}: {e}")
                failed_list.append((uid, "Unknown Player", "API Timeout / Error"))
                for grp in targets:
                    send_msg(int(grp), f"❌ <b>API ERROR / TIMEOUT FOR UID <code>{uid}</code></b>")
                
        save_data(db)
        
        grand_summary = f"╔══════════════════════════════╗\n"
        grand_summary += f"   {CE_STAR2} <b>FINAL SUMMARY REPORT</b> {CE_STAR2}\n"
        grand_summary += f"╚══════════════════════════════╝\n\n"
        
        grand_summary += f"🟢 <b>SUCCESSFUL UIDS (-1 Day Reduced):</b>\n"
        if success_list:
            for suid, sname, sdays in success_list:
                grand_summary += f"├ <code>{suid}</code> | {sname} | ({sdays} Days Left)\n"
        else: grand_summary += f"├ <i>None</i>\n"
            
        grand_summary += f"\n🔴 <b>FAILED UIDS (Days Saved):</b>\n"
        if failed_list:
            for fuid, fname, freason in failed_list:
                grand_summary += f"├ <code>{fuid}</code> | {fname}\n"
        else: grand_summary += f"├ <i>None</i>\n"
            
        grand_summary += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        grand_summary += f"├ {CE_PIN} <b>Total Active Slots :</b> <b>{len(db['uids'])}</b>\n"
        grand_summary += f"├ {CE_HEART} <b>Likes Sent This Run:</b> <b>{total_run_likes}</b>\n"
        grand_summary += f"└ {CE_TIME} <b>Next Auto Run Time :</b> <code>{db.get('auto_time', '04:00')} AM IST</code>"
        
        for grp in targets:
            try: send_msg(int(grp), grand_summary, reply_markup=get_buy_owner_buttons())
            except: pass
    finally:
        execution_lock.release()

@bot.message_handler(commands=['alllikes', 'runnow'])
def trigger_now_cmd(message):
    if not check_command_permission(message): return
    try:
        if execution_lock.locked():
            send_msg(message.chat.id, f"{CE_ALERT} <b>AUTOLIKE PROCESS IS ALREADY RUNNING!</b>")
            return
        send_msg(message.chat.id, f"{CE_TIME} <b>Manual execution triggered...</b>")
        threading.Thread(target=run_likes_process, args=(message.chat.id,)).start()
    except Exception as e:
        print(f"Trigger Error: {e}")

# ==================== OWNER CONTROL PANEL COMMANDS ====================

@bot.message_handler(commands=['timeoff'])
def timeoff_cmd(message):
    if not is_owner(message.from_user.id): return
    db["bot_status"] = "OFF"
    save_data(db)
    send_msg(message.chat.id, f"{CE_MUTE} <b>Bot auto-run disabled.</b>")

@bot.message_handler(commands=['timeon'])
def timeon_cmd(message):
    if not is_owner(message.from_user.id): return
    db["bot_status"] = "ON"
    save_data(db)
    send_msg(message.chat.id, f"{CE_CHECK} <b>Bot auto-run enabled.</b>")

@bot.message_handler(commands=['likeoff'])
def likeoff_cmd(message):
    if not is_admin(message.from_user.id): return
    db["like_command_status"] = "OFF"
    save_data(db)
    send_msg(message.chat.id, f"{CE_MUTE} <b>/like command turned off.</b>")

@bot.message_handler(commands=['likeon'])
def likeon_cmd(message):
    if not is_admin(message.from_user.id): return
    db["like_command_status"] = "ON"
    save_data(db)
    send_msg(message.chat.id, f"{CE_CHECK} <b>/like command turned on.</b>")

@bot.message_handler(commands=['addadmin'])
def addadmin_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        target_id = int(message.text.split()[1])
        if target_id not in db["admins"]:
            db["admins"].append(target_id)
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} Admin <code>{target_id}</code> added.")
    except: send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/addadmin {{id}}</code>")

@bot.message_handler(commands=['removeadmin'])
def removeadmin_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        target_id = int(message.text.split()[1])
        if target_id in db["admins"]:
            db["admins"].remove(target_id)
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} Admin <code>{target_id}</code> removed.")
    except: send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/removeadmin {{id}}</code>")

@bot.message_handler(commands=['admins'])
def admins_cmd(message):
    if not check_command_permission(message): return
    text = f"<b>👑 BOT ADMINS LIST:</b>\n\n• Owner: <code>{OWNER_ID}</code>\n"
    for a in db.get("admins", []):
        text += f"• Admin: <code>{a}</code>\n"
    send_msg(message.chat.id, text)

@bot.message_handler(commands=['setgroup'])
def setgroup_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        gid = str(message.text.split()[1])
        if gid not in db["groups"]:
            db["groups"].append(gid)
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} Group <code>{gid}</code> authorized.")
    except: send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/setgroup {{group_id}}</code>")

@bot.message_handler(commands=['removegroup'])
def removegroup_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        gid = str(message.text.split()[1])
        if gid in db["groups"]:
            db["groups"].remove(gid)
            save_data(db)
            send_msg(message.chat.id, f"{CE_CHECK} Group <code>{gid}</code> removed.")
    except: send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/removegroup {{group_id}}</code>")

@bot.message_handler(commands=['groups'])
def groups_cmd(message):
    if not check_command_permission(message): return
    text = f"<b>📌 AUTHORIZED GROUPS:</b>\n\n"
    for g in db["groups"]: text += f"• <code>{g}</code>\n"
    send_msg(message.chat.id, text)

@bot.message_handler(commands=['setlimit'])
def setlimit_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        lim = int(message.text.split()[1])
        db["limit"] = lim
        save_data(db)
        send_msg(message.chat.id, f"{CE_CHECK} Max limit set to {lim}")
    except: send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/setlimit {{number}}</code>")

@bot.message_handler(commands=['settime'])
def settime_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        time_str = message.text.split()[1]
        hh, mm = time_str.split(":")
        if not (0 <= int(hh) < 24 and 0 <= int(mm) < 60): raise ValueError
        db["auto_time"] = f"{int(hh):02d}:{int(mm):02d}"
        save_data(db)
        send_msg(message.chat.id, f"{CE_CHECK} Auto-run time set to <code>{db['auto_time']} AM IST</code>")
    except: send_msg(message.chat.id, f"{CE_ALERT} Usage: <code>/settime HH:MM</code>")

@bot.message_handler(commands=['notify'])
def notify_cmd(message):
    if not is_owner(message.from_user.id): return
    try:
        parts = message.text.split(maxsplit=2)
        target_user = parts[1]
        notif_msg = parts[2]
        send_msg(target_user, f"🔔 <b>NOTIFICATION FROM OWNER:</b>\n\n{notif_msg}", reply_markup=get_buy_owner_buttons())
        send_msg(message.chat.id, f"{CE_CHECK} Sent to <code>{target_user}</code>!")
    except Exception as e:
        send_msg(message.chat.id, f"{CE_ALERT} Error: {e}")

# ==================== UNAUTHORIZED USER CATCH-ALL GUARD ====================
@bot.message_handler(func=lambda message: True)
def unauthorized_guard(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        chat_type = message.chat.type
        
        if is_admin(user_id) or is_group_allowed(chat_id): return
            
        if chat_type == "private":
            text = f"{CE_MUTE} <b>YOU ARE NOT AUTHORIZED TO USE THIS BOT!</b>\n\n"
            text += f"{CE_ALERT} <b>Please contact owner to get access.</b>"
            send_msg(chat_id, text, reply_markup=get_unauthorized_button())
    except Exception as e:
        print(f"Guard Error: {e}")

# ==================== BACKGROUND MONITOR LOOP ====================
def native_scheduler_loop():
    global last_executed_record
    print("[*] Universal IST scheduler activated...")
    
    utc_now = datetime.datetime.now(datetime.timezone.utc) if hasattr(datetime, 'timezone') else datetime.datetime.utcnow()
    ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
    if ist_now.strftime("%H:%M") >= db.get("auto_time", "04:00"):
        last_executed_record = (ist_now.strftime("%Y-%m-%d"), db.get("auto_time", "04:00"))
    
    while True:
        try:
            target_time = db.get("auto_time", "04:00")
            bot_status = db.get("bot_status", "ON")
            
            if bot_status == "ON" and target_time:
                utc_now = datetime.datetime.now(datetime.timezone.utc) if hasattr(datetime, 'timezone') else datetime.datetime.utcnow()
                ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
                
                current_time_str = ist_now.strftime("%H:%M")
                current_date_str = ist_now.strftime("%Y-%m-%d")
                
                current_record = (current_date_str, target_time)
                
                if current_time_str >= target_time and last_executed_record != current_record:
                    print(f"[*] Auto execution trigger at {current_time_str} IST...")
                    run_likes_process()
                    last_executed_record = current_record
                    
        except Exception as e:
            print(f"Scheduler stability exception: {e}")
        time.sleep(10)

if __name__ == '__main__':
    t = threading.Thread(target=native_scheduler_loop, daemon=True)
    t.start()
    
    print("=========================================")
    print("      TEXT-ONLY BOT DEPLOYED SUCCESS     ")
    print("=========================================")
    bot.infinity_polling()

"""
🌈 ROBLOX CHECKER PRO - Single File
Features: Streamlit Web UI + Neon Theme + Multi-module
Modules: Check Item, Định Giá, Scam Detector, History, Bulk, Compare, Export, Avatar 2D
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import time
import re
import sqlite3
import io
from datetime import datetime
from typing import Optional, Dict, List
from functools import wraps
from pathlib import Path

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="🌈 Roblox Checker PRO",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# NEON THEME (7 màu)
# ============================================================
NEON = {
    "pink":   "#FF10F0",
    "cyan":   "#00FFF0",
    "purple": "#BC13FE",
    "green":  "#39FF14",
    "yellow": "#FFFF00",
    "orange": "#FF6B00",
    "red":    "#FF0040",
    "blue":   "#00BFFF",
    "white":  "#FFFFFF",
    "gray":   "#8888AA",
    "bg":     "#0A0A1A",
    "card":   "#14142B",
    "border": "#2A2A4A",
}

TIER_COLORS = {
    "S+": NEON["pink"], "S": NEON["purple"],
    "A+": NEON["cyan"], "A": NEON["blue"],
    "B+": NEON["green"], "B": NEON["yellow"],
    "C": NEON["orange"], "D": NEON["red"],
}


# ============================================================
# ⭐ HEX → RGBA HELPER (FIX Plotly color error)
# ============================================================
def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert #RRGGBB → rgba(r,g,b,a) để dùng với Plotly"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 8:
        hex_color = hex_color[:6]
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ============================================================
# CUSTOM CSS - NEON STYLE
# ============================================================
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

    .stApp {{
        background: radial-gradient(ellipse at top, #1a0a2e 0%, #0a0a1a 50%, #000 100%);
        font-family: 'Rajdhani', sans-serif;
    }}
    
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            linear-gradient(rgba(0,255,240,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,16,240,0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }}

    h1, h2, h3 {{
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 2px;
    }}

    .main-title {{
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, 
            {NEON['pink']}, {NEON['purple']}, {NEON['cyan']}, 
            {NEON['green']}, {NEON['yellow']}, {NEON['orange']}, {NEON['red']});
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        margin-bottom: 0;
        filter: drop-shadow(0 0 20px {NEON['cyan']}88);
    }}
    
    @keyframes shine {{
        to {{ background-position: 200% center; }}
    }}
    
    .subtitle {{
        text-align: center;
        color: {NEON['cyan']};
        font-size: 1rem;
        letter-spacing: 4px;
        margin-top: 0;
        text-shadow: 0 0 10px {NEON['cyan']}88;
    }}

    .neon-card {{
        background: linear-gradient(135deg, {NEON['card']}EE, {NEON['bg']}EE);
        border: 2px solid {NEON['cyan']};
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 
            0 0 20px {NEON['cyan']}44,
            inset 0 0 20px {NEON['cyan']}11;
        transition: all 0.3s ease;
    }}
    .neon-card:hover {{
        box-shadow: 
            0 0 40px {NEON['cyan']}88,
            inset 0 0 30px {NEON['cyan']}22;
        transform: translateY(-3px);
    }}

    .neon-card-pink {{ border-color: {NEON['pink']}; box-shadow: 0 0 20px {NEON['pink']}44, inset 0 0 20px {NEON['pink']}11; }}
    .neon-card-purple {{ border-color: {NEON['purple']}; box-shadow: 0 0 20px {NEON['purple']}44, inset 0 0 20px {NEON['purple']}11; }}
    .neon-card-green {{ border-color: {NEON['green']}; box-shadow: 0 0 20px {NEON['green']}44, inset 0 0 20px {NEON['green']}11; }}
    .neon-card-yellow {{ border-color: {NEON['yellow']}; box-shadow: 0 0 20px {NEON['yellow']}44, inset 0 0 20px {NEON['yellow']}11; }}
    .neon-card-orange {{ border-color: {NEON['orange']}; box-shadow: 0 0 20px {NEON['orange']}44, inset 0 0 20px {NEON['orange']}11; }}
    .neon-card-red {{ border-color: {NEON['red']}; box-shadow: 0 0 20px {NEON['red']}44, inset 0 0 20px {NEON['red']}11; }}

    .stat-box {{
        background: {NEON['card']}CC;
        border-left: 4px solid {NEON['cyan']};
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }}
    .stat-label {{
        color: {NEON['gray']};
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .stat-value {{
        color: {NEON['white']};
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        text-shadow: 0 0 10px currentColor;
    }}

    .tier-badge {{
        display: inline-block;
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        padding: 15px 40px;
        border-radius: 15px;
        border: 3px solid;
        text-shadow: 0 0 20px currentColor;
        animation: pulse 2s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); filter: brightness(1); }}
        50% {{ transform: scale(1.03); filter: brightness(1.3); }}
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {NEON['purple']}, {NEON['pink']}) !important;
        color: white !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 30px !important;
        box-shadow: 0 0 20px {NEON['pink']}66 !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
    }}
    .stButton > button:hover {{
        box-shadow: 0 0 40px {NEON['pink']}CC !important;
        transform: translateY(-2px) !important;
        filter: brightness(1.2);
    }}

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background: {NEON['card']} !important;
        color: {NEON['white']} !important;
        border: 2px solid {NEON['cyan']} !important;
        border-radius: 10px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        box-shadow: 0 0 20px {NEON['cyan']}88 !important;
        border-color: {NEON['pink']} !important;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NEON['bg']}, {NEON['card']}) !important;
        border-right: 2px solid {NEON['purple']};
    }}
    section[data-testid="stSidebar"] .stMarkdown {{
        color: {NEON['white']};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        background: {NEON['card']};
        border-radius: 10px;
        padding: 5px;
        gap: 5px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: {NEON['gray']};
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        border-radius: 8px;
        padding: 10px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {NEON['purple']}, {NEON['pink']}) !important;
        color: white !important;
        box-shadow: 0 0 15px {NEON['pink']}88;
    }}

    [data-testid="stMetricValue"] {{
        color: {NEON['cyan']} !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 10px {NEON['cyan']}88;
    }}
    [data-testid="stMetricLabel"] {{
        color: {NEON['gray']} !important;
        letter-spacing: 1px;
    }}

    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {NEON['cyan']}, {NEON['purple']}, {NEON['pink']}) !important;
        box-shadow: 0 0 15px {NEON['cyan']}88;
    }}

    .stDataFrame {{
        border: 2px solid {NEON['cyan']}44;
        border-radius: 10px;
    }}

    .stAlert {{
        border-radius: 10px;
        border-left: 4px solid {NEON['cyan']};
    }}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: {NEON['bg']}; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {NEON['purple']}, {NEON['cyan']});
        border-radius: 5px;
    }}

    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, {NEON['cyan']}, {NEON['pink']}, transparent);
        box-shadow: 0 0 10px {NEON['cyan']};
    }}

    .risk-badge {{
        display: inline-block;
        padding: 8px 20px;
        border-radius: 20px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        letter-spacing: 2px;
        border: 2px solid;
    }}
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# CONFIG
# ============================================================
CONFIG = {
    "timeout": 15,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AccountCheckerPRO/2.0",
    "rolimons_api": "https://www.rolimons.com/itemapi/itemdetails",
    "rap_to_usd": 0.0035,
    "value_to_usd": 0.0025,
    "age_bonus_per_year": 5000,
    "premium_bonus": 15000,
    "verified_bonus": 25000,
    "banned_penalty": 0.7,
    "trade_lock_penalty": 0.5,
    "new_acc_days": 30,
    "high_value_threshold": 500000,
    "suspicious_ratio": 3.0,
}

DB_PATH = Path("data/history.db")
DB_PATH.parent.mkdir(exist_ok=True)


# ============================================================
# UTILS
# ============================================================
def fmt_num(n):
    try: return f"{int(n):,}"
    except: return "0"

def fmt_short(n):
    try:
        n = int(n)
        if n >= 1_000_000_000: return f"{n/1_000_000_000:.2f}B"
        if n >= 1_000_000:     return f"{n/1_000_000:.2f}M"
        if n >= 1_000:         return f"{n/1_000:.2f}K"
        return str(n)
    except: return "0"

def days_since(date_str):
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return (datetime.now() - dt).days
    except: return 0

def tier_from_value(v):
    if v >= 5_000_000: return "S+"
    if v >= 1_000_000: return "S"
    if v >= 500_000:   return "A+"
    if v >= 100_000:   return "A"
    if v >= 50_000:    return "B+"
    if v >= 10_000:    return "B"
    if v >= 1_000:     return "C"
    return "D"

def risk_level(score):
    if score >= 70: return "RẤT CAO"
    if score >= 40: return "CAO"
    if score >= 20: return "TRUNG BÌNH"
    if score > 0:   return "THẤP"
    return "AN TOÀN"

def retry(max_attempts=3, delay=2):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **k):
            for i in range(max_attempts):
                try: return fn(*a, **k)
                except Exception:
                    if i == max_attempts - 1: raise
                    time.sleep(delay * (i + 1))
        return wrapper
    return deco


# ============================================================
# API WRAPPER
# ============================================================
@st.cache_resource
def get_session():
    s = requests.Session()
    s.headers.update({"User-Agent": CONFIG["user_agent"]})
    return s


@st.cache_data(ttl=1800, show_spinner=False)
def get_rolimons_data():
    try:
        r = get_session().get(CONFIG["rolimons_api"], timeout=30)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def api_get(url, params=None):
    try:
        r = get_session().get(url, params=params, timeout=CONFIG["timeout"])
        if r.status_code == 200: return r.json()
        if r.status_code == 429:
            time.sleep(5)
            return api_get(url, params)
    except Exception:
        pass
    return None


def get_user_by_username(username: str) -> Optional[Dict]:
    try:
        r = get_session().post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": False},
            timeout=CONFIG["timeout"]
        )
        if r.status_code == 200:
            users = r.json().get("data", [])
            if users: return users[0]
    except Exception: pass
    return None


def get_user_by_id(uid: int) -> Optional[Dict]:
    return api_get(f"https://users.roblox.com/v1/users/{uid}")


def get_collectibles(uid: int) -> List[Dict]:
    items = []
    cursor = ""
    while True:
        data = api_get(
            f"https://inventory.roblox.com/v1/users/{uid}/assets/collectibles",
            {"limit": 100, "cursor": cursor, "sortOrder": "Asc"}
        )
        if not data: break
        items.extend(data.get("data", []))
        cursor = data.get("nextPageCursor")
        if not cursor: break
        time.sleep(0.2)
    return items


def get_inventory(uid: int) -> List[Dict]:
    items = []
    cursor = ""
    while True:
        data = api_get(
            f"https://inventory.roblox.com/v2/users/{uid}/inventory/Asset",
            {"limit": 100, "cursor": cursor, "sortOrder": "Asc"}
        )
        if not data: break
        items.extend(data.get("data", []))
        cursor = data.get("nextPageCursor")
        if not cursor: break
        time.sleep(0.2)
    return items


def get_user_groups(uid: int) -> List[Dict]:
    data = api_get(f"https://groups.roblox.com/v2/users/{uid}/groups/roles")
    return data.get("data", []) if data else []


def get_friends_count(uid: int) -> int:
    d = api_get(f"https://friends.roblox.com/v1/users/{uid}/friends/count")
    return d.get("count", 0) if d else 0


def get_followers_count(uid: int) -> int:
    d = api_get(f"https://friends.roblox.com/v1/users/{uid}/followers/count")
    return d.get("count", 0) if d else 0


def get_item_value(asset_id: int) -> Dict:
    data = get_rolimons_data()
    items = data.get("items", {})
    item = items.get(str(asset_id))
    if not item:
        return {"value": 0, "rap": 0, "name": "Unknown", "trend": None, "projected": False, "rare": False}
    return {
        "name": item[0] if len(item) > 0 else "Unknown",
        "rap": item[2] if len(item) > 2 and item[2] != -1 else 0,
        "value": item[3] if len(item) > 3 and item[3] != -1 else 0,
        "trend": item[6] if len(item) > 6 else None,
        "projected": item[7] if len(item) > 7 else False,
        "rare": item[9] if len(item) > 9 else False,
    }


# ============================================================
# AVATAR 2D API
# ============================================================
def get_avatar_2d(uid: int, size: str = "720x720") -> Optional[str]:
    """Lấy ảnh avatar 2D full body"""
    try:
        r = get_session().get(
            "https://thumbnails.roblox.com/v1/users/avatar",
            params={"userIds": uid, "size": size, "format": "Png", "isCircular": False},
            timeout=CONFIG["timeout"]
        )
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data and data[0].get("state") == "Completed":
                return data[0].get("imageUrl")
            elif data:
                return data[0].get("imageUrl")
    except Exception:
        pass
    return None


def get_headshot_2d(uid: int) -> Optional[str]:
    """Lấy ảnh headshot"""
    try:
        r = get_session().get(
            "https://thumbnails.roblox.com/v1/users/avatar-headshot",
            params={"userIds": uid, "size": "420x420", "format": "Png", "isCircular": False},
            timeout=CONFIG["timeout"]
        )
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return data[0].get("imageUrl")
    except Exception:
        pass
    return None


def get_avatar_bust_2d(uid: int) -> Optional[str]:
    """Lấy bust shot"""
    try:
        r = get_session().get(
            "https://thumbnails.roblox.com/v1/users/avatar-bust",
            params={"userIds": uid, "size": "420x420", "format": "Png"},
            timeout=CONFIG["timeout"]
        )
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return data[0].get("imageUrl")
    except Exception:
        pass
    return None


def get_wearing_items(uid: int) -> List[Dict]:
    """Lấy items đang mặc"""
    items = []
    try:
        r = get_session().get(
            f"https://avatar.roblox.com/v1/users/{uid}/avatar",
            timeout=CONFIG["timeout"]
        )
        if r.status_code == 200:
            data = r.json()
            for asset in data.get("assets", []):
                items.append({
                    "id": asset.get("id"),
                    "name": asset.get("name"),
                    "type": asset.get("assetType", {}).get("name", "Unknown"),
                })
    except Exception:
        pass
    return items


def get_avatar_scales_2d(uid: int) -> Optional[Dict]:
    """Lấy body scales"""
    try:
        r = get_session().get(
            f"https://avatar.roblox.com/v1/users/{uid}/avatar",
            timeout=CONFIG["timeout"]
        )
        if r.status_code == 200:
            data = r.json()
            return {
                "scales": data.get("scales", {}),
                "playerAvatarType": data.get("playerAvatarType", "R15"),
            }
    except Exception:
        pass
    return None


def get_outfits_2d(uid: int) -> List[Dict]:
    """Lấy outfits đã lưu"""
    try:
        r = get_session().get(
            f"https://avatar.roblox.com/v1/users/{uid}/outfits",
            params={"page": 1, "itemsPerPage": 50, "isEditable": False},
            timeout=CONFIG["timeout"]
        )
        if r.status_code == 200:
            return r.json().get("data", [])
    except Exception:
        pass
    return []


def get_wearing_value_2d(uid: int) -> Dict:
    """Tính value items đang mặc"""
    items = get_wearing_items(uid)
    total_rap = 0
    total_value = 0
    detail = []
    
    for item in items:
        aid = item.get("id")
        if not aid:
            continue
        val = get_item_value(aid)
        rap = val.get("rap", 0) or 0
        value = val.get("value", 0) or 0
        total_rap += rap
        total_value += value
        detail.append({
            "id": aid,
            "name": val.get("name", item.get("name", "Unknown")),
            "type": item.get("type", "Unknown"),
            "rap": rap,
            "value": value,
            "rare": val.get("rare", False),
        })
    
    return {
        "total_items": len(items),
        "total_rap": total_rap,
        "total_value": total_value,
        "items": detail,
    }


# ============================================================
# VALUATOR
# ============================================================
def valuate_account(uid: int, user_info: Dict, progress_cb=None):
    if progress_cb: progress_cb(0.1, "📦 Đang lấy inventory...")
    collectibles = get_collectibles(uid)
    inventory = get_inventory(uid)

    items_detail = []
    total_rap = 0
    total_value = 0
    total_default = 0

    total = len(collectibles)
    for i, item in enumerate(collectibles):
        aid = item.get("assetId") or item.get("id")
        if not aid: continue
        val = get_item_value(aid)
        rap = val.get("rap", 0) or item.get("recentAveragePrice", 0) or 0
        value = val.get("value", 0) or 0
        default_price = item.get("originalPrice", 0) or 0
        total_rap += rap
        total_value += value
        total_default += default_price
        items_detail.append({
            "asset_id": aid,
            "name": val.get("name", item.get("name", "Unknown")),
            "rap": rap,
            "value": value,
            "default_price": default_price,
            "trend": val.get("trend"),
            "projected": val.get("projected", False),
            "rare": val.get("rare", False),
        })
        if progress_cb and total > 0:
            pct = 0.1 + 0.7 * (i + 1) / total
            progress_cb(pct, f"💰 Đang tính giá trị: {i+1}/{total}")

    if progress_cb: progress_cb(0.85, "🧮 Đang tính toán...")

    created = user_info.get("created", "")
    age_days = days_since(created)
    age_years = age_days / 365.25

    bonus = 0
    bonus_bd = []
    age_bonus = int(age_years * CONFIG["age_bonus_per_year"])
    bonus += age_bonus
    bonus_bd.append(f"Account age ({age_years:.1f} năm): +{fmt_num(age_bonus)}")

    if user_info.get("isPremium") or user_info.get("premium"):
        bonus += CONFIG["premium_bonus"]
        bonus_bd.append(f"Premium: +{fmt_num(CONFIG['premium_bonus'])}")
    if user_info.get("hasVerifiedBadge"):
        bonus += CONFIG["verified_bonus"]
        bonus_bd.append(f"Verified: +{fmt_num(CONFIG['verified_bonus'])}")

    penalty = 0
    penalty_bd = []
    if user_info.get("isBanned"):
        penalty += CONFIG["banned_penalty"]
        penalty_bd.append(f"Banned: -{int(CONFIG['banned_penalty']*100)}%")
    if user_info.get("isTradeLocked") or user_info.get("tradeLock"):
        penalty += CONFIG["trade_lock_penalty"]
        penalty_bd.append(f"Trade lock: -{int(CONFIG['trade_lock_penalty']*100)}%")

    subtotal = total_rap + total_value + bonus
    final_value = int(subtotal * (1 - penalty))
    usd = round(final_value * CONFIG["value_to_usd"], 2)
    tier = tier_from_value(final_value)

    if progress_cb: progress_cb(1.0, "✅ Hoàn tất!")

    return {
        "total_items": len(inventory) + len(collectibles),
        "collectibles_count": len(collectibles),
        "regular_items_count": len(inventory),
        "total_rap": total_rap,
        "total_value": total_value,
        "total_default": total_default,
        "bonus": bonus,
        "bonus_breakdown": bonus_bd,
        "penalty_breakdown": penalty_bd,
        "final_value": final_value,
        "usd_estimate": usd,
        "tier": tier,
        "items_detail": items_detail,
        "age_days": age_days,
        "age_years": round(age_years, 1),
    }


# ============================================================
# SCAM DETECTOR
# ============================================================
KNOWN_SCAMMERS = set()

SUS_PATTERNS = [
    r"free.?robux", r"robux.?gen", r"admin", r"moderator",
    r"staff", r"official", r"support", r"\d{6,}",
]


def detect_scam(user_info: Dict, val: Dict, groups: List[Dict], friends: int):
    risks = []
    score = 0

    username = user_info.get("name", "")
    display_name = user_info.get("displayName", "")
    age_days = val.get("age_days", 0)
    final_value = val.get("final_value", 0)
    rap = val.get("total_rap", 0)
    value = val.get("total_value", 0)
    collectibles = val.get("collectibles_count", 0)

    for pattern in SUS_PATTERNS:
        if re.search(pattern, username.lower()):
            risks.append(f"⚠️  Username chứa pattern sus: `{pattern}`")
            score += 15
            break

    if age_days < CONFIG["new_acc_days"] and final_value > CONFIG["high_value_threshold"]:
        risks.append(f"🚨 Acc mới ({age_days} ngày) nhưng value cao ({fmt_num(final_value)}) → có thể bị hack/stolen")
        score += 40

    if rap > 0 and value / rap > CONFIG["suspicious_ratio"]:
        risks.append(f"⚠️  Value/RAP ratio cao bất thường: {value/rap:.2f}x")
        score += 20

    if username.lower() in KNOWN_SCAMMERS:
        risks.append("🚨 Username trong blacklist scammer!")
        score += 100

    if friends == 0 and final_value > 100_000:
        risks.append("⚠️  0 friends nhưng value cao → có thể là alt/bot")
        score += 15

    fake_brands = ["roblox", "admin", "mod", "staff", "support"]
    if display_name and username:
        if display_name.lower() != username.lower():
            for b in fake_brands:
                if b in display_name.lower() and b not in username.lower():
                    risks.append(f"⚠️  Display name giả mạo brand: `{display_name}`")
                    score += 20
                    break

    projected = sum(1 for i in val.get("items_detail", []) if i.get("projected"))
    if collectibles > 0 and projected / collectibles > 0.5:
        risks.append(f"⚠️  {projected}/{collectibles} items projected (giá có thể giảm)")
        score += 10

    rare_low = sum(1 for i in val.get("items_detail", [])
                   if i.get("rare") and i.get("rap", 0) < 1000)
    if rare_low > 5:
        risks.append(f"⚠️  {rare_low} items rare nhưng RAP thấp → có thể fake")
        score += 15

    if user_info.get("isBanned"):
        risks.append("🚨 Account đã bị BAN!")
        score += 50

    score = min(score, 100)
    return {
        "score": score,
        "level": risk_level(score),
        "risks": risks if risks else ["✅ Không phát hiện dấu hiệu scam"],
    }


# ============================================================
# HISTORY DB
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            value INTEGER,
            rap INTEGER,
            tier TEXT,
            risk_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_history(uid, username, value, rap, tier, risk):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (user_id, username, value, rap, tier, risk_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (uid, username, value, rap, tier, risk))
    conn.commit()
    conn.close()


def get_history(uid=None):
    conn = sqlite3.connect(DB_PATH)
    if uid:
        df = pd.read_sql_query(
            "SELECT * FROM history WHERE user_id=? ORDER BY timestamp",
            conn, params=(uid,)
        )
    else:
        df = pd.read_sql_query(
            "SELECT * FROM history ORDER BY timestamp DESC LIMIT 100",
            conn
        )
    conn.close()
    return df


# ============================================================
# UI COMPONENTS
# ============================================================
def render_header():
    st.markdown(f"""
    <div style="text-align:center; padding: 20px 0;">
        <h1 class="main-title">🌈 ROBLOX CHECKER PRO</h1>
        <p class="subtitle">⚡ ACCOUNT VALUATOR • SCAM DETECTOR • NEON EDITION ⚡</p>
    </div>
    """, unsafe_allow_html=True)


def stat_card(label, value, color=NEON["cyan"]):
    return f"""
    <div class="stat-box" style="border-left-color: {color};">
        <div class="stat-label">{label}</div>
        <div class="stat-value" style="color: {color};">{value}</div>
    </div>
    """


def neon_card(content, color="cyan"):
    return f'<div class="neon-card neon-card-{color}">{content}</div>'


def tier_badge(tier):
    color = TIER_COLORS.get(tier, NEON["gray"])
    return f"""
    <div style="text-align:center; padding: 20px;">
        <div class="tier-badge" style="color: {color}; border-color: {color}; 
                    box-shadow: 0 0 30px {color}88, inset 0 0 30px {color}22;">
            {tier}
        </div>
        <div style="color: {NEON['gray']}; letter-spacing: 3px; margin-top: 10px;">
            TIER
        </div>
    </div>
    """


def risk_badge(level, score):
    color_map = {
        "RẤT CAO": NEON["red"],
        "CAO": NEON["orange"],
        "TRUNG BÌNH": NEON["yellow"],
        "THẤP": NEON["green"],
        "AN TOÀN": NEON["cyan"],
    }
    color = color_map.get(level, NEON["gray"])
    return f"""
    <div style="text-align:center; padding: 20px;">
        <div class="risk-badge" style="color: {color}; border-color: {color};
                    box-shadow: 0 0 20px {color}88;">
            {level} • {score}/100
        </div>
    </div>
    """


def render_user_info_html(user, val, friends, followers):
    badges = []
    if user.get("isBanned"): badges.append(f'<span style="color:{NEON["red"]}; font-weight:700;">🔴 BANNED</span>')
    if user.get("hasVerifiedBadge"): badges.append(f'<span style="color:{NEON["blue"]}; font-weight:700;">✔ VERIFIED</span>')
    if user.get("isPremium") or user.get("premium"): badges.append(f'<span style="color:{NEON["yellow"]}; font-weight:700;">⭐ PREMIUM</span>')
    
    avatar = f"https://www.roblox.com/headshot-thumbnail/image?userId={user['id']}&width=150&height=150&format=png"
    
    return f"""
    <div style="display:flex; gap:20px; align-items:center;">
        <img src="{avatar}" style="border-radius:50%; border:3px solid {NEON['cyan']};
             box-shadow: 0 0 25px {NEON['cyan']}88; width:120px; height:120px; object-fit:cover;"
             onerror="this.style.display='none'">
        <div>
            <h2 style="color:{NEON['cyan']}; margin:0; font-family:'Orbitron';">{user.get('displayName', user.get('name'))}</h2>
            <p style="color:{NEON['gray']}; margin:5px 0;">@{user.get('name')} • ID: {user.get('id')}</p>
            <p style="color:{NEON['white']}; margin:5px 0;">📅 {user.get('created','N/A')[:10]} ({val['age_years']} năm)</p>
            <p style="color:{NEON['white']}; margin:5px 0;">👥 {fmt_num(friends)} friends • {fmt_num(followers)} followers</p>
            <p style="margin:8px 0 0 0;">{' • '.join(badges)}</p>
        </div>
    </div>
    """


def render_valuation(val):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("📦 TOTAL ITEMS", fmt_num(val['total_items']), NEON["cyan"]), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("💎 LIMITED", fmt_num(val['collectibles_count']), NEON["purple"]), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("💰 TOTAL RAP", f"{fmt_short(val['total_rap'])} R$", NEON["green"]), unsafe_allow_html=True)
    with c4:
        st.markdown(stat_card("📊 VALUE", fmt_short(val['total_value']), NEON["pink"]), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"""
        <div class="neon-card neon-card-pink" style="text-align:center; padding:30px;">
            <div style="color:{NEON['gray']}; letter-spacing:3px; text-transform:uppercase;">
                ➜ FINAL ESTIMATED VALUE
            </div>
            <div style="font-family:'Orbitron'; font-size:3rem; font-weight:900;
                        background: linear-gradient(90deg, {NEON['pink']}, {NEON['purple']}, {NEON['cyan']});
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        filter: drop-shadow(0 0 20px {NEON['pink']}88);">
                {fmt_num(val['final_value'])}
            </div>
            <div style="color:{NEON['green']}; font-size:1.3rem; margin-top:10px;">
                ~ ${val['usd_estimate']} USD
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(tier_badge(val['tier']), unsafe_allow_html=True)
    
    if val['bonus_breakdown'] or val['penalty_breakdown']:
        c1, c2 = st.columns(2)
        with c1:
            if val['bonus_breakdown']:
                items_html = "".join(f'<li style="color:{NEON["green"]}; margin:5px 0;">+ {b}</li>' 
                                     for b in val['bonus_breakdown'])
                st.markdown(f"""
                <div class="neon-card neon-card-green">
                    <h4 style="color:{NEON['green']}; margin:0 0 10px 0;">✨ BONUS</h4>
                    <ul style="margin:0; padding-left:20px;">{items_html}</ul>
                </div>
                """, unsafe_allow_html=True)
        with c2:
            if val['penalty_breakdown']:
                items_html = "".join(f'<li style="color:{NEON["red"]}; margin:5px 0;">- {p}</li>' 
                                     for p in val['penalty_breakdown'])
                st.markdown(f"""
                <div class="neon-card neon-card-red">
                    <h4 style="color:{NEON['red']}; margin:0 0 10px 0;">⚠️ PENALTY</h4>
                    <ul style="margin:0; padding-left:20px;">{items_html}</ul>
                </div>
                """, unsafe_allow_html=True)


def render_items_table(val):
    if not val['items_detail']:
        st.info("Không có limited items")
        return
    
    df = pd.DataFrame(val['items_detail'])
    df = df.sort_values("value", ascending=False)
    df["RAP"] = df["rap"].apply(lambda x: f"{x:,}")
    df["VALUE"] = df["value"].apply(lambda x: f"{x:,}")
    df["TREND"] = df["trend"].apply(lambda t: "📈 Up" if t == 1 else ("📉 Down" if t == 0 else "➖ Flat"))
    df["PROJ"] = df["projected"].apply(lambda x: "⚠️" if x else "")
    df["RARE"] = df["rare"].apply(lambda x: "💎" if x else "")
    
    display = df[["name", "RAP", "VALUE", "TREND", "PROJ", "RARE"]].rename(
        columns={"name": "ITEM NAME"}
    )
    
    st.dataframe(display, use_container_width=True, height=400)
    
    top = df.head(10).copy()
    top["value_num"] = top["value"].astype(int)
    top = top[top["value_num"] > 0]
    
    if not top.empty:
        fig = go.Figure(go.Bar(
            x=top["value_num"],
            y=top["name"],
            orientation="h",
            marker=dict(
                color=top["value_num"],
                colorscale=[[0, NEON["cyan"]], [0.5, NEON["purple"]], [1, NEON["pink"]]],
                line=dict(color=NEON["pink"], width=1),
            ),
            text=top["value_num"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(color=NEON["white"]),
        ))
        fig.update_layout(
            title=dict(text="🏆 TOP 10 ITEMS GIÁ TRỊ NHẤT", font=dict(color=NEON["cyan"], size=18, family="Orbitron")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=NEON["white"]),
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(gridcolor=NEON["border"], title="Value"),
            yaxis=dict(gridcolor=NEON["border"], autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)


def render_scam(scam):
    # ⭐ FIX: dùng rgba() thay vì hex + alpha
    color_map = {
        "RẤT CAO": NEON["red"],
        "CAO": NEON["orange"],
        "TRUNG BÌNH": NEON["yellow"],
        "THẤP": NEON["green"],
        "AN TOÀN": NEON["cyan"],
    }
    color = color_map.get(scam["level"], NEON["gray"])
    
    st.markdown(risk_badge(scam["level"], scam["score"]), unsafe_allow_html=True)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=scam["score"],
        title=dict(text="RISK SCORE", font=dict(color=NEON["white"], family="Orbitron")),
        number=dict(font=dict(color=color, size=50, family="Orbitron")),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor=NEON["gray"], tickfont=dict(color=NEON["gray"])),
            bar=dict(color=color, thickness=0.3),
            bgcolor=NEON["card"],
            borderwidth=2,
            bordercolor=NEON["border"],
            steps=[
                dict(range=[0, 20],   color=hex_to_rgba(NEON["cyan"], 0.15)),   # ✅ FIX
                dict(range=[20, 40],  color=hex_to_rgba(NEON["green"], 0.15)),  # ✅ FIX
                dict(range=[40, 70],  color=hex_to_rgba(NEON["yellow"], 0.15)), # ✅ FIX
                dict(range=[70, 100], color=hex_to_rgba(NEON["red"], 0.15)),    # ✅ FIX
            ],
            threshold=dict(line=dict(color=NEON["red"], width=4), thickness=0.8, value=70),
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=NEON["white"]),
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"### 🛡️ Chi tiết ({len([r for r in scam['risks'] if '✅' not in r])} cảnh báo)")
    for r in scam["risks"]:
        if "✅" in r:
            st.success(r)
        elif "🚨" in r:
            st.error(r)
        else:
            st.warning(r)


def render_groups(groups):
    if not groups:
        st.info("Không có groups")
        return
    for g in groups[:10]:
        grp = g.get("group", {})
        role = g.get("role", {})
        st.markdown(f"""
        <div class="neon-card" style="padding:10px; margin:5px 0;">
            <span style="color:{NEON['cyan']};">🏰 {grp.get('name','N/A')}</span>
            <span style="color:{NEON['gray']}; float:right;">[{role.get('name','Member')}]</span>
        </div>
        """, unsafe_allow_html=True)
    if len(groups) > 10:
        st.caption(f"... và {len(groups)-10} groups khác")


def render_history_chart(uid, username):
    df = get_history(uid)
    if len(df) < 2:
        st.info("Cần ít nhất 2 lần check để vẽ biểu đồ. Hãy check lại acc này sau!")
        return
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["value"],
        mode="lines+markers",
        name="Final Value",
        line=dict(color=NEON["pink"], width=3, shape="spline"),
        marker=dict(size=10, color=NEON["cyan"], line=dict(color=NEON["pink"], width=2)),
        fill="tozeroy",
        fillcolor=hex_to_rgba(NEON["pink"], 0.13),  # ✅ FIX
    ))
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["rap"],
        mode="lines+markers",
        name="RAP",
        line=dict(color=NEON["green"], width=2, dash="dot"),
        marker=dict(size=6, color=NEON["green"]),
    ))
    
    fig.update_layout(
        title=dict(text=f"📈 LỊCH SỬ GIÁ - {username}", font=dict(color=NEON["cyan"], family="Orbitron", size=18)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=NEON["white"]),
        xaxis=dict(gridcolor=NEON["border"], title="Thời gian"),
        yaxis=dict(gridcolor=NEON["border"], title="Giá trị"),
        hovermode="x unified",
        height=400,
        legend=dict(bgcolor="rgba(20,20,43,0.8)", bordercolor=NEON["cyan"], borderwidth=1),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 🎨 AVATAR 2D - FULL NEON UI
# ============================================================
def render_avatar(uid: int, username: str):
    """🎨 AVATAR TAB - Full Neon UI với 7 màu"""
    
    # Title gradient
    st.markdown(f"""
    <div style="text-align:center; padding:15px 0;">
        <h2 style="font-family:'Orbitron'; font-size:2rem; font-weight:900;
                   background: linear-gradient(90deg, 
                       {NEON['pink']}, {NEON['purple']}, {NEON['cyan']}, 
                       {NEON['green']}, {NEON['yellow']}, {NEON['orange']}, {NEON['red']});
                   background-size: 200% auto;
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   animation: shine 3s linear infinite;
                   filter: drop-shadow(0 0 15px {NEON['cyan']}88);
                   margin:0;">
            🎨 AVATAR / SKIN INSPECTOR
        </h2>
        <p style="color:{NEON['gray']}; letter-spacing:4px; font-size:0.85rem;">
            ━━━ FULL 2D VIEW • NEON EDITION ━━━
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("🎨 Đang tải dữ liệu avatar..."):
        avatar_url = get_avatar_2d(uid, "720x720")
        headshot_url = get_headshot_2d(uid)
        bust_url = get_avatar_bust_2d(uid)
        wearing = get_wearing_items(uid)
        scales = get_avatar_scales_2d(uid)
        outfits = get_outfits_2d(uid)
        wearing_value = get_wearing_value_2d(uid)
    
    # ===== STATS (4 NEON CARDS) =====
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("👕 ĐANG MẶC", f"{wearing_value['total_items']} items", 
                              NEON["pink"]), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("💰 WEARING VALUE", 
                              f"{fmt_short(wearing_value['total_value'])}", 
                              NEON["green"]), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("📈 WEARING RAP", 
                              f"{fmt_short(wearing_value['total_rap'])} R$", 
                              NEON["cyan"]), unsafe_allow_html=True)
    with c4:
        rig = scales.get("playerAvatarType", "R15") if scales else "R15"
        st.markdown(stat_card("🦴 RIG TYPE", rig, NEON["yellow"]), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== 3 AVATAR VIEWS =====
    st.markdown(f"""
    <div style="text-align:center; margin: 20px 0 10px 0;">
        <span style="color:{NEON['cyan']}; font-family:'Orbitron'; 
                     letter-spacing:3px; font-size:1rem;
                     text-shadow: 0 0 10px {NEON['cyan']}88;">
            ═══ AVATAR PREVIEWS ═══
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # FULL BODY - Cyan
    with col1:
        st.markdown(f"""
        <div style="text-align:center; color:{NEON['cyan']};
                    font-family:'Orbitron'; font-size:0.85rem; 
                    letter-spacing:2px; margin-bottom:8px;
                    text-shadow: 0 0 8px {NEON['cyan']}88;">
            🎭 FULL BODY
        </div>
        """, unsafe_allow_html=True)
        
        if avatar_url:
            st.markdown(f"""
            <div style="padding:15px;
                        background: linear-gradient(135deg, #1a0a2e, #0a0a1a);
                        border: 3px solid {NEON['cyan']};
                        border-radius: 20px;
                        box-shadow: 0 0 40px {NEON['cyan']}88,
                                    inset 0 0 30px {NEON['cyan']}22;">
                <img src="{avatar_url}" 
                     style="width:100%; display:block; margin:0 auto;
                            border-radius:12px;
                            filter: drop-shadow(0 0 20px {NEON['cyan']}88);">
            </div>
            <div style="text-align:center; margin-top:12px;">
                <a href="{avatar_url}" target="_blank" 
                   style="display:inline-block; padding:8px 20px;
                          background:linear-gradient(135deg,{NEON['cyan']},{NEON['blue']});
                          color:white; text-decoration:none;
                          border-radius:10px; font-family:'Orbitron';
                          font-size:0.75rem; font-weight:700; letter-spacing:1px;
                          box-shadow: 0 0 15px {NEON['cyan']}66;">
                    📥 TẢI FULL
                </a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding:40px 15px; text-align:center;
                        background:{NEON['card']}88;
                        border:2px dashed {NEON['cyan']}88;
                        border-radius:15px;">
                <div style="color:{NEON['cyan']}; font-size:2rem;">⏳</div>
                <p style="color:{NEON['gray']}; font-size:0.85rem;">
                    Đang render...<br>Thử lại sau 5-10s
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # BUST SHOT - Purple
    with col2:
        st.markdown(f"""
        <div style="text-align:center; color:{NEON['purple']};
                    font-family:'Orbitron'; font-size:0.85rem; 
                    letter-spacing:2px; margin-bottom:8px;
                    text-shadow: 0 0 8px {NEON['purple']}88;">
            🧑 BUST SHOT
        </div>
        """, unsafe_allow_html=True)
        
        if bust_url:
            st.markdown(f"""
            <div style="padding:15px;
                        background: linear-gradient(135deg, #1a0a2e, #0a0a1a);
                        border: 3px solid {NEON['purple']};
                        border-radius: 20px;
                        box-shadow: 0 0 40px {NEON['purple']}88,
                                    inset 0 0 30px {NEON['purple']}22;">
                <img src="{bust_url}" 
                     style="width:100%; display:block; margin:0 auto;
                            border-radius:12px;
                            filter: drop-shadow(0 0 20px {NEON['purple']}88);">
            </div>
            <div style="text-align:center; margin-top:12px;">
                <a href="{bust_url}" target="_blank" 
                   style="display:inline-block; padding:8px 20px;
                          background:linear-gradient(135deg,{NEON['purple']},{NEON['pink']});
                          color:white; text-decoration:none;
                          border-radius:10px; font-family:'Orbitron';
                          font-size:0.75rem; font-weight:700; letter-spacing:1px;
                          box-shadow: 0 0 15px {NEON['purple']}66;">
                    📥 TẢI BUST
                </a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding:40px 15px; text-align:center;
                        background:{NEON['card']}88;
                        border:2px dashed {NEON['purple']}88;
                        border-radius:15px;">
                <div style="color:{NEON['purple']}; font-size:2rem;">⏳</div>
                <p style="color:{NEON['gray']}; font-size:0.85rem;">
                    Đang render...<br>Thử lại sau 5-10s
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # HEADSHOT - Pink
    with col3:
        st.markdown(f"""
        <div style="text-align:center; color:{NEON['pink']};
                    font-family:'Orbitron'; font-size:0.85rem; 
                    letter-spacing:2px; margin-bottom:8px;
                    text-shadow: 0 0 8px {NEON['pink']}88;">
            🎯 HEADSHOT
        </div>
        """, unsafe_allow_html=True)
        
        if headshot_url:
            st.markdown(f"""
            <div style="padding:15px;
                        background: linear-gradient(135deg, #1a0a2e, #0a0a1a);
                        border: 3px solid {NEON['pink']};
                        border-radius: 20px;
                        box-shadow: 0 0 40px {NEON['pink']}88,
                                    inset 0 0 30px {NEON['pink']}22;">
                <img src="{headshot_url}" 
                     style="width:100%; display:block; margin:0 auto;
                            border-radius:12px;
                            filter: drop-shadow(0 0 20px {NEON['pink']}88);">
            </div>
            <div style="text-align:center; margin-top:12px;">
                <a href="{headshot_url}" target="_blank" 
                   style="display:inline-block; padding:8px 20px;
                          background:linear-gradient(135deg,{NEON['pink']},{NEON['orange']});
                          color:white; text-decoration:none;
                          border-radius:10px; font-family:'Orbitron';
                          font-size:0.75rem; font-weight:700; letter-spacing:1px;
                          box-shadow: 0 0 15px {NEON['pink']}66;">
                    📥 TẢI HEAD
                </a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding:40px 15px; text-align:center;
                        background:{NEON['card']}88;
                        border:2px dashed {NEON['pink']}88;
                        border-radius:15px;">
                <div style="color:{NEON['pink']}; font-size:2rem;">⏳</div>
                <p style="color:{NEON['gray']}; font-size:0.85rem;">
                    Đang render...<br>Thử lại sau 5-10s
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== RARE WEARING ITEMS (7-COLOR NEON GRID) =====
    rare_wearing = [i for i in wearing_value["items"] 
                    if i.get("rare") or i.get("value", 0) > 10000]
    rare_wearing.sort(key=lambda x: x.get("value", 0), reverse=True)
    
    neon_cycle = ["pink", "purple", "cyan", "green", "yellow", "orange", "red"]
    
    if rare_wearing:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <h3 style="font-family:'Orbitron'; 
                   background: linear-gradient(90deg, {NEON['pink']}, {NEON['purple']}, {NEON['cyan']});
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   text-align:center; margin-bottom:20px;">
            💎 RARE ITEMS ĐANG MẶC ({len(rare_wearing)})
        </h3>
        """, unsafe_allow_html=True)
        
        cols = st.columns(min(len(rare_wearing), 4))
        for i, item in enumerate(rare_wearing[:8]):
            color_key = neon_cycle[i % len(neon_cycle)]
            color_hex = NEON[color_key]
            val_str = fmt_short(item.get("value") or item.get("rap") or 0)
            rare_badge = "💎 RARE" if item.get("rare") else "⭐ HIGH"
            
            with cols[i % 4]:
                st.markdown(f"""
                <div style="padding:15px; text-align:center; margin:5px 0;
                            background: linear-gradient(135deg, {NEON['card']}EE, {NEON['bg']}EE);
                            border: 2px solid {color_hex};
                            border-radius: 15px;
                            box-shadow: 0 0 20px {color_hex}66,
                                        inset 0 0 15px {color_hex}11;">
                    <div style="color:{color_hex}; font-size:0.7rem; 
                                letter-spacing:2px; font-weight:700;">
                        {rare_badge}
                    </div>
                    <div style="color:{NEON['white']}; font-weight:600; 
                                margin:10px 0; min-height:45px; font-size:0.9rem;
                                line-height:1.3;">
                        {item['name'][:35]}
                    </div>
                    <div style="color:{NEON['green']}; 
                                font-family:'Orbitron'; font-size:1.2rem;
                                font-weight:700;
                                text-shadow: 0 0 10px {NEON['green']}88;">
                        {val_str}
                    </div>
                    <div style="color:{NEON['gray']}; font-size:0.7rem; margin-top:8px;
                                letter-spacing:1px;">
                        {item.get('type','')[:20]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== WEARING ITEMS BY TYPE =====
    if wearing:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <h3 style="font-family:'Orbitron'; 
                   background: linear-gradient(90deg, {NEON['cyan']}, {NEON['purple']}, {NEON['pink']});
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   text-align:center; margin-bottom:20px;">
            👕 ITEMS ĐANG MẶC ({len(wearing)})
        </h3>
        """, unsafe_allow_html=True)
        
        types = {}
        for item in wearing:
            t = item.get("type", "Unknown")
            types.setdefault(t, []).append(item)
        
        for type_idx, (type_name, items) in enumerate(sorted(types.items())):
            color_key = neon_cycle[type_idx % len(neon_cycle)]
            color_hex = NEON[color_key]
            
            with st.expander(f"📁 **{type_name}** ({len(items)} items)", expanded=False):
                for item in items:
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between;
                                align-items:center;
                                padding:12px 18px; margin:4px 0;
                                background:{NEON['card']}AA;
                                border-radius:10px;
                                border-left:4px solid {color_hex};
                                box-shadow: 0 0 12px {color_hex}33;">
                        <span style="color:{NEON['white']}; font-weight:500;">
                            👕 {item['name']}
                        </span>
                        <span style="color:{color_hex}; font-size:0.7rem; 
                                     font-family:'Orbitron'; letter-spacing:1px;">
                            ID: {item['id']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Distribution chart
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <h3 style="font-family:'Orbitron'; 
                   background: linear-gradient(90deg, {NEON['green']}, {NEON['yellow']}, {NEON['orange']});
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   text-align:center; margin-bottom:20px;">
            📊 PHÂN BỐ ITEMS THEO TYPE
        </h3>
        """, unsafe_allow_html=True)
        
        type_counts = pd.DataFrame([
            {"Type": t, "Count": len(items)} for t, items in types.items()
        ]).sort_values("Count", ascending=True)
        
        fig = go.Figure(go.Bar(
            x=type_counts["Count"],
            y=type_counts["Type"],
            orientation="h",
            marker=dict(
                color=type_counts["Count"],
                colorscale=[
                    [0, NEON["cyan"]],
                    [0.5, NEON["purple"]],
                    [1, NEON["pink"]],
                ],
                line=dict(color=NEON["pink"], width=1),
            ),
            text=type_counts["Count"],
            textposition="outside",
            textfont=dict(color=NEON["white"], family="Orbitron"),
        ))
        fig.update_layout(
            title=dict(text="🎭 WEARING ITEMS BY TYPE",
                       font=dict(color=NEON["cyan"], family="Orbitron", size=16)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=NEON["white"]),
            height=max(300, len(types) * 45),
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(gridcolor=NEON["border"], title="Số lượng"),
            yaxis=dict(gridcolor=NEON["border"]),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ===== OUTFITS =====
    if outfits:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <h3 style="font-family:'Orbitron'; 
                   background: linear-gradient(90deg, {NEON['red']}, {NEON['orange']}, {NEON['yellow']});
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   text-align:center; margin-bottom:20px;">
            👗 OUTFITS ĐÃ LƯU ({len(outfits)})
        </h3>
        """, unsafe_allow_html=True)
        
        cols = st.columns(min(len(outfits), 5))
        for i, outfit in enumerate(outfits[:15]):
            color_key = neon_cycle[i % len(neon_cycle)]
            color_hex = NEON[color_key]
            
            with cols[i % 5]:
                st.markdown(f"""
                <div style="padding:15px; text-align:center; margin:5px 0;
                            background: linear-gradient(135deg, {NEON['card']}, {NEON['bg']});
                            border: 2px solid {color_hex};
                            border-radius: 12px;
                            box-shadow: 0 0 15px {color_hex}55;
                            min-height:80px;">
                    <div style="color:{NEON['white']}; font-size:0.85rem; 
                                font-weight:600; line-height:1.3;">
                        👗 {outfit.get('name', 'Unnamed')[:25]}
                    </div>
                    <div style="color:{color_hex}; font-size:0.7rem; margin-top:8px;
                                font-family:'Orbitron'; letter-spacing:1px;">
                        {len(outfit.get('assets', []))} items
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== BODY SCALES =====
    if scales and scales.get("scales"):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <h3 style="font-family:'Orbitron'; 
                   background: linear-gradient(90deg, {NEON['purple']}, {NEON['pink']}, {NEON['red']});
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   text-align:center; margin-bottom:20px;">
            🦴 BODY SCALES
        </h3>
        """, unsafe_allow_html=True)
        
        sc = scales["scales"]
        scale_labels = {
            "height": ("📏 HEIGHT", "cyan"),
            "width": ("↔️ WIDTH", "purple"),
            "head": ("🧠 HEAD", "pink"),
            "depth": ("🎯 DEPTH", "green"),
            "proportion": ("⚖️ PROPORTION", "yellow"),
            "bodyType": ("💪 BODY TYPE", "orange"),
        }
        
        cols = st.columns(3)
        for i, (key, (label, color_key)) in enumerate(scale_labels.items()):
            val = sc.get(key, "N/A")
            color_hex = NEON[color_key]
            
            if isinstance(val, (int, float)):
                val_display = f"{val:.2f}"
            else:
                val_display = str(val) if val else "N/A"
            
            with cols[i % 3]:
                st.markdown(f"""
                <div style="padding:15px; margin:5px 0;
                            background: linear-gradient(135deg, {NEON['card']}, {NEON['bg']});
                            border-left: 4px solid {color_hex};
                            border-radius: 12px;
                            box-shadow: 0 0 15px {color_hex}33;">
                    <div style="color:{color_hex}; font-size:0.75rem;
                                letter-spacing:2px; font-weight:700;">
                        {label}
                    </div>
                    <div style="color:{NEON['white']}; 
                                font-family:'Orbitron'; 
                                font-size:1.4rem; font-weight:900;
                                text-shadow: 0 0 10px {color_hex}88;
                                margin-top:5px;">
                        {val_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== 3D PROFILE LINK =====
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center; padding:20px;">
        <p style="color:{NEON['gray']}; font-size:0.9rem; margin-bottom:15px;
                  letter-spacing:2px;">
            ━━━ XEM AVATAR 3D TRÊN ROBLOX ━━━
        </p>
        <a href="https://www.roblox.com/users/{uid}/profile" target="_blank"
           style="display:inline-block; padding:15px 40px;
                  background:linear-gradient(90deg, 
                      {NEON['pink']}, {NEON['purple']}, {NEON['cyan']}, 
                      {NEON['green']}, {NEON['yellow']}, {NEON['orange']}, {NEON['red']});
                  background-size: 200% auto;
                  color:white; text-decoration:none; 
                  border-radius:15px;
                  font-family:'Orbitron'; font-weight:900; 
                  font-size:1rem; letter-spacing:3px;
                  box-shadow: 0 0 30px {NEON['purple']}88;
                  animation: shine 3s linear infinite;">
            🌐 XEM PROFILE ROBLOX
        </a>
        <p style="color:{NEON['gray']}; font-size:0.8rem; margin-top:15px;">
            💡 Avatar 3D xoay/zoom trực tiếp trên web Roblox
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# EXPORT
# ============================================================
def export_json(user, val, scam):
    data = {
        "user": user,
        "valuation": {k: v for k, v in val.items() if k != "items_detail"},
        "items": val["items_detail"],
        "scam": {k: v for k, v in scam.items()},
        "exported_at": datetime.now().isoformat(),
    }
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def export_csv(val):
    if not val["items_detail"]:
        return ""
    df = pd.DataFrame(val["items_detail"])
    return df.to_csv(index=False)


def export_excel(user, val, scam):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        summary = pd.DataFrame({
            "Field": ["Username", "User ID", "Tier", "Final Value", "USD Estimate",
                      "Total RAP", "Total Value", "Collectibles", "Total Items",
                      "Account Age (days)", "Risk Score", "Risk Level"],
            "Value": [
                user.get("name"), user.get("id"), val["tier"], val["final_value"],
                val["usd_estimate"], val["total_rap"], val["total_value"],
                val["collectibles_count"], val["total_items"],
                val["age_days"], scam["score"], scam["level"],
            ]
        })
        summary.to_excel(writer, sheet_name="Summary", index=False)
        
        if val["items_detail"]:
            pd.DataFrame(val["items_detail"]).to_excel(writer, sheet_name="Items", index=False)
        
        pd.DataFrame({"Risk": scam["risks"]}).to_excel(writer, sheet_name="Scam", index=False)
    
    return buf.getvalue()


# ============================================================
# MAIN CHECK FUNCTION
# ============================================================
def run_check(identifier: str):
    progress = st.progress(0, text="🔍 Bắt đầu...")
    
    progress.progress(0.05, text=f"🔍 Đang tìm: {identifier}")
    
    if identifier.isdigit():
        user_info = get_user_by_id(int(identifier))
    else:
        brief = get_user_by_username(identifier)
        user_info = get_user_by_id(brief["id"]) if brief else None
    
    if not user_info:
        progress.empty()
        st.error(f"❌ Không tìm thấy account: **{identifier}**")
        return None
    
    uid = user_info["id"]
    progress.progress(0.08, text=f"✅ Tìm thấy: {user_info['name']}")
    
    groups = get_user_groups(uid)
    friends = get_friends_count(uid)
    followers = get_followers_count(uid)
    
    def cb(pct, msg):
        progress.progress(pct, text=msg)
    
    val = valuate_account(uid, user_info, progress_cb=cb)
    
    progress.progress(0.95, text="🛡️ Đang phân tích scam...")
    scam = detect_scam(user_info, val, groups, friends)
    
    try:
        save_history(uid, user_info["name"], val["final_value"], val["total_rap"], val["tier"], scam["score"])
    except Exception:
        pass
    
    progress.progress(1.0, text="✅ Hoàn tất!")
    time.sleep(0.3)
    progress.empty()
    
    return {
        "user": user_info,
        "val": val,
        "scam": scam,
        "groups": groups,
        "friends": friends,
        "followers": followers,
    }


# ============================================================
# PAGES
# ============================================================
def page_single_check():
    st.markdown("### 🔍 CHECK ACCOUNT")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        identifier = st.text_input(
            "Nhập username hoặc User ID",
            placeholder="vd: builderman hoặc 156",
            label_visibility="collapsed",
        )
    with col2:
        check_btn = st.button("🚀 CHECK", use_container_width=True)
    
    if check_btn and identifier.strip():
        with st.spinner("Đang xử lý..."):
            result = run_check(identifier.strip())
        
        if result:
            st.session_state["last_result"] = result
            st.rerun()
    
    if "last_result" in st.session_state:
        r = st.session_state["last_result"]
        user, val, scam = r["user"], r["val"], r["scam"]
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown(neon_card(render_user_info_html(user, val, r["friends"], r["followers"]), "cyan"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ⭐ 6 TABS - thêm Avatar
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "💰 ĐỊNH GIÁ", "📦 ITEMS", "🛡️ SCAM", 
            "👥 GROUPS", "🎨 AVATAR", "📈 LỊCH SỬ"
        ])
        
        with tab1:
            render_valuation(val)
        
        with tab2:
            render_items_table(val)
        
        with tab3:
            render_scam(scam)
        
        with tab4:
            render_groups(r["groups"])
        
        with tab5:
            render_avatar(user["id"], user["name"])
        
        with tab6:
            render_history_chart(user["id"], user["name"])
        
        # Export
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 💾 EXPORT")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "📄 JSON",
                data=export_json(user, val, scam),
                file_name=f"report_{user['name']}.json",
                mime="application/json",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "📊 CSV",
                data=export_csv(val),
                file_name=f"items_{user['name']}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c3:
            try:
                st.download_button(
                    "📗 EXCEL",
                    data=export_excel(user, val, scam),
                    file_name=f"report_{user['name']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception:
                st.button("📗 EXCEL (lỗi)", disabled=True, use_container_width=True)


def page_bulk_check():
    st.markdown("### 📦 BULK CHECK - Check nhiều acc cùng lúc")
    st.caption("Nhập mỗi dòng 1 username hoặc ID (tối đa 50)")
    
    text = st.text_area(
        "Danh sách accounts",
        placeholder="builderman\n156\nRoblox\n...",
        height=200,
        label_visibility="collapsed",
    )
    
    max_items = st.slider("Giới hạn số acc", 1, 50, 10)
    
    if st.button("🚀 BULK CHECK", use_container_width=True):
        lines = [l.strip() for l in text.splitlines() if l.strip()][:max_items]
        if not lines:
            st.warning("Chưa có gì để check")
            return
        
        progress = st.progress(0)
        status = st.empty()
        results = []
        
        for i, identifier in enumerate(lines):
            status.info(f"🔍 [{i+1}/{len(lines)}] Đang check: **{identifier}**")
            progress.progress((i + 1) / len(lines))
            
            try:
                if identifier.isdigit():
                    user = get_user_by_id(int(identifier))
                else:
                    brief = get_user_by_username(identifier)
                    user = get_user_by_id(brief["id"]) if brief else None
                
                if not user:
                    results.append({
                        "Username": identifier, "ID": "-", "Status": "❌ Not found",
                        "Tier": "-", "Value": 0, "RAP": 0, "Items": 0,
                        "Age (y)": 0, "Risk": 0, "Risk Level": "-",
                    })
                    continue
                
                uid = user["id"]
                groups = get_user_groups(uid)
                friends = get_friends_count(uid)
                val = valuate_account(uid, user)
                scam = detect_scam(user, val, groups, friends)
                
                results.append({
                    "Username": user.get("name"), "ID": uid, "Status": "✅ OK",
                    "Tier": val["tier"], "Value": val["final_value"],
                    "RAP": val["total_rap"], "Items": val["collectibles_count"],
                    "Age (y)": val["age_years"], "Risk": scam["score"],
                    "Risk Level": scam["level"],
                })
            except Exception as e:
                results.append({
                    "Username": identifier, "ID": "-", "Status": f"❌ {e}",
                    "Tier": "-", "Value": 0, "RAP": 0, "Items": 0,
                    "Age (y)": 0, "Risk": 0, "Risk Level": "-",
                })
        
        status.empty()
        progress.empty()
        
        if results:
            df = pd.DataFrame(results)
            st.success(f"✅ Đã check {len(results)} accounts!")
            
            valid = df[df["Status"] == "✅ OK"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("✅ Thành công", len(valid))
            c2.metric("💰 Tổng value", fmt_short(valid["Value"].sum()))
            c3.metric("📊 Value TB", fmt_short(valid["Value"].mean() if len(valid) else 0))
            c4.metric("🏆 Best", valid.loc[valid["Value"].idxmax(), "Username"] if len(valid) else "-")
            
            df_sorted = df.sort_values("Value", ascending=False)
            st.dataframe(df_sorted, use_container_width=True, height=400)
            
            csv = df_sorted.to_csv(index=False)
            st.download_button("📊 Tải CSV", csv, "bulk_results.csv", "text/csv")
            
            if len(valid) > 1:
                fig = px.bar(
                    valid.sort_values("Value", ascending=True),
                    x="Value", y="Username", orientation="h",
                    color="Value",
                    color_continuous_scale=[
                        [0, NEON["cyan"]], [0.5, NEON["purple"]], [1, NEON["pink"]]
                    ],
                )
                fig.update_layout(
                    title=dict(text="📊 SO SÁNH VALUE", font=dict(color=NEON["cyan"], family="Orbitron")),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=NEON["white"]), height=400,
                    xaxis=dict(gridcolor=NEON["border"]),
                    yaxis=dict(gridcolor=NEON["border"]),
                )
                st.plotly_chart(fig, use_container_width=True)


def page_compare():
    st.markdown("### ⚔️ SO SÁNH 2 ACCOUNT")
    
    c1, c2 = st.columns(2)
    with c1:
        u1 = st.text_input("Account 1", placeholder="username/ID", key="cmp1")
    with c2:
        u2 = st.text_input("Account 2", placeholder="username/ID", key="cmp2")
    
    if st.button("⚔️ SO SÁNH", use_container_width=True):
        if not (u1.strip() and u2.strip()):
            st.warning("Nhập đủ 2 account")
            return
        
        with st.spinner("Đang phân tích..."):
            r1 = run_check(u1.strip())
            r2 = run_check(u2.strip())
        
        if not (r1 and r2):
            return
        
        a, b = r1, r2
        va, vb = a["val"], b["val"]
        sa, sb = a["scam"], b["scam"]
        
        rows = [
            ("Username", a["user"]["name"], b["user"]["name"]),
            ("Tier", va["tier"], vb["tier"]),
            ("Final Value", fmt_num(va["final_value"]), fmt_num(vb["final_value"])),
            ("USD", f"${va['usd_estimate']}", f"${vb['usd_estimate']}"),
            ("Total RAP", fmt_num(va["total_rap"]), fmt_num(vb["total_rap"])),
            ("Collectibles", fmt_num(va["collectibles_count"]), fmt_num(vb["collectibles_count"])),
            ("Age (years)", f"{va['age_years']}", f"{vb['age_years']}"),
            ("Friends", fmt_num(a["friends"]), fmt_num(b["friends"])),
            ("Risk Score", f"{sa['score']}/100", f"{sb['score']}/100"),
            ("Risk Level", sa["level"], sb["level"]),
        ]
        
        df = pd.DataFrame(rows, columns=["Field", a["user"]["name"], b["user"]["name"]])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if va["final_value"] > vb["final_value"]:
            winner = a["user"]["name"]
            diff = va["final_value"] - vb["final_value"]
        elif vb["final_value"] > va["final_value"]:
            winner = b["user"]["name"]
            diff = vb["final_value"] - va["final_value"]
        else:
            winner = "HÒA"
            diff = 0
        
        if winner != "HÒA":
            st.markdown(f"""
            <div class="neon-card neon-card-green" style="text-align:center;">
                <h2 style="color:{NEON['green']}; margin:0;">🏆 WINNER</h2>
                <h1 style="color:{NEON['cyan']}; font-family:'Orbitron'; margin:10px 0;">{winner}</h1>
                <p style="color:{NEON['gray']};">Cao hơn: <b style="color:{NEON['green']};">+{fmt_num(diff)}</b></p>
            </div>
            """, unsafe_allow_html=True)
        
        fig = go.Figure()
        for name, v, s in [(a["user"]["name"], va, sa), (b["user"]["name"], vb, sb)]:
            fig.add_trace(go.Scatterpolar(
                r=[
                    min(v["final_value"] / 100000, 10),
                    min(v["total_rap"] / 100000, 10),
                    v["age_years"],
                    min(v["collectibles_count"] / 10, 10),
                    (100 - s["score"]) / 10,
                ],
                theta=["Value", "RAP", "Age", "Items", "Safety"],
                fill="toself",
                name=name,
            ))
        fig.update_layout(
            polar=dict(
                bgcolor=NEON["card"],
                radialaxis=dict(color=NEON["gray"], gridcolor=NEON["border"]),
                angularaxis=dict(color=NEON["cyan"], gridcolor=NEON["border"]),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=NEON["white"]),
            height=450,
            title=dict(text="📊 RADAR COMPARISON", font=dict(color=NEON["cyan"], family="Orbitron")),
            legend=dict(bgcolor="rgba(20,20,43,0.8)", bordercolor=NEON["cyan"]),
        )
        st.plotly_chart(fig, use_container_width=True)


def page_history():
    st.markdown("### 📈 LỊCH SỬ CHECK")
    
    df = get_history()
    if df.empty:
        st.info("Chưa có dữ liệu lịch sử. Hãy check 1 acc trước!")
        return
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Tổng checks", len(df))
    c2.metric("👤 Unique accs", df["user_id"].nunique())
    c3.metric("💰 Total value", fmt_short(df["value"].sum()))
    c4.metric("🏆 Max value", fmt_short(df["value"].max()))
    
    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True, height=400)


# ============================================================
# MAIN APP
# ============================================================
def main():
    inject_css()
    init_db()
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:15px 0;">
            <h1 style="font-family:'Orbitron'; color:{NEON['cyan']}; 
                       text-shadow: 0 0 15px {NEON['cyan']}; margin:0;">
                🎯 PRO
            </h1>
            <p style="color:{NEON['gray']}; letter-spacing:3px; margin:5px 0;">
                ROBLOX CHECKER
            </p>
        </div>
        <hr>
        """, unsafe_allow_html=True)
        
        page = st.radio(
            "📌 MENU",
            ["🔍 Check Account", "📦 Bulk Check", "⚔️ So Sánh", "📈 Lịch Sử"],
            label_visibility="collapsed",
        )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="color:{NEON['gray']}; font-size:0.8rem; padding:10px;">
            <p>🌈 <b style="color:{NEON['pink']};">NEON EDITION v2.1</b></p>
            <p>⚡ Multi-module • Streamlit UI</p>
            <p>🎨 Avatar 2D Inspector</p>
            <p>💾 SQLite history tracking</p>
            <p>📊 Chart + Export</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🗑️ XÓA LỊCH SỬ", use_container_width=True):
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM history")
            conn.commit()
            conn.close()
            st.success("Đã xóa!")
            time.sleep(1)
            st.rerun()
    
    render_header()
    
    if page == "🔍 Check Account":
        page_single_check()
    elif page == "📦 Bulk Check":
        page_bulk_check()
    elif page == "⚔️ So Sánh":
        page_compare()
    elif page == "📈 Lịch Sử":
        page_history()
    
    st.markdown(f"""
    <div style="text-align:center; padding:30px 0 10px 0; color:{NEON['gray']}; font-size:0.85rem;">
        🌈 Made with <span style="color:{NEON['pink']};">♥</span> • Neon Edition 2025
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

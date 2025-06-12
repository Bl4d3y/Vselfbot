import json
import os
import random
import time
from pathlib import Path

COMMANDS = {}
DEV_COMMANDS = {}

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "economy.json"
COOLDOWN_FILE = DATA_DIR / "cooldowns.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(file):
    if file.exists():
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def get_data():
    return load_json(DATA_FILE)

def get_cooldowns():
    return load_json(COOLDOWN_FILE)

def save_data(data):
    save_json(DATA_FILE, data)

def save_cooldowns(cooldowns):
    save_json(COOLDOWN_FILE, cooldowns)

def get_user(user_id):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"wallet": 0, "bank": 0, "inventory": []}
        save_data(data)
    return data[uid]

def update_user(user_id, key, value):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"wallet": 0, "bank": 0, "inventory": []}
    data[uid][key] += value
    save_data(data)

def set_user_value(user_id, key, value):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"wallet": 0, "bank": 0, "inventory": []}
    data[uid][key] = value
    save_data(data)

def check_cooldown(user_id, command, seconds):
    uid = str(user_id)
    cooldowns = get_cooldowns()
    now = time.time()
    last = cooldowns.get(uid, {}).get(command, 0)
    if now - last < seconds:
        return seconds - (now - last)
    cooldowns.setdefault(uid, {})[command] = now
    save_cooldowns(cooldowns)
    return 0

# --- Commands ---

async def bal(bot, message, args):
    user = get_user(message.author.id)
    await message.channel.send(f"💰 Wallet: ${user['wallet']:,} | 🏦 Bank: ${user['bank']:,}")

async def work(bot, message, args):
    remaining = check_cooldown(message.author.id, "work", 30)
    if remaining > 0:
        return await message.channel.send(f"⏳ Wait {int(remaining)}s to work again.")
    amount = random.randint(50, 150)
    update_user(message.author.id, "wallet", amount)
    await message.channel.send(f"🚰️ You worked and earned ${amount}!")

async def dep(bot, message, args):
    if not args or not args[0].isdigit():
        return await message.channel.send("Usage: `!dep <amount>`")
    amount = int(args[0])
    user = get_user(message.author.id)
    if user["wallet"] < amount:
        return await message.channel.send("❌ Not enough wallet money.")
    update_user(message.author.id, "wallet", -amount)
    update_user(message.author.id, "bank", amount)
    await message.channel.send(f"✅ Deposited ${amount} to bank.")

async def withdraw(bot, message, args):
    if not args or not args[0].isdigit():
        return await message.channel.send("Usage: `!with <amount>`")
    amount = int(args[0])
    user = get_user(message.author.id)
    if user["bank"] < amount:
        return await message.channel.send("❌ Not enough bank money.")
    update_user(message.author.id, "bank", -amount)
    update_user(message.author.id, "wallet", amount)
    await message.channel.send(f"✅ Withdrew ${amount} to wallet.")

async def rob(bot, message, args):
    if not args or not message.mentions:
        return await message.channel.send("Usage: `!rob @user`")
    target = message.mentions[0]
    if target.id == message.author.id:
        return await message.channel.send("❌ You can't rob yourself.")
    victim = get_user(target.id)
    if victim["wallet"] < 50:
        return await message.channel.send("❌ Not enough money to rob.")
    stolen = random.randint(10, min(200, victim["wallet"]))
    update_user(message.author.id, "wallet", stolen)
    update_user(target.id, "wallet", -stolen)
    await message.channel.send(f"💸 You robbed {target.display_name} and got ${stolen}!")

async def inventory(bot, message, args):
    user = get_user(message.author.id)
    inv = user.get("inventory", [])
    if not inv:
        return await message.channel.send("🏰 Inventory is empty.")
    items = "\n".join(f"- {item}" for item in inv)
    await message.channel.send(f"📅 Inventory:\n{items}")

# --- Dev Commands ---

async def additem(bot, message, args):
    if message.author.id not in bot.config["DEV_ID"]:
        return await message.channel.send("❌ Unauthorized.")
    if len(args) < 2 or not message.mentions:
        return await message.channel.send("Usage: `!additem <@user> <item>`")
    target = message.mentions[0]
    item = " ".join(args[1:])
    data = get_data()
    data[str(target.id)]["inventory"].append(item)
    save_data(data)
    await message.channel.send(f"🏳️ Added `{item}` to {target.display_name}'s inventory.")

async def setbal(bot, message, args):
    if message.author.id not in bot.config["DEV_ID"]:
        return await message.channel.send("❌ Unauthorized.")
    if len(args) < 3 or not args[2].isdigit() or not message.mentions:
        return await message.channel.send("Usage: `!setbal <@user> <wallet/bank> <amount>`")
    target = message.mentions[0]
    key = args[1].lower()
    value = int(args[2])
    if key not in ["wallet", "bank"]:
        return await message.channel.send("❌ Use wallet or bank only.")
    set_user_value(target.id, key, value)
    await message.channel.send(f"📍 Set {target.display_name}'s {key} to ${value}.")

COMMANDS = {
    "bal": (bal, "Check your wallet and bank balance"),
    "work": (work, "Work to earn some cash"),
    "dep": (dep, "Deposit money to your bank"),
    "with": (withdraw, "Withdraw money from your bank"),
    "rob": (rob, "Rob another user's wallet"),
    "inv": (inventory, "Check your inventory")
}

DEV_COMMANDS = {
    "additem": (additem, "Give a user a custom item"),
    "setbal": (setbal, "Set a user's wallet or bank")
}

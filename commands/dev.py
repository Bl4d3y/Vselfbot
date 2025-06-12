import os
import sys
import discord
import asyncio
from datetime import datetime

DEV_COMMANDS = {}

async def restart(bot, message, args):
    await message.channel.send("🔁 Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)

async def status(bot, message, args):
    if "|" not in " ".join(args):
        return await message.channel.send("Usage: `!status <type> | <text>`")
    st, txt = " ".join(args).split("|", 1)
    st, txt = st.strip().lower(), txt.strip()
    if st == "playing":
        activity = discord.Game(name=txt)
    elif st == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=txt)
    elif st == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=txt)
    elif st == "streaming":
        activity = discord.Streaming(name=txt, url="https://twitch.tv/nevrloose")
    else:
        return await message.channel.send("❌ Invalid type.")
    await bot.change_presence(activity=activity)
    await message.channel.send(f"✅ Status set to **{st.title()}**: `{txt}`")

async def say(bot, message, args):
    if not args:
        return await message.channel.send("Usage: `!say <message>`")
    await message.channel.send(" ".join(args))

async def leaveguild(bot, message, args):
    if not args:
        return await message.channel.send("Usage: `!leaveguild <guild_id>`")
    guild = bot.get_guild(int(args[0]))
    if not guild:
        return await message.channel.send("❌ Guild not found.")
    await guild.leave()
    await message.channel.send(f"👋 Left guild `{guild.name}`")

async def servers(bot, message, args):
    guilds = bot.guilds
    msg = "\n".join([f"{g.name} (ID: {g.id})" for g in guilds])
    await message.channel.send(f"📡 **{len(guilds)} servers:**\n```{msg}```")

async def dmall(bot, message, args):
    sent = failed = 0
    if not args:
        return await message.channel.send("Usage: `!dmall <message>`")
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot or member == bot.user:
                continue
            try:
                await member.send(" ".join(args))
                sent += 1
            except:
                failed += 1
    await message.channel.send(f"📨 Sent to {sent} users, failed on {failed}.")

async def react(bot, message, args):
    if not args:
        return await message.channel.send("Usage: `!react <emoji>`")
    if not message.reference:
        return await message.channel.send("⚠️ Reply to a message to react.")
    try:
        replied = await message.channel.fetch_message(message.reference.message_id)
        await replied.add_reaction(args[0])
        await message.channel.send("✅ Reaction added.")
    except Exception as e:
        await message.channel.send(f"❌ Failed to react: {e}")

async def userinfo(bot, message, args):
    user = message.mentions[0] if message.mentions else message.author
    embed = discord.Embed(title=f"User Info - {user}", color=0xff77ff)
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Bot?", value=user.bot)
    embed.add_field(name="Created", value=user.created_at.strftime("%Y-%m-%d"))
    embed.set_thumbnail(url=user.avatar.url if user.avatar else discord.Embed.Empty)
    await message.channel.send(embed=embed)

async def serverinfo(bot, message, args):
    guild = message.guild
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=0xff77ff)
    embed.add_field(name="ID", value=guild.id)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Owner", value=guild.owner)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
    await message.channel.send(embed=embed)

async def purge(bot, message, args):
    try:
        amount = int(args[0])
        await message.channel.purge(limit=amount + 1)
        msg = await message.channel.send(f"🧹 Deleted {amount} messages.")
        await asyncio.sleep(2)
        await msg.delete()
    except:
        await message.channel.send("Usage: `!purge <amount>`")

async def nick(bot, message, args):
    if not message.mentions or len(args) < 2:
        return await message.channel.send("Usage: `!nick @user <new nickname>`")
    member = message.mentions[0]
    new_nick = " ".join(args[1:])
    try:
        await member.edit(nick=new_nick)
        await message.channel.send(f"📝 Changed nickname to `{new_nick}`")
    except:
        await message.channel.send("❌ Failed to change nickname.")

async def roleinfo(bot, message, args):
    if not message.role_mentions:
        return await message.channel.send("Mention a role.")
    role = message.role_mentions[0]
    embed = discord.Embed(title=f"Role Info - {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id)
    embed.add_field(name="Members", value=len(role.members))
    embed.add_field(name="Mentionable", value=role.mentionable)
    await message.channel.send(embed=embed)

async def ping(bot, message, args):
    latency = round(bot.latency * 1000)
    await message.channel.send(f"🏓 Pong! `{latency}ms`")

async def remind(bot, message, args):
    if len(args) < 2:
        return await message.channel.send("Usage: `!remind <seconds> <message>`")
    try:
        seconds = int(args[0])
        reminder = " ".join(args[1:])
        await message.channel.send(f"⏰ Reminder set for {seconds} seconds.")
        await asyncio.sleep(seconds)
        await message.channel.send(f"🔔 Reminder: {reminder}")
    except:
        await message.channel.send("❌ Invalid input.")

async def mentionrole(bot, message, args):
    if not message.role_mentions:
        return await message.channel.send("Mention a role to ping.")
    role = message.role_mentions[0]
    await message.channel.send(f"{role.mention} ping!")

async def channelinfo(bot, message, args):
    ch = message.channel
    embed = discord.Embed(title=f"Channel Info - {ch.name}", color=0xff77ff)
    embed.add_field(name="ID", value=ch.id)
    embed.add_field(name="Type", value=str(ch.type))
    embed.add_field(name="Created", value=ch.created_at.strftime("%Y-%m-%d"))
    await message.channel.send(embed=embed)

async def emojiinfo(bot, message, args):
    if not message.guild.emojis:
        return await message.channel.send("No custom emojis in this server.")
    emojis = "\n".join([f"{e.name} – `<:{e.name}:{e.id}>`" for e in message.guild.emojis])
    await message.channel.send(f"😃 **Emojis in `{message.guild.name}`:**\n```{emojis}```")

async def dev_wrapper(bot, message, args, func):
    if message.author.id not in bot.config["DEV_ID"]:
        return await message.channel.send("❌ You are not authorized.")
    await func(bot, message, args)

DEV_COMMANDS["restart"] = lambda b, m, a: dev_wrapper(b, m, a, restart)
DEV_COMMANDS["status"] = lambda b, m, a: dev_wrapper(b, m, a, status)
DEV_COMMANDS["say"] = lambda b, m, a: dev_wrapper(b, m, a, say)
DEV_COMMANDS["leaveguild"] = lambda b, m, a: dev_wrapper(b, m, a, leaveguild)
DEV_COMMANDS["servers"] = lambda b, m, a: dev_wrapper(b, m, a, servers)
DEV_COMMANDS["dmall"] = lambda b, m, a: dev_wrapper(b, m, a, dmall)
DEV_COMMANDS["react"] = lambda b, m, a: dev_wrapper(b, m, a, react)
DEV_COMMANDS["userinfo"] = lambda b, m, a: dev_wrapper(b, m, a, userinfo)
DEV_COMMANDS["serverinfo"] = lambda b, m, a: dev_wrapper(b, m, a, serverinfo)
DEV_COMMANDS["purge"] = lambda b, m, a: dev_wrapper(b, m, a, purge)
DEV_COMMANDS["nick"] = lambda b, m, a: dev_wrapper(b, m, a, nick)
DEV_COMMANDS["roleinfo"] = lambda b, m, a: dev_wrapper(b, m, a, roleinfo)
DEV_COMMANDS["ping"] = lambda b, m, a: dev_wrapper(b, m, a, ping)
DEV_COMMANDS["remind"] = lambda b, m, a: dev_wrapper(b, m, a, remind)
DEV_COMMANDS["mentionrole"] = lambda b, m, a: dev_wrapper(b, m, a, mentionrole)
DEV_COMMANDS["channelinfo"] = lambda b, m, a: dev_wrapper(b, m, a, channelinfo)
DEV_COMMANDS["emojiinfo"] = lambda b, m, a: dev_wrapper(b, m, a, emojiinfo)

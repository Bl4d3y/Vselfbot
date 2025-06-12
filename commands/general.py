import random

async def ping(bot, message, args):
    latency = round(bot.latency * 1000, 2)
    await message.channel.send(f"🏓 Pong! Latency: {latency}ms")

async def joke(bot, message, args):
    jokes = [
        "Why don’t scientists trust atoms? Because they make up everything!",
        "Why did the computer get cold? Because it left its Windows open!",
        "Why do Java developers wear glasses? Because they can’t C#."
    ]
    await message.channel.send(random.choice(jokes))

async def roll(bot, message, args):
    await message.channel.send(f"🎲 You rolled a **{random.randint(1, 6)}**!")

async def coinflip(bot, message, args):
    await message.channel.send(f"🪙 {random.choice(['Heads', 'Tails'])}")

COMMANDS = {
    "ping": ping,
    "joke": joke,
    "roll": roll,
    "coinflip": coinflip
}

import json
from core.client import SelfBot

with open("config.json") as f:
    config = json.load(f)

client = SelfBot(config)
client.run(config["TOKEN"], bot=False)

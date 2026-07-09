import os
from pathlib import Path

import discord
import yaml
from dotenv import load_dotenv

load_dotenv()


def load_discord_ids(bot_name: str) -> dict[str, int]:
    config_path = Path(__file__).resolve().parent.parent / "discord_ids.yml"

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    bot_config = data.get("bots", {}).get(bot_name)
    if not isinstance(bot_config, dict):
        raise RuntimeError(f"Missing bots.{bot_name} in {config_path}")

    resolved: dict[str, int] = {}
    for key, ref in bot_config.items():
        value = ref
        if isinstance(ref, str) and not ref.isdigit():
            value = data
            for part in ref.split("."):
                value = value[part]
        resolved[key] = int(value)

    return resolved


TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG = load_discord_ids("temari")
STARTUP_CHANNEL_ID = CONFIG["STARTUP_CHANNEL_ID"]

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    channel = client.get_channel(STARTUP_CHANNEL_ID)
    if channel is not None:
        await channel.send("起動しました")


client.run(TOKEN)

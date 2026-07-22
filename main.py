import os
import random
import datetime
from pathlib import Path

import discord
from discord.ext import tasks
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
# チャット反応は削除しましたが、後々必要になる場合を考慮してインテント自体は残しています
intents.message_content = True 
client = discord.Client(intents=intents)

# 日本時間の13時 (JST) を設定
JST = datetime.timezone(datetime.timedelta(hours=9))
LUNCH_TIME = datetime.time(hour=13, minute=0, tzinfo=JST)

@tasks.loop(time=LUNCH_TIME)
async def daily_lunch_request():
    """毎日13時にランダムな食べ物を要求するタスク"""
    channel = client.get_channel(STARTUP_CHANNEL_ID)
    if channel is not None:
        # ランダムに出力する食べ物のリスト
        foods = [
            "ハンバーグ", "ラーメン", "焼肉", "肉じゃが", 
            "オムレツ", "パフェ", "唐揚げ", "お寿司"
        ]
        food = random.choice(foods)
        
        # 指定されたシンプルなセリフ
        await channel.send(f"プロデューサー今日は{food}食べたい")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    
    # 13時の定期タスクを開始
    if not daily_lunch_request.is_running():
        daily_lunch_request.start()

    channel = client.get_channel(STARTUP_CHANNEL_ID)
    if channel is not None:
        await channel.send("起動しました")

# チャット反応 (on_message) は削除しました

client.run(TOKEN)
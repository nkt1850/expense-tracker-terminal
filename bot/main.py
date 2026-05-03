import os
import sys
from pathlib import Path

import discord
from discord.ext import commands

from bot.database import init_database
from bot.config import DISCORD_BOT_TOKEN

sys.path.insert(0, str(Path(__file__).parent.parent))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    
    try:
        await bot.add_cog(ExpenseCog(bot))
        await bot.tree.sync()
        print("Commands synced")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    
    print("Bot is ready!")

def run():
    init_database()
    
    token = DISCORD_BOT_TOKEN or os.environ.get("DISCORD_BOT_TOKEN")
    
    if not token:
        print("Error: No Discord bot token found. Set DISCORD_BOT_TOKEN in .env or config.py")
        print(f"Please add your bot token to: {Path(__file__).parent.parent / '.env'}")
        return
    
    bot.run(token)

if __name__ == "__main__":
    run()
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from cogs.EventEntry import EventEntry

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") 
if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN is not set in the environment variables.")

PREFIX = ".s"


class EventBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents)

    async def on_ready(self):
        await self.add_cog(EventEntry(self))
        print("I'm ready to rumble.")


bot = EventBot()

bot.run(BOT_TOKEN)


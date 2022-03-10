import discord
from discord.ext import commands

import aiohttp
import asyncio
import logging

import config

class SlashBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = kwargs.get("logger", None)
        self.session = kwargs.get("session", None)
        self.config = kwargs.get("config", __import__("config"))

        self._cogs = ["cogs.mido_admins", "jishaku"]

    #on_ready
    async def on_ready(self):
        self.logger.info("startup...")

        for i in self._cogs:
            try:
                self.load_extension(i)
            except Exception as exc:
                self.logger.warning(f"failed to load {i}: {exc}")
            else:
                self.logger.info(f"{i} load")

        self.logger.info("on_ready!")


#intents value
intents = discord.Intents.all()

#logging init
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s]: %(message)s"
)
logger = logging.getLogger("discord")

#bot main instance
bot = SlashBot(
    command_prefix=config.PREFIX,
    intents=intents,
    logger=logger,
    session=aiohttp.ClientSession(),
    config=__import__("config")
)

if __name__ == "__main__":
    try:
        bot.run(config.TOKEN)
    except Exception as exc:
        logger.critical(exc)
    else:
        logger.info("enabling discordbot...")

import discord
from discord.ext import commands

import asyncio
import io
import os
import textwrap
import traceback
import sys
from contextlib import redirect_stdout

from lib import utils

class mido_admins(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._ = None
        self.success = "✅"
        self.failed = "❌"

    #eval
    @commands.is_owner()
    @commands.command(name="eval", usage="eval <code>")
    async def _eval(self, ctx, *, code: str=None):
        if not code:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content="> 評価するコードを入力してね！")

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'self': self,
            '_': self._
        }

        env.update(globals())
        code = utils.cleanup_code(code)
        stdout = io.StringIO()
        to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as exc:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content=f"```py\n{exc.__class__.__name__}: {exc}\n```")

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as exc:
            await ctx.message.add_reaction(self.failed)
            value = stdout.getvalue()
            return await utils.reply_or_send(ctx, content=f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            await ctx.message.add_reaction(self.success)

            if ret is None:
                if value:
                    await utils.reply_or_send(ctx, content=f'```py\n{value}\n```')
            else:
                self._ = ret
                await utils.reply_or_send(ctx, content=f'```py\n{value}{ret}\n```')

    #shell
    @commands.is_owner()
    @commands.command(name="shell", aliases=["sh"], usage="shell <command>")
    async def shell(self, ctx, *, command=None):
        if not command:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content=f"> 実行するコマンドを入力してね！")

        stdout, stderr = await utils.run_process(ctx, command)
        if stderr:
            text = f"```\nstdout: \n{stdout} \n\nstderr: \n{stderr}\n```"
        else:
            text = f"```\nstdout: \n{stdout} \n\nstderr: \nnone\n```"

        try:
            await ctx.message.add_reaction(self.success)
            return await utils.reply_or_send(ctx, content=text)   
        except Exception as exc:
            await ctx.message.add_reaction(self.failed)
            return await utils.reply_or_send(ctx, content=f"```py\n{exc}\n```")


def setup(bot):
  bot.add_cog(mido_admins(bot))

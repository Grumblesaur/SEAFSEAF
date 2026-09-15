from typing import Awaitable

import discord
from discord.ext import commands

def response(ctx: commands.Context | discord.Interaction, content: str, file: discord.File | None = None) -> Awaitable:
    if isinstance(ctx, commands.Context):
        if ctx.interaction is None:
            res = ctx.message.reply(content, file=file)
        else:
            res = ctx.send(content, file=file)
    else:
        if file is None:
            res = ctx.response.send_message(content)
        else:
            res = ctx.response.send_message(content, file=file)
    return res

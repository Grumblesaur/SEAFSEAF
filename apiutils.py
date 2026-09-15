from typing import Awaitable, Literal

import discord
from discord.ext import commands
from discord.interactions import MISSING

Bool = Literal['yes', 'no']


def response(ctx: commands.Context | discord.Interaction, content: str, file: discord.File | None = None) -> Awaitable:
    if isinstance(ctx, commands.Context):
        kw = {'file': file}
        if ctx.interaction is None:
            res = ctx.message.reply(content, **kw)
        else:
            res = ctx.send(content, **kw)
    else:
        res = ctx.response.send_message(content, file=MISSING if file is None else file)
    return res


def parse_bool(s: Bool) -> bool:
    return s == 'yes'

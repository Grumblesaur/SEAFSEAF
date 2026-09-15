from typing import Literal

from discord.ext import commands

import apiutils
from randomizer import DifficultyOrder, PlanetOrder, FactionOrder, Mission


class Missions(commands.Cog, name="Missions"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='faction', aliases=['enemy', 'enemies'])
    async def faction(self, ctx: commands.Context):
        """Receive an assignment for a faction to fight."""
        fo = FactionOrder()
        await apiutils.response(ctx, str(fo))

    @commands.hybrid_command(name='difficulty', aliases=['diff', 'level'])
    async def difficulty(self, ctx: commands.Context):
        """Receive an assignment for a difficulty to play at."""
        do = DifficultyOrder()
        await apiutils.response(ctx, str(do))

    @commands.hybrid_command(name='planet', aliases=['world'])
    async def planet(self, ctx: commands.Context):
        """Receive an assignment for planetary conditions to play under."""
        po = PlanetOrder()
        await apiutils.response(ctx, str(po))

    @commands.hybrid_command(name='mission', aliases=['orders', 'order'])
    async def mission(self, ctx: commands.Context, mission_type: Literal['faction', 'planet', 'difficulty'] | None = None):
        """Receive a mission based on the specified `mission_type` or a random one if left blank."""
        if mission_type is not None:
            order = Mission.from_string(mission_type).order()
        else:
            order = Mission.randomize()
        await apiutils.response(ctx, str(order))


async def setup(bot):
    await bot.add_cog(Missions(bot))

from discord.ext import commands

from randomizer import DifficultyOrder, PlanetOrder, FactionOrder, Mission


class Missions(commands.Cog, name="Missions"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['enemy', 'enemies'])
    async def faction(self, ctx: commands.Context):
        """Receive an assignment for a faction to fight."""
        fo = FactionOrder()
        await ctx.message.reply(str(fo))

    @commands.command(aliases=['diff', 'level'])
    async def difficulty(self, ctx: commands.Context):
        """Receive an assignment for a difficulty to play at."""
        do = DifficultyOrder()
        await ctx.message.reply(str(do))

    @commands.command(aliases=['world', 'environ', 'environment'])
    async def planet(self, ctx: commands.Context):
        """Receive an assignment for planetary conditions to play under."""
        po = PlanetOrder()
        await ctx.message.reply(str(po))

    @commands.command()
    async def mission(self, ctx: commands.Context):
        """Receive a random faction, planet, or difficulty assignment."""
        ms = Mission()
        await ctx.message.reply(ms)


async def setup(bot):
    await bot.add_cog(Missions(bot))

from discord.ext import commands

class Missions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['enemy', 'enemies'])
    async def faction(self, ctx: commands.Context):
        fo = self.bot.randomizer.faction_order()
        await ctx.message.reply(fo)

    @commands.command(aliases=['diff', 'level'])
    async def difficulty(self, ctx: commands.Context):
        do = self.bot.randomizer.difficulty_order()
        await ctx.message.reply(do)

    @commands.command(aliases=['world', 'environ', 'environment'])
    async def planet(self, ctx: commands.Context):
        po = self.bot.randomizer.planet_order()
        await ctx.message.reply(po)

    @commands.command()
    async def mission(self, ctx: commands.Context):
        mt = self.bot.randomizer.mission()
        await ctx.message.reply(mt)


async def setup(bot):
    await bot.add_cog(Missions(bot))

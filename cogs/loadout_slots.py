from discord.ext import commands
from exceptions import StratagemSubtypeMismatch
from registration import PrimaryType, SecondaryType, ThrowableType, StratagemType, StratagemSubtype, ArmorWeight


class LoadoutSlots(commands.Cog, name="Loadout Slots"):
    def __init__(self, bot):
        self.bot = bot

    # noinspection type-hints
    @commands.command()
    async def primary(self, ctx: commands.Context, ptype: PrimaryType.from_string = None, count: int = 1):
        """Receive an assignment for a primary weapon from anywhere in the SEAF catalog."""
        msg = self.bot.randomizer.primary(ptype, count)
        await ctx.message.reply(msg)

    # noinspection type-hints
    @commands.command()
    async def secondary(self, ctx: commands.Context, stype: SecondaryType.from_string = None, count: int = 1):
        """Receive an assignment for a secondary weapon from anywhere in the SEAF catalog."""
        msg = self.bot.randomizer.secondary(stype, count)
        await ctx.message.reply(msg)

    # noinspection type-hints
    @commands.command()
    async def throwable(self, ctx: commands.Context, ttype: ThrowableType.from_string = None, count: int = 1):
        """Receive an assignment for a throwable weapon from anywhere in the SEAF catalog."""
        msg = self.bot.randomizer.throwable(ttype, count)
        await ctx.message.reply(msg)

    # noinspection type-hints
    @commands.command()
    async def stratagem(self, ctx: commands.Context,
                        stype: StratagemType.from_string = None,
                        sstype: StratagemSubtype.from_string = None,
                        count: int = 1):
        """Receive an assignment for a stratagem from anywhere in the SEAF catalog."""
        try:
            msg = self.bot.randomizer.stratagems(by_type=stype, by_subtype=sstype, n=count)
        except StratagemSubtypeMismatch as e:
            msg = str(e)
        await ctx.message.reply(msg)

    # noinspection type-hints
    @commands.command()
    async def booster(self, ctx: commands.Context, count: int = 1):
        """Receive an assignment for a booster from anywhere in the SEAF catalog."""
        msg = self.bot.randomizer.booster(n=count)
        await ctx.message.reply(msg)


    # noinspection type-hints
    @commands.command()
    async def armor(self, ctx: commands.Context, aw: ArmorWeight.from_string = None, count: int = 1):
        """Receive an assignment for an armor set from anywhere in the SEAF catalog."""
        msg = self.bot.randomizer.armor(by_weight=aw, n=count)
        await ctx.message.reply(msg)


async def setup(bot):
    await bot.add_cog(LoadoutSlots(bot))

from discord.ext import commands
from inventory import Source, SourceGroup
from tracking import RegistrationMode
from more_itertools import chunked

class Registration(commands.Cog, name="Registration"):
    def __init__(self, bot):
        self.bot = bot

    # noinspection type-hints
    @commands.command(aliases=['reg'])
    async def register(self, ctx: commands.Context, rmode: RegistrationMode.from_string, *sources):
        """register <rmode: Add | Set | Drop | Clear> [source, ...]
        - Add: Includes items from listed sources.
        - Set: Sets the contents of one's inventory to that of the listed sources.
        - Drop: Excludes items from listed sources.
        - Clear: Erases one's inventory, ignoring all source arguments.

        Use the sources command to view all available equipment sources."""
        sources = list(sources)
        Source.replace_shorthand(sources)
        sources = set(sources)
        msg = self.bot.inventory_database.register(str(ctx.message.author.id), sources, rmode=rmode)
        await ctx.message.reply(msg)

    # noinspection type-hints
    @commands.command(aliases=['viewsource', 'viewsources', 'listsources', 'listsource'])
    @commands.cooldown(1, 15)
    async def sources(self, ctx: commands.Context, source_group: SourceGroup.from_string = SourceGroup.All):
        """sources [source_group: All | Basic | SuperDestroyer | Campaign | Warbonds | Legendary | SuperStore | Premium | Etc]

        View a list of equipment sources for use with register. Pass a source group to narrow down the results."""
        parts = ['# Equipment Sources']
        if source_group is SourceGroup.All:
            for sources in chunked(source_group.sources(), n=4):
                part = []
                for src in sources:
                    part.append(f'`{src.name}`: {src.value}')
                parts.append(f'- {" | ".join(part)}')
        else:
            for src in source_group.sources():
                parts.append(f'- `{src.name}`: {src.value}')
        await ctx.message.reply('\n'.join(parts))

    # noinspection type-hints
    @commands.command(aliases=['des', 'desig', 'designation'])
    async def designations(self, ctx: commands.Context, rmode: RegistrationMode.from_string, *designations: str):
        """designations <rmode: Add | Drop> [item designation, ...]

        Add or drop individual items by designation, e.g. `SG-8` or `AX/AR-23`. Designations are space-separated.

        Enter designationless items (Eagle and Orbital stratagems) by removing spaces from their names, e.g. `EagleAirstrike`.
        You can leave off part of the name of it's distinct, e.g. `Orbital120` for `Orbital 120mm HE Barrage`."""
        if rmode in {RegistrationMode.Clear, RegistrationMode.Set}:
            await ctx.message.reply(f'Operation `{rmode.name}` not supported for this action. Use `Add` or `Drop` instead.')
            return

        msg = self.bot.inventory_database.register(designations=set(designations), rmode=rmode)
        await ctx.message.reply(msg)

    # noinspection type-hints
    @commands.command()
    async def name(self, ctx: commands.Context, rmode: RegistrationMode.from_string, *, name: str):
        """name <rmode: Add | Drop> <item name>

        Add or drop an item by name, e.g. `SG-8 Punisher` or `AX/AR-23 Guard Dog`. Only one name can be used at a time."""
        if rmode in {RegistrationMode.Clear, RegistrationMode.Set}:
            await ctx.message.reply(f'Operation `{rmode.name}` not supported for this action. Use `Add` or `Drop` instead.')
            return

        msg = self.bot.inventory_database.register(names=set(name), rmode=rmode)
        await ctx.message.reply(msg)


async def setup(bot):
    await bot.add_cog(Registration(bot))

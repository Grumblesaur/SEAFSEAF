from discord.ext import commands
from inventory import Source, SourceGroup
from registration import RegistrationMode

FakeCog = commands.Cog()

class UserRegistration(commands.Cog, name="User Registration"):
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
        for src in source_group.sources():
            parts.append(f'- `{src.name}`: {src.value}')
        await ctx.message.reply('\n'.join(parts))




async def setup(bot):
    await bot.add_cog(UserRegistration(bot))

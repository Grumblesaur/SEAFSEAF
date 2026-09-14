import discord
import more_itertools
from discord.ext import commands
import shutil
from pathlib import Path
from exceptions import UnknownEquipment, NoSourcesSpecified
from equipment import RegPreset
from inventory import Source
from registration import RegistrationMode

FakeCog = commands.Cog()

class UserRegistration(commands.Cog, name="User Registration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register(self, ctx: commands.Context):
        """Register your owned equipment."""
        if len(ctx.message.attachments) != 1:
            await ctx.message.reply("Helldiver! You must attach only your equipment worksheet."
                                    + f" Use {self.bot.prefix}catalog to get a blank template.")
            return
        file = ctx.message.attachments.pop()
        handle = str(ctx.message.author.id)
        await file.save(tmp := self.bot.temp_files / f'{handle}.ods')
        try:
            self.bot.registry.register(tmp, handle, self.bot.catalog)
        except UnknownEquipment as e:
            await ctx.message.reply(str(e))
        else:
            await ctx.message.reply("Helldiver, your equipment list has been registered. Ensure your registration is"
                                    " kept up to date as you are granted authorization for new equipment by"
                                    " executing this command again with an updated file.")
        finally:
            tmp.unlink()

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


    @commands.command(aliases=['viewsource', 'listsources', 'listsource'])
    @commands.cooldown(1, 15)
    async def sources(self, ctx: commands.Context, source_group):
        pass


async def setup(bot):
    await bot.add_cog(UserRegistration(bot))

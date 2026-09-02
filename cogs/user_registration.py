from collections import defaultdict

import discord
import more_itertools
from discord.ext import commands
import shutil
from pathlib import Path
from exceptions import UnknownEquipment, UnknownRegistrationPreset, NoSourcesSpecified
from registration import RegPreset, EqSource

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

    # noinspection type-hints,PyTypeHints
    @commands.command(aliases=["preset", "registerpreset"])
    async def regpreset(self, ctx: commands.Context, preset: RegPreset.from_string):
        handle = str(ctx.message.author.id)
        self.bot.registry.register_preset(handle, preset, self.bot.catalog)
        await ctx.message.reply("Helldiver, your equipment preset has been registered as your equipment list."
                                " Ensure your registration is kept up to date as you are authorized access to new"
                                " equipment by executing this command again with a more permissive preset.")

    @commands.command(aliases=['presets', 'viewpreset'])
    @commands.cooldown(1, 15)
    async def viewpresets(self, ctx: commands.Context):
        header = ("Any of the following **Presets** or their `abbreviations` may be used"
                  f" as an argument to the {self.bot.prefix}regpreset command. All associated"
                  " equipment will be registered.")

        preset_lines = [f'- **{ev.name}** `{ev.value}`: {ev.description()}' for ev in RegPreset]
        await ctx.message.reply(header + "\n" + '\n'.join(preset_lines))

    # noinspection type-hints,PyTypeHints
    @commands.command(aliases=['sources', 'registersources', 'regsource', 'registersource'])
    async def regsources(self, ctx: commands.Context, *sources: EqSource.from_string):
        handle = str(ctx.message.author.id)
        if not sources:
            raise NoSourcesSpecified("You must specify at least one equipment source with this command."
                                     f" Use `{self.bot.prefix}viewsources` for more information.")
        self.bot.registry.register_sources(handle, sources, self.bot.catalog)
        await ctx.message.reply("Helldiver, your authorized equipment sources have been registered. Ensure your"
                                " registration is kept up to date as you are authorized access to new equipment"
                                " by executing this command with more sources listed.")

    @commands.command(aliases=['viewsource', 'listsources', 'listsource'])
    @commands.cooldown(1, 15)
    async def viewsources(self, ctx: commands.Context):
        source_items = [f'`{ev.name}`: {ev.value}' for ev in EqSource]
        item_chunks = more_itertools.chunked(source_items, n=3)
        source_list = [f'- {" | ".join(chunk)}' for chunk in item_chunks]
        header = (f'The following is a list of equipment sources. These can be passed to the `{self.bot.prefix}regsources`'
                  ' command by their `abbreviation` (`RR` for "Redacted Regiment") or by a matching prefix of the target source (e.g. `Dem` for'
                  ' "Democratic Detonation").')

        await ctx.message.reply(header + '\n\n' + '\n'.join(source_list))

    @commands.command(aliases=["unreg"])
    async def unregister(self, ctx: commands.Context):
        """Unregister your equipment list."""
        self.bot.registry.unregister(str(ctx.message.author.id))
        await ctx.message.reply("Helldiver! Your equipment list has been wiped from our servers. Failure to re-register"
                                " in a timely fashion will have you scheduled for time in our reeducation camps.")

    @commands.command(aliases=["worksheet", "spreadsheet", "catalogue"])
    async def catalog(self, ctx: commands.Context):
        """Receive a copy of the equipment catalog."""
        src = Path(self.bot.ods_file)
        dst = self.bot.temp_files / f'{ctx.message.author.display_name}-equipment-catalog{src.suffix}'
        shutil.copy(src, dst)
        await ctx.message.reply("Helldiver! Here is your copy of the Super Earth Armed Forces Equipment Catalog."
                                + " Mark cells in the `Add` column to track the availability of equipment aboard your"
                                + f" super destroyer. When finished, reupload this file with the {self.bot.prefix}register"
                                + " command.\n\nIf your IT personnel are away at the reeducation camps,"
                                + " download this Super Earth-approved"
                                + " [software package](https://www.libreoffice.org/download/).",
                                file=discord.File(dst))
        dst.unlink()


async def setup(bot):
    await bot.add_cog(UserRegistration(bot))

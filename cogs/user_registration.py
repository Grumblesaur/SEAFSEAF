from discord.ext import commands
import shutil
from pathlib import Path
from exceptions import UnknownEquipment


FakeCog = commands.Cog()

class UserRegistration(commands.Cog):
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
                                    " kept up to date as your super destroyer is granted access to new equipment by"
                                    " executing this command again with an updated file.")
        finally:
            tmp.unlink()

    @commands.command()
    async def unregister(self, ctx: commands.Context):
        """Unregister your equipment list."""
        self.bot.registry.unregister(str(ctx.message.author.id))
        await ctx.message.reply("Helldiver! Your equipment list has been wiped from our servers. Failure to re-register"
                                " in a timely fashion will have you scheduled for time in our reeducation camps.")

    @commands.command()
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
                                + " [software package](https://www.libreoffice.org/download/).")
        dst.unlink()


async def setup(bot):
    await bot.add_cog(UserRegistration(bot))

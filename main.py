import os
import shutil
import discord
import configuration
from discord.ext import commands
from pathlib import Path

from exceptions import UnknownEquipment, StratagemSubtypeMismatch
from randomizer import Randomizer
from registration import PlayerRegistry, EquipmentCatalog, PrimaryType, SecondaryType, ThrowableType, StratagemType, \
    StratagemSubtype, ArmorWeight


class SEAFSEAF(commands.Bot):
    async def on_ready(self):
        print(f'Logged in as `{self.user}`.')
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(
                                       type=discord.ActivityType.custom,
                                       name="custom",
                                       state="Ready to randomize.",
                                   ))


config = configuration.load()
os.makedirs(temp_files := config['paths']['temp'], exist_ok=True)
os.makedirs(registry_files := config['paths']['registry'], exist_ok=True)
registry = PlayerRegistry(registry_files)
catalog = EquipmentCatalog(config['paths']['source'])
randomizer = Randomizer(registry, catalog)
intents = discord.Intents.default()
intents.message_content = True
prefix = config['config']['prefix']
bot = SEAFSEAF(intents=intents, command_prefix=prefix)


@bot.command()
async def register(ctx: commands.Context):
    """Register your owned equipment."""
    if len(ctx.message.attachments) != 1:
        await ctx.message.reply("Helldiver! You must attach only your equipment worksheet."
                                + f" Use {prefix}catalog to get a blank template.")
        return
    file = ctx.message.attachments.pop()
    handle = str(ctx.message.author.id)
    await file.save(tmp := temp_files / f'{handle}.ods')
    try:
        registry.register(tmp, handle, catalog)
    except UnknownEquipment as e:
        await ctx.message.reply(str(e))
    else:
        await ctx.message.reply("Helldiver, your equipment list has been registered. Ensure your registration is"
                                " kept up to date as your super destroyer is granted access to new equipment by"
                                " executing this command again with an updated file.")
    finally:
        tmp.unlink()

@bot.command()
async def unregister(ctx: commands.Context):
    """Unregister your equipment list."""
    registry.unregister(str(ctx.message.author.id))
    await ctx.message.reply("Helldiver! Your equipment list has been wiped from our servers. Failure to re-register"
                            " in a timely fashion will have you scheduled for time in our reeducation camps.")

@bot.command()
async def catalog(ctx: commands.Context):
    """Receive a copy of the equipment catalog."""
    src = Path(config['source'])
    dst = temp_files / f'{ctx.message.author.display_name}-equipment-catalog{src.suffix}'
    shutil.copy(src, dst)
    await ctx.message.reply("Helldiver! Here is your copy of the Super Earth Armed Forces Equipment Catalog."
                            + " Mark cells in the `Add` column to track the availability of equipment aboard your"
                            + f" super destroyer. When finished, reupload this file with the {prefix}register"
                            + " command.\n\nIf your IT personnel are away at the reeducation camps,"
                            + " download this Super Earth-approved"
                            + " [software package](https://www.libreoffice.org/download/).")
    dst.unlink()

# noinspection type-hints
@bot.command()
async def primary(ctx: commands.Context, ptype: PrimaryType.from_string = None, count: int = 1):
    """Receive an assignment for a primary weapon from anywhere in the SEAF catalog."""
    msg = randomizer.primary(ptype, count)
    await ctx.message.reply(msg)

# noinspection type-hints
@bot.command()
async def secondary(ctx: commands.Context, stype: SecondaryType.from_string = None, count: int = 1):
    """Receive an assignment for a secondary weapon from anywhere in the SEAF catalog."""
    msg = randomizer.secondary(stype, count)
    await ctx.message.reply(msg)

# noinspection type-hints
@bot.command()
async def throwable(ctx: commands.Context, ttype: ThrowableType.from_string = None, count: int = 1):
    """Receive an assignment for a throwable weapon from anywhere in the SEAF catalog."""
    msg = randomizer.throwable(ttype, count)
    await ctx.message.reply(msg)

# noinspection type-hints
@bot.command()
async def stratagem(ctx: commands.Context,
                    stype: StratagemType.from_string = None,
                    sstype: StratagemSubtype.from_string = None,
                    count: int = 1):
    """Receive an assignment for a stratagem from anywhere in the SEAF catalog."""
    try:
        msg = randomizer.stratagems(by_type=stype, by_subtype=sstype, n=count)
    except StratagemSubtypeMismatch as e:
        msg = str(e)
    await ctx.message.reply(msg)

# noinspection type-hints
@bot.command()
async def booster(ctx: commands.Context, count: int = 1):
    """Receive an assignment for a booster from anywhere in the SEAF catalog."""
    msg = randomizer.booster(n=count)
    await ctx.message.reply(msg)


# noinspection type-hints
@bot.command()
async def armor(ctx: commands.Context, aw: ArmorWeight.from_string = None, count: int = 1):
    """Receive an assignment for an armor set from anywhere in the SEAF catalog."""
    msg = randomizer.armor(by_weight=aw, n=count)
    await ctx.message.reply(msg)



def main():
    bot.run(config['auth']['token'])


if __name__ == '__main__':
    main()

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
    def __init__(self, *args, **kwargs):
        self.registry: PlayerRegistry = kwargs.pop('seaf_registry')
        self.catalog: EquipmentCatalog = kwargs.pop('seaf_catalog')
        self.randomizer: Randomizer = kwargs.pop('seaf_randomizer')
        self.config: dict = kwargs.pop('seaf_config')
        self.prefix = self.config['config']['prefix']
        self.temp_files = Path(self.config['paths']['temp'])
        self.registered = Path(self.config['paths']['registry'])
        os.makedirs(self.temp_files, exist_ok=True)
        os.makedirs(self.registered, exist_ok=True)
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'Logged in as `{self.user}`.')
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(
                                       type=discord.ActivityType.custom,
                                       name="custom",
                                       state="Ready to randomize.",
                                   ))

    async def register(self, ctx: commands.Context):
        """Register your owned equipment."""
        if len(ctx.message.attachments) != 1:
            await ctx.message.reply("Helldiver! You must attach only your equipment worksheet."
                                    + f" Use {self.prefix}catalog to get a blank template.")
            return
        file = ctx.message.attachments.pop()
        handle = str(ctx.message.author.id)
        await file.save(tmp := self.temp_files / f'{handle}.ods')
        try:
            self.registry.register(tmp, handle, self.catalog)
        except UnknownEquipment as e:
            await ctx.message.reply(str(e))
        else:
            await ctx.message.reply("Helldiver, your equipment list has been registered. Ensure your registration is"
                                    " kept up to date as your super destroyer is granted access to new equipment by"
                                    " executing this command again with an updated file.")
        finally:
            tmp.unlink()

    async def unregister(self, ctx: commands.Context):
        """Unregister your equipment list."""
        self.registry.unregister(str(ctx.message.author.id))
        await ctx.message.reply("Helldiver! Your equipment list has been wiped from our servers. Failure to re-register"
                                " in a timely fashion will have you scheduled for time in our reeducation camps.")

    async def catalog(self, ctx: commands.Context):
        """Receive a copy of the equipment catalog."""
        src = Path(self.config['source'])
        dst = self.temp_files / f'{ctx.message.author.display_name}-equipment-catalog{src.suffix}'
        shutil.copy(src, dst)
        await ctx.message.reply("Helldiver! Here is your copy of the Super Earth Armed Forces Equipment Catalog."
                                + " Mark cells in the `Add` column to track the availability of equipment aboard your"
                                + f" super destroyer. When finished, reupload this file with the {self.prefix}register"
                                + " command.\n\nIf your IT personnel are away at the reeducation camps,"
                                + " download this Super Earth-approved"
                                + " [software package](https://www.libreoffice.org/download/).")
        dst.unlink()

    # noinspection type-hints
    async def primary(self, ctx: commands.Context, ptype: PrimaryType.from_string = None, count: int = 1):
        """Receive an assignment for a primary weapon from anywhere in the SEAF catalog."""
        msg = self.randomizer.primary(ptype, count)
        await ctx.message.reply(msg)

    # noinspection type-hints
    async def secondary(self, ctx: commands.Context, stype: SecondaryType.from_string = None, count: int = 1):
        """Receive an assignment for a secondary weapon from anywhere in the SEAF catalog."""
        msg = self.randomizer.secondary(stype, count)
        await ctx.message.reply(msg)

    # noinspection type-hints
    async def throwable(self, ctx: commands.Context, ttype: ThrowableType.from_string = None, count: int = 1):
        """Receive an assignment for a throwable weapon from anywhere in the SEAF catalog."""
        msg = self.randomizer.throwable(ttype, count)
        await ctx.message.reply(msg)

    # noinspection type-hints
    async def stratagem(self, ctx: commands.Context,
                        stype: StratagemType.from_string = None,
                        sstype: StratagemSubtype.from_string = None,
                        count: int = 1):
        """Receive an assignment for a stratagem from anywhere in the SEAF catalog."""
        try:
            msg = self.randomizer.stratagems(by_type=stype, by_subtype=sstype, n=count)
        except StratagemSubtypeMismatch as e:
            msg = str(e)
        await ctx.message.reply(msg)

    # noinspection type-ihnts
    async def booster(self, ctx: commands.Context, count: int = 1):
        """Receive an assignment for a booster from anywhere in the SEAF catalog."""
        msg = self.randomizer.booster(n=count)
        await ctx.message.reply(msg)


    # noinspection type-hints
    async def armor(self, ctx: commands.Context, aw: ArmorWeight.from_string = None, count: int = 1):
        """Receive an assignment for an armor set from anywhere in the SEAF catalog."""
        msg = self.randomizer.armor(by_weight=aw, n=count)
        await ctx.message.reply(msg)






def main():
    config = configuration.load()
    registry = PlayerRegistry(ods_file := config['paths']['source'])
    catalog = EquipmentCatalog(ods_file)
    randomizer = Randomizer(registry, catalog)
    bot = SEAFSEAF(command_prefix=config['config']['prefix'],
                   seaf_registry=registry,
                   seaf_catalog=catalog,
                   seaf_config=config,
                   seaf_randomizer=randomizer,)
    bot.run(config['auth']['token'])

if __name__ == '__main__':
    main()

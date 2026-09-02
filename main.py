import os
from pathlib import Path

import discord
import configuration
from discord.ext import commands

from exceptions import RandomizerError
from randomizer import Randomizer
from registration import PlayerRegistry, EquipmentCatalog


class SEAFSEAF(commands.Bot):
    def __init__(self, config, *args, **kwargs):
        self.temp_files = Path(config['paths']['temp'])
        os.makedirs(self.temp_files, exist_ok=True)

        self.registry_files = config['paths']['registry']
        os.makedirs(self.registry_files, exist_ok=True)
        self.registry = PlayerRegistry(Path(self.registry_files))
        self.ods_file = config['paths']['source']
        self.catalog = EquipmentCatalog(self.ods_file)
        self.randomizer = Randomizer(self.registry, self.catalog)
        self.prefix = config['config']['prefix']
        self.config = config
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, command_prefix=self.prefix)

    def run(self, token: str | None = None, **kwargs):
        super().run(token or self.config['auth']['token'], **kwargs)

    async def setup_hook(self) -> None:
        for cog in os.listdir('./cogs'):
            if cog.startswith('__'):
                continue
            cog_path = Path(cog)
            cog_spec = f'cogs.{cog_path.name.removesuffix(cog_path.suffix)}'
            print(f'Loading {cog_spec} ...')
            await bot.load_extension(cog_spec)

    async def on_ready(self):
        print(f'Logged in as `{self.user}`.')
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(
                                       type=discord.ActivityType.custom,
                                       name="custom",
                                       state="Ready to randomize.",
                                   ))

    async def on_command_error(self, ctx: commands.Context, error):
        if not hasattr(error, 'original'):
            print('UNHANDLED/NO ORIGINAL:', error)
        elif isinstance(error.original, RandomizerError):
            await ctx.message.reply(str(error.original))
            print('HANDLED:', error.original)
        else:
            print('UNHANDLED:', error)


bot = SEAFSEAF(configuration.load())
bot.run()

import os
from pathlib import Path

import discord
import configuration
from discord.ext import commands

from tracking import InventoryTracker
from exceptions import RandomizerError


class SEAFSEAF(commands.Bot):
    def __init__(self, config, *_args, **_kwargs):
        self.temp_files = Path(config['paths']['temp'])
        os.makedirs(self.temp_files, exist_ok=True)

        self.registry_files = config['paths']['registry']
        os.makedirs(self.registry_files, exist_ok=True)
        self.inventory_database = InventoryTracker(Path(self.registry_files))
        self.prefix = config['config']['prefix']
        self.config = config
        intents = discord.Intents.default()
        # noinspection dunder-slots,unresolved-references
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
        print('Syncing command tree...')
        synced_commands = await self.tree.sync()
        print('Synced commands:', synced_commands)

    async def on_ready(self):
        print(f'Logged in as `{self.user}`.')
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(
                                       type=discord.ActivityType.custom,
                                       name="custom",
                                       state="Ready to randomize.",
                                   ))

    # noinspection method-overriding
    async def on_command_error(self, ctx: commands.Context, error):
        if not hasattr(error, 'original'):
            print('UNHANDLED/NO ORIGINAL:', error)
        elif isinstance(error.original, RandomizerError):
            await ctx.message.reply(str(error.original))
            print('HANDLED:', error.original)
        else:
            print('UNHANDLED:', error)
            raise error.original


bot = SEAFSEAF(configuration.load())
bot.run()

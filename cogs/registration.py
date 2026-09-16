from enum import Enum
from typing import Literal, Iterable

import discord
from discord import app_commands
from discord.ext import commands

import apiutils
from inventory import Source, SourceGroup
from tracking import RegistrationMode
from more_itertools import chunked

RMode = Literal['Add', 'Remove']

class Dropdown(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption], minimum: int = 1, maximum: int | None = None,
                 placeholder: str = 'Make your choices.'):
        super().__init__(placeholder=placeholder, min_values=minimum, max_values=(maximum or len(options)), options=options)


class EnumerationView(discord.ui.View):
    def __init__(self, enum_values: list[Enum], **kwargs):
        super().__init__(timeout=kwargs.get('timeout', 180))
        self.values = None
        options = [discord.SelectOption(label=ev.name, description=ev.value) for ev in enum_values]
        dd = Dropdown(options, **kwargs)
        async def select_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.values = dd.values
            self.stop()
        dd.callback = select_callback
        self.add_item(dd)


class Registration(commands.Cog, name="Registration"):
    def __init__(self, bot):
        self.bot = bot


    @staticmethod
    def _fetch_source_group(itx: discord.Interaction) -> SourceGroup:
        sg = SourceGroup.All
        match itx.command.name:
            case 'warbonds':
                sg = SourceGroup.Warbonds
            case 'legendary':
                sg = SourceGroup.Legendary
            case 'superstore':
                sg = SourceGroup.SuperStore
            case 'superdestroyer':
                sg = SourceGroup.SuperDestroyer
            case 'campaign':
                sg = SourceGroup.Campaign
            case 'basic':
                sg = SourceGroup.Basic
            case 'premium':
                sg = SourceGroup.Premium
            case 'other':
                sg = SourceGroup.Etc
        return sg

    async def source_core(self, itx: discord.Interaction, registration_mode: RMode):
        await itx.response.defer()
        rmode = RegistrationMode.from_string(registration_mode)
        sg = self._fetch_source_group(itx)
        view = EnumerationView(sg.sources())
        await itx.followup.send(rmode.sentence(), view=view)
        await view.wait()
        sources = [Source.from_string(v) for v in view.values]
        Source.replace_shorthand(sources)
        msg = self.bot.inventory_database.register(str(itx.user.id),
                                                   sources=set(sources),
                                                   rmode=rmode)
        await itx.followup.send(msg)

    @app_commands.command(name='warbonds', description='Select regular warbonds to add or remove equipment.')
    async def warbonds(self, itx: discord.Interaction, registration_mode: RMode):
        await self.source_core(itx, registration_mode)

    @app_commands.command(name="legendary", description='Select legendary warbonds to add or remove equipment.')
    async def legendary(self, itx: discord.Interaction, registration_mode: RMode):
        await self.source_core(itx, registration_mode)

    @app_commands.command(name='basic', description='Select basic equipment sources to add or remove equipment.')
    async def basic(self, itx: discord.Interaction, registration_mode: RMode):
        await self.source_core(itx, registration_mode)

    @app_commands.command(name='superdestroyer', description='Select super destroyer facilities to add or remove equipment.')
    async def superdestroyer(self, itx: discord.Interaction, registration_mode: RMode):
        await self.source_core(itx, registration_mode)

    @app_commands.command(name='superstore', description='Select super store pages to add or remove equipment.')
    async def superstore(self, itx: discord.Interaction, registration_mode: RMode):
        await self.source_core(itx, registration_mode)

    @app_commands.command(name='premium', description='Select premium content categories to add or remove equipment.')
    async def premium(self, itx: discord.Interaction, registration_mode: RMode):
        await self.source_core(itx, registration_mode)

    @app_commands.command(name='campaigns', description='Select campaigns to add or remove equipment.')
    async def campaigns(self, itx: discord.Interaction, registration_mode: RMode):
        await self.source_core(itx, registration_mode)

    @app_commands.command(name='other', description='Select from other equipment categories to add or remove equipment.')
    async def other(self, itx: discord.Interaction, registration_mode: RMode):
        await self.source_core(itx, registration_mode)

    @app_commands.command(name='clear-inventory', description='Unregister all your equipment.')
    async def clear(self, itx: discord.Interaction):
        msg = self.bot.inventory_database.register(str(itx.user.id), rmode=RegistrationMode.Clear)
        await itx.response.send_message(msg)

    # noinspection type-hints
    @commands.command(aliases=['reg'])
    async def register(self, ctx: commands.Context, rmode: RegistrationMode.from_string, *sources: Source.from_string):
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
        msg = '\n'.join(parts)
        if len(msg) > 2000:
            with open(path := (self.bot.temp_files / 'sources.md'), 'w', encoding='utf-8') as f:
                f.write(msg)
            await ctx.message.reply('The full list of sources is too long for Discord. This file shows all of them.'
                                    f' For in-chat viewing, try with a source group, e.g. `{self.bot.prefix}sources Warbonds`.',
                                    file=discord.File(path))
            return
        await ctx.message.reply(msg)

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

import discord
from discord import app_commands
from discord.ext import commands

import utils
import apiutils
from apiutils import Bool, parse_bool
from equipment import Squad, Piecemeal, Playstyle, DefaultDive
from inventory import Slot, Everything

SQUADMATE_DESC = "A member of this server to include in your squad."

class Loadout(commands.Cog, name='Loadout'):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(name='squadloadout', aliases=['loadout'])
    @app_commands.describe(squadmate1=SQUADMATE_DESC, squadmate2=SQUADMATE_DESC, squadmate3=SQUADMATE_DESC)
    async def squadloadout(self, ctx: commands.Context, squadmate1: discord.Member | None = None,
                      squadmate2: discord.Member | None = None, squadmate3: discord.Member | None = None):
        """Receive a loadout assignment. Mention up to three squadmates."""
        message_parts = []
        players = [ctx.message.author]
        players.extend(filter(None, [squadmate1, squadmate2, squadmate3]))
        handles_to_names = {str(user.id): user.display_name for user in players}
        auto_registered = []
        for handle in handles_to_names:
            if handle not in self.bot.inventory_database:
                self.bot.inventory_database.register(handle)
                auto_registered.append(handles_to_names[handle])
        if auto_registered:
            message_parts.append(f'{utils.format_series(auto_registered, backticks=False)}, you'
                                 ' have been auto-registered with stock equipment, Helldivers'
                                 f' Mobilize, and super destroyer stratagems. Use `{self.bot.prefix}register`'
                                 f' to update your equipment selection.')
        squad = Squad(handles_to_names, self.bot.inventory_database)
        message_parts.append(str(squad))
        await apiutils.response(ctx, '\n\n'.join(message_parts))

    async def _slots_core(self, ctx: commands.Context | discord.Interaction, handle: str, slots: set[Slot]):
        message_parts = []
        if handle not in self.bot.inventory_database:
            inventory = Everything
            message_parts.append('You are unregistered. Your equipment will be chosen from the whole SEAF catalog.'
                                 f' Use `register` to change this.')
        else:
            inventory = self.bot.inventory_database.fetch(handle)
        loadout = Piecemeal(inventory, slots)
        message_parts.append(str(loadout))
        await apiutils.response(ctx, '\n\n'.join(message_parts))

    @app_commands.command(name='soloslots', description="Randomize equipment for specific loadout slots.")
    @app_commands.describe(primary="Should a primary weapon be included?")
    async def soloslots(self, itx: discord.Interaction, primary: Bool = 'no', secondary: Bool = 'no',
                        throwable: Bool = 'no', stratagems: Bool = 'no', booster: Bool = 'no',
                        armor: Bool = 'no'):
        """Name one or more slots to construct a partial loadout."""
        slots = set()
        handle = str(itx.user.id)
        if parse_bool(primary):
            slots.add(Slot.Primary)
        if parse_bool(secondary):
            slots.add(Slot.Secondary)
        if parse_bool(throwable):
            slots.add(Slot.Throwable)
        if parse_bool(stratagems):
            slots.add(Slot.Stratagem)
        if parse_bool(booster):
            slots.add(Slot.Booster)
        if parse_bool(armor):
            slots.add(Slot.Armor)
        return await self._slots_core(itx, handle, slots)

    # noinspection type-hints
    @commands.command(name='slots', description="Randomize equipment for specific loadout slots.")
    async def slots(self, ctx: commands.Context, *slots: Slot.from_string):
        """Name one or more slots to construct a partial loadout."""
        handle = str(ctx.message.author.id)
        return await self._slots_core(ctx, handle, set(slots))


    @commands.hybrid_command(name='squadroles', aliases=['roles', 'role'])
    @app_commands.describe(squadmate1=SQUADMATE_DESC, squadmate2=SQUADMATE_DESC, squadmate3=SQUADMATE_DESC)
    async def squadroles(self, ctx: commands.Context, squadmate1: discord.Member | None = None,
                         squadmate2: discord.Member | None = None, squadmate3: discord.Member | None = None):
        """Receive role assignments to choose your own weapons by. Include up to three squadmates."""
        users = {ctx.message.author}
        users.update(filter(None, [squadmate1, squadmate2, squadmate3]))
        ps = Playstyle([u.display_name for u in users])
        await apiutils.response(ctx, str(ps))

    @commands.hybrid_command(name='defaultdivers', aliases=['defaultdiver', 'defaultdive', 'default', 'dd'])
    @app_commands.describe(squadmate1=SQUADMATE_DESC, squadmate2=SQUADMATE_DESC, squadmate3=SQUADMATE_DESC)
    async def defaultdivers(self, ctx: commands.Context, squadmate1: discord.Member | None = None,
                           squadmate2: discord.Member | None = None, squadmate3: discord.Member | None = None):
        """Receive default diver loadout assignments. Include up to three squadmates."""
        users = {ctx.message.author}
        users.update(filter(None, [squadmate1, squadmate2, squadmate3]))
        dd = DefaultDive([u.display_name for u in users])
        await apiutils.response(ctx, str(dd))


async def setup(bot):
    await bot.add_cog(Loadout(bot))

from discord.ext import commands

import utils
from eqrandomizer import Squad, Piecemeal, Playstyle
from inventory import Slot, Everything


class Loadout(commands.Cog, name='Loadout'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def loadout(self, ctx: commands.Context, *_mentions):
        """loadout [@mention, ...]

        Receive a loadout assignment. Mention up to three squadmates."""
        message_parts = []
        handles_to_names = {str(ctx.message.author.id): ctx.message.author.display_name}
        for count, mention in enumerate(ctx.message.mentions, start=1):
            if len(handles_to_names) >= 4:
                break
            handles_to_names[str(mention.id)] = mention.display_name
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
        await ctx.message.reply('\n\n'.join(message_parts))

    # noinspection type-hints
    @commands.command()
    async def slots(self, ctx: commands.Context, *slots: Slot.from_string):
        """slots <slot> [additional slots ...]
        Valid slots: Primary | Secondary | Throwable | Stratagem | Booster | Armor

        Name one or more slots to construct a partial loadout."""
        message_parts = []
        if (handle := str(ctx.message.author.id)) not in self.bot.inventory_database:
            inventory = Everything
            message_parts.append('You are unregistered. Your equipment will be chosen from the entire'
                                 f' SEAF catalog. Use `{self.bot.prefix}register` to change this.')
        else:
            inventory = self.bot.inventory_database.fetch(handle)
        loadout = Piecemeal(inventory, set(slots))
        message_parts.append(str(loadout))
        await ctx.message.reply('\n\n'.join(message_parts))

    @commands.command()
    async def squadroles(self, ctx: commands.Context, *_mentions):
        """squadroles [@mention, ...]

        Receive role assignments to choose your own weapons by. Mention up to three squadmates."""
        users = {ctx.message.author}
        users.update(ctx.message.mentions)
        ps = Playstyle([u.display_name for u in users])
        await ctx.message.reply(str(ps))

    @commands.command(aliases=['default', 'dd'])
    async def defaultdiver(self, ctx: commands.Context, *_mentions):
        """defaultdiver [@mention, ...]

        Receive default diver loadout assignments. Mention up to three squadmates."""



async def setup(bot):
    await bot.add_cog(Loadout(bot))

from discord.ext import commands

import utils
from eqrandomizer import Squad, Piecemeal
from equipment import Slot
from inventory import Everything


class Loadout(commands.Cog, name='Loadout'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def loadout(self, ctx: commands.Context, *_mentions):
        """Produce a full loadout for yourself, with up to three mentioned players."""
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
                                 f'to update your equipment selection.')
        squad = Squad(handles_to_names, self.bot.inventory_database)
        message_parts.append(str(squad))
        await ctx.message.reply('\n\n'.join(message_parts))

    # noinspection type-hints
    @commands.command()
    async def slots(self, ctx: commands.Context, *slots: Slot.from_string):
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


async def setup(bot):
    await bot.add_cog(Loadout(bot))

from discord.ext import commands


class FullLoadout(commands.Cog, name='Full Loadout'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def solo(self, ctx: commands.Context):
        if (user_handle := str(ctx.message.author.id)) not in self.bot.registry:
            await ctx.message.reply(f'No registration records found for you, {ctx.message.author.display_name}.'
                                    f" You must register your equipment to generate a personalized loadout."
                                    f" Use `{self.bot.prefix}register` for more information.")
            return
        loadout = self.bot.randomizer.solo_loadout(user_handle)
        msg = f'__{ctx.message.author.display_name}__, your loadout is:\n' + loadout[user_handle]
        await ctx.message.reply(msg)

    @commands.command()
    async def squad(self, ctx: commands.Context, *_mentions):
        user_handles = {str(ctx.message.author.id): ctx.message.author.display_name}
        for mention in ctx.message.mentions:
            user_handles[str(mention.id)] = mention.display_name
        loadouts = self.bot.randomizer.squad_loadout(list(user_handles.keys()))
        msg = [
            'Helldivers! These are your equipment assignments:',
        ]
        for user_handle, loadout_text in sorted(loadouts.items(), key=lambda p: p[1]):
            msg.append(f'__{user_handles[user_handle]}__:\n{loadout_text}')
        await ctx.message.reply('\n\n'.join(msg))



async def setup(bot):
    await bot.add_cog(FullLoadout(bot))

'''
MIT License

Copyright (c) 2021 Caio Alexandre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import discord
from discord.ext import commands

from utils.menus import Menu
from utils import checks
from utils import database


class ColoursTable(database.Table, table_name='colours'):
    user_id = database.Column(database.Integer(big=True), primary_key=True, index=True)
    colours = database.Column(database.Array(database.Integer(big=True)))
    fragments = database.Column(database.JSON, default="'{}'::jsonb")


class ColourConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        name = '「🎨」' + argument.capitalize()
        colour = discord.utils.get(ctx.guild.roles, name=name)

        if not colour:
            return None

        return colour if colour in ctx.cog.colours else None


class Colours(commands.Cog, name='Cores'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def has_color(self, member: discord.Member, colour: discord.Role):
        if any(r in self.bot.premium_roles for r in member.roles):
            return True

        query = 'SELECT colours FROM colours WHERE user_id = $1'
        fetch = await self.bot.manager.fetch_row(query, member.id)

        if not fetch:
            return False

        return colour.id in fetch['colours']

    @commands.Cog.listener()
    async def on_first_ready(self):
        cosmic = self.bot.cosmic
        self.colours = [r for r in cosmic.roles if r.name.startswith('「🎨」')]

    @commands.group(aliases=['color'], invoke_without_command=True)
    async def colour(self, ctx: commands.Context, *, colour: ColourConverter):
        await self.colour_add(ctx, colour=colour)

    @colour.command(name='add')
    async def colour_add(self, ctx: commands.Context, *, colour: ColourConverter):
        if not await self.has_color(ctx.author, colour):
            return await ctx.reply('Você não possui esta cor.')

        if not colour:
            return await ctx.reply('Cor não encontrada.')

        if colour in ctx.author.roles:
            return await ctx.reply('Você já está com esta cor.')

        to_remove = []
        for role in ctx.author.roles:
            if role in self.colours:
                to_remove.append(role)

        await ctx.author.remove_roles(*to_remove, reason='Removendo cores anteriores')
        await ctx.author.add_roles(colour, reason='Adicionando uma cor')

        message = f'Cor {colour.mention} adicionada.'
        if to_remove:
            mentions = ', '.join([role.mention for role in to_remove])
            message += f'\nAs seguintes cores foram removidas: {mentions}'

        await ctx.reply(message)

    @colour.command(name='list')
    async def colour_list(self, ctx: commands.Context):
        colours = [role.mention for role in self.colours]

        menu = Menu(colours, per_page=12)
        await menu.start(ctx)

    @commands.command(aliases=['colors'])
    async def colours(self, ctx: commands.Context):
        await self.colour_list(ctx)


def setup(bot: commands.Bot):
    bot.add_cog(Colours(bot))

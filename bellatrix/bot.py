import os
import re
import logging

import discord
from discord.ext import commands

from utils.context import Context


# TODO: Adicionar uma documentação decente.

COSMIC_GUILD_ID = 795017809402921041
STAFF_ROLE_ID = 795026574453899304

all_extensions = []
for root, _, files in os.walk('extensions'):
    for file in files:
        path = os.path.join(root, file)

        if not os.path.isfile(path):
            continue

        path, ext = os.path.splitext(path)
        if ext != '.py':
            continue

        # regex é um ser muito estranho.
        extension = re.sub('\\\\|\/', '.', path)
        all_extensions.append(extension)

class Bellatrix(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='b/', intents=discord.Intents.all())
        self.logger = logging.getLogger('bellatrix')
        
    async def on_ready(self):
        self.cosmic = self.get_guild(COSMIC_GUILD_ID)
        self.staff_role = self.cosmic.get_role(STAFF_ROLE_ID)

        for ext in all_extensions:
            try:
                self.load_extension(ext)
            except Exception:
                self.logger.exception(f'Extension \'{ext}\' could not be loaded.')
            else:
                self.logger.info(f'Extension \'{ext}\' has been loaded.')

        print(f'Online com {len(self.users)} usuários')

    async def on_message(self, message: discord.Message):
        if not isinstance(message.author, discord.Member):
            return

        if message.author.bot:
            return

        if not message.guild:
            return

        await self.process_commands(message)

    async def process_commands(self, message: discord.Message):
        ctx = await self.get_context(message, cls=Context)
        await self.invoke(ctx)
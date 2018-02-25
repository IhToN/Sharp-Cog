import discord
from discord.ext import commands
import json

class DegoosSpigot:
    """Degoos Spigot Verifier"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verify(self):
        """Verify the user and his plugins!"""

        #Your code will go here
        await self.bot.say("I can do stuff!")

def setup(bot):
    bot.add_cog(DegoosSpigot(bot))


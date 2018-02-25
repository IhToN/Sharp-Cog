import discord
from discord.ext import commands
import json
import requests

class DegoosSpigot:
    """Degoos Spigot Verifier"""

    def __init__(self, bot):
        self.bot = bot
        self.url = "http://vps168498.ovh.net:9080/SpigotBuyerCheck-1.0-SNAPSHOT/api/checkbuyer?user_id="

    @commands.command()
    async def verify(self):
        """Verify the user and his plugins!"""
        response = requests.get(self.url + '31163')
        data = response.json()

        #Your code will go here
        await self.bot.say(data)

def setup(bot):
    bot.add_cog(DegoosSpigot(bot))


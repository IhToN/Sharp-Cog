import discord
from discord.ext import commands
import json
import requests

class DegoosSpigot:
    """Degoos Spigot Verifier"""

    def __init__(self, bot):
        self.bot = bot
        self.url = "http://vps168498.ovh.net:9080/SpigotBuyerCheck-1.0-SNAPSHOT/api/checkbuyer?"

    @commands.command()
    async def checkbuyer(self, type, userinfo):
        """Verify the user and his plugins!"""
        node = ""
        if type == "id":
            node = "user_id=" + userinfo
        elif type == "name":
            node = "username=" + userinfo
        else:
            node = None

        if node:
            response = requests.get(self.url + node)
            data = response.json()
        else:
            data = "You can only search by 'id' or 'name':\n!verify name IhToN"

        #Your code will go here
        await self.bot.say(data)

    @commands.command()
    async def punch(self, user: discord.Member):
        """I will puch anyone! >.<"""

        # Your code will go here
        await self.bot.say("ONE PUNCH! And " + user.mention + " is out! ლ(ಠ益ಠლ)")


def setup(bot):
    bot.add_cog(DegoosSpigot(bot))


import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
import json
import os
import requests

folder = os.path.join('data', 'degoos')


class DegoosSpigot:
    """Degoos Spigot Verifier"""

    def __init__(self, bot):
        self.bot = bot
        self.url = "http://vps168498.ovh.net:9080/SpigotBuyerCheck-1.0-SNAPSHOT/api/checkbuyer?"
        self.verified_users = dataIO.load_json(os.path.join(folder, "verified_users.json"))

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

        # Your code will go here
        await self.bot.say(data)

    @commands.command()
    async def punch(self, user: discord.Member):
        """I will puch anyone! >.<"""

        # Your code will go here
        await self.bot.say("ONE PUNCH! And " + user.mention + " is out! ლ(ಠ益ಠლ)")

    @commands.group(no_pm=False, invoke_without_command=True, pass_context=True)
    async def verify(self, ctx, *, message):
        await self.bot.say('Verify command')

    @verify.command(pass_context=True)
    @checks.is_owner()
    async def auth(self, ctx, authcode: str):
        """Confirm authorization code"""

        await self.bot.say("Authcode introducido: " + authcode)
        await self.bot.say("Usuario a comprobar: " + str(ctx.message.author))
        # self.settings["TOGGLE"] = not self.settings["TOGGLE"]
        # if self.settings["TOGGLE"]:
        #     await self.bot.say("I will reply on mention.")
        # else:
        #     await self.bot.say("I won't reply on mention anymore.")
        # dataIO.save_json("data/apiai/settings.json", self.settings)

def check_folders():
    if not os.path.exists(folder):
        print("Creating " + folder + " folder...")
        os.makedirs(folder)


def check_files():
    f = os.path.join(folder, "verified_users.json")
    data = {"users": []}
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, data)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(DegoosSpigot(bot))

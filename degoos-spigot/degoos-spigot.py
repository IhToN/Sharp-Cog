import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
import json
import os
import uuid
import requests

folder = os.path.join('data', 'degoos')


class DegoosSpigot:
    """Degoos Spigot Verifier"""

    def __init__(self, bot):
        self.bot = bot
        self.url = "http://vps168498.ovh.net:9080/SpigotBuyerCheck-1.0-SNAPSHOT/api/"
        self.verified_users = dataIO.load_json(os.path.join(folder, "verified_users.json"))

    @commands.group(no_pm=False, invoke_without_command=True, pass_context=True)
    async def checkbuyer(self, type, userinfo):
        """Verify the user and his plugins!"""

        await self.bot.say("You can only search by 'id', 'name' or 'user':\n!verify name IhToN")

    @checkbuyer.command(pass_context=True)
    async def id(self, ctx, userid):
        await self.bot.say(requests.get(self.url + "checkbuyer?user_id=" + userid).json())

    @checkbuyer.command(pass_context=True)
    async def name(self, ctx, username):
        await self.bot.say(requests.get(self.url + "checkbuyer?username=" + username).json())

    @commands.command()
    async def punch(self, user: discord.Member):
        """I will puch anyone! >.<"""

        # Your code will go here
        await self.bot.say("ONE PUNCH! And " + user.mention + " is out! ლ(ಠ益ಠლ)")

    @commands.group(no_pm=False, invoke_without_command=True, pass_context=True)
    async def verify(self, ctx, *, your_spigot_account):
        randomcode = str(uuid.uuid4())
        authorid = ctx.message.author.id
        data = requests.get(self.url + "checkbuyer?username=" + your_spigot_account).json()

        await self.bot.say('JSON Parsed: ' + str(data))
        if 'bought' in data and 'spigotid' in data:
            if len(data['bought']) > 0 and data['spigotid'] != -1:
                if authorid in self.verified_users["users"]:
                    if self.verified_users["users"][authorid]["verified"]:
                        await self.bot.say('You are already verified!')
                else:
                    # todo: send message to spigot user
                    request = requests.get(
                        self.url + "sendauth?username=" + your_spigot_account + "&authcode=" + randomcode + "&hash_key=*degoos%team*")
                    await self.bot.say('Data requested: ' + str(request))
                    data = request.json()
                    if 'messageSent' in data:
                        if data['messageSent']:
                            self.verified_users["users"][authorid] = {"spigotid": data["spigotid"],
                                                                      "authcode": randomcode, "verified": False}
                            await self.bot.say(
                                'We\'ve sent you a Private Message in Spigot with your Authorization Code. Check it!')
                        else:
                            await self.bot.say('Something went wrong. Please try again later.')
                    else:
                        await self.bot.say('Something went wrong. Please try again later.')

                await self.bot.say('Random UUID: ' + str(self.verified_users["users"]))
            else:
                await self.bot.say('You haven\'t bought any of our plugins.')
        else:
            await self.bot.say('Our verification server is busy, please try again later.')

    @verify.command(pass_context=True)
    async def auth(self, ctx, authcode: str):
        """Confirm authorization code"""
        authorid = ctx.message.author.id

        if authorid in self.verified_users["users"]:
            if self.verified_users["users"][authorid]["verified"]:
                await self.bot.say('You are already verified!')
            elif self.verified_users["users"][authorid]["authcode"] == authcode:
                self.verified_users["users"][authorid]["verified"] = True
                await self.bot.say('You\'ve been verified correctly :D')
            else:
                await self.bot.say('That\'s not your authorization code!')
        else:
            await self.bot.say(
                'We couln\'t find your user in our verification list. Have you used the !verify YourUser command?')

        await self.bot.say("Authcode introducido: " + authcode)
        await self.bot.say("Usuario a comprobar: " + ctx.message.author.id)
        # self.settings["TOGGLE"] = not self.settings["TOGGLE"]
        # if self.settings["TOGGLE"]:
        #     await self.bot.say("I will reply on mention.")
        # else:
        #     await self.bot.say("I won't reply on mention anymore.")
        # dataIO.save_json("data/apiai/settings.json", self.settings)

    @verify.command(pass_context=True)
    @checks.is_owner()
    async def refresh(self, ctx):
        """Confirm authorization code"""
        self.verified_users = {"users": {}}
        await self.bot.say("Verification list cleaned.")


def check_folders():
    if not os.path.exists(folder):
        print("Creating " + folder + " folder...")
        os.makedirs(folder)


def check_files():
    f = os.path.join(folder, "verified_users.json")
    os.remove(f)
    data = {"users": {}}
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, data)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(DegoosSpigot(bot))

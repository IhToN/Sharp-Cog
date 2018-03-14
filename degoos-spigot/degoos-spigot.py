import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
import os
import uuid
import requests

folder = os.path.join('data', 'degoos')
verified_role = 'Verified'


class DegoosSpigot:
    """Degoos Spigot Verifier"""

    def __init__(self, bot):
        self.bot = bot
        self.url = "http://vps168498.ovh.net:9080/SpigotBuyerCheck-1.0-SNAPSHOT/api/"
        self.verified_users = dataIO.load_json(os.path.join(folder, "verified_users.json"))
        print('Verified users loaded: ' + str(len(self.verified_users)))

    @commands.group(no_pm=False, invoke_without_command=True, pass_context=True)
    async def checkbuyer(self, ctx):
        """Verify the user and his plugins!"""

        await self.bot.send_message(ctx.message.author, "You can only search by 'id', 'name' or 'user':\n!verify name IhToN")

    @checkbuyer.command(pass_context=True)
    async def id(self, ctx, userid):
        await self.bot.send_message(ctx.message.author, requests.get(self.url + "checkbuyer?user_id=" + userid).json())

    @checkbuyer.command(pass_context=True)
    async def name(self, ctx, username):
        await self.bot.send_message(ctx.message.author, requests.get(self.url + "checkbuyer?username=" + username).json())

    @checkbuyer.command(pass_context=True)
    async def mention(self, ctx, discord_user: discord.User):
        discordid = discord_user.id
        if discordid in self.verified_users["users"]:
            if self.verified_users["users"][discordid]["verified"]:
                spigotid = self.verified_users["users"][discordid]["spigotid"]
                data = requests.get(self.url + "checkbuyer?user_id=" + str(spigotid)).json()
                await self.bot.send_message(ctx.message.author, str(data))
            else:
                await self.bot.send_message(ctx.message.author, str(discord_user) + " is not verified yet.")
        else:
            await self.bot.send_message(ctx.message.author, str(discord_user) + " has not registered in the system yet.")

    @commands.command()
    async def punch(self, user: discord.Member):
        """I will puch anyone! >.<"""
        await self.bot.say("ONE PUNCH! And " + user.mention + " is out! ლ(ಠ益ಠლ)")

    @commands.group(invoke_without_command=True, no_pm=True, pass_context=True)
    async def verify(self, ctx, *, your_spigot_account):
        await self.bot.delete_message(ctx.message)

        authorid = ctx.message.author.id
        if authorid in self.verified_users["users"]:
            if self.verified_users["users"][authorid]["verified"]:
                await self.bot.send_message(ctx.message.author, 'You are already verified!')
            else:
                await self.bot.send_message(ctx.message.author, 'Check your Spigot Inbox or ask and Admin :wink:')
        else:
            randomcode = str(uuid.uuid4())
            data = requests.get(self.url + "checkbuyer?username=" + your_spigot_account).json()

            if 'bought' in data and 'spigotid' in data:
                if len(data['bought']) > 0 and data['spigotid'] != -1:
                    request = requests.get(
                        self.url + "sendauth?username=" + your_spigot_account + "&auth_code=" + randomcode + "&hash_key=deg-tem-159")
                    msg_data = request.json()
                    if 'messageSent' in msg_data:
                        if msg_data['messageSent']:
                            self.verified_users["users"][authorid] = {"spigotid": data["spigotid"],
                                                                      "authcode": randomcode, "verified": False}
                            await self.bot.send_message(ctx.message.author,
                                'We\'ve sent you a Private Message in Spigot with your Authorization Code. Check it!')
                        else:
                            await self.bot.send_message(ctx.message.author, 'Something went wrong. Please try again later.')
                    else:
                        await self.bot.send_message(ctx.message.author, 'Something went wrong. Please try again later.')
                else:
                    await self.bot.send_message(ctx.message.author, 'You haven\'t bought any of our plugins.')
            else:
                await self.bot.send_message(ctx.message.author, 'Our verification server is busy, please try again later.')

    @verify.command(no_pm=True, pass_context=True)
    async def auth(self, ctx, authcode: str):
        print('Borramos mensaje')
        #await self.bot.delete_message(ctx.message)
        """Confirm authorization code"""
        author = ctx.message.author
        authorid = ctx.message.author.id

        await self.bot.send_message(ctx.message.author, 'We are going to check your verification status, give us a moment, please.')

        print('Comprobamos usuario en verify')
        if authorid in self.verified_users["users"]:
            print('Usuario está en la lista de espera')
            if self.verified_users["users"][authorid]["verified"]:
                print('Usuario está verificado')
                await self.bot.send_message(ctx.message.author, 'You are already verified!')
            elif self.verified_users["users"][authorid]["authcode"] == authcode:
                print('Authcode correcto')
                self.verified_users["users"][authorid]["verified"] = True

                roles = False
                try:
                    print('Cargamos roles')
                    roles = [role for role in ctx.message.server.roles if not role.is_everyone]
                    print('Server roles: ' + str(roles))
                except AttributeError:
                    print("This server has no roles... what even?\n")

                if roles:
                    print('Hay roles')
                    role = discord.utils.get(roles, name=verified_role)
                    if role is not None:
                        print('Se ha encontrado el rol: ' + str(role))
                        await self.bot.add_roles(author, role)
                        await self.bot.send_message(ctx.message.author, 'We\'ve updated your role to: ' + str(role))
                        print('We\'ve updated your role to: ' + str(role))

                f = os.path.join(folder, "verified_users.json")
                dataIO.save_json(f, self.verified_users)

                print('Verificado el usuario y guardado')
                await self.bot.send_message(ctx.message.author, 'You\'ve been verified correctly :D')
            else:
                print('Authcode incorrecto')
                await self.bot.send_message(ctx.message.author, 'That\'s not your authorization code!')
        else:
            await self.bot.send_message(ctx.message.author,
                'We couln\'t find your user in our verification list. Have you used the !verify YourUser command?')

    @verify.command(no_pm=True, pass_context=True)
    @checks.is_owner()
    async def reload(self, ctx):
        await self.bot.delete_message(ctx.message)
        """Confirm authorization code"""
        self.verified_users = dataIO.load_json(os.path.join(folder, "verified_users.json"))
        await self.bot.send_message(ctx.message.author, "Verification list reloaded.")
        await self.bot.send_message(ctx.message.author, str(self.verified_users))


def check_folders():
    if not os.path.exists(folder):
        print("Creating " + folder + " folder...")
        os.makedirs(folder)


def check_files():
    f = os.path.join(folder, "verified_users.json")
    data = {"users": {}}
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, data)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(DegoosSpigot(bot))

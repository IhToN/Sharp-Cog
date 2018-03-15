import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
import os
import uuid
import requests
import json

folder = os.path.join('data', 'degoos')
verified_role = 'Verified'


class DegoosSpigot:
    """Degoos Spigot Verifier"""

    def __init__(self, bot):
        self.bot = bot
        self.url = "http://vps168498.ovh.net:9080/SpigotBuyerCheck-1.0-SNAPSHOT/api/"
        self.verified_users = dataIO.load_json(os.path.join(folder, "verified_users.json"))
        print('Verified users loaded: ' + str(len(self.verified_users['users'])))

    @commands.group(name='checkbuyer', aliases=['cb'], no_pm=False, invoke_without_command=True, pass_context=True)
    @checks.admin_or_permissions(view_audit_logs=True)
    async def checkbuyer(self, ctx):
        """Verify the user and his plugins!"""

        await self.bot.send_message(ctx.message.author,
                                    "You can only search by 'id', 'name' or 'user':\n!checkbuyer name IhToN")

    @checkbuyer.command(name='id', pass_context=True)
    @checks.admin_or_permissions(view_audit_logs=True)
    async def id(self, ctx, userid):
        if ctx.message.server:
            await self.bot.delete_message(ctx.message)

        js_data = requests.get(self.url + "checkbuyer?user_id=" + userid).json()

        message = '```javascript' + '\n'
        message += 'User Data: \n'
        message += json.dumps(js_data, sort_keys=True, indent=4)
        message += '```'
        await self.bot.send_message(ctx.message.author, message)

    @checkbuyer.command(name='name', pass_context=True)
    @checks.admin_or_permissions(view_audit_logs=True)
    async def name(self, ctx, username):
        if ctx.message.server:
            await self.bot.delete_message(ctx.message)

        js_data = requests.get(self.url + "checkbuyer?username=" + username).json()

        message = '```javascript' + '\n'
        message += 'User Data: \n'
        message += json.dumps(js_data, sort_keys=True, indent=4)
        message += '```'
        await self.bot.send_message(ctx.message.author, message)

    @checkbuyer.command(name='mention', aliases=['user'], pass_context=True)
    @checks.admin_or_permissions(view_audit_logs=True)
    async def mention(self, ctx, discord_user: discord.User):
        if ctx.message.server:
            await self.bot.delete_message(ctx.message)

        discordid = discord_user.id
        if discordid in self.verified_users["users"]:
            if self.verified_users["users"][discordid]["verified"]:
                spigotid = self.verified_users["users"][discordid]["spigotid"]
                js_data = requests.get(self.url + "checkbuyer?user_id=" + str(spigotid)).json()

                message = '```javascript' + '\n'
                message += 'User Data: \n'
                message += json.dumps(js_data, sort_keys=True, indent=4)
                message += '```'
                await self.bot.send_message(ctx.message.author, message)
            else:
                await self.bot.send_message(ctx.message.author, str(discord_user) + " is not verified yet.")
        else:
            await self.bot.send_message(ctx.message.author,
                                        str(discord_user) + " has not registered in the system yet.")

    @checkbuyer.command(name='all', pass_context=True)
    @checks.admin_or_permissions(view_audit_logs=True)
    async def _all(self, ctx):
        if ctx.message.server:
            await self.bot.delete_message(ctx.message)

        message = '```javascript' + '\n'
        message += 'Verified Discord Users: \n'
        for key, value in self.verified_users["users"].items():
            server = ctx.message.server
            user_id = key
            if server:
                user_id = server.get_member(int(key))
            message += '· ' + user_id + '\n'
        message += '```'
        await self.bot.send_message(ctx.message.author, message)

    @checkbuyer.command(name='json', pass_context=True)
    @checks.admin_or_permissions(view_audit_logs=True)
    async def _json(self, ctx):
        if ctx.message.server:
            await self.bot.delete_message(ctx.message)

        message = '```javascript' + '\n'
        message += 'Verified Users: \n'
        message += json.dumps(self.verified_users, sort_keys=True, indent=4)
        message += '```'
        await self.bot.send_message(ctx.message.author, message)

    @commands.command()
    async def punch(self, user: discord.Member):
        """I will puch anyone! >.<"""
        await self.bot.say("ONE PUNCH! And " + user.mention + " is out! ლ(ಠ益ಠლ)")

    @commands.group(name='verify', invoke_without_command=True, no_pm=True, pass_context=True)
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
                            await self.bot.send_message(ctx.message.author,
                                                        'Something went wrong. Please try again later.')
                    else:
                        await self.bot.send_message(ctx.message.author, 'Something went wrong. Please try again later.')
                else:
                    await self.bot.send_message(ctx.message.author, 'You haven\'t bought any of our plugins.')
            else:
                await self.bot.send_message(ctx.message.author,
                                            'Our verification server is busy, please try again later.')

    @verify.command(name='auth', no_pm=True, pass_context=True)
    async def auth(self, ctx, authcode: str):
        await self.bot.delete_message(ctx.message)
        """Confirm authorization code"""
        author = ctx.message.author
        authorid = ctx.message.author.id

        await self.bot.send_message(ctx.message.author,
                                    'We are going to check your verification status, give us a moment, please.')

        if authorid in self.verified_users["users"]:
            if self.verified_users["users"][authorid]["verified"]:
                await self.bot.send_message(ctx.message.author, 'You are already verified!')
            elif self.verified_users["users"][authorid]["authcode"] == authcode:
                self.verified_users["users"][authorid]["verified"] = True

                roles = False
                try:
                    roles = [role for role in ctx.message.server.roles if not role.is_everyone]
                except AttributeError:
                    print("This server has no roles... what even?\n")

                if roles:
                    role = discord.utils.get(roles, name=verified_role)
                    if role is not None:
                        await self.bot.add_roles(author, role)
                        await self.bot.send_message(ctx.message.author, 'We\'ve updated your role to: ' + str(role))

                f = os.path.join(folder, "verified_users.json")
                dataIO.save_json(f, self.verified_users)

                await self.bot.send_message(ctx.message.author, 'You\'ve been verified correctly :D')
            else:
                await self.bot.send_message(ctx.message.author, 'That\'s not your authorization code!')
        else:
            await self.bot.send_message(ctx.message.author,
                                        'We couln\'t find your user in our verification list. Have you used the !verify YourUser command?')

    @verify.command(name='reload', no_pm=True, pass_context=True)
    @checks.is_owner()
    async def reload(self, ctx):
        await self.bot.delete_message(ctx.message)
        """Confirm authorization code"""
        self.verified_users = dataIO.load_json(os.path.join(folder, "verified_users.json"))

        message = '```javascript' + '\n'
        message += json.dumps(self.verified_users, sort_keys=True, indent=4)
        message += '```'
        await self.bot.send_message(ctx.message.author, "Verification list reloaded!")
        await self.bot.send_message(ctx.message.author, message)


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

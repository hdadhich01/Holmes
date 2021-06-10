from datetime import datetime
import discord
from discord.ext import commands
from discord.ext.commands import BotMissingPermissions, CommandOnCooldown, CommandNotFound, MissingPermissions
import humanize
import json
from replit import db

class Events(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.Cog.listener()
  async def on_command_completion(self, ctx):
    print(f"✅　{ctx.command.name.upper()} Command")

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    if isinstance(error, BotMissingPermissions):
      permission = error.missing_perms[0].replace("_", " ").title()
      await ctx.send(f"{self.bot.errorEmoji} This command requires me to have the `{permission}` permission")
    elif isinstance(error, MissingPermissions):
      permission = error.missing_perms[0].replace("_", " ").title()
      await ctx.send(f"{self.bot.errorEmoji} This command requires you to have the `{permission}` permission")
    elif not isinstance(error, CommandNotFound):
      if isinstance(error, CommandOnCooldown):
        await ctx.send(f"{self.bot.errorEmoji} You are on cooldown for `{round(error.retry_after, 2)}` seconds")
      else:
        await ctx.send(f"{self.bot.errorEmoji} An error occurred\n```{error}```")
        if ctx.command:
          ctx.command.reset_cooldown(ctx)
    else:
      await ctx.send(f"{self.bot.errorEmoji} An error occurred\n```{error}```")
    print(f"❌‎‎‎　ERROR ({error})")
  
  @commands.Cog.listener()
  async def on_guild_join(self, guild):
    with open("prefixes.json", "r") as file:
      prefixes = json.load(file)
    prefixes[str(guild.id)] = "h!"
    with open("prefixes.json", "w") as file:
      json.dump(prefixes, file, indent = 2)
    await self.bot.change_presence(status = discord.Status.online, activity = discord.Activity(type = discord.ActivityType.watching, name = f"{self.bot.memberCount()} users • @{self.bot.user.name}"))
    try:
      channel = discord.utils.get(guild.channels, name = "general")
      channel = discord.utils.get(guild.channels, name = "lobby") if not channel else channel
      if channel:
        embed = discord.Embed(title = ":spy: Holmes", description = "Hello there! My prefix is `h!`\nCheck out my commands with `h!help`\nYou can change my prefix with `h!prefix <prefix>`", color = 0x9c7a61, timestamp = datetime.utcnow())
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        embed.set_footer(text = f"{guild.name}", icon_url = guild.icon_url)
        await channel.send(content = None, embed = embed)
    except:
      pass
  
  @commands.Cog.listener()
  async def on_guild_remove(self, guild):
    with open("prefixes.json", "r") as file:
      prefixes = json.load(file)
    del prefixes[str(guild.id)]
    with open("prefixes.json", "w") as file:
      json.dump(prefixes, file, indent = 2)
    await self.bot.change_presence(status = discord.Status.online, activity = discord.Activity(type = discord.ActivityType.watching, name = f"{self.bot.memberCount()} users • @{self.bot.user.name}"))
  
  @commands.Cog.listener()
  async def on_message(self, message):
    # bot mention
    if self.bot.user.mentioned_in(message):
      prefix = "h!"
      if message.guild:
        with open("prefixes.json", "r") as file:
          prefixes = json.load(file)
        prefix = prefixes[str(message.guild.id)]
      await message.channel.send(f":spy: Hello there! My prefix is `{prefix.replace(' ', '')}` (usage: `{prefix}help`)")
    
    # afk stuff
    if message.guild:
      if message.guild.me.guild_permissions.manage_nicknames:
        # afk user returns
        ctx = await self.bot.get_context(message)
        if not str(ctx.command) == "afk":
          if str(message.author.id) in db:
            del db[str(message.author.id)]
            if not message.author.guild_permissions.administrator:
              await message.author.edit(nick = message.author.display_name[6:])
            await message.reply(f":wave: Welcome back, I removed your AFK", delete_after = 3)
            print("✅　AFK RETURN Event")

        # afk user mentioned
        if message.mentions:
          for i in message.mentions:
            if str(i.id) in db:
              time = datetime.now() - datetime.strptime(db[str(i.id)][0], '%Y-%m-%d %H:%M:%S.%f')
              nickname = i.display_name[6:] if not i.guild_permissions.administrator else i.display_name
              # w/o message
              if not db[str(i.id)][1]:
                await message.channel.send(f":spy: `{nickname}` is AFK ({humanize.naturaltime(time)})")
              # with message
              else:
                await message.channel.send(f":spy: `{nickname}` is AFK ({humanize.naturaltime(time)})\n```\n{db[str(i.id)][1]}```")
              print("✅　AFK MENTION Event")

def setup(bot):
  bot.add_cog(Events(bot))
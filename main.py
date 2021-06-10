from art import tprint
from datetime import datetime
import discord
from discord.ext import commands
from HelpCommand import HelpCommand
import json
from keepAlive import keepAlive
import os
from replit import db

def get_prefix(bot, message):
  if message.guild:
    with open("prefixes.json", "r") as file:
      prefixes = json.load(file)
    return prefixes[str(message.guild.id)]
  else:
    return "h!"

bot = commands.Bot(command_prefix = get_prefix, intents = discord.Intents.all(), case_insensitive = True)

bot.help_command = HelpCommand(command_attrs = {
   "name": "help",
   "aliases": ["info"],
   "cooldown": commands.Cooldown(1, 5, commands.BucketType.user)
})

@bot.event
async def on_ready():
  def memberCount():
    return len([member for member in bot.get_all_members() if not member.bot])
  bot.memberCount = memberCount
  bot.errorEmoji = "<:error:759595263341494292>"
  bot.checkmarkEmoji = "<:checkmark:759595263076728842>"
  bot.loadingEmoji = "<a:loading:851608303942631474>"
  print(f"Loading Cogs:")
  for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
      bot.load_extension(f"cogs.{filename[:-3]}")
      print(f"- {filename}")

  # afk reapplication
  for server in bot.guilds:
    for member in server.members:
      if str(member.id) in db:
        if not member.display_name.startswith("[AFK] "):
          del db[str(member.id)]
      else:
        if member.display_name.startswith("[AFK] "):
          db[str(member.id)] = [str(datetime.now()), None]
  
  tprint(bot.user.name)
  await bot.change_presence(status = discord.Status.online, activity = discord.Activity(type = discord.ActivityType.watching, name = f"{memberCount()} users • @{bot.user.name}"))
  bot.startTime = datetime.now()

keepAlive()
bot.run(os.environ["token"], bot = True, reconnect = True)
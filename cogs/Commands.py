from datetime import datetime
import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import humanize
import psutil
import random

class Commands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(help = "Displays a specified hex code", aliases = ["colour"])
  @commands.cooldown(1, 5, BucketType.user) 
  async def color(self, ctx, hexCode: discord.Color):
    embed = discord.Embed(title = ":trackball: Color", description = str(hexCode).lower(), color = hexCode, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    embed.set_image(url = f"https://www.colorhexa.com/{str(hexCode).lower()[1:]}.png")
    await ctx.send(embed = embed)
  
  @commands.command(help = "Flips a coin", aliases = ["coin", "coinflip", "flipcoin"])
  @commands.cooldown(1, 5, BucketType.user) 
  async def flip(self, ctx):
    responses = {"Heads": "https://i.imgur.com/92xg7uR.png", "Tails": "https://i.imgur.com/TjqDdBI.png"}
    choice = random.choice(["Heads", "Tails"])
    embed = discord.Embed(title = ":coin: Flip a Coin", description = f"It's `{choice}`", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    embed.set_thumbnail(url = responses[choice])
    await ctx.send(embed = embed)
  
  @commands.command(help = "Displays the server icon", aliases = ["servericon"])
  @commands.guild_only()
  @commands.cooldown(1, 5, BucketType.user) 
  async def icon(self, ctx):
    embed = discord.Embed(title = ":frame_photo: Server Icon", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    embed.set_image(url = self.bot.server.icon_url)
    await ctx.send(embed = embed)
  
  @commands.command(help = "Displays my invite link", aliases = ["inv"])
  @commands.guild_only()
  @commands.cooldown(1, 5, BucketType.user) 
  async def invite(self, ctx):
    embed = discord.Embed(title = ":inbox_tray: Invite Link", description = "You can invite the bot using this [link](https://discord.com/api/oauth2/authorize?client_id=851538022356615208&permissions=134605888&scope=bot)", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_thumbnail(url = self.bot.user.avatar_url)
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    await ctx.send(embed = embed)
  
  @commands.command(help = "Shuts me down", aliases = ["die", "dropdead"])
  @commands.is_owner()
  async def kill(self, ctx):
    await ctx.send(f"{self.bot.checkmarkEmoji} Jumping off a cliff!")
    await self.bot.close()
  
  @commands.command(help = "Sets your nickname", aliases = ["nickname", "setnick", "setnickname"])
  @commands.guild_only()
  @commands.bot_has_permissions(manage_nicknames = True)
  @commands.cooldown(1, 5, BucketType.user) 
  async def nick(self, ctx, *, nickname):
    if len(nickname) >= 1 and len(nickname) <= 32:
      await ctx.author.edit(nick = nickname)
      await ctx.send(f"{self.bot.checkmarkEmoji} Your nickname was set to `{nickname}`!")
    else:
      await ctx.send(f"{self.bot.errorEmoji} Nicknames can only be up to `32` characters long!")
  
  @commands.command(help = "Displays a user's profile picture", aliases = ["avatar", "av", "pic", "picture"])
  @commands.cooldown(1, 5, BucketType.user) 
  async def pfp(self, ctx, member: discord.Member = None):
    member = ctx.author if not member else member
    embed = discord.Embed(title = ":frame_photo: Profile Picture", description = member.mention, color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    embed.set_image(url = member.avatar_url)
    await ctx.send(embed = embed)
  
  @commands.command(help = "Displays my latency among other statistics", aliases = ["latency", "statistics", "stats"])
  @commands.cooldown(1, 5, BucketType.user) 
  async def ping(self, ctx):
    embed = discord.Embed(title = "🏓 Pong!", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    embed.add_field(name = "Latency", value = f"`{round(self.bot.latency * 1000)}`ms", inline = True)
    embed.add_field(name = "Hardware", value = f"`{psutil.cpu_count()}` Cores \n`{round(psutil.cpu_percent())}`% CPU Usage \n`{round(psutil.virtual_memory().percent)}`% RAM Usage", inline = True)
    embed.add_field(name = "Last Restart", value = humanize.naturaltime(datetime.now() - self.bot.startTime), inline = True)
    await ctx.send(embed = embed)
  
  @commands.command(help = "Displays your dong size", aliases = ["dong"])
  @commands.cooldown(1, 5, BucketType.user) 
  async def pp(self, ctx):
    length = float(random.randint(0, 400)) / 10
    output = ""
    i = 0
    ratings = {8: "Atomlike", 16: "Smol", 24: "Average", 32: "Large", 40: "BBC"}
    index = 0
    
    for i in ratings:
      if length > i:
        index += 1
      else:
        break
    for i in range(round(length)):
     output += "="
    
    embed = discord.Embed(title = ":eggplant: PP Rater", description = f"8{output}D \n**Length:** `{round(length, 2)}` inches \n**Rating:** `{ratings[list(ratings.keys())[index]]}`", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    embed.set_thumbnail(url = ctx.author.avatar_url)
    await ctx.send(embed = embed)
  
  @commands.command(help = "Displays a user's spotify status", aliases = ["music"])
  @commands.guild_only()
  @commands.cooldown(1, 5, BucketType.user) 
  async def spotify(self, ctx, member: discord.Member = None):
    member = ctx.author if not member else member
    listening = False
    if member.activities:
      for i in member.activities:
        if i.type == discord.ActivityType.listening:
          listening = True
          activity = i
          break
    if not listening:
      await ctx.send(f"{self.bot.errorEmoji} {'You' if member == ctx.author else 'They'} aren't listening to anything")
      return
    passed = int((datetime.now() - activity.start).total_seconds())
    total = int((activity.end - activity.start).total_seconds())
    duration = list("▱▱▱▱▱▱▱▱")
    for i in range(int((passed / total) * len(duration))):
      duration[i] = "▰"
    embed = discord.Embed(title = "<:spotify:841831747867377684> Spotify", description = member.mention, color = activity.color, timestamp = datetime.utcnow())
    embed.add_field(name = "Title", value = f"[{activity.title}](https://open.spotify.com/track/{activity.track_id})", inline = True)
    embed.add_field(name = f"Artist{'s' if len(activity.artists) > 1 else ''}", value = ", ".join(activity.artists), inline = True)
    embed.add_field(name = "Album", value = activity.album, inline = True)
    embed.add_field(name = "Timestamp", value = f"```yaml\n{int(passed / 60)}:{(passed % 60):02d} / {int(total / 60)}:{(total % 60):02d}```", inline = True)
    embed.add_field(name = "Duration", value = f"```yaml\n{''.join(duration)}```", inline = True)
    embed.set_image(url = activity.album_cover_url)
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    await ctx.send(embed = embed)

def setup(bot):
  bot.add_cog(Commands(bot))
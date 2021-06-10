import aiohttp
import asyncio
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import html2text
import humanize
import io
import json
import ordinal
import portolan
import random
from replit import db
import uuid

class DatabaseCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(help = "Sets your AFK status", aliases = ["busy", "bye", "gn"])
  async def afk(self, ctx, *, message = None):
    if not ctx.guild:
      await ctx.send(f"{self.bot.errorEmoji} This command only works in a server")
      return
    if not ctx.me.guild_permissions.manage_nicknames:
      raise commands.BotMissingPermissions(["manage_nicknames"])
    if ctx.author.display_name.startswith("[AFK] "):
      return
    if ctx.me.top_role > ctx.author.top_role and not ctx.author.guild_permissions.administrator:
      if len(ctx.author.display_name) <= 26:
        await ctx.author.edit(nick = f"[AFK] {ctx.author.display_name}")
      else:
        await ctx.author.edit(nick = f"[AFK] {ctx.author.display_name[:-6]}")
    db[str(ctx.author.id)] = [str(ctx.message.created_at), message]
    text = f"{self.bot.checkmarkEmoji} Set your AFK"
    if message:
      text += f"\n```{message}```"
    await ctx.send(text)
  
  @commands.command(help = "Displays a ranodom fact", aliases = ["randomfact"])
  @commands.guild_only()
  @commands.cooldown(1, 10, BucketType.user) 
  async def fact(self, ctx):
    message = await ctx.send(f"{self.bot.loadingEmoji} Loading...")
    async with aiohttp.ClientSession() as session:
      async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as reply:
        data = await reply.json()
    embed = discord.Embed(title = ":book: Fact", description = f"{data['text']}", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    await message.edit(content = None, embed = embed)
  
  @commands.command(help = "Sends a multiplayer quiz", aliases = ["f", "race", "r"])
  @commands.guild_only()
  @commands.cooldown(1, 10, BucketType.channel)
  async def fast(self, ctx):
    original = await ctx.send(f"{self.bot.loadingEmoji} Loading...")
    choice = random.randint(0, 2)

    def math():
      operation, numbers, answer = random.choice(["×", "/", "+", "-"]), [], 0
      if operation == "×":
        numbers = [random.randint(0, 20), random.randint(0, 20)]
        answer = numbers[0] * numbers[1]
      elif operation == "/":
        denominator = random.randint(1, 20)
        answer = random.randint(1, 20)
        numbers = [denominator * answer, denominator]
      elif operation == "+":
        numbers = [random.randint(50, 100), random.randint(50, 100)]
        answer = numbers[0] + numbers[1]
      else:
        numbers = [random.randint(50, 100), random.randint(50, 100)]
        while numbers[0] < numbers[1]:
          numbers = [random.randint(50, 100), random.randint(50, 100)]
        answer = numbers[0] - numbers[1]
      
      embed = discord.Embed(title = ":zap: Math Showdown", description = f"First to solve the following wins!\n```py\n{numbers[0]} {operation} {numbers[1]}```", color = 0x9c7a61, timestamp = datetime.utcnow())
      embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
      return [embed, answer]
    
    async def word():
      async with aiohttp.ClientSession() as session:
        async with session.get("https://random-word-api.herokuapp.com/word?number=1") as reply:
          data = await reply.json()
      answer = data[0][::-1]
      embed = discord.Embed(title = ":zap: Word Showdown", description = f"First to type the following backwards wins!\n```yaml\n{data[0]}```", color = 0x9c7a61, timestamp = datetime.utcnow())
      embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
      return [embed, answer]
    
    def find():
      wrong, correct = ":white_large_square:", ":brown_square:"
      table = [[wrong, wrong, wrong], [wrong, wrong, wrong], [wrong, wrong, wrong]]
      answerTable = [["1a", "1b", "1c"], ["2a", "2b", "2c"], ["3a", "3b", "3c"]]
      randChoice = [random.randint(0, 2), random.randint(0, 2)]
      row, column, answer = randChoice[0], randChoice[1], answerTable[randChoice[0]][randChoice[1]]
      table[row][column] = correct
      rowPH = ["`1`", "`2`", "`3`"]
      printedTable = "⠀⠀`A`⠀`B`⠀`C`\n"
      for i in range(0, 3):
        printedTable += f"`{rowPH[i]}` "
        for j in range(0, 3):
          printedTable += f"||{table[i][j]}|| "
        printedTable += "\n"
      embed = discord.Embed(title = ":zap: Bubble Wrap", description = f"First to type the location to {correct} wins!\n(ex: `B2` or `2B`)\n\n{printedTable}", color = 0x9c7a61, timestamp = datetime.utcnow())
      embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
      return [embed, answer]
    
    pack = await [math, word, find][choice]() if choice == 1 else [math, word, find][choice]()
    await original.edit(content = None, embed = pack[0])
    
    def check(message):
      if choice == 2:
        return message.content.lower() in [pack[1], pack[1][::-1]] and message.channel == ctx.channel
      else:
        return message.content.lower() == str(pack[1]) and message.channel == ctx.channel
    try:
      message = await self.bot.wait_for("message", timeout = 15, check = check)
    except asyncio.TimeoutError:
      await original.edit(content = f"{self.bot.errorEmoji} Event has expired", embed = None)
    else:
      await message.add_reaction(self.bot.checkmarkEmoji)
      await ctx.send(f"{message.author.mention} wins!")
  
  @commands.command(help = "Displays your grades (read [here](https://pastebin.com/30DtnU4p))")
  @commands.cooldown(1, 20, BucketType.user) 
  async def grades(self, ctx, username, password):
    message = await ctx.send(f"{self.bot.loadingEmoji} Loading...")
    if ctx.message.guild:
      try:
        await ctx.message.delete()
      except:
        pass
      embed = discord.Embed(title = ":books: Grades", description = f"You can't use this command here, please DM me and try again", color = 0x9c7a61, timestamp = datetime.utcnow())
      embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
      await message.edit(content = None, embed = embed)
      ctx.command.reset_cooldown(ctx)
      return
    async with aiohttp.ClientSession(auth = aiohttp.BasicAuth(username, password)) as session:
      async with session.get(f"https://dvhs.schoolloop.com/mapi/login?version=3&devToken={uuid.uuid4()}&devOS=iPhone9,4&year={datetime.now().year}") as reply:
        if reply.status != 200:
          if "user" in await reply.text():
            await message.edit(content = f"{self.bot.errorEmoji} Username not found")
          else:
            await message.edit(content = f"{self.bot.errorEmoji} Incorrect password")
          return
        studentDB = await reply.json(content_type = None)
      async with session.get(f"https://dvhs.schoolloop.com/mapi/report_card?studentID={studentDB['userID']}") as reply:
        resultDB = await reply.json(content_type = None)
    
    embed = discord.Embed(title = ":scroll: Grades", description = "Your grades/credentials are **never** saved (read [here](https://www.google.com/))", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    for i in resultDB:
      if i["courseName"] != "Access":
        period = "A" if i["period"] == "0" else i["period"]
        lastUpdated = "null" if i["lastUpdated"] == "null" else humanize.naturaltime(datetime.now() - datetime.strptime(i["lastUpdated"], "%m/%d/%y %I:%M %p"))
        embed.add_field(name = f"{period} - {i['courseName']}", value = f"Teacher: `{i['teacherName']}`\nGrade: `{i['grade']}` (`{i['score']}`)\nLast Updated: {lastUpdated}", inline = False)
    await message.edit(content = None, embed = embed)
  
  @commands.command(help = "Displays a random joke")
  @commands.cooldown(1, 10, BucketType.user) 
  async def joke(self, ctx):
    message = await ctx.send(f"{self.bot.loadingEmoji} Loading...")
    async with aiohttp.ClientSession() as session:
      async with session.get("https://official-joke-api.appspot.com/jokes/random") as reply:
        data = await reply.json()
    embed = discord.Embed(title = ":book: A joke", description = f"**{data['setup']}**", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    await message.edit(content = None, embed = embed)
    embed = discord.Embed(title = ":book: A joke", description = f"**{data['setup']}**\n{data['punchline']}", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    await asyncio.sleep(2)
    await message.edit(content = None, embed = embed)
  
  @commands.command(help = "Strips off text from an attachment", aliases = ["read", "scan"])
  @commands.cooldown(1, 20, BucketType.user)
  async def ocr(self, ctx, engine = 2):
    message = await ctx.send(f"{self.bot.loadingEmoji} Scanning... (this will take a moment)")
    if ctx.message.attachments:
      if engine not in [1, 2]:
        await message.edit(content = f"{self.bot.errorEmoji} Invalid engine, choose `1` or `2` (more info at https://ocr.space/ocrapi#ocrengine)")
        return
      for i in ctx.message.attachments:
        if i.size / 1000 <= 1024:
          async def process(url, apiKey, engine):
            payload = {"url": url, "apikey": apiKey, "OCREngine": engine}
            async with aiohttp.ClientSession() as session:
              async with session.post("https://api.ocr.space/parse/image", data = payload) as reply:
                return await reply.json()
          results = await process(i.url, "8031c0b2f488957", engine)
          if results["IsErroredOnProcessing"]:
            await message.edit(content = f"{self.bot.errorEmoji} An error occured (maybe try again with `!ocr {1 if engine == 2 else 2}`)\n```\n{results['ErrorMessage'][0]}```")
            return
          if not results["ParsedResults"][0]["ParsedText"]:
            await message.edit(content = f"{self.bot.errorEmoji} No text found (if this is an error, try again with `!ocr {1 if engine == 2 else 2}`)")
            return
          if len(results["ParsedResults"][0]["ParsedText"]) > 1024:
            embed = discord.Embed(title = ":newspaper: Optical Character Recognition", color = 0x9c7a61, timestamp = datetime.utcnow())
            embed.add_field(name = "Details", value = f"Name: [{i.filename}]({i.url})\nSize: `{round(i.size / 1000, 2)}` kilobytes\nProcess: `{round(int(results['ProcessingTimeInMilliseconds']) / 1000, 2)}` seconds\nEngine: `{engine}` (see more [here](https://ocr.space/ocrapi#ocrengine))", inline = False)
            embed.add_field(name = "Results", value = f"```\n{results['ParsedResults'][0]['ParsedText']}```", inline = False)
            embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
            await message.edit(content = None, embed = embed)
            await ctx.send(file = discord.File(io.StringIO(results["ParsedResults"][0]["ParsedText"]), filename = "results.txt"))
            return
          embed = discord.Embed(title = ":newspaper: Optical Character Recognition", color = 0x9c7a61, timestamp = datetime.utcnow())
          embed.add_field(name = "Details", value = f"Name: [{i.filename}]({i.url})\nSize: `{round(i.size / 1000, 2)}` kilobytes\nProcess: `{round(int(results['ProcessingTimeInMilliseconds']) / 1000, 2)}` seconds\nEngine: `{engine}` (see more [here](https://ocr.space/ocrapi#ocrengine))", inline = False)
          embed.add_field(name = "Results", value = f"```\n{results['ParsedResults'][0]['ParsedText']}```", inline = False)
          embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
          await message.edit(content = None, embed = embed)
        else:
          await message.edit(content = f"{self.bot.errorEmoji} Your file exceeds the `1024` kilobyte limit")
    else:
      await message.edit(content = f"{self.bot.errorEmoji} Try attaching something")
  
  @commands.command(help = "Predicts your fortune", aliases = ["8ball"])
  @commands.cooldown(1, 10, BucketType.user) 
  async def predict(self, ctx, *, question: str):
    message = await ctx.send(f"{self.bot.loadingEmoji} Loading...")
    async with aiohttp.ClientSession() as session:
      async with session.get(f"https://8ball.delegator.com/magic/JSON/{question}") as reply:
        data = await reply.json()
    embed = discord.Embed(title = ":8ball: The Mighty 8Ball", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.add_field(name = "Question", value = question, inline = False)
    embed.add_field(name = "Response", value = data["magic"]["answer"], inline = False)
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    embed.set_thumbnail(url = "https://i.imgur.com/LkSBSuR.gif")
    await message.edit(content = None, embed = embed)
  
  @commands.command(help = "Changes the prefix", aliases = ["changeprefix"])
  @commands.guild_only()
  @commands.has_permissions(manage_permissions = True)
  @commands.cooldown(1, 10, BucketType.user)
  async def prefix(self, ctx, *, prefix):
    if not ctx.guild:
      await ctx.send(f"{self.bot.errorEmoji} This command only works in a server")
      return
    if not ctx.author.guild_permissions.manage_permissions:
      raise commands.MissingPermissions
    if len(prefix) <= 5:
      prefix = prefix.replace(" ", "")
      with open("prefixes.json", "r") as file:
        prefixes = json.load(file)
      if prefix.isalpha():
        prefix += " "
      prefixes[str(ctx.guild.id)] = prefix
      with open("prefixes.json", "w") as file:
        json.dump(prefixes, file, indent = 2)
      await ctx.send(f"{self.bot.checkmarkEmoji} The prefix has been changed to `{prefix.replace(' ', '')}` (usage: `{prefix}help`)")
    else:
      await ctx.send(f"{self.bot.errorEmoji} The prefix can be no longer than `5` characters")
  
  @commands.command(help = "Roasts a user", aliases = ["burn", "insult"])
  @commands.cooldown(1, 10, BucketType.user)
  async def roast(self, ctx, *, member: discord.Member = None):
    member = ctx.author if not member else member
    content = None if not member else member.mention
    message = await ctx.send(f"{self.bot.loadingEmoji} Loading...")
    async with aiohttp.ClientSession() as session:
      async with session.get("https://evilinsult.com/generate_insult.php?lang=en&type=json") as reply:
        data = await reply.json()
    embed = discord.Embed(title = "<:pepeLaugh:812786514911428608> Insult", description = data["insult"], color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    await message.edit(content = content, embed = embed)
  
  @commands.command(help = "Displays the trivia leaderboard", aliases = ["lb", "leaderboard", "^"])
  @commands.cooldown(1, 10, BucketType.user)
  async def top(self, ctx):
    with open("cogs/points.json", "r") as file:
      data = json.load(file)
    data = dict(sorted(data.items(), key = lambda item: item[1]))
    data = dict(reversed(list(data.items())))
    lb = []
    for i in data:
      if ctx.author.id == int(i):
        lb.append(f"<@{i}> • `{data[i]}` :star:")
      else:
        lb.append(f"<@{i}> • `{data[i]}`")
    emojis = [":first_place:", ":second_place:", ":third_place:"]
    output = ""
    if len(lb) <= 15:
      for i in lb:
        if lb.index(i) <= 2:
          output += f"\n{emojis[lb.index(i)]} "
        else:
          output += f"\n**{ordinal(lb.index(i) + 1)} **"
        output += lb[lb.index(i)]
    else:
      for i in range(15):
        if i <= 2:
          output += f"\n{emojis[i]} "
        else:
          output += f"\n**{ordinal(i + 1)}** "
        output += lb[i]
    
    with open("prefixes.json", "r") as file:
      prefixes = json.load(file)

    embed = discord.Embed(title = ":trophy: Leaderboard", description = f"Top 15 Trivia Command Users\nLevel up with `{prefixes[str(ctx.guild.id)]}trivia`\n{output}", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    await ctx.send(embed = embed)
  
  @commands.command(help = "Sends a singleplayer quiz", aliases = ["q", "question", "quiz", "t"])
  @commands.cooldown(1, 20, BucketType.user)
  async def trivia(self, ctx, difficulty: str = None):
    message = await ctx.send(f"{self.bot.loadingEmoji} Loading...")
    difficulties = {"e": "easy", "m": "medium", "h": "hard"}
    points = {"easy": 1, "medium": 2, "hard": 3}
    with open("prefixes.json", "r") as file:
      prefixes = json.load(file)
    
    if difficulty:
      if difficulty[0].lower() in difficulties:
        difficulty = difficulties[difficulty[0].lower()]
      else:
        await message.edit(content = f"{self.bot.errorEmoji} You can only choose an `easy`, `medium`, or `hard` question")
        ctx.command.reset_cooldown(ctx)
        return
    else:
      difficulty = random.choice(list(difficulties.values()))
    
    async with aiohttp.ClientSession() as session:
      async with session.get(f"https://opentdb.com/api.php?amount=1&difficulty={difficulty}&type=multiple") as reply:
        data = await reply.json()

    category = html2text.html2text(data["results"][0]["category"]).replace("\n", "")
    question = html2text.html2text(data["results"][0]["question"]).replace("\n", "")
    choices = [html2text.html2text(data["results"][0]["correct_answer"]).replace("\n", "")]
    for i in data["results"][0]["incorrect_answers"]:
      choices.append(html2text.html2text(i).replace("\n", ""))
    random.shuffle(choices)
    correctIndex = choices.index(html2text.html2text(data["results"][0]["correct_answer"]).replace("\n", ""))
    reactionsList = ["🇦", "🇧", "🇨", "🇩"]
    embed = discord.Embed(title = ":student: Trivia", description = f"**Category**: {category}\n**Difficulty**: {difficulty.capitalize()}\n**Question**: {question}\n\n{reactionsList[0]} {choices[0]}\n{reactionsList[1]} {choices[1]}\n{reactionsList[2]} {choices[2]}\n{reactionsList[3]} {choices[3]}\n\nreact with your answer within `10` seconds", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    await message.edit(content = None, embed = embed)
    for i in reactionsList:
      await message.add_reaction(i)
    
    def check(reaction, user):
      return user == ctx.author and str(reaction.emoji) in reactionsList
    try:
      reaction, user = await self.bot.wait_for("reaction_add", timeout = 10, check = check)
    
    # expired
    except asyncio.TimeoutError:
      await message.clear_reactions()
      # points system
      with open("cogs/points.json", "r") as file:
        data = json.load(file)
      if str(ctx.author.id) in data:
        if data[str(ctx.author.id)] > 0:
          data[str(ctx.author.id)] -= 1
      with open("cogs/points.json", "w") as file:
        json.dump(data, file, indent = 2)
      
      reactionsList[correctIndex] = self.bot.checkmarkEmoji
      embed = discord.Embed(title = f":alarm_clock: Expired! (-{points[difficulty]} points)", description = f"**Category**: {category}\n**Difficulty**: {difficulty.capitalize()}\n**Question**: {question}\n\n{reactionsList[0]} {choices[0]}\n{reactionsList[1]} {choices[1]}\n{reactionsList[2]} {choices[2]}\n{reactionsList[3]} {choices[3]}\n\nview the global leaderboard with `{prefixes[str(ctx.guild.id)]}top`", color = 0xFF383E, timestamp = datetime.utcnow())
      embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
      await message.edit(content = None, embed = embed)
    
    # responded
    else:
      await message.clear_reactions()
      # correct answer
      if reactionsList.index(str(reaction.emoji)) == correctIndex:
        # points system
        with open("cogs/points.json", "r") as file:
          data = json.load(file)
        if str(ctx.author.id) not in data:
          data[str(ctx.author.id)] = points[difficulty]
        else:
          data[str(ctx.author.id)] += points[difficulty]
        with open("cogs/points.json", "w") as file:
          json.dump(data, file, indent = 2)
        
        reactionsList[correctIndex] = self.bot.checkmarkEmoji
        embed = discord.Embed(title = f"{self.bot.checkmarkEmoji} Correct! (+{points[difficulty]} points)", description = f"**Category**: {category}\n**Difficulty**: {difficulty.capitalize()}\n**Question**: {question}\n\n{reactionsList[0]} {choices[0]}\n{reactionsList[1]} {choices[1]}\n{reactionsList[2]} {choices[2]}\n{reactionsList[3]} {choices[3]}\n\nview the global leaderboard with `{prefixes[str(ctx.guild.id)]}top`", color = 0x3FB97C, timestamp = datetime.utcnow())
        embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
        await message.edit(content = None, embed = embed)
      
      # wrong answer
      else:
        # points system
        with open("cogs/points.json", "r") as file:
          data = json.load(file)
        if str(ctx.author.id) in data:
          if data[str(ctx.author.id)] > points[difficulty]:
            data[str(ctx.author.id)] -= points[difficulty]
          else:
            data[str(ctx.author.id)] = 0
          with open("cogs/points.json", "w") as file:
            json.dump(data, file, indent = 2)
        
        reactionsList[reactionsList.index(str(reaction.emoji))] = self.bot.errorEmoji
        reactionsList[correctIndex] = self.bot.checkmarkEmoji
        embed = discord.Embed(title = f"{self.bot.errorEmoji} Incorrect! (-{points[difficulty]} points)", description = f"**Category**: {category}\n**Difficulty**: {difficulty.capitalize()}\n**Question**: {question}\n\n{reactionsList[0]} {choices[0]}\n{reactionsList[1]} {choices[1]}\n{reactionsList[2]} {choices[2]}\n{reactionsList[3]} {choices[3]}\n\nview the global leaderboard with `{prefixes[str(ctx.guild.id)]}top`", color = 0xFF383E, timestamp = datetime.utcnow())
        embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
        await message.edit(content = None, embed = embed)
  
  @commands.command(help = "Displays the weather for a specifed city")
  @commands.cooldown(1, 20, BucketType.user) 
  async def weather(self, ctx, *, city):
    message = await ctx.send(f"{self.bot.loadingEmoji} Loading...")
    async with aiohttp.ClientSession() as session:
      async with session.get(f"http://api.openweathermap.org/data/2.5/weather?appid=e83935ef7ce7823925eeb0bfd2db3f7f&q={city}") as reply:
        data = await reply.json()
    
    if data["cod"] == "404":
      await message.edit(content = f"{self.bot.errorEmoji} Invalid city")
      return
    
    sunrise = datetime.fromtimestamp(int(data["sys"]["sunrise"])) - timedelta(hours = 7)
    sunset = datetime.fromtimestamp(int(data["sys"]["sunset"])) - timedelta(hours = 7)
    embed = discord.Embed(title = ":partly_sunny: Weather", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar_url)
    embed.set_thumbnail(url = f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@4x.png")
    embed.add_field(name = "City", value = f"`{data['name']}`, `{data['sys']['country']}`", inline = True)
    embed.add_field(name = "Condition", value = f"`{(data['weather'][0]['description']).title()}`", inline = True)
    embed.add_field(name = "Cloudiness", value = f"`{data['clouds']['all']}`%", inline = True)
    embed.add_field(name = "Temperature", value = f"`{round((1.8 * ((data['main']['temp']) - 273.15)) + 32)}`°F", inline = True)
    embed.add_field(name = "Humidity", value = f"`{data['main']['humidity']}`%", inline = True)
    embed.add_field(name = "Wind", value = f"`{round((data['wind']['speed'] * 2.24), 1)}`mph `{portolan.abbr(degree = data['wind']['deg'])}`", inline = True)
    embed.add_field(name = "Sunrise", value = f"{sunrise.strftime('`%I`:`%M` `%p`')} PST", inline = True)
    embed.add_field(name = "Sunset", value = f"{sunset.strftime('`%I`:`%M` `%p`')} PST", inline = True)
    await message.edit(content = None, embed = embed)

def setup(bot):
  bot.add_cog(DatabaseCommands(bot))
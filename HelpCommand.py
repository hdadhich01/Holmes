from datetime import datetime
import discord
from discord.ext import commands

class HelpCommand(commands.HelpCommand):
  def command_help_signature(self, command):
    return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

  async def send_bot_help(self, mapping):
    output = "Developer: <@410590963379994639>\nGithub: [Link](https://github.com/TheHarpagon/Holmes) (drop issues/suggestions)\nTop.gg: [Link](https://top.gg/bot/851538022356615208) (drop a vote/review)\n"
    for cog, commands in mapping.items():
      filtered = await self.filter_commands(commands, sort = True)
      for command in filtered:
        output += f"\n`{self.clean_prefix}{command.qualified_name}` {command.help}"
    embed = discord.Embed(title = ":scroll: Help", description = output)
    await self.get_destination().send(embed = embed)
  
  async def send_command_help(self, command):
    title = command.qualified_name
    if title in ["afk", "ocr"]:
      title = title.upper()
    embed = discord.Embed(title = title, description = f"{command.help}", color = 0x9c7a61, timestamp = datetime.utcnow())
    embed.add_field(name = "Syntax", value = f"`{self.clean_prefix}{command.qualified_name} {command.signature}`\nNote: `[]` is optional; `<>` is required")
    if command.aliases:
      aliases = f"`{command.aliases[0]}`"
      for i in command.aliases:
        aliases += f", `{i}`"
      embed.add_field(name = "Aliases", value = aliases, inline=False)

    channel = self.get_destination()
    await channel.send(embed=embed)
from typing import Optional
import discord
from discord import app_commands
import os

from discord import interactions
from keep_alive import keep_alive
import replit

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

db = replit.db
db["players"] = []

@client.event
async def on_ready():
  await tree.sync()
  print("Ready!")

@tree.command(name = "hello", description = "says hello")
async def hello(interaction):
  await interaction.response.send_message("Hello!")

@tree.command(name = "database", description= "devs only command")
async def database(interaction):
  if interaction.user.id == 1077648874002460672:
    users = db["players"]
    await interaction.response.send_message(users)
  else:
    await interaction.response.send_message("know your place hooman.")

@tree.command(name= "reset", description= "thanos snap lol")
async def reset(interaction):
  if interaction.user.id == 1077648874002460672:
    users = db["players"]
    del users
  else:
    await interaction.response.send_message("know your place hooman.")

@tree.command(name= "register", description= "Neko will remember you <3")
async def register(interaction):
  userid = str(interaction.user.id)
  if userid in db["players"]:
    await interaction.response.send_message("Got short term memory loss?")
  else:
    db["players"].append(userid)
    await interaction.response.send_message("you are registered now, yayy!")

@tree.command(name="avatar", description="shows avatar")
async def avatar(interaction, user: Optional[discord.Member] = None):
  if user is None:
    user = interaction.user
    embed = discord.Embed(title=f"pfp of {user.display_name}", color=0xe91e63)
    embed.set_image(url=user.display_avatar)
    await interaction.response.send_message(embed=embed)
  else:
    embed = discord.Embed(title=f"pfp of {user.display_name}")
    embed.set_image(url=user.display_avatar)
    await interaction.response.send_message(embed=embed)

keep_alive()

my_secret = os.environ['TOKEN']
client.run(my_secret)
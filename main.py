from typing import Optional
import discord
from discord import app_commands
import os
from discord import interactions
from keep_alive import keep_alive
from discord import Member
import replit

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

db = replit.db

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name="with your mom"))
  await tree.sync()
  print("Ready!")

@tree.command(name = "hello", description = "says hello")
async def hello(interaction):
  await interaction.response.send_message("Hello!")

@tree.command(name = "database", description= "devs only command")
async def database(interaction):
  if interaction.user.id == 1077648874002460672:
    users = dict(db)
    await interaction.response.send_message(users)
  else:
    await interaction.response.send_message("know your place hooman.")

@tree.command(name= "reset", description= "thanos snap lol")
async def reset(interaction):
  if interaction.user.id == 1077648874002460672:
    del db[]
  else:
    await interaction.response.send_message("know your place hooman.")

@tree.command(name= "register", description= "Neko will remember you <3")
async def register(interaction):
  userid = str(interaction.user.id)
  registered_users = db.get() 
  
  if userid in registered_users:
    await interaction.response.send_message("Got short term memory loss?")
  else:
    registered_users.append(userid)
    db[] = registered_users 
    await interaction.response.send_message("You are registered now, yayy!")

@tree.command(name="avatar", description="shows avatar")
async def avatar(interaction, user: Optional[Member] = None):
  if user is None:
    user = interaction.user
    embed = discord.Embed(title=f"pfp of {user.display_name}", color=0xe91e63)
    embed.set_image(url=user.display_avatar)
    await interaction.response.send_message(embed=embed)
  else:
    embed = discord.Embed(title=f"pfp of {user.display_name}")
    embed.set_image(url=user.display_avatar)
    await interaction.response.send_message(embed=embed)

@tree.command(name="profile")
async def profile(interaction, user: Optional[Member] = None):
  if user is None:
    user = interaction.user
  
  user_id = str(user.id)
  print(members)

  user_data = db.get(user_id, None)
  if user_data is None:
    await interaction.response.send_message("User is not registered probably.")
    return

  xp = user_data.get("xp", 1) 
  army_space = user_data.get("army_space", 30)

  embed = discord.Embed(title=f"Profile of {user.display_name}", color=0xe91e63)
  embed.set_thumbnail(url=user.display_avatar)
  embed.add_field(name="Level:", value=1, inline=True)
  embed.add_field(name="XP:", value=f"{xp}/100", inline=True)
  embed.add_field(name="Clan:", value="in dev", inline=False)
  embed.add_field(name="Army space:", value=army_space)

  await interaction.response.send_message(embed=embed)

keep_alive()

my_secret = os.environ['TOKEN']
client.run(my_secret)
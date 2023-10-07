from typing import Optional
import discord
from discord import app_commands
import os
from discord import interactions
from keep_alive import keep_alive
from discord import Member
import mysql.connector as ms
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

psd = os.environ['psd']
hst = os.environ['hst']
myd = ms.connect(host=hst, database='freedb_players', user='freedb_skeee', password=psd)
mydb = myd.cursor()
#mydb.execute("CREATE TABLE users(uid VARCHAR(20))")

async def ping_database():
  while True:
    await asyncio.sleep(180)
    myd.ping(reconnect=True)

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name="with your mom"))
  await tree.sync()
  client.loop.create_task(ping_database())
  print("Ready!")

@tree.command(name = "hello", description = "says hello")
async def hello(interaction):
  await interaction.response.send_message("Hello!")

@tree.command(name="kick", description="Kicks a member")
async def kick(interaction, user: Member, reason: Optional[str] = "No reason provided"):
  userid = interaction.user.id
  memberid = user.id

  if interaction.guild.me.guild_permissions.kick_members:
    if interaction.user.guild_permissions.kick_members:
      if user.guild_permissions.kick_members:
        await interaction.response.send_message(f"{user.mention} has been kicked successfully")
        await user.kick(reason=reason)
      else:
        await interaction.response.send_message(":middle_finger:")
    else:
      await interaction.response.send_message(":middle_finger:")
  else:
    await interaction.response.send_message("gimme the necessary permission first dummies.")

@tree.command(name="mute", description="mutes a member")
async def mute(interaction, user: Member, duration: Optional[int] = None):
  if interaction.guild.me.guild_permissions.mute_members:
    if interaction.user.guild_permissions.mute_members:
      if user.guild_permissions.mute_members:
        user.edit(mute=True)
        if duration:
          await asyncio.sleep(duration)
          user.edit(mute=False)
      else:
        await interaction.response.send_message(":middle_finger:")
    else:
      interaction.response.send_message("middle_finger:")
  else:
    interaction.response.send_message("gimme the necessary permissions dummy!")

@tree.command(name="unmute", description="unmutes a member")
async def mute(interaction, user: Member):
  if interaction.guild.me.guild_permissions.mute_members:
    if interaction.user.guild_permissions.mute_members:
      user.edit(mute=False)
    else:
      interaction.response.send_message("middle_finger:")
  else:
    interaction.response.send_message("gimme the necessary permissions dummy!")

@tree.command(name = "database", description= "devs only command")
async def database(interaction):
  if interaction.user.id == 1077648874002460672:
    mydb.execute("SELECT UID FROM users")
    users = mydb.fetchall()
    user_list = ", ".join(str(user[0]) for user in users)
    await interaction.response.send_message(f"```Registered users: {user_list}```")
  else:
    await interaction.response.send_message(":middle_finger:")

@tree.command(name= "reset", description= "thanos snap lol")
async def reset(interaction):
  if interaction.user.id == 1077648874002460672:
    mydb.execute("DROP TABLE users")
    await interaction.response.send_message("reset success.")
  else:
    await interaction.response.send_message(":middle_finger:")

@tree.command(name= "register", description= "Neko will remember you <3")
async def register(interaction):
  userid = str(interaction.user.id)
  mydb.execute("SELECT * FROM users WHERE UID = %s", (userid,))
  result = mydb.fetchone()
  
  if result:
    await interaction.response.send_message("Got a short term memory loss?")
  else:
    def_level = 1
    def_army = 30
    def_exp = 1
    mydb.execute("INSERT INTO users (UID, level, exp, army_space) VALUES (%s, %s, %s, %s)",
    (userid, def_level, def_exp, def_army))
    myd.commit()
    await interaction.response.send_message("Yayy, I will remember you now UwU")

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

  userid = str(user.id)
  mydb.execute("SELECT * FROM users WHERE UID = %s", (userid,))
  result = mydb.fetchone()

  if result:
    uid, level, army_space, exp = result
    embed = discord.Embed(title=f"Profile of {user.display_name}", color=0xe91e63)
    embed.set_thumbnail(url=user.display_avatar)
    embed.add_field(name="Level:", value=level, inline=True)
    embed.add_field(name="XP:", value=f"{exp}/100", inline=True)
    embed.add_field(name="Army Space:", value=army_space, inline=False)
    embed.add_field(name="Clan:", value="coming soon", inline=False)
    await interaction.response.send_message(embed=embed)
  else:
    await interaction.response.send_message("User is not registered.")


keep_alive()

my_secret = os.environ['TOKEN']
client.run(my_secret)
from typing import Optional
import discord
from discord import app_commands
import os
from discord import interactions
from keep_alive import keep_alive
from discord import Member
import mysql.connector as ms

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

psd = 'X9p37jz3j!9qmtb'
hst = 'sql.freedb.tech'
myd = ms.connect(host=hst, database='freedb_players', user='freedb_skeee', password=psd)
mydb = myd.cursor()
mydb.execute("CREATE TABLE users(uid VARCHAR(20))")

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
    mydb.execute("SELECT UID FROM USERS")
    users = mydb.fetchall()
    user_list = ", ".join(str(user[0]) for user in users)
    await interaction.response.send_message(f"```Registered users: {user_list}```")
  else:
    await interaction.response.send_message(":middle_finger:")

@tree.command(name= "reset", description= "thanos snap lol")
async def reset(interaction):
  if interaction.user.id == 1077648874002460672:
    mydb.execute("DROP TABLE USERS")
    await interaction.response.send_message("reset success.")
  else:
    await interaction.response.send_message(":middle_finger:")

@tree.command(name= "register", description= "Neko will remember you <3")
async def register(interaction):
  userid = str(interaction.user.id)
  mydb.execute("SELECT * FROM USERS WHERE UID = %s", (userid,))
  result = mydb.fetchone()
  
  if result:
    await interaction.response.send_message("You are already registered!")
  else:
    mydb.execute("INSERT INTO USERS (UID) VALUES (%s)", (userid,))
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

'''@tree.command(name="profile")
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

  await interaction.response.send_message(embed=embed)'''

keep_alive()

my_secret = os.environ['TOKEN']
client.run(my_secret)
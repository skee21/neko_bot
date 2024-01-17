from typing import Optional
import discord
from discord import app_commands
import os
from discord import interactions
from keep_alive import keep_alive
from discord import Member
import mysql.connector as ms
import asyncio
import datetime
import spotipy
#import logging

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

psd = os.environ['psd']
hst = os.environ['hst']

myd = ms.connect(host=hst, database='freedb_players',  user='freedb_skee21', password=psd)
mydb = myd.cursor()
#mydb.execute("CREATE TABLE users(uid VARCHAR(20))")

#logging.basicConfig(filename='discord.log', format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',level=logging.INFO)

async def ping_database():
  while True:
    await asyncio.sleep(60)
    myd.ping(reconnect=True)

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name="with your mom"))
  await tree.sync()
  client.loop.create_task(ping_database())
  print("The bot is ready!")

async def on_message(message):
  msg = message.content.lower()
  if message.author == client.user:
    return
    
  if msg.startswith('hello'):
    await message.channel.send(f'hello <@{message.author.id}>, you virgin')
    await message.author.send("you lost bbg? :smirk:")

client.event(on_message)

@tree.command(name = "hello", description = "says hello")
async def hello(interaction):
  await interaction.response.send_message("Hello!")

@tree.command(name = "ghostping", description = "ghost pings a user")
async def ghostping(interaction, user: Member):
  '''cooldown = app_commands.Cooldown(1, 600)
  if not cooldown.update_rate_limit():
    tokens = cooldown.get_tokens(current=1)
    if tokens < 0:
      await interaction.response.send_message("wait 10 mins before using this command again")
    return'''
  
  try:
    memberid = user.id
    await user.send("you lost bbg? :smirk:")
    await interaction.response.send_message("pinged :thumbsup:", ephemeral=True, delete_after=3)
    with open("pings.txt" , "a") as f:
      f.write(f"{interaction.user.id} pinged {memberid}\n")
  except discord.Forbidden:
    await interaction.response.send_message("user has dms disabled :x:", ephemeral=True, delete_after=3)
  except discord.HTTPException as e:
    await interaction.response.send_message(f"error: {e}", ephemeral=True, delete_after=3)

@tree.command(name = "pings", description = "shows the pings")
async def pings(interaction):
  if interaction.user.id == 1077648874002460672:
    with open("pings.txt", "r") as f:
      lines = f.readlines()

    send = lines[-5:]
    await interaction.response.send_message("\n".join(send))
  else:
    await interaction.response.send_message(":middle_finger:")
  
@tree.command(name="contact_dev", description="send a message to skee, the developer of neko")
async def contact_dev(interaction, msg: str):
  userid = str(1077648874002460672)
  user = await client.fetch_user(userid)
  sender = interaction.user
  try:
    await user.send(f"{sender.mention} sent you a message: {msg}")
    await interaction.response.send_message(f"Message sent to skee: {msg}")
  except discord.Forbidden:
    await interaction.response.send_message("I can't send messages to skee atm, try his email, `skee21@proton.me`")

@tree.command(name="kick", description="Kicks a member")
async def kick(interaction, user: Member, reason: Optional[str] = "No reason provided"):
  userid = interaction.user.id
  memberid = user.id

  if interaction.guild.me.guild_permissions.kick_members:
    if interaction.user.guild_permissions.kick_members:
      await interaction.response.send_message(f"{user.mention} has been kicked successfully")
      await user.kick(reason=reason)
    else:
      await interaction.response.send_message(":middle_finger: :middle_finger:")
  else:
    await interaction.response.send_message("gimme the necessary permission first dummies.")

@tree.command(name="mute", description="mutes a member")
async def mute(interaction, user: Member, duration: int = 1440, reason: Optional[str]= "No reason"):
  if interaction.guild.me.guild_permissions.moderate_members:
    if interaction.user.guild_permissions.moderate_members:
      time = datetime.timedelta(minutes=duration)
      await user.timeout(time, reason=reason)
      await interaction.response.send_message(f"user muted for {time} successfully.")
    else:
      await interaction.response.send_message(":middle_finger: :middle_finger:")
  else:
    interaction.response.send_message("gimme the necessary permissions dummy!")

@tree.command(name="unmute", description="unmutes a member")
async def unmute(interaction, user: Member):
  if interaction.guild.me.guild_permissions.moderate_members:
    if interaction.user.guild_permissions.moderate_members:
      await user.edit(timed_out_until=None)
      await interaction.response.send_message(f"{user.mention} has been unmuted successfully!")
    else:
      await interaction.response.send_message(":middle_finger:")
  else:
    await interaction.response.send_message("gimme the necessary permissions dummy!")

@tree.command(name='ban', description='bans a member')
async def ban(interaction, user: Member, reason: Optional[str] = "no reason"):
  if interaction.guild.me.guild_permissions.ban_members:
    if interaction.user.guild_permissions.ban_members:
      await interaction.response.send_message(f"{user.name} has been banned for {reason}")
      await interaction.guild.ban(user, reason=reason, delete_message_days=1)
    else:
      await interaction.response.send_message(":middle_finger:")
  else:
    await interaction.response.send_message("give me the necessary permissions first dummy.")

@tree.command(name="unban", description="unban a prisoner")
async def unban(interaction, user: str, reason: Optional[str]):
  user = await client.fetch_user(user)
  if interaction.guild.me.guild_permissions.ban_members:
    if interaction.user.guild_permissions.ban_members:
      await interaction.guild.unban(user, reason=reason)
      await interaction.response.send_message(f"{user.name} has been unbanned.")
    else:
      await interaction.response.send_message(":middle_finger:")
  else:
    await interaction.response.send_message("give me the necessary permissions first dummy.")

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
    av = user.avatar.url
    embed = discord.Embed(title=f"pfp of {user.display_name}")
    embed.set_image(url=av)
    await interaction.response.send_message(embed=embed)

@tree.command(name="server_avatar", description="shows the avatar of server")
async def server_avatar(interaction):
  guild = interaction.guild
  embed = discord.Embed(title=f"Server PFP of {guild.name}")
  embed.set_image(url=guild.icon.url)
  await interaction.response.send_message(embed=embed)

@tree.command(name="profile", description="shows warrior profile")
async def profile(interaction, user: Optional[Member] = None):
  if user is None:
    user = interaction.user

  userid = str(user.id)
  mydb.execute("SELECT UID, level, army_space, exp, clan FROM users WHERE UID = %s", (userid,))
  result = mydb.fetchone()

  if result:
    uid, level, army_space, exp, clan = result
    embed = discord.Embed(title=f"Profile of {user.display_name}", color=0xe91e63)
    embed.set_thumbnail(url=user.display_avatar)
    embed.add_field(name="Level:", value=level, inline=True)
    embed.add_field(name="XP:", value=f"{exp}/100", inline=True)
    embed.add_field(name="Army Space:", value=army_space, inline=False)
    embed.add_field(name="Clan:", value=clan, inline=False)
    await interaction.response.send_message(embed=embed)
  else:
    await interaction.response.send_message("User is not registered.")

@tree.command(name="balance", description="shows your treasury and wallet balance")
async def balance(interaction):
  user = interaction.user
  userid = user.id
  mydb.execute("SELECT treasury, wallet FROM users WHERE uid = %s", (userid,))
  result = mydb.fetchone()

  if result:
    treasury, wallet = result
    embed = discord.Embed(title=f"Balance of {user.display_name}", color=0xe91e63)
    embed.set_thumbnail(url=user.display_avatar)
    embed.add_field(name="Treasury:", value= treasury, inline=False)
    embed.add_field(name="Wallet:", value= wallet, inline=False)
    await interaction.response.send_message(embed=embed)
  else:
    await interaction.response.send_message("you are not registered.")

@tree.command(name="credit", description="withdraw money from treasury")
async def credit(interaction, amount: int):
  user = interaction.user
  userid = str(user.id)
  mydb.execute("SELECT treasury, wallet FROM users WHERE uid = %s", (userid,))
  result = mydb.fetchone()

  if result:
    treasury, wallet = result
    if treasury >= amount:
      balance_wallet = wallet + amount
      balance_treasury = treasury - amount
      mydb.execute("update users set wallet = %s, treasury = %s where uid = %s", (balance_wallet, balance_treasury, userid))
      myd.commit()
      await interaction.response.send_message(f"withdrew {amount} from treasury. Remaining balance:```treasury: {balance_treasury}\n wallet: {balance_wallet}```")
      #await balance(interaction)
    else:
      await interaction.response.send_message("insufficient amount in your treasury")
  else:
    await interaction.response.send_message("you are not registered.")

@tree.command(name="debit", description="add money to treasury")
async def debit(interaction, amount: int):
  user = interaction.user
  userid = user.id
  mydb.execute("SELECT treasury, wallet FROM users WHERE uid = %s", (userid,))
  result = mydb.fetchone()
  if result:
    treasury, wallet = result
    if wallet >= amount:
      balance_wallet = wallet - amount
      balance_treasury = treasury + amount
      mydb.execute("update users set wallet = %s, treasury = %s where uid = %s", (balance_wallet, balance_treasury, userid))
      myd.commit()
      await interaction.response.send_message(f"added {amount} to treasury. Remaining balance:```treasury: {balance_treasury}\n wallet: {balance_wallet}```")
      #await balance(interaction)
    else:
      await interaction.response.send_message("insufficient amount in your wallet")
  else:
    await interaction.response.send_message("you are not registered.")

async def get_balance_data(user_id):
  mydb.execute("SELECT treasury, wallet FROM users WHERE uid = %s", (user_id,))
  result = mydb.fetchone()
  if result:
    treasury, wallet = result
    return treasury, wallet
  else:
    raise ValueError("User is not registered")

@tree.command(name="give", description="give money to another user")
async def give(interaction, user: Member, amount: int):
  receiverid = user.id
  senderid = interaction.user.id

  if interaction.user == user:
    await interaction.response.send_message("trying to be smart hooman?")
    return

  sender_treasury, sender_wallet = await get_balance_data(senderid)
  if sender_wallet >= amount:
    sender_wallet -= amount
    recipient_treasury, recipient_wallet = await get_balance_data(receiverid)
    recipient_wallet += amount
    mydb.execute("UPDATE users SET wallet = %s, treasury = %s WHERE uid = %s", (sender_wallet, sender_treasury, senderid))
    mydb.execute("UPDATE users SET wallet = %s, treasury = %s WHERE uid = %s", (recipient_wallet, recipient_treasury, receiverid))
    myd.commit()
    await interaction.response.send_message(f"you successfully gave {amount} to {user.mention}")
  else:
    await interaction.response.send_message("you are broke lmao")

class train_button(discord.ui.Button):
   def __init__(self):
     super().__init__(label='Train', style=discord.ButtonStyle.green)
   async def callback(self, interaction):
     await interaction.response.send_message('In development, try later', ephemeral=True)

class dropdown_troops(discord.ui.Select):
  def __init__(self):
    mydb.execute("SELECT name FROM troops")
    result = mydb.fetchall()
    options = [discord.SelectOption(label=row[0], value=row[0]) for row in result]

    super().__init__(placeholder="choose an option", min_values=1, max_values=1, options=options)

  async def callback(self, interaction):
    selected_values = interaction.data['values']
    for troop_name in selected_values:
      mydb.execute("SELECT * FROM troops WHERE name = %s", (troop_name,))
      result = mydb.fetchone()
      name, level, atk, hp, req_level, cost, army_space = result
      embed = discord.Embed(title=f"Troop: {name}", color=0xe91e63)
      embed.add_field(name="Level:", value=level, inline=True)
      embed.add_field(name="Atk:", value=atk, inline=True)
      embed.add_field(name="HP:", value=hp, inline=True)
      embed.add_field(name="Required Level:", value=req_level, inline=False)
      embed.add_field(name="Cost:", value=cost, inline=True)
      embed.add_field(name="Army Space:", value=army_space, inline=True)
      view = discord.ui.View().add_item(train_button())
      await interaction.response.send_message(embed=embed, view=view)

class dropdownview_troops(discord.ui.View):
  def __init__(self):
    super().__init__()
    self.add_item(dropdown_troops())

@tree.command(name="troops", description="view info on troops")
async def troops(interaction):
  view = dropdownview_troops()
  await interaction.response.send_message("Choose a troop to view its information:", view=view)

class fight_button(discord.ui.Button):
  def __init__(self):
    super().__init__(label='Fight', style=discord.ButtonStyle.red)
  async def callback(self, interaction):
    await interaction.response.send_message('In development, try later', ephemeral=True)

class dropdown_enemies(discord.ui.Select):
  def __init__(self):
    mydb.execute("SELECT name FROM enemies")
    result = mydb.fetchall()
    options = [discord.SelectOption(label=row[0], value=row[0]) for row in result]

    super().__init__(placeholder="choose an option", min_values=1, max_values=1, options=options)

  async def callback(self, interaction):
    selected_values = interaction.data['values']
    for enemy_name in selected_values:
      mydb.execute("SELECT * FROM enemies WHERE name = %s", (enemy_name,))
      result = mydb.fetchone()
      name, atk, hp, req_level, cost, xp_bonus, coin_bonus = result
      embed = discord.Embed(title=f"Enemy: {name}", color=0xe91e63)
      embed.add_field(name="Atk:", value=atk, inline=True)
      embed.add_field(name="HP:", value=hp, inline=True)
      embed.add_field(name="Required Level:", value=req_level, inline=False)
      embed.add_field(name="Cost:", value=cost, inline=False)
      embed.add_field(name="XP bonus:", value=xp_bonus, inline=True)
      embed.add_field(name="Coin bonus:", value=coin_bonus, inline=True)
      view = discord.ui.View().add_item(fight_button())
      await interaction.response.send_message(embed=embed, view=view)

class dropdownview_enemies(discord.ui.View):
  def __init__(self):
    super().__init__()
    self.add_item(dropdown_enemies())
    
@tree.command(name="enemies", description="view enemies info")
async def enemies(interaction):
  view = dropdownview_enemies()
  await interaction.response.send_message("Choose a enemy to view its information:", view=view)

class join_button(discord.ui.Button):
  def __init__(self):
    super().__init__(label='Join', style=discord.ButtonStyle.green)
  async def callback(self, interaction):
    userid = interaction.user.id
    clan_name = interaction.data['values'][0]
    mydb.execute("SELECT uid, clan FROM users WHERE userid = %s", (userid,))
    result = mydb.fetchall()
    if result:
      current_clan = result['clan']
      if current_clan:
        await interaction.response.send_message(f"You are already in a clan")
      else:
        mydb.execute("UPDATE users SET clan = %s WHERE userid = %s", (clan_name, userid))
        mydb.commit()
        await interaction.response.send_message(f"You have joined the clan: {clan_name}", ephemeral=True)
    else:
      await interaction.response.send_message("You are not registered. Please use /register to register")

class info_button(discord.ui.Button):
  def __init__(self):
    super().__init__(label='clan info', style=discord.ButtonStyle.green)
  async def callback(self, interaction):
    await interaction.response.send_message('In development, try later', ephemeral=True)

class clan_buttons(discord.ui.View):
  def __init__(self):
    super().__init__()
    self.add_item(join_button())
    self.add_item(info_button())

class dropdown_clans(discord.ui.Select, discord.ui.View):
  def __init__(self):
    mydb.execute("SELECT * FROM clans")
    clans_data = mydb.fetchall()
    options = [discord.SelectOption(label=row[0], value=row[0]) for row in clans_data]

    super().__init__(placeholder="choose an option", min_values=1, max_values=1, options=options)

  async def callback(self, interaction):
    mydb.execute("SELECT * FROM clans")
    clans_data = mydb.fetchall()
    selected_value = interaction.data['values'][0]
    for clan_info in clans_data:
      clan_name, leader, members, rank = clan_info
      if clan_name == selected_value:
        embed = discord.Embed(title=f"Name: {clan_name}", color=0xC71585)
        embed.add_field(name='Leader', value=f"<@{leader}>")
        embed.add_field(name='Members', value=members)
        embed.add_field(name='Rank', value=rank)
        #view = discord.ui.View().add_item(clan_buttons())
        view = clan_buttons()
        await interaction.response.send_message(embed=embed, view=view)

class dropdownview_clans(discord.ui.View):
  def __init__(self):
    super().__init__()
    self.add_item(dropdown_clans())
    
@tree.command(name="clans", description="view the list of clans")
async def clans(interaction):
  view = dropdownview_clans()
  await interaction.response.send_message("Choose a clan to view its information:", view=view)

keep_alive()

my_secret = os.environ['TOKEN']
client.run(my_secret)
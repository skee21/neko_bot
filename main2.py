import os
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive
from replit import db
import asyncio
import datetime
import logging
import asyncio
import math
import instaloader

#setting up bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(intents=intents , command_prefix='!')

#logging.basicConfig(
 # filename='discord.log',
  #format='%(asctime)s [%(levelname)s]: %(message)s',
  #datefmt='%Y-%m-%d %H:%M:%S',
  #level=logging.INFO)

muted_users = {}

xp_db = {}
level_db = {}
troops_db = {
  'goblins': {
    'name': 'Goblin',
    'img': 'https://i.pinimg.com/originals/58/36/f6/5836f663fc34e15054914ee2594be49b.jpg',
    'level': 1,
    'atk': 10,
    'hp': 50,
    'req_level': 1,
    'cost': 40,
    'army space': 2,
  }
}
monster_db={
  'slime':
  {
    'name':'slime',
    'img':'https://www.transformationmarketing.com/wp-content/uploads/2015/10/Slime-Monster.jpg',
    'hp': 50,
    'atk': 10,
    'req_level': 1,
    'xp_bonus':'10 xp',
    'coin_bonus': 1000,
    'cost': 200,
  },
  'bear':
  {
    'name': 'bear',
    'img': 'https://www.wallpaperflare.com/static/904/602/463/digital-art-bears-armor-fantasy-art-wallpaper.jpg',
    'hp': 150,
    'atk': 30,
    'req_level': 3,
    'xp_bonus': '50 xp',
    'coin_bonus': 3000,
    'cost': 500,
  }
}
clan_db = {
  'Nameless':
  {
    'name': 'nameless',
    'leader': '1077648874002460672',
    'img': 'https://vk.gy/images/105625-nameless-cleaned-logo.png',
    'motto': 'We are the nameless and no one can control us.',
  },
  'Necromancers':
  {
    'name': 'necromancers',
    'leader': '855123468252086292',
    'img': 'https://yt3.ggpht.com/a/AATXAJzPsHmpc4hYKQXwN95T36fUAdz6217M_ofPdw=s900-c-k-c0xffffffff-no-rj-mo',
    'motto': 'Lets play with the dead, after killing the one alive...',
  },
  'Valhalla':
  {
    'name': 'valhalla',
    'leader': '607051974382452739',
    'img': 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.valhalla.lu%2Flogofullmobile4.png&f=1&nofb=1&ipt=7b54bafbeb15bf06bf4f206627eb0732c853b80b66844a577088dd0b34c079c4&ipo=images',
    'motto': 'come join us, lets not just conquer the world but even the gods',
  }
}
members_db = {
  "Nameless":{'1077648874002460672', },
  "Necromancers":{'855123468252086292', },
  "Valhalla":{'607051974382452739',},
}
db['clan_data'] = clan_db
army_db = {}

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  await bot.change_presence(activity=discord.Game(name="with your mom"))
    #logging.info("Bot started.")

  bot.loop.create_task(check_mute_expiry())

@bot.command()
async def dtbs(ctx):
  if str(ctx.author.id) == '1077648874002460672':
    keys = db.keys()
    await ctx.reply(keys)
  else:
    await ctx.reply("bitch! it's devs only command!")
    #logging.info("database has been accessed")

@bot.command()
async def reset(ctx):
  if str(ctx.author.id) == '1077648874002460672':
    await ctx.reply("are you sure you want to reset?")
    
    def check(msg):
      return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ['yes', 'no']

    try:
      response = await bot.wait_for('message', check=check, timeout=60)
      if response.content.lower() == "yes":
        keys = db.keys()
        for key in keys:
          del db[key]
        await ctx.send("all users have been reset")
      else:
        await ctx.send("no changes were made.")
    except asyncio.TimeoutError:
      await ctx.send("<@1077648874002460672> you timed out, no changes were made.")
  else:
    await ctx.reply("bitch, it's devs only command!")

@bot.command()
async def clans(ctx):
  for clan_name, clan_info in clan_db.items():
    embed = discord.Embed(title=f"Name: {clan_name}", color=0xC71585)
    embed.set_thumbnail(url=clan_info['img'])
    leader = clan_info['leader']
    embed.add_field(name='Leader', value=f"<@{leader}>")
    embed.add_field(name="Motto", value=clan_info['motto'], inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def join(ctx, *, name: str=None):
  userid = str(ctx.author.id)
  user = db[userid]
  if name is None:
    await ctx.reply("please enter the name of clan you wanna join.")
    return

  if 'clan' in user and user['clan']:
    await ctx.reply("you are already in a clan.")
  else:
    if name not in clan_db:
      await ctx.reply("clan not found, remember that clan names are case sensitive.")
    else:
      user['clan'] = name
      await ctx.reply(f"you have successfully joined the {name} clan")

@bot.command()
async def members(ctx, name: str=None):
  if name is None:
    await ctx.reply("enter the clan name please.")
    return

  if name not in clan_db:
    await ctx.reply("invalid name, use !clan to see available clans and keep in mind, names are case sensitive.")
  else:
    membs = len(members_db[name])
    await ctx.send(f"Total members in clan {name} are {membs}.")

@bot.command()
async def leave(ctx):
  userid = str(ctx.author.id)
  user = db[userid]

  if 'clan' not in user or not user['clan']:
    await ctx.reply("you are not a member of any clan.")
    return
  
  clan = user['clan']
  clan_info = clan_db[clan]

  if userid == clan_info['leader']:
    await ctx.reply("you can't leave because you are the leader lmao. Transfer ownership before leaving.")
    return
    
  await ctx.reply(f"are you sure you want to leave {user['clan']}?")

  def check(msg):
    return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ['yes', 'no']

  try:
    response = await bot.wait_for('message', check=check, timeout=20)
    if response.content.lower() == "yes":
      await ctx.reply(f"you have successfully left the {user['clan']}.")
      del user['clan']
    else:
      await ctx.send("alright, still a member yay!")
  except asyncio.TimeoutError:
    await ctx.send("timed out, take decisions quickly.")


@bot.command()
async def profile(ctx, member:discord.Member = None):
  if member is None:
    member = ctx.author
    
  userid = str(member.id)
  user = db[userid]
  clan_name = user.get('clan', 'Not in a clan')
  if clan_name in clan_db:
    clan_r = clan_db[clan_name]
    leader_id = str(clan_r['leader'])
  else:
    leader_id = "69"

  if userid in xp_db:#Check if the user is in the XP db
    xp = xp_db[userid]['xp']
    level = 1 + xp // 100  # 100 XP required to level up
  else:
    xp = 1  # Default XP for new users
    level = 1
    army_space = 30

  level_db[userid] = {'level': level, 'army_space': army_space}

  user_avatar = member.avatar.url

  embed = discord.Embed(title=f"Profile for {member.name}", color=0xC71585)
  embed.set_thumbnail(url=user_avatar)
  embed.add_field(name="Level", value=level, inline=True)
  embed.add_field(name="XP", value=f"{xp}/100", inline=True)
  embed.add_field(name="Army space", value=army_space, inline=False)
  if leader_id == userid:
    embed.add_field(name='Clan', value=f"{clan_name} (leader)", inline=False)
  else:
    embed.add_field(name='Clan', value=clan_name, inline=False)  

  await ctx.send(embed=embed)
  #logging.info(f"{ctx.author.id} checked profile ")

@bot.command()
async def outcast(ctx, user: discord.Member = None):
  if user is None:
    await ctx.reply("Please mention the user.")
    return

  author_id = str(ctx.author.id)
  user_id = str(user.id)

  if author_id == user_id:
    await ctx.reply("You can't kick yourself.")
    return

  author_info = db.get(author_id)
  user_info = db.get(user_id)

  if author_info is None:
    await ctx.reply("You are not in a clan.")
    return

  author_clan = author_info.get('clan')
  user_clan = user_info.get('clan')

  if user_clan is None:
    await ctx.reply(f"{user.mention} is not in any clan.")
    return

  if author_clan == user_clan:
    clan_info = clan_db.get(author_clan)
    leader_id = clan_info.get('leader')

    if author_id == leader_id:
      await ctx.reply(f"Are you sure you want to outcast {user.mention}? (Reply with 'yes' or 'no')")

      def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ['yes', 'no']

      try:
        response = await bot.wait_for('message', check=check, timeout=20)

        if response.content.lower() == "yes":
          user_info['clan'] = None  # Remove the clan from user's info
          await ctx.reply(f"{user.mention} has been outcasted.")
        else:
          await ctx.send("Good decision, why throw away free labor?")
      except asyncio.TimeoutError:
          await ctx.send("Timed out, take decisions quickly.")
    else:
      await ctx.reply("Know your place, you are not the clan leader.")
  else:
    await ctx.reply("You both are not in the same clan.")

@bot.command()
async def invite(ctx, user: discord.Member = None):
  if user is None:
    await ctx.reply("Mention the user bitch, who are you inviting your dead grandma?")
    return

  author_id = str(ctx.author.id)
  author_info = db[author_id]
  user_id = str(user.id)
  author_clan = author_info.get('clan')

  if author_clan is None:
    await ctx.send("You are not in a clan. You need to be in a clan to invite others.")
    return

  clan_info = clan_db[author_clan]
  leader_id = clan_info['leader']

  if author_id != leader_id:
    await ctx.send("Only the clan leader can invite others to the clan.")
  else:
    user_clan = db[user_id].get('clan')

    if user_clan is not None:
      await ctx.send(f"{user.mention} is already in a clan.")
    else:
      await ctx.send(f"{user.mention}, do you want to join the {author_clan}? (Reply with 'yes' or 'no')")

      def check(msg):
        return msg.author == user and msg.channel == ctx.channel and msg.content.lower() in ['yes', 'no']

      try:
        response = await bot.wait_for('message', check=check, timeout=20)
        if response.content.lower() == "yes":
          db[user_id]['clan'] = author_clan 
          await ctx.reply(f"{user.mention} has successfully joined the {author_clan}.")
        else:
          await ctx.send(f"{user.mention} has rejected the invitation to join your clan.")
      except asyncio.TimeoutError:
        await ctx.send("Timed out. Make decisions quickly.")

@bot.command()
async def mute(ctx, user: discord.Member=None, time_in_minutes: int = 5, *, reason: str = None):
  #logging.info(f"mute command used by {ctx.author.id} for {user.id}")
  if user is None:
    await ctx.reply("Please mention the user")
    return
  
  if time_in_minutes <= 0:
    await ctx.reply("please enter a valid duration for mute.")
    return
  
  if ctx.author.guild_permissions.mute_members:
    if ctx.guild.me.guild_permissions.mute_members:
      if user == ctx.author:
        await ctx.send("Dummy you cannot mute yourself.")
      else: # Get the mute role (create it if it doesn't exist)
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role is None:
          mute_role = await ctx.guild.create_role(
              name="Muted",
              reason="To mute users",
          )
          for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False)
      
      # Add the mute role to the user
      await user.add_roles(mute_role, reason=reason)
      #logging.info(f"{user} muted")
  
      # Inform the user about the mute via DM
      if reason:
        await user.send(f"You have been muted in {ctx.guild.name} for {time_in_minutes}. **REAON TO MUTE**: {reason}")
      else:
        await user.send(f"You have been muted in {ctx.guild.name} for {time_in_minutes} minutes.")
  
        # Inform the server about the mute
        if reason:
          await ctx.send(f"{user.mention} have been muted in {ctx.guild.name} for {time_in_minutes} :pensive:. **REAON TO MUTE**: {reason}")
        else:
          await ctx.send(f"{user.mention} has been muted for {time_in_minutes} minutes :pensive:.")
        #logging.info("sent mute info to server and DM")
  
        # Schedule an unmute task
        await asyncio.sleep(time_in_minutes * 60)  # Convert minutes to seconds
        await user.remove_roles(mute_role, reason="Mute duration expired.")
        await user.send("**yayy! you have been unmuted.**")
        #logging.info(f"{user.id} has been unmuted.")
    else:
      await ctx.reply("idiots, gimme the necessary permissions first!")
      #logging.info("failed to mute, missing permissions.")
  else:
    await ctx.reply("you can't use this command, skill issues :joy:")
    #logging.info(f"mute command failed by {ctx.author.id}, user doesn't have permission to mute.")

async def check_mute_expiry():
  now = datetime.datetime.now()
  to_remove = []
  for user_id, unmute_time in muted_users.items():
      if now >= unmute_time:
        guild_id, member_id = user_id.split("-")
        guild = bot.get_guild(int(guild_id))
        member = guild.get_member(int(member_id))
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
          await member.remove_roles(mute_role, reason="Mute duration expired.")
        to_remove.append(user_id)
  for user_id in to_remove:
    muted_users.pop(user_id, None)

@bot.command()
async def unmute(ctx, *, user:discord.Member):
  #logging.info(f"{ctx.author.id} used unmute command for {user.id}")
  if user is None:
    await ctx.reply("please mention the user you want to unmute.")
    return
    
  if ctx.author.guild_permissions.mute_members:
    if user == ctx.author:
      await ctx.send("dummy, you tagged yourself.")
    else:
      mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

    await user.remove_roles(mute_role, reason="Mute duration expired.")
    #logging.info(f"unmuted {user.id}")
    await ctx.send(f"{user.mention} has been unmuted :thumbsup:")
    await user.send("**yayy! you have been unmuted.**")
  else:
    await ctx.reply("you don't have the permission to use this command!")
    #logging.info(f"{ctx.author.id} tried to unmute {user.id} but failed.")

@bot.command()
async def kick(ctx, user:discord.Member, reason: str = None):
  #logging.info(f"{ctx.author.id} used kick command.")
  if ctx.author.guild_permissions.kick_members:
    if user == ctx.author:
      await ctx.reply("hehe silly, you tagged yourself.")
    else:
      if ctx.guild.me.guild_permissions.kick_members:
        
        if reason is not None:
          await user.send(f"you have been kicked from {ctx.guild.name} due to {reason} :pensive:")
          await ctx.reply(f"{user.name} has been kicked due to {reason} :joy:")
          await user.kick(reason=reason)
        else:
          await user.send(f"you have been kicked from {ctx.guild.name} :pensive:")
          await ctx.reply(f"{user.name} has been kicked :joy:")
          await user.kick(reason=reason)
        #logging.info(f"kicked {user.id}")
      else:
        await ctx.reply("idiots, gimme the permissions to use this command first.")
        #logging.info("couldn't kick due to missing permission.")
  else:
    await ctx.reply("you don't have permissions to use this command lol skill issues :joy:")
    #logging.info("couldn't kick since user is missing permissions.")

@bot.command()
async def balance(ctx, user: discord.Member = None):
  if user is None:
    author_id = str(ctx.author.id)
    if author_id in db:
      embed = discord.Embed(title=f"Balance of user {ctx.author.display_name}", color=0xC71585)
      embed.set_thumbnail(url=ctx.author.avatar.url)
      embed.add_field(name="Purse:", value=f"${db[author_id]['purse']}", inline=False)
      embed.add_field(name="Treasury:", value=f"${db[author_id]['treasury']}", inline=False)
      await ctx.send(embed=embed)
    else:
      await ctx.reply("You're not registered.")
  else:
    user_id = str(user.id)
    if user_id in db:
      embed = discord.Embed(title=f"Balance of user {user.display_name}", color=0xC71585)
      embed.set_thumbnail(url=user.avatar.url)
      embed.add_field(name="Purse:", value=f"${db[user_id]['purse']}", inline=False)
      embed.add_field(name="Treasury:", value=f"${db[user_id]['treasury']}", inline=False)
      await ctx.send(embed=embed)
    else:
      await ctx.reply(f"{user.mention} is not registered.")


@bot.event
async def on_message(message):
  await bot.process_commands(message)
  msg = message.content.lower()
  if message.author == bot.user:
    return

  #setting up database to register users
  knownuser = False
  keys = db.keys()
  if str(message.author.id) in keys:
    knownuser = True
  else:
    db[str(message.author.id)] = {"purse": 5000, "treasury": 10000, "relics": None}

  if msg.startswith('hello'):
    await message.channel.send(f'hello <@{message.author.id}>, you virgin')
    await message.author.send("you lost bbg? :smirk:")
    #logging.info("replied to a hello message")
    
def checkuser(id):
  logging.info("checking if user is registered or not.")
  keys = db.keys()
  if id in keys:
    return True
  else:
    return False

@bot.command()
async def debit(ctx, amount: int = 0):
  if amount <= 0: 
    await ctx.reply("Please provide a valid amount to debit.")
    return

  userid = str(ctx.author.id)
  if checkuser(userid): #checks if the user is registered
    if amount <= db[userid]['purse']:
      db[userid]['treasury'] += amount
      db[userid]['purse'] -= amount
      #logging.info(f"{ctx.author.id} debited {amount} to their treasury.")
    else:
      await ctx.reply("Insufficient balance in your purse.")
      #logging.info("debit failed due to insufficient balance.")
  await balance(ctx)

@bot.command()
async def credit(ctx, amount: int = 0):
  if amount <= 0: #amount can't be less than 0
    await ctx.reply("Please provide a valid amount to credit.")
    return

  userid = str(ctx.author.id)
  if checkuser(userid): #checks if user is registered
    if amount <= db[userid]['treasury']:
      db[userid]['purse'] += amount
      db[userid]['treasury'] -= amount
      #logging.info(f"{ctx.author.id} credited {amount} to their treasury.")
    else:
      await ctx.reply("Insufficient balance in your treasury.")
      #logging.info("credit failed due to insufficient balance.")
  await balance(ctx)

@bot.command()
async def troops(ctx):
  userid = str(ctx.author.id)
  if userid not in db:
    await ctx.reply("you are not registered")
    return

  user_data = db[userid]
  user_level = user_data.get('level', 1)
    
  avatar = ctx.author.avatar.url
  embed = discord.Embed(title=f"Troops owned by {ctx.author.name}", color=0xC71585)
  embed.set_thumbnail(url=avatar)
  
  for troop_name, troop_info in troops_db.items():
    if user_level >= troop_info['req_level']:
      army_db['troops'] = {}
      embed.add_field(name=troop_name, value=f"Level: {troop_info['level']}", inline=True)

  await ctx.send(embed=embed)
      
@bot.command()
async def train(ctx, troop_name: str, amount: int = None):
  troop_name = troop_name.lower()
  if amount is None:
    amount = 1

  userid = str(ctx.author.id)
  if userid not in db:
    await ctx.reply("You are not registered.")
    return

  user_data = db[userid]
  user_level = user_data.get('level', 1)

  # Check if the troop exists
  troop_info = troops_db.get(troop_name)
  if not troop_info:
    await ctx.reply(f"baka! {troop_name} doesn't exist")
    return

  space_needed = amount * troop_info.get('army space', 0)
  space_avl = user_data.get('army_space', 30)

  # Check if user has enough army space
  if space_needed > space_avl:
    await ctx.reply("baka! not enough army space")
    return

  credit_req = amount * troop_info.get('cost')

  if credit_req > user_data['purse']:
    await ctx.reply("baka! you are broke, maybe withdraw money from treasury or beg from friends")
    return

  if user_level >= troop_info.get('req_level', 1):
    if 'troops' not in user_data:
      user_data['troops'] = {}

    user_data['purse'] -= credit_req
    trained_troops = user_data['troops']
    trained_troops[troop_name] = trained_troops.get(troop_name, 0) + amount
    user_data['troops'] = trained_troops

    await ctx.reply(f"you have successfully trained {amount} {troop_name}")
    await balance(ctx)
  else:
    await ctx.reply("Baka, you don't have that troop unlocked. Use !troops to check troops you own.")


@bot.command()
async def army(ctx):
  userid = str(ctx.author.id)
  if userid not in db:
    await ctx.reply("You are not registered.")
    return

  user_data = db[userid]
  trained_troops = user_data.get('troops', {})

  if not trained_troops:
    await ctx.reply("Baka! Train some troops before running this command.")
    return

  user_avatar = ctx.author.avatar.url

  embed = discord.Embed(title=f"Troops Trained by {ctx.author.name}", color=0xC71585)
  embed.set_thumbnail(url=user_avatar)

  for troop, count in trained_troops.items():
    embed.add_field(name=f"Troop: {troop}", value=f"Amount: {count}", inline=True)

  await ctx.reply(embed=embed)

@bot.command()
async def troopinfo(ctx, *, name: str=None):
  if name is None:
    await ctx.reply("baka you forgot to write the troop's name!!")
    return

  name = name.lower()
  if name not in troops_db:
    await ctx.reply("troop not found!")
    return

  troop_info = troops_db[name] 
  embed = discord.Embed(title=f"Troop Info: {troop_info['name']}", color=0xC71585)
  embed.set_thumbnail(url=troop_info['img'])
  embed.add_field(name="Name:", value=troop_info['name'], inline=False)
  embed.add_field(name="Level:", value=troop_info['level'], inline=False)
  embed.add_field(name="Attack:", value=troop_info['atk'], inline=False)
  embed.add_field(name="HP", value=troop_info['hp'], inline=False)
  embed.add_field(name="Required Level:", value=troop_info['req_level'], inline=False)
  embed.add_field(name="Training cost:", value=troop_info['cost'], inline=False)
  embed.add_field(name="Army Space:", value=troop_info['army space'], inline=False)

  await ctx.send(embed=embed)
  
@bot.command()
async def monsters(ctx):
    embed = discord.Embed(title="List of Monsters Available", color=0xC71585)

    for monster_name, monster_info in monster_db.items():
        # Add each monster's name, image, and required level to the embed
        embed.add_field(name=monster_name, value=f"Required Level: {monster_info['req_level']}", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def monsterinfo(ctx, *, name: str=None):
  if name is None:
    await ctx.reply("Please provide the name of monster you wanna check")
    return

  name = name.lower()
  if name not in monster_db:
    await ctx.reply("This monster is not present!!")
    return

  mons_info = monster_db[name] 

  embed = discord.Embed(title=f"Monster Info: {mons_info['name']}", color=0xC71585)
  embed.set_thumbnail(url=mons_info['img'])
  embed.add_field(name="Name:", value=mons_info['name'], inline=False)
  embed.add_field(name="Required level to fight:", value=mons_info['req_level'])
  embed.add_field(name="Atk:", value=mons_info['atk'], inline=False)
  embed.add_field(name="HP", value=mons_info['hp'] ,inline=False)
  embed.add_field(name="Fighting cost:", value=mons_info['cost'] ,inline=False)
  embed.add_field(name="Coins bonus:", value=mons_info['coin_bonus'] ,inline=False)
  embed.add_field(name="XP bonus:", value=mons_info['xp_bonus'] ,inline=False)

  await ctx.reply(embed=embed)

mons_name = ""

@bot.command()
async def avatar(ctx, user:discord.Member=None):
  global mons_name
  if user is None:
    user = ctx.author
    
  avatar = user.avatar.url
  embed = discord.Embed(title=f"PFP of {user.name}", color=0xC71585)
  embed.set_image(url=avatar)
  await ctx.send(embed=embed)

@bot.command()
async def fight(ctx, *, name: str= None):
  user = ctx.author
  userid = str(ctx.author.id)
  user_data = db.get(userid, {"troops": {}})
  db[userid] = user_data
  trained_troops = user_data.get('troops')

  if name is None:
    await ctx.reply("enter the name of monster you wanna fight.")
  else:
    name = name.lower()
    if name not in monster_db:
      await ctx.reply("this monster doesn't exists!")
    else:
      monster_info = monster_db.get(name)
      user_info = db[userid]
      user_level = user_info.get('level', 1)
      req_level = monster_info.get('req_level')
      if user_level < req_level:
        await ctx.reply("you aren't strong enough to fight this monster yet. Level up and get stronger first.")
      else:
        if ctx.guild.me.guild_permissions.manage_channels:
          guild = ctx.guild
          overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
          }
          channel_name = f"{user.name}'s-battlefield"
          battlefield = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, category=None)
          await ctx.reply(f"please head to {battlefield.mention} to continue.")
          await battlefield.send(f"{user.mention} please start your battle here.")
          embed = discord.Embed(title=f"{name}", color=0xC71585)
          embed.set_image(url=monster_info['img'])
          await battlefield.send(embed=embed)
          user_info['active_monster'] = name
          print(user_info['active_monster'])
        else:
          await ctx.send("I am missing permissions to create channels. please contact mods.")
  
@bot.command()
async def deploy(ctx, name: str=None, amount: int=1):
  userid = str(ctx.author.id)
  user_data = db[userid]
  trained_troops = user_data.get('troops', {})
  monster = user_data['active_monster']
  print(monster)
  print(trained_troops)
  
  if name is None:
    await ctx.reply("Please enter the troop's name you want to deploy.")
    return

  name = name.lower()
  if name not in trained_troops:
    if name not in troops_db:
      await ctx.reply("Troop not found")
    else: 
      await ctx.reply("you have not trained this troop.")
  else:
    if amount <= 0:
      await ctx.reply("enter a valid amount.")
    else:
      if name in user_data['troops'] and user_data['troops'][name] >= amount:
        user_data['troops'][name] -= amount
        await ctx.send(f"deployed {amount} {troops}.")
        
        
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help to see available commands.")


keep_alive()

my_secret = os.environ['token']
bot.run(my_secret)
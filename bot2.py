from click import command
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import time
from datetime import datetime
import json
import requests
import praw
import random


reddit = praw.Reddit(
    client_id="Your reddit client id",
    client_secret="Your clien secret",
    username="Reddit username",
    password="Reddit pass",
    user_agent="python69 *any useragent*",
    check_for_async=False,
)


def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=get_prefix, pass_context=True)


@client.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = "!"

    with open("prefixes.json", "w") as f:
        prefixes = json.dump(prefixes, f)


@client.command(aliases=["cp"])
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", "w") as f:
        prefixes = json.dump(prefixes, f)
    await ctx.channel.send(f'Prefix changed to "{prefix}"')


now = datetime.now()
current_time = now.strftime("%H:%M:%S")


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


@client.command(aliases=["prefix"])
async def botprefix(ctx):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    pre = prefixes[str(ctx.guild.id)]
    await ctx.channel.send(f"Prefix {pre}")


sus_words = ["nigga", "faggot"]


@client.event
async def on_message(message):
    for words in sus_words:
        if words in message.content:
            await message.delete()
    await client.process_commands(message)




## fun for everyone ##


@client.command(aliases=["ins"])
async def insult(ctx, member: discord.Member = None):

    userName = member
    BASE_URL = "https://insult.mattbas.org"
    req_URL = f"{BASE_URL}/api/insult.txt?who={userName}"
    r = requests.get(req_URL)
    insultS = r.text
    # if not member:
    #     await ctx.channel.send(f"Atleast mention someone")
    try:
        if member == client.user:
            await ctx.channel.send(f"I won't insult myself :sunglasses:")
        else:
            if r.status_code == 200:
                await ctx.channel.send(insultS)
            else:
                await ctx.channel.send("Status Code Error!")
    except discord.ext.commands.errors.MemberNotFound:
        await ctx.channel.send("No user Found!")


@client.command(aliases=["memes"])
async def meme(ctx, *, subreddit="memes"):
    subs = []
    subreddit = reddit.subreddit("memes")

    top = subreddit.top(limit=50)
    for submission in top:
        subs.append(submission)

    random_sub = random.choice(subs)
    name = random_sub.title
    url = random_sub.url
    em = discord.Embed(title=name)
    em.set_image(url=url)
    await ctx.channel.send(embed=em)


@client.command(aliases=["play"])
async def playmusic(ctx, url: str):
    voicechannel = discord.utils.get(ctx.guild.voice_channels, name="general")
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice.is_connected():
        await voicechannel.connect()
    else:
        await ctx.say("Already is in voice channel!")

#music function  coming soon i am still learning!


## Multipurpose Bot Tools ##


@client.command(aliases=["ses"])
async def session(ctx):
    await ctx.channel.send("Logged in as {0.user}".format(client))


@client.command(aliases=["ct", "cnt"])
async def currenttime(ctx):
    timemebed = discord.Embed(title="Current Time", colour=discord.Colour.red())
    timemebed.add_field(name="Time", value=current_time, inline=True)
    await ctx.channel.send(embed=timemebed)


@client.command(aliases=["p"])
async def ping(ctx):
    ping = round(client.latency, 1)
    ping_embed2 = discord.Embed(
        title="Latency", description="Bot Latency", color=discord.Colour.green()
    )
    ping_embed2.add_field(name="Latency", value=ping, inline=True)
    await ctx.channel.send(embed=ping_embed2)


@client.command(aliases=["temp"])
async def temprature(ctx, *, city):

    API_KEY = "Your open weather api key *Only use openweather to use this function*"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    req_url = f"{BASE_URL}?appid={API_KEY}&q={city}"
    response = requests.get(req_url)

    if response.status_code == 200:
        data = response.json()

        weather = data["weather"][0]["description"]
        Temperature = str(round(data["main"]["temp"] - 273)) + "C°"
        Converter = round(data["main"]["temp"] - 273)
        TemperatureFar = str((Converter * 9 / 5) + 32) + "F°"

        pressure = str(data["main"]["pressure"]) + "hPa"
        humidity = str(data["main"]["humidity"]) + "%"
        windspeed = str(data["wind"]["speed"]) + "m/s"
        windtheta = str(data["wind"]["deg"]) + "°"

        embed1 = discord.Embed(
            title="Weather of: " + city, description="", color=discord.Colour.blue()
        )
        embed1.set_author(name="Bot Weather")
        embed1.set_thumbnail(url=ctx.author.avatar_url)
        embed1.add_field(name="Weather", value=weather, inline=False)
        embed1.add_field(name="Temprature", value=Temperature, inline=True)
        embed1.add_field(name="Temprature", value=TemperatureFar, inline=True)
        embed1.add_field(name="Presure", value=pressure, inline=False)
        embed1.add_field(name="Humidity", value=humidity, inline=False)
        embed1.add_field(name="Windspeed", value=windspeed, inline=False)
        embed1.add_field(name="WindAngle", value=windtheta, inline=False)
        await ctx.channel.send(embed=embed1)

    else:
        await ctx.channel.send("Enter Correct city name")


## Moderation Tools ##


@client.command(aliases=["cls"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=3):
    await ctx.channel.purge(limit=amount)


@client.command(aliases=["k", "kick"])
@commands.has_permissions(kick_members=True)
async def kickmember(ctx, member: discord.Member, *, reason="null"):
    # time.sleep(0.5)
    await member.send(
        f"You have been kicked out from { ctx.guild.name} reason specified: { reason } "
    )
    await member.kick(reason=reason)
    await ctx.channel.send(f"{ member} Kicked! ")


@client.command(aliases=["warn , wrn, w"])
@commands.has_permissions(ban_members=True)
async def warn(ctx, member: discord.Member, *, reason="null"):
    await member.send(f"You have been warned for reason: {reason}")
    await ctx.channel.send(f"{member} has been warned! reason: {reason}")


@client.command(aliases=["b", "ban"])
@commands.has_permissions(ban_members=True)
async def banmember(ctx, member: discord.Member, *, reason="null"):
    # time.sleep(0.5)
    await member.send(
        f"You have been banned from { ctx.guild.name} reason specified: { reason } "
    )
    await member.ban(reason=reason)
    await ctx.channel.send(f"{ member} Banned! ")


@client.command(aliases=["ub", "unban"])
@commands.has_permissions(ban_members=True)
async def unbanmembers(ctx, *, member):
    banned_members = await ctx.guild.bans()
    member_name, member_disc = member.split("#")

    for banned_entry in banned_members:
        user = banned_entry.user
        if (user.name, user.discriminator) == (member_name, member_disc):
            await ctx.guild.unban(user)
            await ctx.channel.send(member_name + "has been unbanned")
            return
    await ctx.channel.send("User Not Found!")


@client.command(aliases=["m", "mute"])
@commands.has_permissions(kick_members=True)
async def mutemember(ctx, member: discord.Member):
    muted_role = ctx.guild.get_role("A role Muted role id in INT format")
    await member.add_roles(muted_role)
    await ctx.channel.send(f"{member.mention} , has been muted")


@client.command(aliases=["um", "unmute"])
@commands.has_permissions(kick_members=True)
async def unmutemember(ctx, member: discord.Member):
    muted_role = ctx.guild.get_role(849632316388671528)
    await member.remove_roles(muted_role)
    await ctx.channel.send(f"{member.mention} , has been unmuted")


# Token
client.run("Your Bot Token Here")

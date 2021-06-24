import asyncio
import discord
import os
import nacl
import random
import youtube_dl

import helper_functions

from discord.ext import commands
from dotenv import load_dotenv


bot = discord.ext.commands.Bot(command_prefix = "$")

client = discord.Client()

players = {}

#------------------------------------------

youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

#-------------------------------------

@bot.event
async def on_ready():
    print(str(bot.user.name) + ' has connected to Discord!')
    guild = discord.utils.get(bot.guilds)
    # await bot.change_presence(activity = discord.Activity(
    #                       type = discord.ActivityType.watching,
    #                       name = 'time pass by...'))
    #await bot.change_presence(activity = discord.Game('League of Legends'))
    print("The value of guild is " + str(guild ))

@bot.command(name='hello', help="Says 'hello!' to the user")
async def hello(ctx):
    await ctx.send("Hello " + str(ctx.author.name) + "!")

@bot.command(name='habibi')
async def habibi(ctx):
    await ctx.send("Hello 7abibi!")

@bot.command(name='inspire')
async def inspire(ctx):
    quote = helper_functions.get_quote()
    await ctx.send(quote)
    await ctx.message.delete()

@bot.command(name='repeat')
async def repeat(ctx, *, message):
    await ctx.send(message)
    await ctx.message.delete()

@bot.command(name='rolldice', help='Simulates rolling dice.')
async def roll(ctx):
    dice = [
        str(random.choice(range(1, 6)))
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='LAWRENCE')
async def lawrence(ctx):
    if ctx.voice_client is None:
      voice_channel = ctx.message.author.voice
      if voice_channel != None:
        author = ctx.message.author
        channel = author.voice.channel
        await channel.connect()
        player = await YTDLSource.from_url("https://www.youtube.com/watch?v=-Abmb_Bkw38", loop=bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))
        await ctx.send("Playing LAWRENCE's theme")
      else:
        await ctx.send("SUMMER BODY READY")
        return

@bot.command(name='ALEX')
async def alex(ctx):
  Alex = ['https://cdn.discordapp.com/attachments/662498586503806978/713179030441951312/Alexsidewalk.gif', 'https://cdn.discordapp.com/attachments/662498586503806978/714981225156182077/AlexNewFrontWalk.gif']
  num = random.choice(range(0,2))
  await ctx.send(Alex[num])
  if ctx.voice_client.is_connected():
    async with ctx.typing():
        player = await YTDLSource.from_url("https://www.youtube.com/watch?v=E7oMBq1vkCM", loop=bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send("Playing ALEX's theme")

@bot.command(name='join')
async def join(ctx):
    voice_channel = ctx.message.author.voice
    if voice_channel != None:
      author = ctx.message.author
      channel = author.voice.channel
      await channel.connect()
    else:
      await ctx.send("Go into a voice channel habibi")

@bot.command(name='leave')
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command(name='play')
async def play_youtube(ctx, *, url):
    """Plays audio from youtube url"""
    # voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    if ctx.voice_client is None:
      voice_channel = ctx.message.author.voice
      if voice_channel != None:
        author = ctx.message.author
        channel = author.voice.channel
        await channel.connect()
      else:
        await ctx.send("Go into a voice channel habibi")
        return
    
    # if audio not playing, play link
    if not ctx.voice_client.is_playing():
      async with ctx.typing():
          player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
          ctx.voice_client.play(player, after=lambda e: print('Player error: '+ str(e)) if e else None)
          await ctx.send('Now playing: {}'.format(player.title))
    else:
      await ctx.send("Audio already playing, queueing song")

@bot.command(name='stop')
async def stop_youtube(ctx):
  if ctx.voice_client.is_playing():
    ctx.voice_client.stop()
  else:
    await ctx.send("No audio currently playing habibi")

@bot.command(name='pause')
async def pause_youtube(ctx):
  if ctx.voice_client.is_playing():
    ctx.voice_client.pause()
  else:
    await ctx.send("No audio currently playing habibi")
  
@bot.command(name='resume')
async def resume_youtube(ctx):
  ctx.voice_client.resume()

load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))

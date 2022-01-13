# speecher-bot code
import discord
import os

import utils
import secrets
import random

from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
from ttsaudio import VOICES_LIST, getAudioFromTTSaudio

AUDIOS = utils.load_audios()
AUDIOS_NAVIDAD = utils.load_audios_navidad()
AUDIOS_ANIO_NUEVO = utils.load_audios_anio_nuevo()

load_dotenv()

activity = discord.Activity(type=discord.ActivityType.watching, name=" porno.")
intents = discord.Intents().default()
intents.members = True
bot = commands.Bot(command_prefix="!", activity=activity, intents=intents)


TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
FFMPEG_EXE = str(os.getenv('FFMPEG_EXE'))



@bot.event
async def on_ready():
    print(f'{bot.user.name} está conectado a Discord!')


@bot.event
async def on_message(message):
    mention = f'<@!{bot.user.id}>'
    if mention in message.content:
        ctx = await bot.get_context(message)
        sanitized = message.content.replace(mention,"")
        if not sanitized:
            await ctx.send("Acaso te gusto bb?")
        else:
            await speech(ctx,*(sanitized.split(" ")))
    elif "@" in message.content:
        await message.channel.send("Uhhhh que vales verga dice")
    else:
        await bot.process_commands(message)


@bot.command(name="speech", brief="Reproduce en audio un texto, se puede indicar la voz al final del comando..")
async def speech(ctx, *args ):
    text = " ".join(args)
    lang = "es-us"

    for word in args:
        if "-" in word:
            lang = word.replace("-","")
            text = text.replace(""+word,"")

    if len(text) <= 0:
        await ctx.send("Pa que chucha me llamas.")
    else:
        audio_name = None
        try:
            audio_name = getAudioFromTTSaudio(text, lang=lang.capitalize())
        except Exception as exception:
            await ctx.send(exception)
        
        if not ctx.author.voice:
            await ctx.send("Primero entra en un canal de voz subnormal!")
        elif audio_name:
            channel = ctx.author.voice.channel
            voice_client = ctx.voice_client
            if not voice_client:
                voice_client = await channel.connect()           
            audio = discord.FFmpegPCMAudio('temp/'+audio_name, executable=FFMPEG_EXE) 
            if not ctx.voice_client.is_playing():
                await ctx.send(f"{ctx.author.name} ha enviado un audio!")
                voice_client.play(audio, after= None)
            else:
                await ctx.send("Pérame we!")
            

@bot.command(name="voices", brief="Lista las voces disponibles.")
async def voices(ctx):
    voces = "Las voces tradicionales basadas en el código de lenguaje: "
    voces = voces +"\nURL: https://cloud.google.com/text-to-speech/docs/voices \n"
    voces = voces +"Y las voces custom: "
    for voz in VOICES_LIST:
        voces = voces + voz + "\n"
    await ctx.send(voces)

@bot.command(name="audios", brief="Muestra los audios disponibles")
async def audios(ctx):
    audios = ""
    for element in AUDIOS.keys():
        audios += element+"\n"
    if utils.es_navidad():
        for element in AUDIOS_NAVIDAD.keys():
            audios += element+"\n"
    if utils.es_anio_nuevo():
        for element in AUDIOS_ANIO_NUEVO.keys():
            audios += element+"\n"
    await ctx.send(audios)

@bot.command(name="yt", brief="Reproduce el audio de un video de YouTube.")
async def yt(ctx, *args):
    url = " ".join(args)
    vc = ctx.voice_client
    if not vc: 
        vc = await ctx.author.voice.channel.connect()
    player = await utils.YTDLSource.from_url(url, loop=bot.loop, stream=True)    
    
    if not ctx.voice_client.is_playing():
        vc.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Reproduciendo: {}'.format(player.title))
    else:
        await ctx.send("Pérame we!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        command = error.__str__().split('"')[1]
        audio_file = None
        if(command in AUDIOS.keys()):
            audio_file = AUDIOS[command]
            
        elif(command in AUDIOS_NAVIDAD.keys()):
            if utils.es_navidad():
                audio_file = AUDIOS_NAVIDAD[command]
            else:
                await ctx.send("Que eres tonto mmv, todavia falta para Navidad.")
        elif(command in AUDIOS_ANIO_NUEVO.keys()):
            if utils.es_anio_nuevo():
                audio_file = AUDIOS_ANIO_NUEVO[command]
            else:
                await ctx.send("Que eres tonto mmv, todavia falta para fin de año.")
        else:
            await ctx.send("No te entiendo wey :c")
        
        if audio_file:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_channel = ctx.voice_client
                if not voice_channel:
                    voice_channel = await channel.connect()
                if not ctx.voice_client.is_playing():
                    audio = discord.FFmpegPCMAudio(audio_file, executable=FFMPEG_EXE)
                    voice_channel.play(audio, after= None)
                else:
                    await ctx.send("Pérame we!")
            else:
                await ctx.send("Primero entra en un canal de voz subnormal!")
    else:
        raise error

@bot.command(name="callate", brief="Detiene el audio que se está reproduciendo.")
async def silenciar(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
    else:
        await ctx.send("Subnormal, ni si quiera estoy hablando.")

@bot.command(name="aguanta", brief="Pausa lo que esté reproduciendo.")
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
    else:
        await ctx.send("Subnormal, ni si quiera estoy hablando.")

@bot.command(name="sigue", brief="Sigue reproduciendo un audio en caso de haberlo pausado.")
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()   
    else:
        await ctx.send("No se que quieres que diga xd.")

@bot.command(name="sortear", brief="Toma a alguien al azar del canal de voz.")
async def sortear(ctx, qty = 1):
    if ctx.author.voice and ctx.author.voice.channel:
        vc = ctx.author.voice.channel
        members = vc.members
        member_names = []
        for mem in members:
            member_names.append(mem.display_name)
        if qty <= len(members):
            if qty == 1:
                member = secrets.choice(member_names)
                await ctx.send(f"El cojudo que ganó es {member}")
            else:
                members = random.sample(member_names, qty)
                for i in range(qty):
                    await ctx.send(f"{i+1} es {members[i]}")
        else:
            await ctx.send("A parte de feo tonto, que no vez que te falta gente pa ese sorteo.")
    else:
        await ctx.send("Primero entra en un canal de voz, tonto hp")


bot.run(TOKEN)
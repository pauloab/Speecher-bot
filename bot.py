# speecher-bot code
import discord
import os

from discord.errors import ClientException
import utils
import secrets
import random

from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
from gtts import gTTS
from ttsaudio import VOICES_LIST, getAudioFromTTSaudio

AUDIOS = utils.load_audios()
AUDIOS_NAVIDAD = utils.load_audios_navidad()
AUDIOS_ANIO_NUEVO = utils.load_audios_anio_nuevo()

load_dotenv()

intents = discord.Intents().default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
FFMPEG_EXE = str(os.getenv('FFMPEG_EXE'))


@bot.event
async def on_ready():
    print(f'{bot.user.name} está conectado a Discord!')

@bot.command(name="speech", brief="Reproduce en audio un texto, se puede indicar la voz al final del comando..")
async def speech(ctx, text: str, lang: str ="es-es" ):
    if(lang.capitalize() in VOICES_LIST):
        getAudioFromTTSaudio(text, lang=lang.capitalize())
    else:
        try:
            sound = gTTS(text=text, lang=lang, slow=False).save("temp/test.mp3")
        except ValueError:
            lang = None
            await ctx.send("No conozco ese lenguaje, a ver cuando el perro del Paulo me lo instala xd")
    if lang:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = ctx.voice_client
            if not voice_client:
                voice_client = await channel.connect()           
            audio = discord.FFmpegPCMAudio('temp/test.mp3', executable=FFMPEG_EXE) 
            await ctx.send(f"{ctx.author.name} ha enviado un audio!")
            voice_client.play(audio, after= None)
        else:
            await ctx.send("Primero entra en un canal de voz subnormal!")

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
async def yt(ctx, url):

    vc = ctx.voice_client
    if not vc: 
        vc = await ctx.author.voice.channel.connect()
    player = await utils.YTDLSource.from_url(url, loop=bot.loop, stream=True)    
    vc.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send('Reproduciendo: {}'.format(player.title))

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
                audio = discord.FFmpegPCMAudio(audio_file, executable=FFMPEG_EXE)
                voice_channel.play(audio, after= None)
            else:
                await ctx.send("Primero entra en un canal de voz subnormal!")
    elif isinstance(error, ClientException):
        await ctx.send("Pérame we!")
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
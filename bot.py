# speecher-bot code
import discord
import os
import utils

from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
from gtts import gTTS
from ttsaudio import VOICES_LIST, getAudioFromTTSaudio

AUDIOS = utils.load_audios()
AUDIOS_NAVIDAD = utils.load_audios_navidad()

load_dotenv()

bot = commands.Bot(command_prefix='!')

TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('GUILD')
FFMPEG_EXE = str(os.getenv('FFMPEG_EXE'))


@bot.event
async def on_ready():
    print(f'{bot.user.name} está conectado a Discord!')

@bot.command(name="speech")
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
            elif voice_client.is_playing():
                await ctx.send(f"Pérame we!")    
            
            audio = discord.FFmpegPCMAudio('temp/test.mp3', executable=FFMPEG_EXE) 
            await ctx.send(f"{ctx.author.name} ha enviado un audio!")
            voice_client.play(audio, after= None)
        else:
            await ctx.send("Primero entra en un canal de voz subnormal!")

@bot.command(name="voices")
async def voices(ctx):
    voces = "Las voces tradicionales basadas en el código de lenguaje: "
    voces = voces +"\nURL: https://cloud.google.com/text-to-speech/docs/voices \n"
    voces = voces +"Y las voces custom: "
    for voz in VOICES_LIST:
        voces = voces + voz + "\n"
    await ctx.send(voces)

@bot.command(name="audios")
async def audios(ctx):
    audios = ""
    for element in AUDIOS.keys():
        audios += element+"\n"
    if utils.es_navidad():
        for element in AUDIOS_NAVIDAD.keys():
            audios += element+"\n"
    await ctx.send(audios)

@bot.command(name="h")
async def help(ctx):
    txt = "1.!speech 'texto en comillas' - Lee el texto con la voz en español predeterminada. "
    txt = txt + "\n2.!speech 'texto en comillas' codigo-voz  - Lee el texto con la voz que le pidas o con el codigo de lenguaje."
    txt = txt + "\n3.!voices - Lista las voces disponibles"
    txt = txt + "\n4.!help - Este comando ps"
    txt = txt + "\npsdt: No uses el comando !help que me dio pereza implementarlo"
    await ctx.send(txt)

@bot.command(name="yt")
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
        else:
            await ctx.send("No te entiendo wey :c")
        
        if audio_file:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_channel = ctx.voice_client
                if not voice_channel:
                    voice_channel = await channel.connect()
                elif ctx.voice_client.is_playing():
                    await ctx.send(f"Pérame we!")
                audio = discord.FFmpegPCMAudio(audio_file, executable=FFMPEG_EXE)
                voice_channel.play(audio, after= None)
            else:
                await ctx.send("Primero entra en un canal de voz subnormal!")
    else:
        raise error

@bot.command(name="callate")
async def silenciar(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
    else:
        await ctx.send("Subnormal, ni si quiera estoy hablando.")

bot.run(TOKEN)
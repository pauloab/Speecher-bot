import asyncio
import discord
import os
import youtube_dl


from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
FFMPEG_EXE = os.getenv('FFMPEG_EXE')



def load_audios() -> dict:
    AUDIO_LIST = {}
    for filename in os.listdir("audio/"):
        if filename.endswith(".mp3"): 
            clean_filename = filename.lower().strip().removesuffix(".mp3")
            AUDIO_LIST[clean_filename] = "audio/"+filename
    return AUDIO_LIST

def load_audios_navidad() -> dict:
    AUDIO_LIST = {}
    for filename in os.listdir("audio/navidad/"):
        if filename.endswith(".mp3"): 
            clean_filename = filename.lower().strip().removesuffix(".mp3")
            AUDIO_LIST[clean_filename] = "audio/navidad/"+filename
    return AUDIO_LIST

def load_audios_anio_nuevo() -> dict:
    AUDIO_LIST = {}
    for filename in os.listdir("audio/anio/"):
        if filename.endswith(".mp3"): 
            clean_filename = filename.lower().strip().removesuffix(".mp3")
            AUDIO_LIST[clean_filename] = "audio/anio/"+filename
    return AUDIO_LIST


def es_navidad() -> bool:
    fecha_actual = datetime.today()
    return fecha_actual.month == 12 and fecha_actual.day <= 25

def es_anio_nuevo() -> bool:
    fecha_actual = datetime.today()
    return fecha_actual.month == 12

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
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
        return cls(discord.FFmpegPCMAudio(filename, executable=FFMPEG_EXE, **ffmpeg_options), data=data)


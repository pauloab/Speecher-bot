import requests
import os
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()    
URL = os.getenv('TTSURL')

VOICES_LIST = ["Zeina",
 "Nicole",
 "Russell",
 "Vitoria",
 "Camila",
 "Ricardo",
 "Brian",
 "Amy",
 "Emma",
 "Chantal",
 "Lucia",
 "Enrique",
 "Conchita",
 "Zhiyu",
 "Naja",
 "Mads",
 "Ruben",
 "Lotte",
 "Lea",
 "Mathieu",
 "Celine",
 "Marlene",
 "Vicki",
 "Hans",
 "Karl",
 "Dora",
 "Raveena",
 "Aditi",
 "Bianca",
 "Carla",
 "Giorgio",
 "Takumi",
 "Mizuki",
 "Seoyeon",
 "Mia",
 "Liv",
 "Jan",
 "Maja",
 "Ewa",
 "Jacek",
 "Ines",
 "Cristiano",
 "Carmen",
 "Maxim",
 "Tatyana",
 "Astrid",
 "Filiz",
 "Salli",
 "Joey",
 "Kimberly",
 "Justin",
 "Joanna",
 "Kendra",
 "Ivy",
 "Matthew",
 "Miguel",
 "Lupe",
 "Penelope",
 "Gwyneth",
 "Geraint"]

def getAudioFromTTSaudio(text,lang="Ricardo"):
    Audio_name = "test.mp3"
    if(lang.capitalize() in VOICES_LIST):
        data = {"msg":text,"lang":lang, "source":"ttsmp3"}
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(URL,data=data,headers=headers) 
        MP3_URL = response.json().get("URL", None)
        headers = {'Content-type': "audio/mpeg"}
        if MP3_URL:
            response = requests.get(MP3_URL,headers=headers) 
            with open('temp/'+Audio_name, 'wb') as f:
                f.write(response.content)
        else:
            raise Exception("Algo pasó con las voces personalizadas :c, inténtalo más tarde.")
            Audio_name = None
    else:
        try:
            sound = gTTS(text=text, lang=lang, slow=False).save("temp/"+Audio_name)
        except ValueError:
            raise Exception("No conozco ese lenguaje, a ver cuando el perro del Paulo me lo instala xd")
            Audio_name = None
    return Audio_name

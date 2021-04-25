from time import ctime
import time
from numpy.lib.function_base import place
import speech_recognition as sr
import webbrowser
import playsound
import os
import random
import numpy as np
from gtts import gTTS
import face_recognition
import os
import cv2
from face_recognition.api import face_encodings
import requests
from datetime import datetime
import tkinter as tkinter
from threading import Thread
import subprocess

greetingCommands = np.loadtxt(fname='./Commands/GreetingsCommands.txt',delimiter=',',dtype=np.str)
exitCommands = np.loadtxt(fname='./Commands/ExitCommands.txt',delimiter=',',dtype=np.str)

r = sr.Recognizer() 
FACE_DIR = "./Faces/"
ADMIN_DIR = './Admin/'
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = "cnn"

known_faces = []
known_names = []

def face_auth():
    global match, date_time
    now = datetime.now() # current date and time
    date_time = now.strftime("%d-%m-%Y-%H-%M-%S")
    
    for name in os.listdir(FACE_DIR):
        
        for filename in os.listdir(f"{FACE_DIR}{name}"):
            image = face_recognition.load_image_file(f"{FACE_DIR}/{name}/{filename}")
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            known_names.append(name)
            
    madison_speak("Capturing Face....")
    cap = cv2.VideoCapture(0)
    ret, frame, = cap.read()
    cv2.imwrite("./Admin/"+date_time+".png", frame)
    cv2.destroyAllWindows()
    cap.release()

    madison_speak("Scanning.....")
    input = face_recognition.load_image_file("./Admin/"+date_time+".png")
    locations = face_recognition.face_locations(input,model=MODEL)
    encodings = face_encodings(input,locations)
    image = cv2.cvtColor(input, cv2.COLOR_RGB2BGR)

    madison_speak("Looking for Matches.....")
    for face_encoding, face_location in zip(encodings,locations):
        result = face_recognition.compare_faces(known_faces,face_encoding, TOLERANCE)
        match = None
        if True in result:
            match = known_names[result.index(True)]
            print(f"Match Found: {match}")
            madison_speak(f"Access Granted, Welcome {match}")
            with open("./Admin/logs.txt", "a") as myfile:
                myfile.write("- " + match+": "+ctime()+"\n")   
            return True
        
        else:
            with open("./Admin/logs.txt", "a") as myfile:
                myfile.write("- Failed Attempt: "+date_time+"\n")  
            madison_speak("Access Denied")
            return False

# listen for audio and convert it to text:
def record_audio(ask=False):
    with sr.Microphone() as source: 
        if ask:
            madison_speak(ask)
        print("Listening......")
        r.pause_threshold = 1
        audio = r.record(source, duration=3)  # listen for the audio via source
    try: 
        print("Recognizing...")     
        query = r.recognize_google(audio, language ='en-in') 
        print(f"User said: {query}\n") 
   
    except sr.UnknownValueError:  # error: recognizer does not understand
        print("Unknown Value")
        return "None"

    except sr.RequestError:
        # error: recognizer is not connected
        madison_speak('Sorry, the service is down')
        return "None"

    return query 

def madison_speak(audio_string):
    textToSpeach = gTTS(text=audio_string,lang='en')
    msg_list.insert(tkinter.END,audio_string)
    r= random.randint(1,10000)
    audio_file = 'audioNO-' +str(r) + '.mp3'
    textToSpeach.save(audio_file)
    playsound.playsound(audio_file)
    #print(audio_string)
    os.remove(audio_file)

def respond(voice_data):
    # Asking the assistant
    if voice_data in greetingCommands:
        madison_speak("Hello my name is Madison, how may i help you?")
        
    # Ask for the time
    if "time" in voice_data.split():
        madison_speak(ctime())
        
    # Check the weather
    if "weather" in voice_data.split():
        api_address='http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q='
        place = record_audio('Where would you like to get the weather for')
        url = api_address + place
        json_data = requests.get(url).json()
        try:
            format_add = json_data['weather'][0]['description']
            madison_speak(f"The weather in {place} is {format_add}")
        except:
            madison_speak("Error when listening could you please try again, thank you")
        
    # Search Google
    if "search" in voice_data.split():
        search_term = record_audio("What shall i search?")
        url = f"https://google.com/search?q={search_term}"
        webbrowser.get().open(url)
        madison_speak(f'Here is what I found for {search_term} on google')

    # For making notes
    if "note" in voice_data.split():
        note = record_audio("What should i note?")
        with open("notes.txt", "a") as myfile:
            myfile.write("- " + note+"\n")    
        madison_speak(f'{note} has been noted')        

    if "help" in voice_data:
        madison_speak(f'{note} has been noted')
                
    if "open" in voice_data.split():
        open = record_audio("What would you like me to open?")
        
        if "logs" in open.split():
            subprocess.call(['notepad.exe', './Admin/logs.txt'])
            
        if "notes" in open.split():
            subprocess.call(['notepad.exe', './notes.txt'])
            
        if "admin" in open.split():
            subprocess.Popen(r'explorer /select,"C:\Users\Adam Varden\Documents\Year 4 Notes\Semester 2\Gesture Based UI\Final Project\Admin"')       
            
    if voice_data in exitCommands:
        exit()

def begin():
    if face_auth() == True:
        time.sleep(1)
        madison_speak(f"How may I help you today, {match}?")
        while 1:
            voice_data = record_audio()
            respond(voice_data) 
            
def UI():
    global msg_list
    root = tkinter.Tk()
    root.title("Madsion")
    messages_frame = tkinter.Frame(root)
    scrollbar = tkinter.Scrollbar(messages_frame)

    msg_list = tkinter.Listbox(messages_frame,height=20, width=50, yscrollcommand=scrollbar.set)


    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msg_list.pack()
    messages_frame.pack()
    tkinter.mainloop()


if __name__ == "__main__":
    global GUI_THREAD,APP_THREAD
    
    GUI_THREAD = Thread(target=UI)
    APP_THREAD = Thread(target=begin)
    APP_THREAD.start()
    GUI_THREAD.start()

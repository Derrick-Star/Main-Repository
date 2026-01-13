import os, subprocess, psutil, threading
import speech_recognition as sr
import pyttsx3
import openai

# ========== CONFIG ==========
openai.api_key = "YOUR_OPENAI_API_KEY"  # Leave empty for full offline
use_online_ai = True if openai.api_key else False

# ========== TTS SETUP ==========
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('voice', engine.getProperty('voices')[1].id)

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

# ========== LISTEN ==========
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio).lower()
    except:
        speak("Sorry, I didn't catch that.")
        return ""

# ========== ONLINE GPT ==========
def ask_gpt(prompt):
    if not use_online_ai:
        return "Online AI is not enabled."
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return res['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# ========== SYSTEM CONTROL ==========
def system_status():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return f"CPU usage is {cpu} percent. RAM usage is {ram} percent."

def run_command(cmd):
    try:
        return subprocess.getoutput(cmd)[:500]
    except Exception as e:
        return str(e)

def handle(command):
    if "status" in command:
        speak(system_status())
    elif "open" in command or "run" in command:
        app = command.replace("open ", "").replace("run ", "")
        os.system(app)
        speak(f"Opening {app}")
    elif "shutdown" in command or "exit" in command:
        speak("Shutting down. Goodbye.")
        exit()
    elif "search" in command or "explain" in command:
        query = command.replace("search", "").replace("explain", "")
        speak("Let me find that for you.")
        answer = ask_gpt(query)
        speak(answer)
    else:
        if use_online_ai:
            speak(ask_gpt(command))
        else:
            speak("Sorry, I can't process that offline.")

# ========== MAIN LOOP ==========
def main():
    speak("Jarvis online and offline assistant ready.")
    while True:
        cmd = listen()
        if cmd:
            threading.Thread(target=handle, args=(cmd,)).start()

if __name__ == "__main__":
    main()
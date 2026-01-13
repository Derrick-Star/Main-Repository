import math
import random
import calendar
from datetime import datetime
import time

# --- Math Functions ---
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return "Cannot divide by zero!" if b == 0 else a / b
def exponentiate(a, b): return a ** b
def square_root(a): return "Cannot take square root of a negative number!" if a < 0 else math.sqrt(a)
def factorial(n):
    if not isinstance(n, int) or n < 0:
        return "Cannot take factorial of a negative number or non-integer!"
    return math.factorial(n)
def random_number(start, end):
    if start > end:
        return "Invalid range!"
    return random.randint(start, end)
def is_prime(n):
    if n <= 1:
        return False
    return all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1))

def crack_time(password):
    charset = 0
    if any(c.islower() for c in password): charset += 26
    if any(c.isupper() for c in password): charset += 26
    if any(c.isdigit() for c in password): charset += 10
    if any(c in "!@#$%^&*()-_=+[]{}|;:`'.,<>?/~" for c in password) : charset += 32

    combinations = charset**len(password)
    guesses_per_second = 1_000_000_000 #it takes one billion guesses/sec

    time_to_crack = combinations / guesses_per_second
    return time_to_crack

# --- Fun Content ---
jokes = [
    "Why don't programmers like nature? It has too many bugs.",
    "Why do Java developers wear glasses? Because they can't C#!",
    "Why was the computer cold? It left its Windows open.",
    "Debugging: Being the detective in a crime movie where you are also the murderer.",
    "Why did the programmer quit his job? He didn’t get arrays.",
    "A user interface is like a joke. If you have to explain it, it’s not that good.",
    "Why did the developer go broke? Because he used up all his cache.",
    "I would tell you a UDP joke, but you might not get it.",
    "There are only 10 types of people in the world: those who understand binary, and those who don’t.",
    "Why did the computer show up late to work? It had a hard drive.",
    "To understand what recursion is, you must first understand recursion.",
    "I told my computer I needed a break, and now it won’t stop sending me Kit-Kat ads.",
    "Why was the smartphone wearing glasses? It lost its contacts.",
    "Why don’t robots ever panic? Because they have nerves of steel.",
    "What’s a computer’s favorite beatle song? 'Let it B…ASIC.'",
    "Knock knock. Who’s there? Java. Java who? Java to wait and see.",
    "Parallel lines have so much in common… it’s a shame they’ll never meet.",
    "What’s a computer’s favorite snack? Microchips.",
    "Why was the computer sticky? It had cookies!",
    "Why did the tech guy cross the road? To troubleshoot the chicken on the other side."
]

fun_facts = [
    "Honey never spoils. Archaeologists found 3000-year-old edible honey in Egyptian tombs.",
    "Octopuses have three hearts and blue blood.",
    "Bananas are berries, but strawberries aren't.",
    "A day on Venus is longer than a year on Venus.",
    "Sharks existed before trees.",
    "Some turtles can breathe through their butts.",
    "Hot water freezes faster than cold water — it's called the Mpemba effect.",
    "There’s a species of jellyfish that can live forever.",
    "The Eiffel Tower can grow over 6 inches in summer due to heat expansion.",
    "Humans share 60% of their DNA with bananas.",
    "Wombat poop is cube-shaped.",
    "The average cloud weighs over a million pounds.",
    "Space smells like seared steak, according to astronauts.",
    "Sloths can hold their breath longer than dolphins.",
    "Cows have best friends and get stressed when separated.",
    "You can hear a blue whale’s heartbeat from 2 miles away.",
    "There are more stars in the universe than grains of sand on Earth.",
    "The human nose can detect over 1 trillion scents.",
    "Some cats are allergic to humans.",
    "Mosquitoes are the deadliest animals in the world."
]

future_predictions = [
    "You will find what you're looking for — eventually.",
    "A surprise is waiting around the corner!",
    "Today is the perfect day to try something new.",
    "You’ll receive a message that changes your perspective.",
    "Good luck is approaching with quiet steps.",
    "An old friend will resurface soon.",
    "You’re about to learn something valuable.",
    "A bold move will pay off — trust your gut.",
    "Don’t ignore small signs today.",
    "Something weird will happen, but you’ll laugh about it.",
    "A dream you had is trying to tell you something.",
    "Your coffee/tea will taste extra good today.",
    "You’ll think of the perfect comeback — an hour too late.",
    "Soon, you’ll win an argument with silence.",
    "Someone's secretly admiring your skills.",
    "Luck favors you when you least expect it.",
    "Beware of overthinking — sometimes yes means yes.",
    "A minor inconvenience today prevents a major one tomorrow.",
    "You will ace a task you've been worried about.",
    "Don't trust the cat. It knows too much."
]

# --- Password Generator ---
def generate_password(length=12):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    return ''.join(random.choices(chars, k=length))

# --- Mood Keywords ---
positive = [
    'good', 'great', 'fine', 'nice', 'interesting', 'beautiful', 'going great', 'yup', 'swell',
    'awesome', 'fantastic', 'amazing', 'wonderful', 'superb', 'positive', 'cool', 'blessed',
    'lovely', 'excellent', 'happy', 'joyful', 'chill', 'content', 'peaceful', 'splendid', 'yay',
    'rocking', 'on top', 'vibing', 'excited', 'motivated', 'productive', 'okay', 'ok', 'alright',
    'fabulous', 'lit', 'dope', 'epic', 'glorious', 'cheerful', 'smiling', 'sunny', 'winning',
    'solid', 'stellar', 'vibe', 'goated', 'on point', 'energized'
]

negative = [
    'bad', 'not fine', 'terrible', 'boring', 'ugly', 'not going great', 'no', 'never', 'sorry',
    'worse', 'worst', 'sad', 'depressed', 'unhappy', 'angry', 'mad', 'pissed', 'upset', 'annoyed',
    'miserable', 'disappointed', 'painful', 'tired', 'exhausted', 'broke', 'rough', 'meh',
    'bleh', 'regret', 'hate', 'down', 'sick', 'crappy', 'drained', 'not good', 'frustrated',
    'confused', 'gloomy', 'lost', 'anxious', 'stressed', 'lame', 'failing'
]

probable = [
    'maybe', 'kinda', 'sorta', 'promising', 'hopefully', 'on god', 'not sure', 'possibly',
    'idk', 'depends', 'in between', 'on the fence', 'could be', 'perhaps', 'somewhat',
    '50/50', 'so-so', 'meh', 'mixed', 'uncertain', 'iffy', 'not bad', 'I guess', 'okish',
    'neutral'
]

# Weather keyword categories and their responses
weather_responses = {
    'rain': "Rain, huh? Hopefully it lets up soon. Grab an umbrella just in case.",
    'sun': "Sunshine sounds great. Just don’t forget sunscreen!",
    'cloud': "Cloudy skies — not too bright, not too gloomy. Just chill vibes.",
    'snow': "Snow? Now that’s magical. Stay warm though!",
    'wind': "Windy, eh? Hold onto your hat.",
    'storm': "Storms can be intense. Stay safe and indoors if you can.",
    'hail': "Hail? That’s wild. Better not stay out too long.",
    'fog': "Foggy weather makes everything feel like a movie scene, doesn’t it?",
    'humid': "Humidity can be a drag. Hydrate!",
    'hot': "Hot days call for cold drinks and shade.",
    'cold': "Cold? Time for jackets and warm drinks.",
    'freezing': "Freezing weather? Stay bundled up!",
    'drizzle': "A light drizzle can be calming. Or annoying, depending on your mood."
}

# Time-based greeting
now = datetime.now()
hour = now.hour

if 5 <= hour < 12:
    print("Good Morning")
elif 12 <= hour < 17:
    print("Good Afternoon")
elif 17 <= hour < 21:
    print("Good Evening")
else:
    print("Good Night")

print("My name's PICA 2.03. If you've used the previous PICA you'd see a difference in tone.")
name = input("What is your name? ").strip()

print(f"Well nice to meet you, {name}. How's the weather over there?")
weather_input = input("The weather here is really ").lower()

# Flexible weather response based on keyword matching
matched_weather = False
for keyword, response in weather_responses.items():
    if keyword in weather_input:
        print(response)
        matched_weather = True
        break

if not matched_weather:
    print("That sounds... unique. Weather can be full of surprises!")

print("By the way, how's your day going?")
user_day = input().lower()

# Mood response logic
if any(word in user_day for word in positive):
    print("Sweeet! Things must be happening to you today.")
elif any(word in user_day for word in negative):
    print("Think positive.")
elif any(word in user_day for word in probable):
    print("Not so sure yourself. So you can decide.")
else:
    print("Nothing I can do, but you can still change it, right?")

# --- Main Interface ---
print("Hey! What do you want to do today?")
print("""
Type one of these commands:
- joke
- calendar
- math
- fun fact
- predict the future
- generate password
- password strenght check
- quit
""")

while True:
    user_input = input(">>> ").strip().lower()

    if user_input == "joke":
        print(random.choice(jokes))

    elif user_input == "calendar":
        try:
            year = int(input("Enter the year: "))
            month = int(input("Enter the month (1-12): "))
            if 1 <= month <= 12:
                print(calendar.month(year, month))
            else:
                print("Invalid month, must be 1-12.")
        except ValueError:
            print("Please enter valid integers for year and month.")

    elif user_input == "math":
        print("Choose: add, subtract, multiply, divide, exponentiate, sqrt, factorial, prime check, random number")
        op = input("Math operation: ").lower().strip()
        try:
            if op == "add":
                a, b = float(input("a: ")), float(input("b: "))
                print("Result:", add(a, b))
            elif op == "subtract":
                a, b = float(input("a: ")), float(input("b: "))
                print("Result:", subtract(a, b))
            elif op == "multiply":
                a, b = float(input("a: ")), float(input("b: "))
                print("Result:", multiply(a, b))
            elif op == "divide":
                a, b = float(input("a: ")), float(input("b: "))
                print("Result:", divide(a, b))
            elif op == "exponentiate":
                a, b = float(input("base: ")), float(input("power: "))
                print("Result:", exponentiate(a, b))
            elif op == "sqrt":
                a = float(input("Number: "))
                print("Result:", square_root(a))
            elif op == "factorial":
                n = int(input("Enter a non-negative integer: "))
                print("Result:", factorial(n))
            elif op == "prime check":
                n = int(input("Number: "))
                print(f"{n} is", "prime." if is_prime(n) else "not prime.")
            elif op == "random number":
                start, end = int(input("Start: ")), int(input("End: "))
                print("Random number:", random_number(start, end))
            else:
                print("Unknown math operation.")
        except ValueError:
            print("Invalid input, please enter numbers correctly.")

    elif user_input == "fun fact":
        print(random.choice(fun_facts))

    elif user_input == "predict the future":
        question = input("Ask your question: ")
        print("🔮", random.choice(future_predictions))

    elif user_input == "generate password":
        try:
            length = int(input("Enter password length (min 4): "))
            if length < 4:
                print("Length too short, must be at least 4.")
            else:
                print("Generated Password:", generate_password(length))
        except ValueError:
            print("Please enter a valid number.")
    
    elif user_input == "password strenght check":
        password = input("Enter password ")
        seconds = crack_time(password)

        def format_time(seconds):
            if seconds < 1:
                return "less than 1 second"
            elif seconds < 60:
                return f"{seconds:.2f} seconds"
            elif seconds < 3600:
                return f"{seconds/60:.2f} minutes"
            elif seconds < 86400:
                return f"{seconds/3600:.2f} hours"
            elif seconds < 31536000:
                return f"{seconds/86400:.2f} days"
            else:
                return f"{seconds/31536000:.2f} years"
        print("Estimated time to crack:",format_time(seconds))


    elif user_input == "quit":
        print("Bye! Come back when you need me.")
        break

    else:
        print("Sorry, I didn't understand that. Try again.")
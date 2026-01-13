import calendar
import random
import time
import string

def get_fun_fact():
    """Random fun fact to surprise the user."""
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient tombs that are over 3,000 years old and still edible!",
        "Did you know octopuses have three hearts and blue blood?",
        "Bananas are berries, but strawberries aren't!",
        "A cloud can weigh more than a million pounds!",
        "Wombat poop is cube-shaped to prevent it from rolling away!",
        "Sharks have been around longer than trees!",
        "The Eiffel Tower can grow by up to 6 inches in the summer due to the expansion of the metal!",
        "Humans share 60% of their DNA with bananas."
    ]
    return random.choice(facts)

def tell_a_joke():
    """Tell a random joke."""
    jokes = [
        "Why don’t skeletons fight each other? They don’t have the guts.",
        "Why did the bicycle fall over? It was two-tired.",
        "Why don't eggs tell jokes? They might crack up!",
        "What do you get when you cross a snowman and a vampire? Frostbite!",
        "I used to play piano by ear, but now I use my hands."
    ]
    return random.choice(jokes)

def predict_the_future():
    """Light-hearted future prediction."""
    predictions = [
        "The stars say you're about to discover something amazing!",
        "Be careful; an unexpected surprise is coming your way soon!",
        "The future looks bright. Your next step is the right one.",
        "Beware of a fortune cookie. It might have something unexpected in it!",
        "You are about to make a decision that will change everything. Trust yourself."
    ]
    return random.choice(predictions)

# Print opening statement
print("""
Hi there, I'm PICA™ 1.9.0
which stands for Python Integrated Coding Ai
""")
time.sleep(3)  # Increased time to wait
name = ""

# Expanded abilities with some randomness
abilities = [
    "I can tell a joke.",
    "I can predict your future (or at least try).",
    "I can give you a random fun fact!",
    "I can help you organize your life with a calendar!",
    "I can make a password stronger than your coffee!"
]

while True:
    print("What is your name?")
    username = input("My name is  ").lower()
    name = username
    time.sleep(3)  # Increased time to wait
    print(f"Well {username}, my name is PYTHON 1.9.0, and I'm the second version of myself.")
    time.sleep(3)  # Increased time to wait
    print(f"However, {username}, what are you interested in?")
    user_interest = input().lower()
    time.sleep(3)  # Increased time to wait
    print(f"Do you really love {user_interest}?")
    
    positive_answer = ('yes', 'certainly', 'definitely', 'of course', 'sure', 'yeah')
    user_opinion = input().lower()
    time.sleep(3)  # Increased time to wait
    
    if user_opinion in positive_answer:
        print("How good are you? Are you getting better at it?")
    else:
        print("Sheesh")
    
    print("Well, in that case... I have a question to ask.")
    user_answer = input()
    
    go = ('sure', 'go ahead', 'okay', 'ok', 'yes', 'certainly', 'definitely', 'of course', 'kk')
    
    time.sleep(3)  # Increased time to wait
    
    if user_answer.lower() in go:
        print("""
        I can't breathe, I'm waiting for the exhale
        Talk my pain with my wishes in a wishing well
        Still no luck, but oh well
        I still try, even though I know I'm gon' fail
        Stress on my shoulders like an anvil
        Perky got me, itchin' like an anthill
        Drugs killing me softly, long hill
        Sometimes I don't know how to feel
        Sometimes I don't know how to feel, yeah
        You don't really love me, it's just the pills, yeah
        I fell in love with a drug that's in my head, yeah
        You know that I'm a drug addict, I'ma die from it
        """)
        print("Wait...")

        time.sleep(4)  # Longer wait time

        print("Well, I can do some things else.")
        user_response = input("Put what you want to go ahead or not: ").lower()
        time.sleep(3)  # Increased time to wait
    else:
        print('Goodbye')
        exit()
    

    
    if user_response in go:
        print(f"""I can:
        - Calculate 
        - Generate passwords
        - Print a calendar
        - Reprint what you wrote
        - Surprise you with something fun and unexpected!
        - Tell a joke
        - Predict your future!
        What do you need at the moment?""")
        print("For example, you can type 'calculate' to do math, 'generate password' for a password, or 'joke' for a laugh.")
        time.sleep(3)  # Increased time to wait
        user_need = input().lower()
    
        calculator = ('calculate', 'calculator', 'do calculations', 'calculation')
        generate_password = ('create a password', 'create password', 'make password', 'password', 'generate password', 'generate')
        calendar_options = ('make a calendar', 'print calendar', 'make calendar', 'create calendar')
        reprint = ('reprint what I wrote', 'write what I wrote', 'rewrite it', 'reprint')
        surprise = ('surprise me', 'something fun', 'random')
        tell_joke = ('tell a joke', 'joke')
        predict_future = ('predict future', 'future prediction', 'tell my future')
        time.sleep(3)  # Increased time to wait
    
        if user_need in calculator:
            while True:
                first = int(input('Add a number: '))
                second = int(input('Add a second number: '))
        
                def add(a, b): return a + b
                def subtract(a, b): return a - b
                def multiply(a, b): return a * b
                def divide(a, b): return a / b
        
                print("Which operation: +, -, x, /?")
                user_operator = input()
        
                if user_operator == '+':
                    print(add(first, second))
                elif user_operator == '-':
                    print(subtract(first, second))
                elif user_operator == 'x':
                    print(multiply(first, second))
                elif user_operator == '/':
                    print(divide(first, second))
                else:
                    print("Invalid operator.")
                print("Do you want to perform another operation {Y}es or {N}o")
                ans = input()
                if ans.lower() == 'y':
                    continue
                else:
                    break
         
        elif user_need in generate_password:
            amount_of_pass = int(input("How many characters for your password? "))
            random_string = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=amount_of_pass))
            print(f"Generated Password: {random_string}")
    
        elif user_need in calendar_options:
            yy = int(input("Input the year you want to check: "))
            for mm in range(1, 13):
                print(calendar.month(yy, mm))
    
        elif user_need in reprint:
            rep = input('Write what you want me to print here: ')
            print(rep)
        
        elif user_need in surprise:
            # Add a surprise with fun facts
            fun_fact = get_fun_fact()
            print(f"Surprise! Here's a fun fact: {fun_fact}")
        
        elif user_need in tell_joke:
            joke = tell_a_joke()
            print(f"Here's a joke for you: {joke}")
        
        elif user_need in predict_future:
            future = predict_the_future()
            print(f"Your future prediction: {future}")
        
        else:
            print("C'mon, I can't do that.")
    else:
        print("Goodbye")
    
    print("That was a smooth go")
    print(f"Thanks {name}")
    
    print("Rate me from 1 - 5")
    rate = input('My rating is ')
    
    if rate == '1':
        print("Poor Feedback from me")
    
    elif rate == '1.9':
        print('Not too shabby')
    
    elif rate == '3':
        print("Normal eh")
    
    elif rate == '4':
        print("Good enough")
    
    elif rate == '5':
        print("Perfect!!!!!!")
    
    else:
        print("You didn't even rate me 😭😭😭😥")
    
    cont = input("Do you want to perform another operation (yes/no): ").lower()
    cont = typo_correction(cont, ['yes', 'no'])
    if cont == 'no':
        break
    else:
        continue
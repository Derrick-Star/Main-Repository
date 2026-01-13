import math
;;t time

def crack_time(password):
    charset = 0
    if any(c.islower() for c in password): charset += 26
    if any(c.isupper() for c in password): charset += 26
    if any(c.isdigit() for c in password): charset += 10
    if any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~" for c in password): charset += 32

    combinations = charset ** len(password)
    guesses_per_second = 1_000_000_000  # e.g. 1 billion guesses/sec

    time_to_crack = combinations / guesses_per_second
    return time_to_crack

password = input("Enter password: ")
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

print("Estimated time to crack:", format_time(seconds))
import math
import random
import calendar
from datetime import datetime
import time

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

info = """
Hi, I am Enzo.
The fourth of my kind... like the Ai and the only named version
V.4.1.0
With upgraded features..... all codes are strictly
original and copied from copywrighted sources.

Disclaimer:
From copywrighted sources means that there is no 
illegally copied code and also all codes
are my previous codes and most of them are
in my Github page


"""
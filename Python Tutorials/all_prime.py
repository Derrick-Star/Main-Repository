def is_prime (num):
    for i in range (2, num):
        if (num % i) == 0:
            return False
    return True

def all_prime(num):
    primes = []
    for n in range(2, num + 1):
        if is_prime(n) is True:
            primes.append(n)
    return primes

num = int(input("Enter a number: "))    
prime_numbers = all_prime(num)
print("All prime numbers up to", num, "are:", prime_numbers)


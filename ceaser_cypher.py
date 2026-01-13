def cipher(code):
    result = ""
    for char in code:
        if char.isalpha():
            shift = 3
            if char.islower():
                base = ord('a')
            else:
                base = ord('A')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char  # keep non-letters as-is
    return result

# Example usage

while True:
    text = input("Enter text to encrypt (or 'exit' to quit): ")
    if text.lower() == 'exit':
        break

    else:
        encrypted = cipher(text)
        print(encrypted)
import math

def area(a, b):
    return 0.5 * a * b

def hypotenuse(opposite, adjacent):
    return math.sqrt(opposite**2 + adjacent**2)

user_input = input("Do you know all sides (Y/N)? ").lower()

if user_input == 'y':
    side_1 = float(input("Enter the first side: "))
    side_2 = float(input("Enter the second side: "))
    side_3 = float(input("Enter the third side: "))
    print("The Perimeter of the Triangle is:", side_1 + side_2 + side_3, "cm")

elif user_input == 'n':
    user_input = input("Do you know the hypotenuse? (Y/N) ").lower()

    if user_input == 'y':
        base = float(input("Enter the Base: "))
        height = float(input("Enter the Height: "))
        print("The Area of the Triangle is:", round(area(base, height), 2), "cm²")

    elif user_input == 'n':
        opposite = float(input("Enter the Opposite: "))
        adjacent = float(input("Enter the Adjacent: "))
        hypo = hypotenuse(opposite, adjacent)
        print("The Hypotenuse is:", round(hypo, 2))
        print("The Perimeter of the Triangle is:", round(opposite + adjacent + hypo, 2), "cm")

    else:
        print("Invalid input. Please enter Y or N.")

else:
    print("Invalid input. Please enter Y or N.")

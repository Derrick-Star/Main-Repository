#take the grades
print('Input your grades')

grade_1= int(input("Grade 1: "))
grade_2= int(input("Grade 2: "))
grade_3= int(input("Grade 3: "))
grade_4= int(input("Grade 4: "))
grade_5= int(input("Grade 5: "))

#create the average
average = grade_1+grade_2+grade_3+grade_4+grade_5/5

print(average)

if average >= 500:
    print('A+')

elif average >= 400:
    print('B-')

elif average >= 300:
    print('C')

elif average >= 200:
    print("D")

elif average >= 100:
    print("E")

else:
    print("F \n You're a Fucking Failure")
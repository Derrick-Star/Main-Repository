#in this lesson or what's it called yes...... tutorial
#we are going to be computing the gravitational force of an object
# the formuala for it is 
#   F = G*m1*m2/r^2
#start by defining G for easier callback

G = 6.673*10**-11
m1 = int(input("Enter the first mass "))
m2 = int(input("Enter the second mass "))
r = int(input("Enter the radius "))

#now that we have defined all those, lets move on

force = G*m1*m2/r**2

print("The Gravitational Force of the object is:", format(force, '.5g'), "N")
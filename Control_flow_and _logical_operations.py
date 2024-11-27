#water bath level scenario
bath_level= int(input("Input water bath level: " )) 
print("water level is: ", bath_level,"cm")
if bath_level > 80:
    print("The bath is overflowing!")
else:
    print("Continue to fill up a bit, but use your head!")

#roller coaster tickiting
print("Welcome to treasure roller coaster rides!")
height= int(input("How tall are you in cm? "))
print("Your height is: ", height, "cm")
if height >= 120:
    print("You can ride the roller coaster!")
    age= int(input("How old are you? "))
    if age <= 12:
        print("Kid, you ride will cost just $5") 
    elif age <= 18:
        print("Your ride will cost you 7$...Enjoy!")
    else:
        print("Please pay $12.")
else:
    print("You have to grow a bit taller to ride!")

#roller coaster tickiting updated with multiple if statements
print("Welcome to treasure roller coaster rides!")
height= int(input("How tall are you in cm? "))
print("Your height is: ", height, "cm")
if height >= 120:
    print("You can ride the roller coaster!")
    age= int(input("How old are you? "))
    if age <= 12:
        bill=5
        print("Kid, you ride will cost just $5") 
    elif age <= 18:
        bill=7
        print("Your ride will cost you 7$...Enjoy!")
    else:
        bill=12
        print("Please pay $12.")
    photo=input("Do want to have a photo taken? Type y for Yes and n for No. ")
    if photo== "y":
        bill+=3
        print("That'll cost you $3 more.")
        print("Your total cost is: $",bill)
    elif photo== "n":
        print("You missed out on some amazing memories.")
        print("Your final bill is: $", bill)
else:
    print("You have to grow a bit taller to ride!")


#Odd and Even
print("Welcome to Odd or Even!")
number=int(input("Enter your number: "))
if number%2 ==0:
    print("You have an even number!")
else:
    print("Your number is an odd number!")


#challenge 1
weight = 85
height = 1.85

bmi = weight / (height ** 2)

# 🚨 Do not modify the values above
# Write your code below 👇

if bmi >= 25:
    print("overweight")
elif bmi >= 18.5:
    print("normal weight")
else:
    print("underweight")

#ph1n3y

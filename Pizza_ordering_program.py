#Pizza order program
import sys

print("Welcome to Python Pizza Deliveries!")

while True: 
    size = input("What size pizza do you want? S, M or L: ")
    if size == "S":
        bill = 15
        pepperoni = input("Do you want pepperoni on your pizza? +$2 Y or N: ")
        if pepperoni == "Y":
            bill += 2
        break  
    elif size == "M":
        bill = 20
        pepperoni = input("Do you want pepperoni on your pizza? +$3 Y or N: ")
        if pepperoni == "Y":
            bill += 3
        break  
    elif size == "L":
        bill = 25
        pepperoni = input("Do you want pepperoni on your pizza? +$3 Y or N: ")
        if pepperoni == "Y":
            bill += 3
        break 
    else:
        print("You typed a wrong input!")  
extra_cheese = input("Do you want extra cheese? +$1 Y or N: ")
if extra_cheese == "Y":
    bill += 1

print("Your total bill is: $", bill)

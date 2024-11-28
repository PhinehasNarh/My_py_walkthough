#Treasure Island Game
print(r'''
*******************************************************************************
          |                   |                  |                     |
 _________|________________.=""_;=.______________|_____________________|_______
|                   |  ,-"_,=""     `"=.|                  |
|___________________|__"=._o`"-._        `"=.______________|___________________
          |                `"=._o`"=._      _`"=._                     |
 _________|_____________________:=._o "=._."_.-="'"=.__________________|_______
|                   |    __.--" , ; `"=._o." ,-"""-._ ".   |
|___________________|_._"  ,. .` ` `` ,  `"-._"-._   ". '__|___________________
          |           |o`"=._` , "` `; .". ,  "-._"-._; ;              |
 _________|___________| ;`-.o`"=._; ." ` '`."\ ` . "-._ /_______________|_______
|                   | |o ;    `"-.o`"=._``  '` " ,__.--o;   |
|___________________|_| ;     (#) `-.o `"=.`_.--"_o.-; ;___|___________________
____/______/______/___|o;._    "      `".o|o_.--"    ;o;____/______/______/____
/______/______/______/_"=._o--._        ; | ;        ; ;/______/______/______/_
____/______/______/______/__"=._o--._   ;o|o;     _._;o;____/______/______/____
/______/______/______/______/____"=._o._; | ;_.--"o.--"_/______/______/______/_
____/______/______/______/______/_____"=.o|o_.--""___/______/______/______/____
/______/______/______/______/______/______/______/______/______/______/_____ /
*******************************************************************************
''')
print("Welcome to Treasure Island.")
print("Your mission is to find the treasure.")

cross_roads=input("You're at a cross road. Where do you want to go? Type 'left' or 'right': ").lower()
if cross_roads=="right":
    print("Wrong turn, fell in a hole. Game Over!")
elif cross_roads=="left":
    lake=input("You've come to a lake. There is an island in the middle of the lake.\n Type 'wait' to wait for a boat. Type 'swim' to swim across: ")
    if lake=="swim":
        print("You got attacked by a crocodile! Game Over!")
    elif lake=="wait":
        print("You arrived at a island unharmed. There is a house with 3 doors.\n One red, one yellow and one blue. Which colour do you choose?")
        door=input("Type 'red', 'yellow' or 'blue': ").lower()
        if door=="red":
            print("It's a room full of fire. Game Over!")
        elif door=="yellow":
            print("You found the treasure! You Win!!")
        elif door=="blue":
            print("You enter a room full of hungry beasts. Game Over!")

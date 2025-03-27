#Reeborg's world(Hurdles challenge 1)

def turn_right():
    turn_left()
    turn_left()
    turn_left()

def jump():
    move()
    turn_left()
    move()
    turn_right()
    move()
    turn_right()
    move()
    turn_left()
    
  #using for loop  
for step in range(6):
    jump()
    
#using while loop
number_of_hurdles=6
while number_of_hurdles>0:
    jump()
    print(number_of_hurdles)


#Reeborg's world(Hurdles challenge 2)
def turn_right():
    turn_left()
    turn_left()
    turn_left()

def over_wall():
    move()
    turn_left()
    move()
    turn_right()
    move()
    turn_right()
    move()
    turn_left()
 

while not at_goal() !=False:
    over_wall()

#ph1n3y

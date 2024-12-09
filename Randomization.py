#printing a random number >=1 and <=10
import random
random_number= random.randint(1,10)
print(random_number)

# prints a random float between 0.0 and < 1.0
import random
random_number_0_to_1 =random.random()
print(random_number_0_to_1)  

#Heads or Tails game
import random
# prints a random integer in the range [1, 2]
if random.randint(1, 2) == 1:
    print("HEAD")
else:
    print("TAIL")

#randomizing lists
import random
friends = ["Alice", "Bob", "Charlie", "David", "Emanuel"]
random.shuffle(friends)
print(friends[0])
#OR
random_index=random.randint(0,4)
print(friends[random_index])
#OR
print(random.choice(friends))

fruits=["apple", "banana", "cherry", "date", "elderberry"]
for fruit in fruits:
    print(fruit)
    print(fruit + " fruit")
print(fruits)


#using for loops to write the max function i.e its the function that outputs the highest value of a list of items
student_scores = [150, 142, 185, 120, 171, 184, 149, 24, 59, 68, 199, 78, 65, 89, 86, 55, 91, 64, 89]
max_score=0
for score in student_scores:
    if score > max_score:
        max_score=score
print(max_score)



#Carl Gauss' 1-100 addtion trick in py
num_add=0
for number in range(1,101):
    num_add+=number
print(num_add)

#FizzBuzz
for number in range(1,101):
    if number % 3 == 0 and number % 5 == 0:
        print("FizzBuzz")
    elif number % 5 == 0:
        print("Buzz")
    elif number % 3 == 0:
        print("Fizz")
    else:
        print(number)

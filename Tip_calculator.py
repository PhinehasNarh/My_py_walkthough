print("Welcome to ph1n3y's tip calculator!")
bill = float(input("What was the total bill? $"))
tip = float(input("What percentage tip would you like to give? "))
split= int(input("How many people to split the bill? "))
total_bill = round((bill + (bill * (tip / 100)))/split, 2)
print(f"Each person should pay: ${total_bill}, not even a dime less")  

#ph1n3y

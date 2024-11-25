print("Welcome to ph1n3y's tip calculator!")
bill = float(input("What was the total bill? $"))
tip = float(input("What percentage tip would you like to give? "))
split= float(input("How many people to split the bill? "))
total_bill = (bill + (bill * (tip / 100)))/split
print(f"Each person should pay: ${total_bill:.2f}, not even a dime less..hahaha")  

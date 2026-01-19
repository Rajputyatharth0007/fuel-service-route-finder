def signup():
    print("Existing user login")
    # Add logic for existing user login here
    userid = input("Enter your user ID: ")
    password = input("Enter your password: ")
    # Validate credentials (this is just a placeholder)
    print(f"Welcome back, {userid}!")

def newuser():
    print("New user fill the details")
    # Add logic for new user registration here
    name = input("Enter your name: ")
    userid = input("Create a user ID: ")
    email = input("Enter your email: ")
    password = input("Create a password: ")
    phone = input("Enter your phone number: ")
    # Save user details (this is just a placeholder)
    print(f"Thank you for registering, {name}!")


logincheck = True
while logincheck == True:
    print("Welcome to Fuel serivce")
    print("Signup(S)/New user(N)")
    choice = input("Enter the choice")

    if (choice == "S"):
        signup()
        logincheck = False
        break 


    elif (choice == "N"):
        newuser()
        logincheck = True
        break
    
    else:
        print("Invalid choice. Please enter 'S' for Signup or 'N' for New user.")
        logincheck = True
        continue



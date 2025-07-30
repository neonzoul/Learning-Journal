# say hello, ask username, role 2 object can select ('admin', 'user') -> say, hello with different message + {username}
# addition: use variable type.
# addition: use JSON data.
# addition: inquirer for Interactive role selection.

import inquirer

# == State Declare ==
hello_msg: str = "hello, world"
username: str = ""
available_roles: tuple[str, ...] = ('admin', 'user', 'guest')
selected_role: str = ""
age: int = 0

# Pack into dictionary then convert to JSON
user_data = {
    "username": username,
    "role": selected_role,
    "age": age
}

def say_hello() -> None:
    print(f"{hello_msg}")

def collect_user_info() -> dict:
    print("--Please Enter Username-- \n")

    username = input('username: ')

    # Interactive role selection
    questions = [
        inquirer.List('role',
                      message="Select your role",
                      choices=available_roles,
                      carousel=True),
    ]
    answers = inquirer.prompt(questions)
    selected_role = answers['role']

    # collect age
    while True:
        try:
            age = int(input('Age: '))
            break
        except ValueError:
            print("Please enter a valid number for age. ")
    
    user_data = {
        "username": username,
        "role": selected_role,
        "age": age
    }
    
    return user_data

say_hello()
user_info = collect_user_info()

print(f"Userinfo: {user_info}")


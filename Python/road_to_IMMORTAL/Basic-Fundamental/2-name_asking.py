hello_message: str = "hello, world"
name: str = ""

def first_hello() -> None:
    print(f"{hello_message}")

def asking_name() -> str:
    name: str = input("What is your name? \n: ")
    return name

first_hello()
name = asking_name()

print(f"hello, {name}")
# We can Declare or Initialize inside class
class Car:
    # can use Special Method to initialize attribute
    # to setup instant of the class (init scope use just inside class Car)
    def __init__(self, name:str, colour: str, horsepower: int) -> None: 
    # can provide specific argument or Information like colour
    # [[ return None because just initialize will not return anything ]]
        self.name = name
        self.colour = colour
        self.horsepower = horsepower

    # (advance) for print the instant information for User easy to read
    def __str__(self) -> str:
        return f'Car(name={self.name} colour={self.colour}, horsepower={self.horsepower})'
    # for call display with provide just name
    def display_with_name(self, name: str) -> str:
        return f'{self.name}(colour is {self.colour}, horsepower: {self.horsepower})'
    

# call the clasee with car information as argument.
# or to customize instant just the specific element.
volvo: Car = Car('volvo', 'red', 200)
print("This volvo car is colour",volvo.colour)
print("and horsepower is",volvo.colour)
print(volvo) # call __str__
print(volvo.display_with_name('volvo')) # call to display provide just Car name

bmw: Car = Car('bmw', 'white', 220)
print(f'This is a {bmw.name}, color is {bmw.colour} and horsepower is {bmw.horsepower}')

class Microwave:
    # == Initailizer(Dunder Method)== [Declare State]
    def __init__(self, brand: str, power_rating: str) -> None:
        self.brand = brand
        self.power_rating = power_rating
        self.turned_on: bool = False

    # -- Method 1 Turned On --
    def turn_on(self) -> None:
        if self.turned_on:
            print(f'Microwave ({self.brand}) is already turned on.')
        else:
            self.turned_on = True
            print(f'Microwave({self.brand}) is now turned on.')

    # -- Method 2 Turned Off --
    def turn_off(self) -> None:
        if self.turned_on:
            print(f'Microwave ({self.brand}) is already turned off.')
        else:
            self.turned_on = False
            print(f'Microwave({self.brand}) is now turned off.')

    # -- Method 3 Run --
    def run(self, seconds: int) -> None:
        if self.turned_on:
            print(f'Running ({self.brand}) for {seconds} seconds')
        else:
            print(f'A mystical force whispers: "Turn on your microwave first..."')

    # -- Dunder Methods -- [[or double underscore method]]
    def __add__(self, other: "Microwave") -> str:
        return f'{self.brand} + {other.brand}'
    
    def __mul__(self, other: "Microwave") -> str:
        return f'{self.brand} * {other.brand}'
    
    # print self (for print user friendly form)
    def __str__(self) -> str:
        return f'{self.brand} (Rating: {self.power_rating})'
    # (if don't have this method when call self class it will call representation 
    # like <__main__.Microwave object at 0x1012dee804> as default)

    # if have __str__ but need to print representation more details
    def __repr__(self) -> str:
        return f'Microwave(brand="{self.brand}", power_rating="{self.power_rating}")'
    
"""
Microwave Brand Database
"""

smeg: Microwave = Microwave(brand='Smeg', power_rating='B')
smeg.turn_on()
smeg.run(30)
smeg.turn_off()
smeg.run(10) # should notic to turn on first.

bosch: Microwave = Microwave(brand='Bosch', power_rating='C')

# call Dunder Method
print(smeg + bosch) # __add__
print(smeg * bosch) # __mul__
print(smeg) # __str__ (print self)
print(bosch)
print(repr(smeg)) # __repr__ (repesentation)

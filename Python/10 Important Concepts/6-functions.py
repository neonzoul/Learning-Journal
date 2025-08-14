from datetime import datetime

# This funtion will privide current time everywhere they called
def show_date() -> None:
    print('this is the current data and time:')
    print(datetime.now())

show_date()
show_date()
#---------------------------------------

# For funtion can more customize able
# can provide parameter
def greet(name: str) -> None: # provide parameter (or argument) call name as string.
    print(f'ว่าพรื่อ, {name}!')

greet('Bob') # call function with provide argument.
greet('Luigi')
#---------------------------------------

# Function can return as result
def add(a: float, b: float) -> float: # [[ provide a,b as float, expect result as float (-> float) ]]
    print(f'>>inside funtion \nfunction parameter: a={a} b={b}<<')
    return a + b
# call function provide argument as number that we need to culculate
print('\nNext line will call function add with Arguments.')
print("after call function add prvide a,b the result that function return = ", add(1, 2))

# In modern Python, the | symbol in a type hint means "or". It's used to create what's called a Union Type.
my_variable: int | str                      # meaning my_variable can be int or str (int union str)
my_variable_bool_or_none: bool | None       # this variable can be True,False,None
id: int | None                              # id can be int or None

# In the SQLModel in the project AutomateOS
"""
./models/ user.py, workflow.py we have
    id: int | None = Field(default=None, Primary_key=True)
Can explain like following.
""" 
# Field() is a special funtion from SQLModel. 
# While the type hint(: int | None) tells Python about type
# Field() tells the database the rules for this column

# Putting It All Together
from sqlmodel import SQLModel ,Field

class User(SQLModel, table=True)
    id: int | None = Field(default=None, primary_key=True)
"""
- id: "We have an attribute named id."
- : int | None: "its type can be an integer | it can be None
    -When first create an object in Python (e.g. a new user), it doesn't have an ID yet,
    so its id is None. After save it to the database, 
    the database assigns it a number, so its id becomes an int
- = Field(...): "And here are the rules for the database column:"
"""

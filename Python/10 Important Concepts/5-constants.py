# in Python dont actually have constant
# But can use Type Annotation and Naming Convention to show that is constant

from typing import Final

# Declare as Final to block reassign the VARIABLE
VERSION: Final[str] = '1.0.12'

# if try to change constant Pylance (or mypy) can Notice.
VERSION = '1.0.13'
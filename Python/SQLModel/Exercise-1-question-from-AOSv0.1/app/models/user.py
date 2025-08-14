from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

# TYPE_CHECKING is used to avoid circular imports while still providing type hints
# This allows us to reference Workflow class without importing it at runtime
if TYPE_CHECKING:
    from .workflow import Workflow


# == Initailize [Declare]== | Declarative Style for SQLModel
class User(SQLModel, table=True):
    """
    User model representing a user in the automation system.
    
    Users are the primary entities that create and manage workflows.
    Each user can have multiple workflows associated with their account.
    Authentication is handled through email and hashed password.
    """
    # -- DECLARING User table model -- | fields and properties
    id: int | None = Field(default=None, primary_key=True)
    
    # User's email address - must be unique and is indexed for fast lookups
    # Used as the primary identifier for authentication
    email: str = Field(unique=True, index=True)
    
    # Hashed password for authentication
    # Never store plain text passwords - always use proper hashing
    hashed_password: str

    # -- DECLARING - Relationship to Workflow model -- (one user to many workflows)
    workflows: List["Workflow"] = Relationship(back_populates="user")
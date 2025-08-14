# Create a temporary script to interact directly with the database models that defined.

from sqlmodel import create_engine, Session, SQLModel
from app.models import User, Workflow # We can import like this because of our __init__.py!

# Define the database file
DATABASE_URL = "sqlite:///database.db"

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    print("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    print("Done.")

# Main function to run our test
def main():
    create_db_and_tables()

    # A session is a conversation with the database
    with Session(engine) as session:

        print("\n--- Step 1: Create a User ---")
        # Notice we DON'T provide an ID. It's None by default.
        user_to_create = User(email="moss@example.com", hashed_password="fake_password_hash")

        session.add(user_to_create)
        session.commit()
        session.refresh(user_to_create) # Refresh to get the ID assigned by the DB

        print("Created User:", user_to_create)


        print("\n--- Step 2: Create a Workflow for that User ---")
        workflow_to_create = Workflow(
            name="My First Automation",
            definition={"trigger": "webhook", "steps": []}, # Example definition
            user=user_to_create # Link it directly to the user object
        )

        session.add(workflow_to_create)
        session.commit()
        session.refresh(workflow_to_create)

        print("Created Workflow:", workflow_to_create)


        print("\n--- Step 3: Query and See the Results ---")
        # Get the user back from the database
        user_from_db = session.get(User, user_to_create.id)

        print("User from DB:", user_from_db)
        if user_from_db is not None:
            print("Workflows belonging to this user:", user_from_db.workflows)
        else:
            print("User not found in the database.")


if __name__ == "__main__":
    main()
This new scenario will force you to combine _reading_ from the database with _writing_ to it, which is the next logical step and a core part of any real application.

### The New Assignment 🎯

**The Workflow Executor and Logger**

**Scenario:** Imagine a user's webhook has just been triggered for one of their workflows. Your task is to write a new script (`test_runner.py`) that simulates what happens in the database: it must **find the correct workflow** and then **log a new 'run' for it**, marking it as successful.

---

### The Reason (Why This Assignment Helps) 🤔

This assignment is designed to make the concepts click by forcing you to use them in a more realistic sequence.

-   **Combines Reading & Writing:** The first script was mostly about _creating_ new things. This script requires you to **first read/find** an existing User and Workflow from the database before you can **write** a new `WorkflowRun` log. This is a much more common real-world pattern.
-   **Reinforces Relationships:** You cannot create a `WorkflowRun` without first having a `Workflow`. This will force you to work with the `User` -> `Workflow` -> `WorkflowRun` relationship chain, making it more tangible.
-   **Simulates Real Application Logic:** This is a small-scale simulation of the absolute core function of your **AutomateOS** execution engine. Understanding this flow is critical.

---

### Your Step-by-Step Guide 🛠️

You will be "doing by myself, thinking by myself," but here is the path to follow.

#### Step 1: Setup Your Script (`test_runner.py`)

1.  In your project root, create a new file named `test_runner.py`.
2.  Copy the setup code from the top of your `test_db.py` file. You will need all the imports, the `DATABASE_URL`, and the `engine` creation. You do not need the `create_db_and_tables` function, as the tables already exist from the last script.

#### Step 2: Find the User and Their Workflow

Your script needs to work with the data you created in the first exercise. We know a `User` with `id=1` and a `Workflow` with `id=1` exist.

-   **Guide:**
    1.  Inside your `main` function, create the `with Session(engine) as session:` block.
    2.  Use `session.get(User, 1)` to fetch the user with an ID of 1 from the database. Store this in a variable like `user_from_db`.
    3.  **Think:** How do you check if the user was actually found? Add an `if` statement to handle the case where `user_from_db` might be `None`.
    4.  **Think:** Once you have the user object, how do you access the workflows that belong to them? Access the relationship attribute you defined in your models and store the first workflow in a variable like `workflow_to_run`.

#### Step 3: Create the New Workflow Log

Now that you have the specific workflow you want to "run," you need to create a `WorkflowRun` object to represent the log record for this execution.

-   **Guide:**
    1.  Create a new instance of your `WorkflowRun` model.
    2.  **Think:** What fields does the `WorkflowRun` model need? Look at its definition in `app/models/workflow_run.py`. It needs a `status` and a `workflow_id`.
    3.  Set the `status` to `"success"`.
    4.  For the `workflow_id`, you can link it directly to the `workflow_to_run` object you retrieved in the previous step. SQLModel is smart enough to handle this relationship.

#### Step 4: Save the Log to the Database

You've created the `WorkflowRun` object in Python, but it doesn't exist in the database yet. Now you must save it.

-   **Guide:**
    -   Use the exact same three-step pattern you learned in the first exercise: `session.add()`, `session.commit()`, and `session.refresh()`.

#### Step 5: Verify Your Work

After committing, the log should be in the database. The final step is to prove it by querying the data back.

-   **Guide:**
    1.  **Think:** You still have the `workflow_to_run` object. How can you see all the `run` logs associated with it?
    2.  Access the relationship attribute for runs (e.g., `workflow_to_run.runs`).
    3.  Print the results. You should see a list containing the new `WorkflowRun` object you just created.

When you run `python test_runner.py`, you should see the `echo=True` output showing you `SELECT`ing the user and workflow, then `INSERT`ing the new workflow run, and finally your `print` statements confirming the result.

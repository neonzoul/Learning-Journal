For the core challenge for Week 3 is mastering the **Producer/Queue/Worker** pattern to handle slow, asynchronous tasks. This is the heart of your `AutomateOS` engine.

Here is a project idea designed specifically to prepare you for this.

### The Assignment: The "QuickThumb" Image Resizer API 📝

You will build a backend service that accepts an image upload, offloads the slow task of resizing it to a background worker, and immediately responds to the user.

### The Reason (Why This is the Perfect Project) 🤔

-   **Real-World Problem:** Resizing an image is a classic example of a task that is too slow to handle in a live web request. Offloading it is a professional-grade solution.
-   **Directly Maps to `AutomateOS`:** The API endpoint acts as your **Webhook Trigger**, and the background resizer is a stand-in for your **Workflow Execution Engine**. It's the exact same architecture.
-   **Forces Asynchronous Thinking:** You will see firsthand why the `async def` webhook is critical for a responsive API that doesn't make users wait.
-   **Introduces New Skills:** You'll learn how to handle file uploads in FastAPI and perform basic image manipulation, which are valuable skills.

---

### Step-by-Step Guide 🛠️

Here is your guide to building the QuickThumb service.

#### Step 1: Project Setup

1.  Create a new project folder (e.g., `quickthumb`).
2.  Set up and activate a virtual environment.
3.  Create your standard `src` folder structure and a `main.py` and `worker.py` in the root.
4.  Create a `requirements.txt` file and add the following, then run `pip install -r requirements.txt`:
    ```
    fastapi
    uvicorn
    sqlmodel
    redis
    rq
    Pillow
    ```
5.  Create two new folders in your project root: `uploads/` and `processed/`.

#### Step 2: Define the Job (`src/tasks.py`)

This file will contain the slow, heavy-lifting function that the worker will execute.

-   **Guide:**
    1.  Create a new file `src/tasks.py`.
    2.  Define a function `resize_image(original_path: str)`.
    3.  Inside this function, use the `Pillow` library (imported as `from PIL import Image`) to:
        -   Open the image from `original_path`.
        -   Resize it to a thumbnail (e.g., 128x128 pixels).
        -   Save the new thumbnail to your `processed/` folder.
        -   Print a confirmation message like `"Resized image and saved to processed folder."`
        -   (Optional) Use `os.remove(original_path)` to delete the original file after processing.

#### Step 3: Build the API (`main.py`)

This is your **Producer**. It receives the image and queues the job.

-   **Guide:**
    1.  Import `FastAPI`, `UploadFile`, `File`, `redis`, and `Queue`.
    2.  Set up your FastAPI app and your connection to the Redis Queue.
    3.  Create one `async def` endpoint: `POST /images/`.
    4.  This endpoint should accept an `image: UploadFile = File(...)` as an argument.
    5.  **Inside the endpoint:**
        -   Save the uploaded image's contents to a temporary file in your `uploads/` folder.
        -   Add a job to the RQ queue by calling `q.enqueue(resize_image, path_to_saved_file)`.
        -   Immediately `return` a JSON response like `{"message": "Image is being resized in the background"}`. **Do not wait for the resizing to finish.**

#### Step 4: Build the Worker (`worker.py`)

This is your **Consumer**. It watches the queue and does the actual work.

-   **Guide:**
    1.  This script will be very simple.
    2.  Import `redis` and `Worker`, `Queue`, `Connection` from `rq`.
    3.  Connect to your Redis instance.
    4.  Create a `Worker` that listens to your queue.
    5.  Start the worker with `worker.work()`.

### How to Run Your Service

You will need **two separate terminals** running at the same time:

1.  **Terminal 1 (The Worker):**
    `python worker.py`
2.  **Terminal 2 (The API):**
    `uvicorn main:app --reload`

You can then use the FastAPI `/docs` page to upload an image file. You should get an instant response from the API, and a few moments later, you will see the confirmation message from your worker in its terminal and the new thumbnail in your `processed/` folder.

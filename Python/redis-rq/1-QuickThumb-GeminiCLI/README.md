# QuickThumb: An Asynchronous Image Resizing API

This project is a demonstration of a fundamental pattern for building robust, scalable web applications. It's an API that accepts an image upload, resizes it to a thumbnail, and saves the result.

While this sounds simple, it's designed to teach one of the most important concepts in backend development: **handling slow tasks without making the user wait.**

## The Analogy: A Restaurant

Imagine you're at a busy restaurant. You, the customer, give your order to a cashier. The cashier takes your order, gives you a receipt, and you can go sit down. You get an immediate response.

Meanwhile, in the kitchen, a chef picks up your order from a ticket line and starts cooking. The cooking might be fast (a salad) or slow (a well-done steak), but you don't have to stand at the counter waiting for it to be done.

This project works exactly like that restaurant.

-   **The Cashier**: Our API server (`main.py`). It's fast, friendly, and its only job is to take the "order" (the image).
-   **The Order Line**: Our **Redis Queue**. This is the ticket rail where the cashier puts new orders.
-   **The Chef**: Our **Worker** (`worker.py`). They work in the "kitchen" (the background), constantly watching the order line for the next job to complete.

## The Problem: Why Do We Need This?

When a user sends a request to a web server (like uploading an image), they expect a response almost instantly. Image processing, however, is **slow**. It can take several seconds.

If our API server (the Cashier) tried to do the resizing itself, the user would be stuck waiting, staring at a loading spinner. This is a bad user experience. If many users upload images at once, the whole application would grind to a halt.

## The Solution: The Producer/Queue/Worker Pattern

This architecture solves the problem by separating the fast work from the slow work.

1.  **Producer (The Cashier - `main.py`)**: The FastAPI server is our "Producer". It produces jobs that need to be done. When it receives an image, it saves the file to a temporary location and places a "job ticket" on the queue. This ticket contains all the information needed to do the job (i.e., the name of the function to run and the path to the image file). It then immediately returns a response to the user, saying, "We've received your order!"

2.  **Queue (The Order Line - `Redis` + `RQ`)**:

    -   **Redis** is an extremely fast, in-memory data store. Because it's so fast, it's the perfect tool to act as our message queue or "order line".
    -   **RQ (Redis Queue)** is a Python library that makes using Redis for this exact purpose incredibly simple. It gives us the tools to easily `enqueue` jobs from our producer and have a `Worker` listen for those jobs.

3.  **Worker (The Chef - `worker.py`)**: The worker is a completely separate Python script that runs in the background. It connects to the same Redis Queue. Its only purpose is to watch the queue for new jobs. When a job appears, the worker picks it up, reads the instructions (e.g., "resize the image at `uploads/xyz.jpg`"), and performs the slow task defined in `src/tasks.py`. It works completely independently of the API server.

### A Note on Windows Compatibility

The standard RQ `Worker` is built for Unix-like operating systems (Linux, macOS) and relies on a command (`os.fork()`) that does not exist on Windows. To ensure this project runs correctly on Windows, we use the `SimpleWorker` class provided by RQ. The `SimpleWorker` runs jobs sequentially in the same process, providing the same core functionality without relying on `fork()`.

### Visual Flow

```
          +-----------------+      +----------------+      +------------------+
User -- > |  FastAPI Server | -- > |   Redis Queue  | -- > |   RQ Worker      |
          |    (main.py)    |      | (The Job List) |      |    (worker.py)   |
          +-----------------+      +----------------+      +------------------+
                 |                                                 |
                 | (Responds Immediately)                          | (Processes Slowly)
                 v                                                 v
          {"message": "Order received!"}                     (Saves thumbnail to 'processed/' folder)
```

## How to Run This Project

#### Prerequisites

-   Python 3.10+
-   Docker Desktop (for running Redis)

#### Step 1: Start Redis

Redis will act as our job queue. The easiest way to run it is with Docker.

```bash
docker run -d --name quickthumb-redis -p 6379:6379 redis:latest
```

#### Step 2: Install Dependencies

Set up a virtual environment and install the required Python packages.

```bash
# Create and activate a virtual environment (e.g., python -m venv .venv)
.venv\Scripts\activate

# Install packages
pip install -r requirement.txt
```

#### Step 3: Run the Worker and Server

You need to run two separate scripts in **two separate terminals**.

**In your FIRST terminal, run the Worker:**
This starts the "Chef" who will listen for jobs.

```bash
python worker.py
```

**In your SECOND terminal, run the API Server:**
This starts the "Cashier" who will accept requests.

```bash
uvicorn main:app --reload
```

#### Step 4: Test It!

-   Open your browser to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
-   Use the interface to upload an image file.
-   You will get an immediate JSON response from the server.
-   A few moments later, you will see activity in your **worker terminal** as it processes the job.
-   Check the `processed/` folder in the project directory to find your new thumbnail!

## Key Takeaways

-   **Asynchronous Processing**: You've built a system that can handle tasks asynchronously, leading to a much better user experience.
-   **Separation of Concerns**: The API server is only concerned with web requests, and the worker is only concerned with processing jobs. This makes the application easier to develop, debug, and scale.
-   **Scalability**: If your image resizing tasks become too much for one worker, you can simply run more worker scripts (more "Chefs") to process jobs in parallel without changing the API code at all.

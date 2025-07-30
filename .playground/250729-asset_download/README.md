# Asset Downloader

A Python tool for downloading multiple files concurrently from URLs.

---

### Why Build This?

Downloading a large number of assets from a list of URLs is often a **slow and manual** process. Traditional scripts typically download files one by one, wasting valuable time waiting for each download to complete before starting the next.

This project was created to solve that problem. By using **asynchronous programming**, it can download multiple files **concurrently**, which dramatically reduces the total time spent waiting. It turns a tedious, manual task into a fast, automated process managed entirely from the command line.

---

## What it does

-   Downloads files from URLs listed in a text file
-   Supports concurrent downloads for faster performance
-   Can download single files or batch process multiple URLs
-   Automatically creates organized download folders
-   Provides progress feedback and error handling

## Usage

```bash
# Download all URLs from urls.txt (default)
python downloader.py

# Download with custom concurrency
python downloader.py --concurrent 10

# Download from a different file
python downloader.py --file my_urls.txt (example file urls.txt)

# Download a single URL
python downloader.py --url "https://example.com/image.jpg"

# Show help
python downloader.py --help
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Add URLs to [`urls.txt`](urls.txt) (one per line)
3. Run the script

## Technical Highlights

-   **Asynchronous Programming**: Using `async`/`await` for concurrent operations
-   **HTTP Requests**: Making web requests with the `httpx` library
-   **File I/O**: Reading from files and writing downloaded content
-   **Command-line Tools**: Building CLI applications with `argparse`
-   **Error Handling**: Managing network failures and file operations
-   **Project Structure**: Organizing code into reusable functions
-   **Path Management**: Working with file paths and directory creation using `os`
-   **List Comprehensions**: Creating task lists efficiently
-   **Context Managers**: Using `async with` for resource management
-   **String Manipulation**: Extracting filenames from URLs

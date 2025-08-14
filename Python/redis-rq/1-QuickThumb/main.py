import os
import uuid
from fastapi import FastAPI, UploadFile, File
from redis import Redis
from rq import Queue
from typing import Dict



# No longer need a direct import of the task function
# from src.tasks import resize_image

# Ensure the directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)

app = FastAPI(title="QuickThumb API")

redis_conn = Redis(host='localhost', port=6379)
q = Queue(connection=redis_conn)

@app.post("/images/")
async def create_upload_file(image: UploadFile = File(...)) -> Dict[str, str]:
    # Type-safe check for the filename.
    if not image.filename:
        return {"error": "No filename provided in the upload."}

    # Unpack the name and extension in a more readable way.
    # Pylance is now happy because it knows image.filename is a string here.
    _root, file_extension = os.path.splitext(image.filename)
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = os.path.join("uploads", unique_filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
    except Exception as e:
        return {"error": f"Failed to save uploaded file: {e}"}

    # Enqueue the job for the worker using a string path.
    # This is a more decoupled and robust pattern.
    q.enqueue('src.tasks.resize_image', temp_file_path)  # type: ignore

    return {"message": "Image is being resized in the background."}
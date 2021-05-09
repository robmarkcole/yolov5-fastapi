import os
import sys

sys.path.insert(0, os.path.realpath(os.path.pardir))
import logging
import uuid

import numpy as np
from celery.result import AsyncResult
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from models import Prediction, Task
from pydantic.typing import List
import time

from celery_tasks.tasks import predict_image

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static/results"
OBJ_DETECTION_URL = "/v1/vision/detection"

isdir = os.path.isdir(UPLOAD_FOLDER)
if not isdir:
    os.makedirs(UPLOAD_FOLDER)

isdir = os.path.isdir(STATIC_FOLDER)
if not isdir:
    os.makedirs(STATIC_FOLDER)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/process")
async def process(files: List[UploadFile] = File(...)):
    tasks = []
    try:
        for file in files:
            d = {}
            try:
                name = str(uuid.uuid4()).split("-")[0]
                ext = file.filename.split(".")[-1]  # e.g. .jpg
                file_name = f"{UPLOAD_FOLDER}/{name}.{ext}"
                with open(file_name, "wb+") as f:  # write to uploads
                    f.write(file.file.read())
                f.close()

                # start task prediction
                task_id = predict_image.delay(os.path.join("api", file_name))
                d["task_id"] = str(task_id)
                d["status"] = "PROCESSING"
                d["url_result"] = f"/api/result/{task_id}"
            except Exception as ex:
                logging.info(ex)
                d["task_id"] = str(task_id)
                d["status"] = "ERROR"
                d["url_result"] = ""
            tasks.append(d)
        return JSONResponse(status_code=202, content=tasks)
    except Exception as ex:
        logging.info(ex)
        return JSONResponse(status_code=400, content=[])


@app.get("/api/result/{task_id}", response_model=Prediction)
async def result(task_id: str):
    task = AsyncResult(task_id)

    # Task Not Ready
    if not task.ready():
        return JSONResponse(
            status_code=202,
            content={"task_id": str(task_id), "status": task.status, "result": ""},
        )

    # Task done: return the value
    task_result = task.get()
    result = task_result.get("result")
    return JSONResponse(
        status_code=200,
        content={
            "task_id": str(task_id),
            "status": task_result.get("status"),
            "result": result,
        },
    )


@app.get("/api/status/{task_id}", response_model=Prediction)
async def status(task_id: str):
    task = AsyncResult(task_id)
    return JSONResponse(
        status_code=200,
        content={"task_id": str(task_id), "status": task.status, "result": ""},
    )


@app.post(OBJ_DETECTION_URL, response_model=Prediction)
async def predict_object(file: UploadFile = File(...)):
    try:
        name = str(uuid.uuid4()).split("-")[0]
        ext = file.filename.split(".")[-1]  # e.g. .jpg
        file_name = f"{UPLOAD_FOLDER}/{name}.{ext}"
        with open(file_name, "wb+") as f:  # write to uploads
            f.write(file.file.read())
        f.close()

        # start task prediction
        task_id = predict_image.delay(os.path.join("api", file_name))
        task = AsyncResult(task_id)

        task_result = task.get() # A blocking call
        result = task_result.get("result") 
        return JSONResponse(
            status_code=200,
            content={
                "task_id": str(task_id),
                "status": task_result.get("status"),
                "result": result,
            },
        )
    except Exception as ex:
        logging.info(ex)
        return JSONResponse(status_code=400, content=[])
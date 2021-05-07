# Yolov5 object detection with FastAPI

Credit: originally a fork of [OurNemanja/YOLOv5-fastapi-celery-redis-rabbitm](https://github.com/OurNemanja/YOLOv5-fastapi-celery-redis-rabbitmq)

Application to expose Yolov5 model using FastAPI. Inferencing requests are submitted to a Celery task queue, and an asynchronous API is available for polling for results. This approach is described in detail in the excellent article [Serving ML Models in Production with FastAPI and Celery](https://towardsdatascience.com/deploying-ml-models-in-production-with-fastapi-and-celery-7063e539a5db) by [@jonathanreadshaw](https://github.com/jonathanreadshaw/ServingMLFastCelery)

- [FastAPI](https://fastapi.tiangolo.com): python framework for building APIs
- [Celery](https://celeryproject.org): task queue with focus on real-time processing
- [RabbitMQ](https://www.rabbitmq.com): message broker used to route messages between API and the workers from Celery
- [Redis](https://redis.io): in-memory database to store results and process status from the tasks

<img src=img/schema.jpg>

# Usage
Run all containers:

```bash
docker-compose up
```

This will start:
- rabbitmq: message broker
- redis: in-memory database on port 6379, simply used by rabbitmq
- worker: application logic (Yolo model, FastAPI and Celery) on port 8000

Perform some API requests using the integrated Swagger UI http://localhost:8000/docs

<img src=img/doc.gif>

API Services available
| Endpoint | Method | Description
| --- | --- | --- |
| http://localhost:8000/api/process | POST | Send one or more pictures to be processed by Yolov5. Return the task_id of each task.
| http://localhost:8000/api/status/<task_id>  | GET  | Retrieve the status of a given task
| http://localhost:8000/api/result/<task_id>    | GET  | Retrieve the results of a given task
| http://localhost:8000/docs   | GET  | Documentation generated for each endpoint
| http://localhost:15672   | GET  | RabbitMQ monitor. User: guest     Password: guest.
| http://localhost   | GET  | Simple webapp to show how to use and display results from the API.

## Development
* `python3 -m venv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `isort .`
* `black .`
* `pytest .` # none implemented

Overview of the code
- [api/app.py](api/app.py): expose the endpoints and send the request task to celery.
- [celery_tasks/tasks.py](celery_tasks/tasks.py): receive the task and send (enqueue) to workers process.
- [celery_tasks/yolo.py](celery_tasks/yolo.py): code to initialize and expose a method receive a picture and return the predictions.
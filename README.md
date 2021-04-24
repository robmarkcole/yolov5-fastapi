# yolov5-fastapi
FastAPI app exposing yolov5 object detection. This will be a simple implementation without requiring extra services. For a more complex implementation with queued requests see [OurNemanja/YOLOv5-fastapi-celery-redis-rabbitmq](https://github.com/OurNemanja/YOLOv5-fastapi-celery-redis-rabbitmq)

- Install yolov5 from pip to keep up to date -> https://github.com/fcakyon/yolov5-pip
- Use new pandas to json method -> https://github.com/ultralytics/yolov5/blob/master/utils/flask_rest_api/restapi.py
- Implement endpoints for compatability with Deepstack -> https://github.com/robmarkcole/tensorflow-lite-rest-server
- Streamlit UI is then available -> https://github.com/robmarkcole/deepstack-ui

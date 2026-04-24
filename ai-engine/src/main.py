import os

import redis
import json
from minio import Minio

from models_wrapper import ModelsEngine
from processor import ViolationProcessor

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
MINIO_URL = os.getenv("MINIO_URL", "minio:9000")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
minio_client = Minio(MINIO_URL, access_key="minioadmin", secret_key="minioadmin", secure=False)

engine = ModelsEngine()
processor = ViolationProcessor(engine, minio_client)

while True:
    task_data = r.blpop("task_queue", timeout=0)
    if task_data:
        violation_id = task_data[1]
        print(f"Processing violation: {violation_id}")

        try:
            objects = list(minio_client.list_objects(
                "scooter-violations",
                prefix=f"originals/{violation_id}",
                recursive=True
            ))

            if not objects:
                raise Exception(f"File for violation {violation_id} not found in MinIO")

            object_name = objects[0].object_name
            file_extension = os.path.splitext(object_name)[1].lower()

            fps, duration, result = processor.process(violation_id, object_name, file_extension)
            print('Finished successfully')
            message = {
                "id": violation_id,
                "status": "COMPLETED",
                "video_duration": duration,
                "fps": fps,
                "violations": result
            }
            r.lpush("finished_queue", json.dumps(message))
        except Exception as e:
            print(f"Error: {e}")
            r.lpush("finished_queue", json.dumps({"id": violation_id, "status": "FAILED"}))
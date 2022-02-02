import asyncio
import json
from os import stat

import aioredis
from src.data import Water
import uvicorn
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from decouple import config
from fastapi import FastAPI, WebSocket, BackgroundTasks, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

r = aioredis.from_url(
    "redis://{ip}:{port}/{db}".format(
        ip=config("REDIS_SERVER_IP"),
        port=config("REDIS_SERVER_PORT", cast=int),
        db=config("REDIS_SERVER_DB", cast=int),
    )
)
KAFKA_URL = "{ip}:{port}".format(
    ip=config("KAFKA_SERVER_IP"),
    port=config("KAFKA_SERVER_PORT", cast=int),
)
KAFKA_INPUT_TOPIC = config("KAFKA_INPUT_TOPIC")
KAFKA_OUTPUT_TOPIC = config("KAFKA_OUTPUT_TOPIC")

producer = None
consumer = None


async def pickle_msg(data: dict) -> bytes:
    return json.dumps(data).encode("utf-8")


async def unpickle_msg(data: bytes) -> dict:
    return json.loads(data.decode("utf-8"))


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


async def redis_task(water: Water):
    await producer.send_and_wait(KAFKA_INPUT_TOPIC, await pickle_msg(water.dict()))
    try:
        consumer = AIOKafkaConsumer(
            KAFKA_OUTPUT_TOPIC,
            bootstrap_servers=KAFKA_URL,
        )
        await consumer.start()
        async for msg in consumer:
            if msg.key.decode("utf-8") == water.job_id:
                print(f"job {water.job_id} finished")
                raise StopIteration
    except StopIteration:
        await r.set(water.job_id, msg.value, ex=60)
    finally:
        await consumer.stop()


@app.on_event("startup")
async def handle_starup():
    global producer, consumer

    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_URL)
    await producer.start()


@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()


@app.websocket("/ws/await_job_done/{job_uuid}")
async def wsproto(ws: WebSocket, job_uuid: str):
    await ws.accept()
    while True:
        if await r.exists(job_uuid):
            await ws.send_text((await r.get(job_uuid)).decode("utf-8"))
            break
        await asyncio.sleep(0.5)
    await ws.close()


@app.post("/schedule")
async def add_task_to_kafka(water: Water, bg: BackgroundTasks):
    bg.add_task(redis_task, water)
    return water.job_id


@app.get("/results/{job_id}")
async def add_task_to_kafka(job_id: str):
    if await r.exists(job_id):
        return await r.get(job_id)
    else:
        raise HTTPException(status_code=404, detail="Not exists")


@app.get("/", response_class=RedirectResponse)
async def redrect_to_index():
    return "/static/index.html"


def run():
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()

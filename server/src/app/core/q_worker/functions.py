import asyncio
import logging

import uvloop
from arq.worker import Worker

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    # ctx["db"] = await anext(async_get_db())  # to use db in async call
    logging.info("Worker Started")

    # initialize models as this is a separate worker process and doesnt share
    # the context of the core fastapi lifecycle
    # --- Warm up the models
    # settings.MODELS["sentence_transformer"] = SentenceTransformer(
    #     settings.HF_EMBEDDINGS_MODEL_NAME
    # )


async def shutdown(ctx: Worker) -> None:
    # await ctx["db"].close() # to use db in async call
    logging.info("Worker end")
    # settings.MODELS.clear()

import argparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# from contextlib import asynccontextmanager

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     pass


# app = FastAPI(lifespan=lifespan)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------

parser = argparse.ArgumentParser(description="Whisper FastAPI Online Server")
parser.add_argument(
    "--host",
    type=str,
    default="localhost",
    help="The host address to bind the server to.",
)
parser.add_argument(
    "--port", type=int, default=8000, help="The port number to bind the server to."
)
args = parser.parse_args()

# -------------------------

# Load demo HTML for the root endpoint
with open("web/index.html", "r", encoding="utf-8") as f:
    html = f.read()


@app.get("/")
async def get():
    return HTMLResponse(html)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info",
    )

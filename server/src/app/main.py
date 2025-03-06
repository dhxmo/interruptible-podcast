from multiprocessing import set_start_method

from starlette.middleware.cors import CORSMiddleware

from .api import router
from .core.config import settings
from .core.setup import create_application

# When using spawn you should guard the part that launches the job in if __name__ == '__main__':.
# `set_start_method` should also go there, and everything will run fine.
try:
    set_start_method("spawn")
except RuntimeError as e:
    print(e)

app = create_application(router=router, settings=settings)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

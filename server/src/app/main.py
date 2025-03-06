import logging

from starlette.middleware.cors import CORSMiddleware

from server.src.api import router
from server.src.app.core.config import settings
from server.src.app.core.setup import create_application

try:
    app = create_application(router=router, settings=settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception as e:
    logging.info("Error starting app", str(e))

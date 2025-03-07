from fastapi import APIRouter

from .webrtc import router as wrtc_router

router = APIRouter(prefix="/v1")
router.include_router(wrtc_router)

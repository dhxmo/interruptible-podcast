from fastapi import APIRouter

from .webRTC import router as wrtc_router

router = APIRouter(prefix="/v1")
router.include_router(wrtc_router)

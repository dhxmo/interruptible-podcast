from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
)
from fastapi import APIRouter

from ...core.setup import sio

router = APIRouter(tags=["wrtc"])

pc = RTCPeerConnection()


@sio.on("connect")
def connect():
    print("-----------server connected-----------")


@sio.on("disconnect")
def connect():
    print("-----------server disconnected-----------")


# @sio.on("sdp")
# async def process_sdp(data: dict):
#     print("------------init sdp", data)
#
#     """Handle SDP messages from React Native client"""
#     if data["type"] == "offer":
#         offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
#         await pc.setRemoteDescription(offer)  # Must be set first!
#
#         answer = await pc.createAnswer()
#         await pc.setLocalDescription(answer)  # Set local before sending
#
#         await sio.emit("sdp", {"type": "answer", "sdp": answer.sdp})
#
#
# @sio.on("ICEcandidate")
# async def process_ice(data):
#     """Handle ICE candidates"""
#     candidate_data = data.get("candidate")
#     print("---------candidate_data", candidate_data)
#
#     if candidate_data:
#         # Convert dict to RTCIceCandidate object
#         candidate = RTCIceCandidate(
#             component=1,  # Usually 1 for RTP
#             foundation="foundation",  # Placeholder, not required
#             priority=0,  # Placeholder, not required
#             protocol="udp",  # Extract from candidate_data if needed
#             ip=candidate_data["candidate"].split(" ")[4],  # Extract IP
#             port=int(candidate_data["candidate"].split(" ")[5]),  # Extract port
#             type=candidate_data["candidate"].split(" ")[
#                 7
#             ],  # Extract type (host, srflx, relay)
#             sdpMid=candidate_data.get("sdpMid"),
#             sdpMLineIndex=candidate_data.get("sdpMLineIndex"),
#         )
#
#         await pc.addIceCandidate(candidate)

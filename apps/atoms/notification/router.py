from fastapi import APIRouter
from . import service

router = APIRouter()


@router.get("/notifications/log")
def get_log():
    return {"notifications": service.notification_log[-50:]}


@router.get("/health")
def health():
    return {"status": "healthy", "service": "notification"}

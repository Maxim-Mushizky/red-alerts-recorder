from fastapi import APIRouter, BackgroundTasks, Depends
import asyncio
from typing import Optional

from red_alerts_listener.backend.api.auth import get_admin_user
from red_alerts_listener.backend.helper_functions import get_red_alert_notification_listener

router = APIRouter()
red_alerts_listener = get_red_alert_notification_listener()
polling_task: Optional[asyncio.Task] = None


@router.post("/start-polling")
async def start_polling(background_tasks: BackgroundTasks):
    global polling_task
    if polling_task is None or polling_task.done():
        polling_task = asyncio.create_task(red_alerts_listener.async_poll_alerts())
        background_tasks.add_task(lambda: None)  # Keeps the background task running
        return {"message": "Alert polling started"}
    return {"message": "Alert polling is already running"}


@router.post("/stop-polling")
async def stop_polling():
    global polling_task
    if polling_task and not polling_task.done():
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
        polling_task = None
        return {"message": "Alert polling stopped"}
    return {"message": "Alert polling is not running"}


@router.get("/polling-status")
async def polling_status():
    global polling_task
    if polling_task and not polling_task.done():
        return {"status": "running"}
    return {"status": "not running"}


@router.get("/get-session-notification-ids")
async def get_session_notification_ids():
    global polling_task
    if polling_task and not polling_task.done():
        return {"Session ids": red_alerts_listener.notification_ids}
    return {"Session ids": "No ids"}

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth import get_current_user_id
from app.database import supabase

router = APIRouter()


class PushSubscriptionBody(BaseModel):
    endpoint: str
    keys: dict  # {p256dh: str, auth: str}


@router.post("/subscribe")
async def subscribe_push(
    body: PushSubscriptionBody,
    user_id: str = Depends(get_current_user_id),
):
    """Store a Web Push subscription for the user."""
    record = {
        "user_id": user_id,
        "endpoint": body.endpoint,
        "p256dh": body.keys.get("p256dh"),
        "auth": body.keys.get("auth"),
    }
    supabase.table("push_subscriptions").upsert(
        record, on_conflict="user_id,endpoint"
    ).execute()
    return {"status": "subscribed"}


@router.delete("/unsubscribe")
async def unsubscribe_push(
    endpoint: str,
    user_id: str = Depends(get_current_user_id),
):
    """Remove a push subscription."""
    supabase.table("push_subscriptions").delete().eq("user_id", user_id).eq(
        "endpoint", endpoint
    ).execute()
    return {"status": "unsubscribed"}


@router.get("/preferences")
async def get_notification_preferences(
    user_id: str = Depends(get_current_user_id),
):
    result = (
        supabase.table("notification_preferences")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else {"daily_jobs": True, "application_reminders": True}


@router.put("/preferences")
async def update_notification_preferences(
    body: dict,
    user_id: str = Depends(get_current_user_id),
):
    body["user_id"] = user_id
    result = (
        supabase.table("notification_preferences")
        .upsert(body, on_conflict="user_id")
        .execute()
    )
    return result.data[0] if result.data else body

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domain.models import User, SyncQueue
from app.application.schemas import SyncPayload, SyncResponse
from app.infrastructure.repositories import SyncQueueRepository
from app.deps import get_current_user
from app.application.exceptions import ValidationException

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/push", response_model=SyncResponse)
async def push_sync(
    data: SyncPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sync_repo = SyncQueueRepository(db)
    synced = 0
    failed = 0
    conflicts = []

    for item in data.items:
        try:
            entity_type = item.get("entity_type")
            entity_id = item.get("entity_id")
            action = item.get("action")
            payload = item.get("payload", {})

            if not entity_type or not action:
                raise ValidationException("entity_type and action are required")

            sync_entry = await sync_repo.create(
                user_id=current_user.id,
                entity_type=entity_type,
                entity_id=entity_id or "",
                action=action,
                payload=payload,
                status="pending",
            )

            synced += 1
        except Exception as e:
            failed += 1
            conflicts.append({"item": item, "error": str(e)})

    await db.commit()

    return SyncResponse(synced=synced, failed=failed, conflicts=conflicts)


@router.get("/pull")
async def pull_sync(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sync_repo = SyncQueueRepository(db)
    pending = await sync_repo.get_pending(current_user.id, limit=100)

    return {
        "items": [
            {
                "id": str(item.id),
                "entity_type": item.entity_type,
                "entity_id": item.entity_id,
                "action": item.action,
                "payload": item.payload,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in pending
        ],
        "count": len(pending),
    }


@router.post("/resolve")
async def resolve_conflict(
    item_id: str,
    resolution: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import uuid
    sync_repo = SyncQueueRepository(db)

    if resolution == "synced":
        await sync_repo.mark_synced(uuid.UUID(item_id))
    elif resolution == "failed":
        await sync_repo.mark_failed(uuid.UUID(item_id), "Conflict resolved as failed")
    else:
        raise ValidationException("Resolution must be 'synced' or 'failed'")

    await db.commit()

    return {"message": f"Conflict resolved: {resolution}"}

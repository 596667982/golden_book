from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import AIConfig
from schemas import AIConfigCreate, AIConfigUpdate, AIConfigOut
from services import ai_service

router = APIRouter(prefix="/api/ai-configs", tags=["ai-configs"])


@router.get("", response_model=list[AIConfigOut])
async def list_configs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIConfig).order_by(AIConfig.id))
    return result.scalars().all()


@router.post("", response_model=AIConfigOut)
async def create_config(data: AIConfigCreate, db: AsyncSession = Depends(get_db)):
    config = AIConfig(**data.model_dump())
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


@router.put("/{config_id}", response_model=AIConfigOut)
async def update_config(config_id: int, data: AIConfigUpdate, db: AsyncSession = Depends(get_db)):
    config = await db.get(AIConfig, config_id)
    if not config:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(config, k, v)
    await db.commit()
    await db.refresh(config)
    return config


@router.delete("/{config_id}")
async def delete_config(config_id: int, db: AsyncSession = Depends(get_db)):
    config = await db.get(AIConfig, config_id)
    if not config:
        raise HTTPException(404, "Not found")
    await db.delete(config)
    await db.commit()
    return {"ok": True}


@router.post("/{config_id}/activate")
async def activate_config(config_id: int, db: AsyncSession = Depends(get_db)):
    # Deactivate all
    all_configs = await db.execute(select(AIConfig))
    for c in all_configs.scalars().all():
        c.is_active = False
    # Activate target
    config = await db.get(AIConfig, config_id)
    if not config:
        raise HTTPException(404, "Not found")
    config.is_active = True
    await db.commit()
    return {"ok": True}


@router.post("/{config_id}/test")
async def test_config(config_id: int, db: AsyncSession = Depends(get_db)):
    config = await db.get(AIConfig, config_id)
    if not config:
        raise HTTPException(404, "Not found")
    return await ai_service.test_connection(config)

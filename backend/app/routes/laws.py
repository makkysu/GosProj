from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.laws_service import LawsService
from app.schemas.category_slug import CategorySlug

laws = APIRouter(prefix='/laws', tags=['laws'])

@laws.get('/')
async def get_laws(category: Optional[CategorySlug] = None, status: Optional[str] = None, search: Optional[str] = None, offset: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    laws_service = LawsService(db)
    return await laws_service.get_laws(category=category.value if category else None, status=status, search=search, offset=offset, limit=limit)

@laws.get('/{rada_id}')
async def get_law_by_id(rada_id: str, db: AsyncSession = Depends(get_db)):
    laws_service = LawsService(db)
    return await laws_service.get_law_by_id(rada_id)

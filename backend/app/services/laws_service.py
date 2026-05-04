from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.laws import Laws
from app.models.categories import Categories
from app.models.law_categories import LawCategories

class LawsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_laws(self, category: Optional[str] = None, status: Optional[str] = None, search: Optional[str] = None, offset: int = 0, limit: int = 50):
        query = select(Laws)
        if search:
            query = query.where(Laws.title.ilike(f'%{search}%'))
        if status:
            query = query.where(Laws.status == status)
        if category:
            query = query.join(LawCategories, Laws.id == LawCategories.law_id)\
                .join(Categories, LawCategories.category_id == Categories.id)\
                .where(Categories.slug == category)
    
        query = query.offset(offset).limit(limit)
    
        result = (await self.db.execute(query)).scalars().all()
        return result

    async def get_law_by_id(self, rada_id: str):
        law = (await self.db.execute(select(Laws).where(Laws.rada_id == rada_id))).scalar_one_or_none()
        return law

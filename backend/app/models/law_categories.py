from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class LawCategories(Base):
    __tablename__ = 'law_categories'

    law_id: Mapped[int] = mapped_column(ForeignKey('laws.id'), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), primary_key=True)

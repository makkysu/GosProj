from sqlalchemy.orm import Mapped, mapped_column
from datetime import date

from app.core.database import Base

class Laws(Base):
    __tablename__ = 'laws'

    id: Mapped[int] = mapped_column(primary_key=True)
    rada_id: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str]
    number: Mapped[str] = mapped_column(nullable=True)
    date_adopted: Mapped[date] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)
    url: Mapped[str]


import datetime

from bot.utils.database import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    TIMESTAMP,
    DateTime,
    ForeignKey,
    Integer,
    Boolean,
    String,
    Text,
    func
)

class TableAssistantModel(Base):
    __tablename__ = "table_assistants"
    table_number: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True
    )
    assistant_id: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True
    )
    sys_prompt: Mapped[str] = mapped_column(Text, nullable=True)

class ThreadModel(Base):
    __tablename__ = "threads"
    user_id: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True
    )
    assistant_id: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=func.now()
    )

class TableModel(Base):
    __tablename__ = "tables"

    user_id: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True, unique=True
    )
    table_number: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True
    )
    username: Mapped[str] = mapped_column(String, nullable=True)

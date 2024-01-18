import datetime

from bot.utils.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Boolean,
    String,
    Text,
    func
)

class TableModel(Base):
    __tablename__ = "tables"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger, index=True, primary_key=True, unique=True
    )
    table_number: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True
    )
    username: Mapped[str] = mapped_column(String, nullable=True)

    threads: Mapped["ThreadModel"] = relationship(back_populates='table')

class TableAssistantModel(Base):
    __tablename__ = "table_assistants"
    
    table_number: Mapped[int] = mapped_column(
        Integer, index=True, primary_key=True
    )
    assistant_id: Mapped[str] = mapped_column(
        String, index=True, nullable=True
    )
    sys_prompt: Mapped[str] = mapped_column(Text)


class ThreadModel(Base):
    __tablename__ = "threads"
 
    # user_id: Mapped[int] = mapped_column(
    #     BigInteger, index=True, primary_key=True
    # )
    thread_id: Mapped[str] = mapped_column(
        String, index=True, primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("tables.user_id"), primary_key=True
    )
    table: Mapped[TableModel] = relationship("TableModel", back_populates="threads")

class UtilModel(Base):
    __tablename__ = "utils"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tables_count: Mapped[int] = mapped_column(Integer, index=True)

import datetime

from bot.utils.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    ForeignKey,
    String,
    Text,
)

class UserModel(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(
        BigInteger, index=True, primary_key=True
    )
    username: Mapped[str] = mapped_column(String, nullable=True)

    assistants: Mapped[list["AssistantModel"]] = relationship(back_populates="user")

class AssistantModel(Base):
    __tablename__ = "assistants"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE")
    )
    assistant_id: Mapped[str] = mapped_column(
        String, index=True, primary_key=True
    )
    sys_prompt: Mapped[str] = mapped_column(Text)

    user: Mapped["UserModel"] = relationship(back_populates="assistants")
    threads: Mapped[list["ThreadModel"]] = relationship(back_populates="assistant")

class ThreadModel(Base):
    __tablename__ = "threads"
    assistant_id: Mapped[str] = mapped_column(
        ForeignKey("assistants.assistant_id", ondelete="CASCADE")
    )
    thread_id: Mapped[str] = mapped_column(
        String, index=True, primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True)
    )
    
    assistant: Mapped["AssistantModel"] = relationship(back_populates="threads")


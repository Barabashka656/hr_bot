from typing import Any, Generic, TypeVar
from bot.handlers.error.exceptions import UserExistException

from bot.utils.database import Base

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

# from .logger import logger
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model = None

    @classmethod
    async def find_one_or_none(
        cls, session: AsyncSession, *filter, **filter_by
    ) -> ModelType | None:
        stmt = select(cls.model).filter(*filter).filter_by(**filter_by)
        return await session.scalar(stmt)

    @classmethod
    async def find_all_with_joinedload_option(
        cls,
        session: AsyncSession,
        load: InstrumentedAttribute,
        *filter,
        offset: int = 0,
        limit: int = 100,
        **filter_by
    ) -> list[ModelType]:
        stmt = (
            select(cls.model)
            .options(joinedload(load))
            .filter(*filter)
            .filter_by(**filter_by)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.mappings().all()

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        *filter,
        offset: int = 0,
        limit: int = 100,
        **filter_by
    ) -> list[ModelType]:
        stmt = (
            select(cls.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @classmethod
    async def add(
        cls,
        session: AsyncSession,
        obj_in: CreateSchemaType | dict[str, Any] | str
    ) -> ModelType | None:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)
        try:
            stmt = insert(cls.model).values(**create_data).returning(cls.model)
            result = await session.execute(stmt)
            return result.scalars().first()
        except IntegrityError as e:
            raise UserExistException()
        except (SQLAlchemyError, Exception) as e:
            return None
        

    @classmethod
    def add_all(cls, session: AsyncSession, data: list):
        objects = [cls.model(**d) for d in data]
        try:
            session.add_all(objects)
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"
            # logger.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            
    @classmethod
    async def delete(cls, session: AsyncSession, *filter, **filter_by) -> None:
        stmt = delete(cls.model).filter(*filter).filter_by(**filter_by)
        await session.execute(stmt)

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        *where,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType | None:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        stmt = (
            update(cls.model)
            .where(*where)
            .values(**update_data)
            .returning(cls.model)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def add_bulk(cls, session: AsyncSession, data: list[dict[str, Any]]):
        try:
            result = await session.execute(insert(cls.model).returning(cls.model), data)
            return result.scalars().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot bulk insert data into table"

            # logger.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None

    @classmethod
    async def update_bulk(cls, session: AsyncSession, data: list[dict[str, Any]]):
        try:
            await session.execute(update(cls.model), data)
        except (SQLAlchemyError, Exception):
            
            return None

    @classmethod
    async def count(cls, session: AsyncSession, *filter, **filter_by):
        stmt = (
            select(func.count())
            .select_from(cls.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await session.execute(stmt)
        return result.scalar()

import base64
import datetime

from bot.handlers.hr.dao import UserDAO
from bot.handlers.hr.schemas import User
from bot.handlers.error.exceptions import UserExistException
from bot.utils.database import async_session_maker

from bot.dao.base import BaseDAO


class UserService:
    @staticmethod
    async def new_user(user_id: int, table_number: int, username: str):
        async with async_session_maker() as session:

            db_user = await UserDAO.add(
                session,
                obj_in=User(
                    user_id=user_id,
                    table_number=table_number,
                    username=username
                )
            )
            await session.commit()
        return db_user

    # @staticmethod
    # async def get_referral_count(user_id: int):
    #     async with async_session_maker() as session:
    #         count = await UserDAO.count(
    #             session,
    #             UserModel.referral_id == user_id,
    #             UserModel.is_verified_referral == True
    #         )
    #         return count

    # @staticmethod
    # async def activate_user(user_id: int):
    #     async with async_session_maker() as session:
    #         moscow_time = UserService.get_current_moscow_time()
    #         await UserDAO.update(
    #             session,
    #             user_id == user_id,
    #             obj_in=User(
    #                 is_active=True,
    #                 last_activate=moscow_time
    #             )
    #         )
    #         await session.commit()

    # @staticmethod
    # async def deactivate_user(user_id: int):
    #     async with async_session_maker() as session:
    #         moscow_time = UserService.get_current_moscow_time()
    #         await UserDAO.update(
    #             session,
    #             UserModel.user_id == user_id,
    #             obj_in=User(
    #                 is_active=False,
    #                 last_deactivate=moscow_time
    #             )
    #         )
    #         await session.commit()
    
    # @staticmethod
    # async def get_balance(user_id: int) -> tuple[int]:
    #     async with async_session_maker() as session:
    #         user: UserModel = await UserDAO.find_one_or_none(session, user_id=user_id)
    #         if user.paid_tokens_balance < 0:
    #             user.paid_tokens_balance = 0
    #             await session.commit()
            
    #         return (user.free_tokens_balance, user.paid_tokens_balance)

    # @staticmethod
    # async def refresh_balance():
    #     async with async_session_maker() as session:
    #         moscow_time = UserService.get_current_moscow_time()
    #         if moscow_time.hour == 0 and moscow_time.minute == 0:
    #             await UserDAO.update(
    #                 session,
    #                 obj_in=User(
    #                     free_tokens_balance=FREE_TOKENS_COUNT
    #                 )
    #             )
    #             await session.commit()

    # @staticmethod
    # def get_current_moscow_time() -> datetime.datetime:
    #     now = datetime.datetime.now()
    #     moscow_timezone = datetime.timezone(datetime.timedelta(hours=3))
    #     return now.astimezone(moscow_timezone)

    # @staticmethod
    # def encode_user_id(user_id: int) -> str:
    #     encrypted_data = user_id ^ SECRET_KEY
    #     encoded_data = (
    #         base64.b64encode(
    #             str(encrypted_data).encode('utf-8')
    #         ).decode('utf-8')
    #     )
    #     bot_nickname = 'unlim_ai_robot'
    #     referral_link = f"https://t.me/{bot_nickname}?start={encoded_data}"
    #     return referral_link

    # @staticmethod
    # def decode_user_id(encoded_data: str):
    #     try:
    #         decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    #     except UnicodeDecodeError:
    #         #return encoded_data
    #         raise InvalidRefException
    #     return int(decoded_data) ^ SECRET_KEY

from bot.dao.base import BaseDAO
from bot.handlers.hr.models import TableModel


class UserDAO(BaseDAO):
    model = TableModel

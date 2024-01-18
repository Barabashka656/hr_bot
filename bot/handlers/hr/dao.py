from bot.dao.base import BaseDAO
from bot.handlers.hr.models import TableAssistantModel, TableModel, ThreadModel, UtilModel


class TableDAO(BaseDAO):
    model = TableModel

class TableAssistantDAO(BaseDAO):
    model = TableAssistantModel
    
class ThreadDAO(BaseDAO):
    model = ThreadModel

class UtilDAO(BaseDAO):
    model = UtilModel
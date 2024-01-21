from bot.dao.base import BaseDAO
from bot.handlers.hr.models import AssistantModel, UserModel, ThreadModel


class UserDAO(BaseDAO):
    model = UserModel

class AssistantDAO(BaseDAO):
    model = AssistantModel
    
class ThreadDAO(BaseDAO):
    model = ThreadModel

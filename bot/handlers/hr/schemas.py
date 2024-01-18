import datetime
from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    table_number: int
    username: str | None
    class Config:
        from_attributes = True

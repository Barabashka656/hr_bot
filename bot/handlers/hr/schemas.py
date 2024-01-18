import datetime
from pydantic import BaseModel


class Table(BaseModel):
    user_id: int
    table_number: int
    username: str | None
    class Config:
        from_attributes = True

class TableAssistant(BaseModel):
    table_number: int | None = None
    assistant_id: str | None = None
    sys_prompt: str | None = None
    class Config:
        from_attributes = True

class ThreadSchema(BaseModel):
    user_id: int | None
    thread_id: str | None
    created_at: datetime.datetime | None
    
    class Config:
        from_attributes = True

class UtilSchema(BaseModel):
    tables_count: int | None
    
    class Config:
        from_attributes = True



import datetime
from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    username: str | None
    class Config:
        from_attributes = True

class Assistant(BaseModel):
    assistant_id: str | None = None
    user_id: int
    sys_prompt: str | None = None
    class Config:
        from_attributes = True

class ThreadSchema(BaseModel):
    assistant_id: str | None
    thread_id: str | None
    created_at: datetime.datetime | None
    
    class Config:
        from_attributes = True

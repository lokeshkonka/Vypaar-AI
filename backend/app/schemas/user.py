from pydantic import BaseModel

class UserInitResponse(BaseModel):
    status: str

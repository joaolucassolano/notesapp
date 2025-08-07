from pydantic import BaseModel
from typing import Optional

class Note(BaseModel):
    title: str
    content: Optional[str] = None
    user_id: int
from typing import Optional

from pydantic import BaseModel


class ModerationResponse(BaseModel):
    status: str
    reason: Optional[str] = None

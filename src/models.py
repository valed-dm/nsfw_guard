from typing import Literal
from typing import Optional

from pydantic import BaseModel


class ModerationResponse(BaseModel):
    status: Literal["OK", "REJECTED"]
    reason: Optional[str] = None


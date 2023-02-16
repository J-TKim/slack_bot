from pydantic import BaseModel


class Challenge(BaseModel):
    type: str
    token: str
    challenge: str

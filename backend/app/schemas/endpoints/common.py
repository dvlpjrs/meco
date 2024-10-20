from pydantic import BaseModel


class JustStatusResponse(BaseModel):
    status: str

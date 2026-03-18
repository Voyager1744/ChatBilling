from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class SussesResponse(BaseModel):
    message: str

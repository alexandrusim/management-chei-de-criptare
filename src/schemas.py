from pydantic import BaseModel

class AlgoritmUpdate(BaseModel):
    nume: str
    tip: str
    dim_cheie: int

    class Config:
        from_attributes = True
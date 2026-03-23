from pydantic import BaseModel
from typing import Optional

class AlgoritmUpdate(BaseModel):
    nume: str
    tip: str
    dim_cheie: int

    class Config:
        from_attributes = True

class FrameworkBase(BaseModel):
    nume: str

class FrameworkCreate(FrameworkBase): pass
class FrameworkUpdate(FrameworkBase): pass

class AlgoritmBase(BaseModel):
    nume: str
    tip: str
    dim_cheie: int

class AlgoritmCreate(AlgoritmBase): pass
class AlgoritmUpdate(AlgoritmBase): pass

class FisierBase(BaseModel):
    nume: str
    extensie: Optional[str] = None
    dimensiune: Optional[int] = None
    path: Optional[str] = None

class FisierCreate(FisierBase): pass
class FisierUpdate(FisierBase): pass

class CheieBase(BaseModel):
    algoritm_id: int
    status: Optional[str] = "Activ"
    val_cheie: Optional[str] = None

class CheieCreate(CheieBase): pass
class CheieUpdate(CheieBase): pass

class PerformantaBase(BaseModel):
    fisier_id: Optional[int] = None
    algoritm_id: Optional[int] = None
    framework_id: Optional[int] = None
    timp: float
    memorie: float
    tip_operatiune: Optional[str] = None

class PerformantaCreate(PerformantaBase): pass
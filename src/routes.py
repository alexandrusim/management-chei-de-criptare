import time, subprocess, os, psutil
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from sql_models import Performanta, Algoritm, Framework, Fisier

router = APIRouter()
BASE_DIR = "files"


def apply_caesar(text: str, shift: int = 3) -> str:
    result = ""
    for char in text:
        if char.isalpha():
            start = ord('a') if char.islower() else ord('A')
            result += chr((ord(char) - start + shift) % 26 + start)
        else:
            result += char
    return result


@router.post("/operatii/criptare-cezar")
def criptare_cezar(nume_fisier: str, shift: int = 3, db: Session = Depends(get_db)):
    cale_in = os.path.join(BASE_DIR, nume_fisier)
    if not os.path.exists(cale_in):
        return {"eroare": "fisierul nu exista!"}

    cale_out = cale_in + ".caesar"

    start_time = time.perf_counter()

    with open(cale_in, 'r') as f:
        continut = f.read()

    criptat = apply_caesar(continut, shift)

    with open(cale_out, 'w') as f:
        f.write(criptat)

    durata = time.perf_counter() - start_time

    noua_perf = Performanta(
        timp=round(durata, 6),
        memorie=0.01,
        tip_operatiune=f"Cezar shift {shift} pe {nume_fisier}",
        algoritm_id=None, framework_id=None, fisier_id=None
    )
    db.add(noua_perf)
    db.commit()

    return {"status": "succes cezar",
            "fisier": cale_out,
            "timp": durata}


@router.get("/istoric-performanta")
def get_stats(db: Session = Depends(get_db)):
    return db.query(Performanta).all()


@router.get("/lista-algoritmi")
def get_alg(db: Session = Depends(get_db)):
    return db.query(Algoritm).all()
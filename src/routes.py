import time, subprocess, os, psutil
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from sql_models import Performanta, Algoritm, Framework, Fisier
from fastapi import HTTPException
from schemas import AlgoritmUpdate


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

    algoritm_cezar = db.query(Algoritm).filter(Algoritm.nume == "Cezar").first()
    if not algoritm_cezar:
        algoritm_cezar = Algoritm(nume="Cezar", tip="Simetric", dim_cheie=0)
        db.add(algoritm_cezar)
        db.commit()
        db.refresh(algoritm_cezar)

    fisier_db = db.query(Fisier).filter(Fisier.nume == nume_fisier).first()
    if not fisier_db:
        dimensiune_fisier = os.path.getsize(cale_in)
        extensie = os.path.splitext(nume_fisier)[1] or ".txt"
        fisier_db = Fisier(nume=nume_fisier, extensie=extensie, dimensiune=dimensiune_fisier, path=cale_in)
        db.add(fisier_db)
        db.commit()
        db.refresh(fisier_db)

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
        algoritm_id=algoritm_cezar.algoritm_id,
        fisier_id=fisier_db.fisier_id,  # <--- ID real
        framework_id=None
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



@router.put("/algoritmi/{algoritm_id}")
def update_algoritm(algoritm_id: int, obj_update: AlgoritmUpdate, db: Session = Depends(get_db)):
    db_alg = db.query(Algoritm).filter(Algoritm.algoritm_id == algoritm_id).first()

    if not db_alg:
        raise HTTPException(status_code=404, detail="algoritmul nu exista :(")

    db_alg.nume = obj_update.nume
    db_alg.tip = obj_update.tip
    db_alg.dim_cheie = obj_update.dim_cheie

    db.commit()
    db.refresh(db_alg)

    return {"status": "actualizat", "date_noi": db_alg}


@router.delete("/istoric-performanta/{perf_id}")
def delete_performanta(perf_id: int, db: Session = Depends(get_db)):
    db_perf = db.query(Performanta).filter(Performanta.performanta_id == perf_id).first()

    if not db_perf:
        raise HTTPException(status_code=404, detail="inregistrarea nu exista :((")

    db.delete(db_perf)
    db.commit()

    return {"status": "succes", "mesaj": f"inregistrarea {perf_id} a fost stearsa"}
import time, os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from sql_models import Performanta, Algoritm, Framework, Fisier, Cheie
from schemas import (AlgoritmCreate, AlgoritmUpdate, FrameworkCreate, FrameworkUpdate,
                     FisierCreate, FisierUpdate, CheieCreate, CheieUpdate, PerformantaCreate)

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


@router.post("/operatii/criptare-cezar", tags=["criptare"], summary="aici criptez un fisier cu Cezar")
def criptare_cezar(nume_fisier: str, shift: int = 3, db: Session = Depends(get_db)):
    cale_in = os.path.join(BASE_DIR, nume_fisier)
    if not os.path.exists(cale_in):
        raise HTTPException(status_code=404, detail="fisieru nu exsta :(")

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
        fisier_id=fisier_db.fisier_id,
        framework_id=None
    )
    db.add(noua_perf)
    db.commit()

    return {"status": "Succes Cezar", "fisier_output": cale_out, "timp_executie": durata}


# ALGORITM
@router.post("/algoritmi", tags=["Algoritm"], summary="Post in tabela algoritm")
def create_algoritm(alg: AlgoritmCreate, db: Session = Depends(get_db)):
    db_alg = Algoritm(**alg.model_dump())
    db.add(db_alg)
    db.commit()
    db.refresh(db_alg)
    return db_alg


@router.get("/algoritmi", tags=["Algoritm"], summary="Get din tabela algoritmi")
def get_algoritmi(db: Session = Depends(get_db)):
    return db.query(Algoritm).all()



@router.put("/algoritmi/{id}", tags=["Algoritm"], summary = "Put la tabela algoritm")
def update_algoritm(id: int, obj_update: AlgoritmUpdate, db: Session = Depends(get_db)):
    db_alg = db.query(Algoritm).filter(Algoritm.algoritm_id == id).first()
    if not db_alg:
        raise HTTPException(status_code=404, detail="alg nu exista")

    db_alg.nume = obj_update.nume
    db_alg.tip = obj_update.tip
    db_alg.dim_cheie = obj_update.dim_cheie

    db.commit()
    db.refresh(db_alg)
    return {"status": "Actualizat", "date_noi": db_alg}


@router.delete("/algoritmi/{id}", tags=["Algoritm"], summary= "delete la tabela Algoritm")
def delete_algoritm(id: int, db: Session = Depends(get_db)):
    db_alg = db.query(Algoritm).filter(Algoritm.algoritm_id == id).first()
    if not db_alg: raise HTTPException(status_code=404, detail="Algoritmul nu exista")
    db.delete(db_alg)
    db.commit()
    return {"status": "Sters", "id": id}


# FRAMEWORK
@router.post("/frameworks", tags=["Framework"], summary = "POST la tabela framework")
def create_framework(fw: FrameworkCreate, db: Session = Depends(get_db)):
    db_fw = Framework(**fw.model_dump())
    db.add(db_fw)
    db.commit()
    db.refresh(db_fw)
    return db_fw


@router.get("/frameworks", tags=["Framework"], summary = "GET din tabela framework")
def get_frameworks(db: Session = Depends(get_db)):
    return db.query(Framework).all()


@router.put("/frameworks/{id}", tags=["Framework"], summary = "PUT in tabela framework")
def update_framework(id: int, fw: FrameworkUpdate, db: Session = Depends(get_db)):
    db_fw = db.query(Framework).filter(Framework.framework_id == id).first()
    if not db_fw: raise HTTPException(status_code=404, detail="Framework-ul nu exista")
    db_fw.nume = fw.nume
    db.commit()
    db.refresh(db_fw)
    return db_fw


@router.delete("/frameworks/{id}", tags=["Framework"], summary = "Delete din tabela framework")
def delete_framework(id: int, db: Session = Depends(get_db)):
    db_fw = db.query(Framework).filter(Framework.framework_id == id).first()
    if not db_fw: raise HTTPException(status_code=404, detail="Framework-ul nu exista")
    db.delete(db_fw)
    db.commit()
    return {"status": "Sters", "id": id}


#  FISIER
@router.post("/fisiere", tags=["Fisier"],summary = "POST in tabela fisier")
def create_fisier(fis: FisierCreate, db: Session = Depends(get_db)):
    db_fis = Fisier(**fis.model_dump())
    db.add(db_fis)
    db.commit()
    db.refresh(db_fis)
    return db_fis


@router.get("/fisiere", tags=["Fisier"], summary = "GET din tabela fisier")
def get_fisiere(db: Session = Depends(get_db)):
    return db.query(Fisier).all()


@router.put("/fisiere/{id}", tags=["Fisier"], summary = "Put in tabela fisier")
def update_fisier(id: int, fis: FisierUpdate, db: Session = Depends(get_db)):
    db_fis = db.query(Fisier).filter(Fisier.fisier_id == id).first()
    if not db_fis: raise HTTPException(status_code=404, detail="Fisierul nu exista")
    for key, value in fis.model_dump(exclude_unset=True).items():
        setattr(db_fis, key, value)
    db.commit()
    db.refresh(db_fis)
    return db_fis


@router.delete("/fisiere/{id}", tags=["Fisier"], summary = "delete din tabela fisier")
def delete_fisier(id: int, db: Session = Depends(get_db)):
    db_fis = db.query(Fisier).filter(Fisier.fisier_id == id).first()
    if not db_fis: raise HTTPException(status_code=404, detail="Fisierul nu exista")
    db.delete(db_fis)
    db.commit()
    return {"status": "Sters", "id": id}


# CHEIE
@router.post("/chei", tags=["Cheie"], summary = "POST in tabela cheie")
def create_cheie(cheie: CheieCreate, db: Session = Depends(get_db)):
    db_cheie = Cheie(**cheie.model_dump())
    db.add(db_cheie)
    db.commit()
    db.refresh(db_cheie)
    return db_cheie


@router.get("/chei", tags=["Cheie"], summary = "Get din tabela cheie")
def get_chei(db: Session = Depends(get_db)):
    return db.query(Cheie).all()


@router.put("/chei/{id}", tags=["Cheie"], summary = "PUT in tabela cheie")
def update_cheie(id: int, cheie: CheieUpdate, db: Session = Depends(get_db)):
    db_cheie = db.query(Cheie).filter(Cheie.cheie_id == id).first()
    if not db_cheie: raise HTTPException(status_code=404, detail="Cheia nu exista")
    for key, value in cheie.model_dump(exclude_unset=True).items():
        setattr(db_cheie, key, value)
    db.commit()
    db.refresh(db_cheie)
    return db_cheie


@router.delete("/chei/{id}", tags=["Cheie"], summary = "delete din tabela cheie")
def delete_cheie(id: int, db: Session = Depends(get_db)):
    db_cheie = db.query(Cheie).filter(Cheie.cheie_id == id).first()
    if not db_cheie: raise HTTPException(status_code=404, detail="Cheia nu exista")
    db.delete(db_cheie)
    db.commit()
    return {"status": "Sters", "id": id}


# PERFORMANTA
@router.post("/performante", tags=["Performanta"], summary = "POST in tabela performanta")
def create_performanta(perf: PerformantaCreate, db: Session = Depends(get_db)):
    db_perf = Performanta(**perf.model_dump())
    db.add(db_perf)
    db.commit()
    db.refresh(db_perf)
    return db_perf


@router.get("/performante", tags=["Performanta"],summary = "Get din tabela performanta")
def get_performante(db: Session = Depends(get_db)):
    return db.query(Performanta).all()



@router.delete("/performante/{id}", tags=["Performanta"],summary = "delete din tabela performanta")
def delete_performanta(id: int, db: Session = Depends(get_db)):
    db_perf = db.query(Performanta).filter(Performanta.performanta_id == id).first()
    if not db_perf: raise HTTPException(status_code=404, detail="Performanta nu exista")
    db.delete(db_perf)
    db.commit()
    return {"status": "Sters", "id": id}
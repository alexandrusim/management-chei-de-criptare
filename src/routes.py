import time, os
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from sql_models import Performanta, Algoritm, Framework, Fisier, Cheie
from schemas import (AlgoritmCreate, AlgoritmUpdate, FrameworkCreate, FrameworkUpdate,
                     FisierCreate, FisierUpdate, CheieCreate, CheieUpdate, PerformantaCreate)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
from cryptography.hazmat.backends import default_backend

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


@router.post("/operatii/criptare-cezar", tags=["criptare"], summary="Cripteaza un fisier cu Cezar")
def criptare_cezar(nume_fisier: str, shift: int = 3, db: Session = Depends(get_db)):
    cale_in = os.path.join(BASE_DIR, nume_fisier)
    if not os.path.exists(cale_in):
        raise HTTPException(status_code=404, detail="Fisierul nu exista")

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


@router.post("/operatii/criptare-aes", tags=["criptare"], summary="Cripteaza un fisier cu AES-256-CBC")
def criptare_aes(fisier_id: int, db: Session = Depends(get_db)):
    fisier_db = db.query(Fisier).filter(Fisier.fisier_id == fisier_id).first()
    if not fisier_db:
        raise HTTPException(status_code=404, detail="Fisierul nu exista in DB")

    cale_in = fisier_db.path
    if not os.path.exists(cale_in):
        raise HTTPException(status_code=404, detail="Fisierul fizic nu a fost gasit")

    cale_out = cale_in + ".enc"

    algoritm_aes = db.query(Algoritm).filter(Algoritm.nume == "AES-256-CBC").first()
    if not algoritm_aes:
        algoritm_aes = Algoritm(nume="AES-256-CBC", tip="Simetric", dim_cheie=256)
        db.add(algoritm_aes)
        db.commit()

    framework_openssl = db.query(Framework).filter(Framework.nume == "OpenSSL").first()
    if not framework_openssl:
        framework_openssl = Framework(nume="OpenSSL")
        db.add(framework_openssl)
        db.commit()

    cheie_bytes = os.urandom(32)
    iv = os.urandom(16)

    cheie_db = Cheie(algoritm_id=algoritm_aes.algoritm_id, val_cheie=cheie_bytes.hex())
    db.add(cheie_db)
    db.commit()
    db.refresh(cheie_db)

    with open(cale_in, 'rb') as f:
        date_clare = f.read()

    hash_sha256 = hashlib.sha256(date_clare).hexdigest()
    start_time = time.perf_counter()

    padder = padding.PKCS7(128).padder()
    date_padded = padder.update(date_clare) + padder.finalize()

    cipher = Cipher(algorithms.AES(cheie_bytes), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    date_criptate = encryptor.update(date_padded) + encryptor.finalize()

    with open(cale_out, 'wb') as f:
        f.write(iv + date_criptate)

    durata = time.perf_counter() - start_time

    fisier_db.hash_original = hash_sha256
    fisier_db.cheie_utilizata_id = cheie_db.cheie_id
    fisier_db.path = cale_out
    db.commit()

    dimensiune_mb = os.path.getsize(cale_out) / (1024 * 1024)
    noua_perf = Performanta(
        timp=round(durata, 6),
        memorie=round(dimensiune_mb, 4),
        tip_operatiune="Criptare AES-256",
        algoritm_id=algoritm_aes.algoritm_id,
        framework_id=framework_openssl.framework_id,
        fisier_id=fisier_db.fisier_id
    )
    db.add(noua_perf)
    db.commit()

    return {
        "status": "Succes",
        "mesaj": "Fisier criptat cu AES",
        "hash_original": hash_sha256,
        "timp_executie_secunde": round(durata, 6)
    }


@router.post("/operatii/decriptare-aes", tags=["decriptare"], summary="Decripteaza AES si verifica Hash")
def decriptare_aes(fisier_id: int, db: Session = Depends(get_db)):
    fisier_db = db.query(Fisier).filter(Fisier.fisier_id == fisier_id).first()
    if not fisier_db or not fisier_db.cheie_utilizata_id:
        raise HTTPException(status_code=400, detail="Fisier invalid sau necriptat")

    cale_in = fisier_db.path
    if not os.path.exists(cale_in):
        raise HTTPException(status_code=404, detail="Fisier fizic lipsa")

    cale_out = cale_in.replace(".enc", ".dec")

    cheie_db = db.query(Cheie).filter(Cheie.cheie_id == fisier_db.cheie_utilizata_id).first()
    cheie_bytes = bytes.fromhex(cheie_db.val_cheie)

    with open(cale_in, 'rb') as f:
        iv = f.read(16)
        date_criptate = f.read()

    start_time = time.perf_counter()

    cipher = Cipher(algorithms.AES(cheie_bytes), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    date_padded = decryptor.update(date_criptate) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    date_clare = unpadder.update(date_padded) + unpadder.finalize()

    durata = time.perf_counter() - start_time

    with open(cale_out, 'wb') as f:
        f.write(date_clare)

    hash_curent = hashlib.sha256(date_clare).hexdigest()
    integritate_ok = (hash_curent == fisier_db.hash_original)

    algoritm_aes = db.query(Algoritm).filter(Algoritm.nume == "AES-256-CBC").first()
    framework_openssl = db.query(Framework).filter(Framework.nume == "OpenSSL").first()

    dimensiune_mb = os.path.getsize(cale_out) / (1024 * 1024)
    noua_perf = Performanta(
        timp=round(durata, 6),
        memorie=round(dimensiune_mb, 4),
        tip_operatiune="Decriptare AES-256",
        algoritm_id=algoritm_aes.algoritm_id if algoritm_aes else None,
        framework_id=framework_openssl.framework_id if framework_openssl else None,
        fisier_id=fisier_db.fisier_id
    )
    db.add(noua_perf)
    db.commit()

    return {
        "status": "Succes",
        "fisier_rezultat": cale_out,
        "integritate_verificata": integritate_ok
    }


@router.post("/operatii/criptare-rsa", tags=["criptare"], summary="Cripteaza un fisier mic cu RSA-2048")
def criptare_rsa(fisier_id: int, db: Session = Depends(get_db)):
    fisier_db = db.query(Fisier).filter(Fisier.fisier_id == fisier_id).first()
    if not fisier_db: raise HTTPException(status_code=404, detail="Fisierul nu exista")

    cale_in = fisier_db.path
    if not os.path.exists(cale_in): raise HTTPException(status_code=404, detail="Fisierul fizic nu a fost gasit")

    dimensiune_fisier = os.path.getsize(cale_in)
    if dimensiune_fisier > 190:
        raise HTTPException(status_code=400, detail="Fisier prea mare pentru RSA (max 190 bytes).")

    cale_out = cale_in + ".rsa_enc"

    algoritm_rsa = db.query(Algoritm).filter(Algoritm.nume == "RSA-2048").first()
    if not algoritm_rsa:
        algoritm_rsa = Algoritm(nume="RSA-2048", tip="Asimetric", dim_cheie=2048)
        db.add(algoritm_rsa)
        db.commit()

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()

    pem_privat = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    cheie_db = Cheie(algoritm_id=algoritm_rsa.algoritm_id, val_cheie=pem_privat.decode('utf-8'))
    db.add(cheie_db)
    db.commit()
    db.refresh(cheie_db)

    with open(cale_in, 'rb') as f:
        date_clare = f.read()

    hash_sha256 = hashlib.sha256(date_clare).hexdigest()
    start_time = time.perf_counter()

    date_criptate = public_key.encrypt(
        date_clare,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    durata = time.perf_counter() - start_time

    with open(cale_out, 'wb') as f:
        f.write(date_criptate)

    fisier_db.hash_original = hash_sha256
    fisier_db.cheie_utilizata_id = cheie_db.cheie_id
    fisier_db.path = cale_out

    framework_openssl = db.query(Framework).filter(Framework.nume == "OpenSSL").first()
    noua_perf = Performanta(
        timp=round(durata, 6),
        memorie=round(len(date_criptate) / (1024 * 1024), 6),
        tip_operatiune="Criptare RSA-2048",
        algoritm_id=algoritm_rsa.algoritm_id,
        framework_id=framework_openssl.framework_id if framework_openssl else None,
        fisier_id=fisier_db.fisier_id
    )
    db.add(noua_perf)
    db.commit()

    return {"status": "Succes", "mesaj": "Criptat cu RSA", "hash_original": hash_sha256}


@router.post("/operatii/decriptare-rsa", tags=["decriptare"], summary="Decripteaza RSA si verifica Hash")
def decriptare_rsa(fisier_id: int, db: Session = Depends(get_db)):
    fisier_db = db.query(Fisier).filter(Fisier.fisier_id == fisier_id).first()
    if not fisier_db or not fisier_db.cheie_utilizata_id:
        raise HTTPException(status_code=400, detail="Fisier invalid sau necriptat")

    cale_in = fisier_db.path
    if not os.path.exists(cale_in): raise HTTPException(status_code=404, detail="Fisier fizic lipsa")

    cale_out = cale_in.replace(".rsa_enc", "_rsa_dec.txt")
    cheie_db = db.query(Cheie).filter(Cheie.cheie_id == fisier_db.cheie_utilizata_id).first()

    private_key = serialization.load_pem_private_key(
        cheie_db.val_cheie.encode('utf-8'),
        password=None,
        backend=default_backend()
    )

    with open(cale_in, 'rb') as f:
        date_criptate = f.read()

    start_time = time.perf_counter()

    date_clare = private_key.decrypt(
        date_criptate,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    durata = time.perf_counter() - start_time

    hash_curent = hashlib.sha256(date_clare).hexdigest()
    integritate_ok = (hash_curent == fisier_db.hash_original)

    with open(cale_out, 'wb') as f:
        f.write(date_clare)

    framework_openssl = db.query(Framework).filter(Framework.nume == "OpenSSL").first()
    noua_perf = Performanta(
        timp=round(durata, 6), memorie=0.001,
        tip_operatiune="Decriptare RSA-2048",
        algoritm_id=cheie_db.algoritm_id,
        framework_id=framework_openssl.framework_id if framework_openssl else None,
        fisier_id=fisier_db.fisier_id
    )
    db.add(noua_perf)
    db.commit()

    return {
        "status": "Succes",
        "fisier_rezultat": cale_out,
        "integritate_verificata": integritate_ok
    }


@router.post("/algoritmi", tags=["Algoritm"], summary="POST in tabela algoritm")
def create_algoritm(alg: AlgoritmCreate, db: Session = Depends(get_db)):
    db_alg = Algoritm(**alg.model_dump())
    db.add(db_alg)
    db.commit()
    db.refresh(db_alg)
    return db_alg


@router.get("/algoritmi", tags=["Algoritm"], summary="GET din tabela algoritmi")
def get_algoritmi(db: Session = Depends(get_db)):
    return db.query(Algoritm).all()


@router.put("/algoritmi/{id}", tags=["Algoritm"], summary="PUT la tabela algoritm")
def update_algoritm(id: int, obj_update: AlgoritmUpdate, db: Session = Depends(get_db)):
    db_alg = db.query(Algoritm).filter(Algoritm.algoritm_id == id).first()
    if not db_alg:
        raise HTTPException(status_code=404, detail="Algoritmul nu exista")

    db_alg.nume = obj_update.nume
    db_alg.tip = obj_update.tip
    db_alg.dim_cheie = obj_update.dim_cheie

    db.commit()
    db.refresh(db_alg)
    return {"status": "Actualizat", "date_noi": db_alg}


@router.delete("/algoritmi/{id}", tags=["Algoritm"], summary="DELETE la tabela Algoritm")
def delete_algoritm(id: int, db: Session = Depends(get_db)):
    db_alg = db.query(Algoritm).filter(Algoritm.algoritm_id == id).first()
    if not db_alg: raise HTTPException(status_code=404, detail="Algoritmul nu exista")
    db.delete(db_alg)
    db.commit()
    return {"status": "Sters", "id": id}


@router.post("/frameworks", tags=["Framework"], summary="POST la tabela framework")
def create_framework(fw: FrameworkCreate, db: Session = Depends(get_db)):
    db_fw = Framework(**fw.model_dump())
    db.add(db_fw)
    db.commit()
    db.refresh(db_fw)
    return db_fw


@router.get("/frameworks", tags=["Framework"], summary="GET din tabela framework")
def get_frameworks(db: Session = Depends(get_db)):
    return db.query(Framework).all()


@router.put("/frameworks/{id}", tags=["Framework"], summary="PUT in tabela framework")
def update_framework(id: int, fw: FrameworkUpdate, db: Session = Depends(get_db)):
    db_fw = db.query(Framework).filter(Framework.framework_id == id).first()
    if not db_fw: raise HTTPException(status_code=404, detail="Framework-ul nu exista")
    db_fw.nume = fw.nume
    db.commit()
    db.refresh(db_fw)
    return db_fw


@router.delete("/frameworks/{id}", tags=["Framework"], summary="DELETE din tabela framework")
def delete_framework(id: int, db: Session = Depends(get_db)):
    db_fw = db.query(Framework).filter(Framework.framework_id == id).first()
    if not db_fw: raise HTTPException(status_code=404, detail="Framework-ul nu exista")
    db.delete(db_fw)
    db.commit()
    return {"status": "Sters", "id": id}


@router.post("/fisiere", tags=["Fisier"], summary="POST in tabela fisier")
def create_fisier(fis: FisierCreate, db: Session = Depends(get_db)):
    db_fis = Fisier(**fis.model_dump())
    db.add(db_fis)
    db.commit()
    db.refresh(db_fis)
    return db_fis


@router.get("/fisiere", tags=["Fisier"], summary="GET din tabela fisier")
def get_fisiere(db: Session = Depends(get_db)):
    return db.query(Fisier).all()


@router.put("/fisiere/{id}", tags=["Fisier"], summary="PUT in tabela fisier")
def update_fisier(id: int, fis: FisierUpdate, db: Session = Depends(get_db)):
    db_fis = db.query(Fisier).filter(Fisier.fisier_id == id).first()
    if not db_fis: raise HTTPException(status_code=404, detail="Fisierul nu exista")
    for key, value in fis.model_dump(exclude_unset=True).items():
        setattr(db_fis, key, value)
    db.commit()
    db.refresh(db_fis)
    return db_fis


@router.delete("/fisiere/{id}", tags=["Fisier"], summary="DELETE din tabela fisier")
def delete_fisier(id: int, db: Session = Depends(get_db)):
    db_fis = db.query(Fisier).filter(Fisier.fisier_id == id).first()
    if not db_fis: raise HTTPException(status_code=404, detail="Fisierul nu exista")
    db.delete(db_fis)
    db.commit()
    return {"status": "Sters", "id": id}


@router.post("/chei", tags=["Cheie"], summary="POST in tabela cheie")
def create_cheie(cheie: CheieCreate, db: Session = Depends(get_db)):
    db_cheie = Cheie(**cheie.model_dump())
    db.add(db_cheie)
    db.commit()
    db.refresh(db_cheie)
    return db_cheie


@router.get("/chei", tags=["Cheie"], summary="GET din tabela cheie")
def get_chei(db: Session = Depends(get_db)):
    return db.query(Cheie).all()


@router.put("/chei/{id}", tags=["Cheie"], summary="PUT in tabela cheie")
def update_cheie(id: int, cheie: CheieUpdate, db: Session = Depends(get_db)):
    db_cheie = db.query(Cheie).filter(Cheie.cheie_id == id).first()
    if not db_cheie: raise HTTPException(status_code=404, detail="Cheia nu exista")
    for key, value in cheie.model_dump(exclude_unset=True).items():
        setattr(db_cheie, key, value)
    db.commit()
    db.refresh(db_cheie)
    return db_cheie


@router.delete("/chei/{id}", tags=["Cheie"], summary="DELETE din tabela cheie")
def delete_cheie(id: int, db: Session = Depends(get_db)):
    db_cheie = db.query(Cheie).filter(Cheie.cheie_id == id).first()
    if not db_cheie: raise HTTPException(status_code=404, detail="Cheia nu exista")
    db.delete(db_cheie)
    db.commit()
    return {"status": "Sters", "id": id}


@router.post("/performante", tags=["Performanta"], summary="POST in tabela performanta")
def create_performanta(perf: PerformantaCreate, db: Session = Depends(get_db)):
    db_perf = Performanta(**perf.model_dump())
    db.add(db_perf)
    db.commit()
    db.refresh(db_perf)
    return db_perf


@router.get("/performante", tags=["Performanta"], summary="GET din tabela performanta")
def get_performante(db: Session = Depends(get_db)):
    return db.query(Performanta).all()


@router.delete("/performante/{id}", tags=["Performanta"], summary="DELETE din tabela performanta")
def delete_performanta(id: int, db: Session = Depends(get_db)):
    db_perf = db.query(Performanta).filter(Performanta.performanta_id == id).first()
    if not db_perf: raise HTTPException(status_code=404, detail="Performanta nu exista")
    db.delete(db_perf)
    db.commit()
    return {"status": "Sters", "id": id}
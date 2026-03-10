from lib2to3.pytree import Base
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, BigInteger, UniqueConstraint, JSON


class Performanta (Base):
    __tablename__ = 'Performanta'

    performanta_id = Column(Integer, primary_key=True)
    timp = Column(Integer, nullable=False)
    memorie = Column(Integer, nullable=False)
    data = Column(Date, nullable=False)
    tip_opertie = Column(String(100), nullable=False)

class Algoritm (Base):
    __tablename__ = 'Algoritmo'

    algoritm_id = Column(Integer, primary_key=True)
    tip = Column(String(100), nullable=False)
    nume = Column(String(100), nullable=False)
    dim_cheie = Column(Integer, nullable=False)
    
class Framework (Base):
    __tablename__ = 'Framework'
    framework_id = Column(Integer, primary_key=True)
    nume = Column(String(100), nullable=False)
    
class Fisier (Base):
    __tablename__ = 'Fisier'
    fisier_id = Column(Integer, primary_key=True)
    nume = Column(String(100), nullable=False)
    extensie = Column(String(10), nullable=False)
    dimensiune = Column(Integer, nullable=False)
    path = Column(String(100), nullable=False)
    
class Cheie (Base):
    __tablename__ = 'Cheie'
    chei_id = Column(Integer, primary_key=True)
    algoritm_id = Column(Integer, ForeignKey('Algoritm.algoritm_id'), nullable=False)
    status = Column(String(20), nullable=False)
    val_cheie = Column(String(100), nullable=False)
    data_creare = Column(Date, nullable=False)
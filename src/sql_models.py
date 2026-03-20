from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Framework(Base):
    __tablename__ = 'Framework'
    framework_id = Column(Integer, primary_key=True, autoincrement=True)
    nume = Column(String(100), nullable=False)
    performante = relationship("Performanta", back_populates="framework")


class Algoritm(Base):
    __tablename__ = 'Algoritm'
    algoritm_id = Column(Integer, primary_key=True, autoincrement=True)
    nume = Column(String(100), nullable=False)
    tip = Column(String(50), nullable=False)
    dim_cheie = Column(Integer, nullable=False)

    performante = relationship("Performanta", back_populates="algoritm")
    chei = relationship("Cheie", back_populates="algoritm")


class Fisier(Base):
    __tablename__ = 'Fisier'
    fisier_id = Column(Integer, primary_key=True, autoincrement=True)
    nume = Column(String(255), nullable=False)
    extensie = Column(String(10))
    dimensiune = Column(BigInteger)
    path = Column(String(255))

    performante = relationship("Performanta", back_populates="fisier")


class Cheie(Base):
    __tablename__ = 'Cheie'
    cheie_id = Column(Integer, primary_key=True, autoincrement=True)
    algoritm_id = Column(Integer, ForeignKey('Algoritm.algoritm_id'), nullable=False)
    status = Column(String(20), default="Activ")
    val_cheie = Column(String(500))
    data_creare = Column(DateTime, default=datetime.utcnow)

    algoritm = relationship("Algoritm", back_populates="chei")


class Performanta(Base):
    __tablename__ = 'Performanta'
    performanta_id = Column(Integer, primary_key=True, autoincrement=True)

    fisier_id = Column(Integer, ForeignKey('Fisier.fisier_id'))
    algoritm_id = Column(Integer, ForeignKey('Algoritm.algoritm_id'))
    framework_id = Column(Integer, ForeignKey('Framework.framework_id'))

    timp = Column(Float, nullable=False)
    memorie = Column(Float, nullable=False)
    tip_operatiune = Column(String(100))
    data = Column(DateTime, default=datetime.utcnow)

    fisier = relationship("Fisier", back_populates="performante")
    algoritm = relationship("Algoritm", back_populates="performante")
    framework = relationship("Framework", back_populates="performante")
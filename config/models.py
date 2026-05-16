from config.database import Base, engine
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase

from typing import List, Optional
from datetime import datetime
 
 ### ORM - Crea todas las tablas y relaciones de la base de datos.
 
class Crew(Base):
    __tablename__ = "Elenco"

    id_elenco: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department: Mapped[Optional[str]]
    job: Mapped[Optional[str]]
    name: Mapped[Optional[str]]

    movie_id: Mapped[int] = mapped_column(ForeignKey("Peliculas.movie_id"))

class Cast(Base):
    __tablename__ = "Actores"

    id_actor: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    character: Mapped[Optional[str]]
    name: Mapped[Optional[str]]

    movie_id: Mapped[int] = mapped_column(ForeignKey("Peliculas.movie_id"))

class Genders(Base):
    __tablename__ = "Generos"

    id_genero: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]]

    movie_id: Mapped[int] = mapped_column(ForeignKey("Peliculas.movie_id"))

class Production_Companies(Base):
    __tablename__ = "Companias"

    id_productora: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company: Mapped[Optional[str]]

    movie_id: Mapped[int] = mapped_column(ForeignKey("Peliculas.movie_id"))

class Production_Countries(Base):
    __tablename__ = "Paises"    

    id_pais_productor: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country: Mapped[Optional[str]]

    movie_id: Mapped[int] = mapped_column(ForeignKey("Peliculas.movie_id"))

class Spoken_Language(Base):
    __tablename__ = "Idiomas"  

    id_idioma: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    language: Mapped[Optional[str]]

    movie_id: Mapped[int] = mapped_column(ForeignKey("Peliculas.movie_id"))

class Machine_Learning(Base):
    __tablename__ = "Indices_ML"  

    id_ml: Mapped[int] = mapped_column(primary_key=True) 
    
    movie_id: Mapped[int] = mapped_column(ForeignKey("Peliculas.movie_id"))

class Movies(Base):
    __tablename__ = "Peliculas"

    budget: Mapped[float]
    movie_id: Mapped[int] = mapped_column(primary_key=True)
    original_language: Mapped[Optional[str]]
    original_title: Mapped[Optional[str]]
    overview: Mapped[Optional[str]]
    popularity: Mapped[float]
    release_date: Mapped[datetime]
    year: Mapped[int]
    month: Mapped[Optional[str]]
    day: Mapped[Optional[str]]
    revenue: Mapped[float]
    runtime: Mapped[float]
    tagline: Mapped[Optional[str]]
    title: Mapped[Optional[str]]
    vote_average: Mapped[float]
    vote_count: Mapped[float]

    elenco: Mapped[List["Crew"]] = relationship()
    actor: Mapped[List["Cast"]] = relationship()
    genero: Mapped[List["Genders"]] = relationship()
    productora: Mapped[List["Production_Companies"]] = relationship()
    pais_productor: Mapped[List["Production_Countries"]] = relationship()
    idioma: Mapped[List["Spoken_Language"]] = relationship()
    ml: Mapped[List["Machine_Learning"]] = relationship()

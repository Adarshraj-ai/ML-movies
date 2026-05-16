import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.session import sessionmaker

db_file = "../database.sqlite" # Directorio donde se creará la DB
directorio = os.path.dirname(os.path.realpath(__file__))
db_url = f"sqlite:///{os.path.join(directorio, db_file)}"

### Creación de la base de datos
engine = create_engine(
    db_url, connect_args={"check_same_thread": False}
    )
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

### Instancia de la base de datos
class Base(DeclarativeBase):
    pass

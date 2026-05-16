import movies.datasets as datasets
import movies.transformaciones as tf
from config.models import Base
from config.database import engine
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import numpy as np

from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine) # Crea la base de datos llamando la instancia BASE del módulo models.
print("Data Base Creation ... OK")

session = Session(engine)

print('Process Iniciated... Please Wait')

### Los datos se transforman en el módulo datasets.

credits, crew, cast = datasets.load_credits()
movies, genders, production_companies, production_countires, spoken_languages = datasets.load_movies()
ml_data = datasets.load_ml_data()

### Realiza la carga de todos los datos ya transformados a la base de datos. 

def load_data():

    movies.to_sql('Peliculas', con=engine, if_exists='append', index=False, chunksize=1000)
    crew.to_sql('Elenco', con=engine, if_exists='append', index=False, chunksize=1000)
    cast.to_sql('Actores', con=engine, if_exists='append', index=False, chunksize=1000)
    genders.to_sql('Generos', con=engine, if_exists='append', index=False, chunksize=1000)
    production_companies.to_sql('Companias', con=engine, if_exists='append', index=False, chunksize=1000)
    production_countires.to_sql('Paises', con=engine, if_exists='append', index=False, chunksize=1000)
    spoken_languages.to_sql('Idiomas', con=engine, if_exists='append', index=False, chunksize=1000)

    print('Data Loading Process ... OK')

### Realiza la carga de los índices del modelo de ML a la base datos y crea el archivo joblib con el modelo. Esta función no retorna nada.

def load_ml_model():
    
    print('Loading Machine Learning Model... Please Wait')

    ml_data['vector'] = ml_data['vector'].apply(tf.raiz_palabra) # Convierte cada palabra a su raíz.
    cv = CountVectorizer(max_features=8000, stop_words='english')
    vectores = cv.fit_transform(ml_data['vector']).toarray().astype(np.float32) # Se asigna formato Float32 para disminuir el uso de memoria sarificando presición.
    cercania = cosine_similarity(vectores)
    print('Tamanio del modelo: ' + str(cercania.shape)) # Imprime el tamaño del modelo para revisar el impacto en memoria.
    joblib.dump(cercania, 'model.joblib') # Crea el archivo joblib donde se almacena el modelo.

    ml_data['id_ml'] = ml_data.index
    ml_data[['id_ml', 'movie_id']].to_sql('Indices_ML', con=engine, if_exists='append', index=False, chunksize=1000) # Carga en la base de datos los índices del modelo de ML.

    print('Machine Learning Data Loading Process ... OK')

session.close()

from ast import literal_eval
import pandas as pd
import movies.transformaciones as tf
import datetime

### Carga de los archivos CSV.
data_movies = pd.read_csv('raw_data/movies_dataset.csv', low_memory=False)
data_credits = pd.read_csv('raw_data/credits.csv')

### Realiza la transformación de credits.csv. Se deanidan los diccionarios y se devuelven como DataFrames independientes.
def load_credits():

    data = data_credits.copy()
    # Se aplica literal_eval para evaluar el Stirng de forma literal.
    data['crew'] = data['crew'].apply(lambda x: literal_eval(x))
    data['cast'] = data['cast'].apply(lambda x: literal_eval(x))
    # Se deanidan los diccionarios y se almacenan como DataFrames independientes.
    crew = tf.desanidar_diccionario(data, 'crew').drop(columns=['credit_id', 'profile_path', 'gender', 'id'])
    cast = tf.desanidar_diccionario(data, 'cast').drop(columns=['credit_id', 'profile_path','cast_id', 'order', 'id', 'gender'])

    return data, crew, cast

### Realiza la transformación de movies_dataset.csv. Se deanidan los diccionarios y se devuelven como DataFrames independientes.
def load_movies():

    data = data_movies.copy()
    
    data.drop_duplicates(inplace=True, subset=['id'])
    data['id'] = tf.convertir_entero(data, 'id')
    data = data[data.id != 0]
    data.dropna(subset=['title', 'production_companies', 'revenue'], inplace=True)

    # Se aplica literal_eval para evaluar el Stirng de forma literal.
    data['genres'] = data['genres'].apply(lambda x: literal_eval(x)) 
    data['production_companies'] = data['production_companies'].apply(lambda x: literal_eval(x)) 
    data['production_countries'] = data['production_countries'].apply(lambda x: literal_eval(x))
    data['spoken_languages'] = data['spoken_languages'].apply(lambda x: literal_eval(x))
    # Se deanidan los diccionarios y se almacenan como DataFrames independientes.
    genders = tf.desanidar_diccionario(data[['genres','id']], 'genres').drop(columns=['id'])
    production_companies = tf.desanidar_diccionario(data[['production_companies','id']], 'production_companies').drop(columns=['id']).rename(columns={'name': 'company'})
    production_countires = tf.desanidar_diccionario(data[['production_countries','id']], 'production_countries').drop(columns=['iso_3166_1']).rename(columns={'name': 'country'})
    spoken_languages = tf.desanidar_diccionario(data[['spoken_languages','id']], 'spoken_languages').drop(columns=['iso_639_1']).rename(columns={'name': 'language'})
   
    data['budget'] = pd.to_numeric(data['budget'])
    data['popularity'] = pd.to_numeric(data['popularity'])

    data['original_language'] = data['original_language'].fillna('')
    data['overview'] = data['overview'].fillna(' ')
    data['release_date'] = data['release_date'].fillna(str(datetime.datetime(1,1,1).date()))
    data['runtime'] = data['runtime'].fillna(0)
    data['tagline'] = data['tagline'].fillna(' ')

    data['day'] = data['release_date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y-%m-%d').weekday() if pd.notna(x) else 0)
    data['year'] = data['release_date'].astype(str).str.extract(r'(\d\d\d\d)', expand=False).astype(int)
    data['month'] = data['release_date'].astype(str).str.extract(r'.[-](\d\d)', expand=False)

    # Mapea los números de mes y día de la semana de acuerdo a los diccionarios correspondientes.
    month_dictionary = {'01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril', '05': 'Mayo',
            '06': 'Junio', '07': 'Julio', '08': 'Agosto', '09': 'Septiembre', '10': 'Octubre', 
            '11': 'Noviembre', '12': 'Diciembre'}
    day_dictionary = {'0': 'Lunes', '1': 'Martes', '2': 'Miercoles', '3': 'Jueves', '4': 'Viernes',
            '5': 'Sabado', '6': 'Domingo'}
    data['month'] = data['month'].apply(lambda x: month_dictionary[x])
    data['day'] = data['day'].apply(lambda x: day_dictionary[str(x)])

    # Elimina las columnas que no son necesarias para el proyecto.
    data = data.drop(columns=['belongs_to_collection','video', 'imdb_id', 'adult', 'poster_path', 
                              'homepage', 'genres', 'production_companies', 'production_countries', 
                              'spoken_languages', 'status']).rename(columns={'id': 'movie_id'})

    return data, genders, production_companies, production_countires, spoken_languages

### Realiza la transformacción de los datasets para devolver un DataFrame con el id de la película y un texto vector que conteniene el resumen, generos, actores y director.
def load_ml_data():

    data = data_movies.copy()

    data = data.dropna(subset=['release_date'])

    # Ajusta el tamaño del modelo, ya que con el dataset completo se requiere más de 16G de ram.
    data = data[data['vote_average'] > 4]
    data = data[data['vote_count'] > 250]

    data = data.drop_duplicates(subset=['id'])
    data['id'] = tf.convertir_entero(data, 'id')
    data= data[data.id != 0]
    data.dropna(subset=['title', 'revenue'], inplace=True)
    data= data.merge(data_credits, on='id')
    data= data[['id', 'title', 'genres', 'overview', 'cast', 'crew', 'tagline']]

    data['crew'] = data['crew'].apply(lambda x: literal_eval(x))
    data['cast'] = data['cast'].apply(lambda x: literal_eval(x))
    data['genres'] = data['genres'].apply(lambda x: literal_eval(x))

    data['crew'] = data['crew'].apply(lambda x: tf.convertir_diccionario(x, data['crew'].name, 'name'))
    data['cast'] = data['cast'].apply(lambda x: tf.convertir_diccionario(x, data['cast'].name, 'name'))
    data['genres'] = data['genres'].apply(lambda x: tf.convertir_diccionario(x, data['genres'].name, 'name'))
    data['crew'] = data['crew'].apply(lambda x: [i.replace(" ","") for i in x])
    data['cast'] = data['cast'].apply(lambda x: [i.replace(" ","") for i in x])
    data['genres'] = data['genres'].apply(lambda x: [i.replace(" ","") for i in x])

    data = data.dropna(subset=['overview'])
    data['tagline'] = data['tagline'].fillna(' ')
    data['overview'] = data['overview'].apply(lambda x: x.split())
    data['tagline'] = data['tagline'].apply(lambda x: x.split())

    data['vector'] = data['overview'] + data['tagline'] + data['genres'] + data['cast'] + data['crew']
    data = data.drop(columns=['overview', 'tagline', 'crew', 'cast', 'genres'])
    data['vector'] = data['vector'].apply(lambda x: " ".join(x))
    data['vector'] = data['vector'].apply(lambda x: x.lower())

    data.rename(columns={'id': 'movie_id'}, inplace=True)

    return data


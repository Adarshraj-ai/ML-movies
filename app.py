from config.models import Crew, Movies, Cast, Machine_Learning
from config.database import engine
from movies.transformaciones import try_or

import joblib
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

print("App is Iniciating...")

session = Session(engine) #Conexión con la base de datos
app = FastAPI(
    title="Movies - Adarsh",
    version="1.0",
    description="Información sobre películas y recomendador.",
) #Instancia de la API

cercania = joblib.load("model.joblib") #Carga el modelo de ML

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

### Rutas de los Endpoints:

# Todos los endpoints realizan consultas a la base de datos mediante el método query de la instancia session.

@app.get('/cantidad_filmaciones_mes/{mes}')
async def cantidad_filmaciones_mes(mes:str):
    ''' Este Endpoint devuelve el número de películas que se estrenaron en un mes específico'''
    res = session.query(Movies).where(Movies.month.ilike(f'{mes}')).count()

    return JSONResponse(status_code = status.HTTP_200_OK, content={'mes': mes, 'cantidad':res})

@app.get('/cantidad_filmaciones_dia/{dia}')
async def cantidad_filmaciones_dia(dia:str):
    '''Este Endpoint devuelve el número de películas estrenadas en un día de la semana específico.'''
    res = session.query(Movies).where(Movies.day.ilike(f'{dia}')).count()
    return JSONResponse(status_code = status.HTTP_200_OK, content={'dia':dia, 'cantidad':res})

@app.get('/score_titulo/{titulo}')
async def score_titulo(titulo: str ):
    '''Este Endpoint devuelve la popularidad de una película consultada.'''
    res  = session.query(Movies).where(Movies.title.ilike(f'{titulo}')).first()
    return JSONResponse(status_code = status.HTTP_200_OK, content={'titulo':titulo, 'anio': res.year, 'popularidad': res.popularity})

@app.get('/votos_titulo/{titulo}')
async def votos_titulo(titulo:str):
    '''Este Endpoitn devuelve la valoración y cantidad de votos de una película consultada siempre y cuando esta tenga al menos 2.000 votos. 
    En caso contrario no devuelve nada.'''
    res  = session.query(Movies).where(Movies.title.ilike(f'{titulo}')).first()

    respuesta_OK = {'Titulo':titulo.title(), 'Anio':res.year, 'Voto_Total':res.vote_count, 'Voto_Promedio':res.vote_average}
    respuesta_ALERT = {'Alerta': 'La pelicula consultada no cuenta con suficientes votos.', 'Info:': {'Titulo':titulo.title(), 'Numero_Votos':res.vote_count} }
    return JSONResponse(status_code = status.HTTP_200_OK, content = respuesta_OK) if res.vote_count >= 2000 else JSONResponse(status_code= status.HTTP_404_NOT_FOUND, content= respuesta_ALERT)

@app.get('/get_actor/{nombre_actor}')
async def get_actor(nombre_actor:str):
    '''Este Endpoint devuelve el éxito de un actor medido a través del retorno (Cuandos dolares genera por cada dolar invertido). 
    Además, devuelve la cantidad de películas que en las que ha participado y el promedio de retorno'''
    actor = session.query(Cast).where(Cast.name.ilike(f'%{nombre_actor}%')).group_by(Cast.name).first()

    list_posibilidades = []
    if actor == None:
        query2 = session.query(Cast).where(Cast.name.ilike(f'%{nombre_actor[:2]}%{nombre_actor[-2:]}%')).group_by(Cast.name).limit(100)
        for row in query2:
            list_posibilidades.append(row.name)
        respuesta_ALERT = {'Error': 'No se encontraron registros, pruebe con alguna de las siguientes opciones', 'Nombres': list_posibilidades}
        
        return JSONResponse(status_code = status.HTTP_404_NOT_FOUND, content = respuesta_ALERT)

    else:
        list_peliculas = []
        ingresos = 0
        contador_peliculas = 0

        query = session.query(Movies, Cast).join(Cast).where(Cast.name == actor.name).order_by(Movies.release_date)
        for row in query:
            ingresos += row[0].revenue
            contador_peliculas += 1
            list_peliculas.append({'Titulo': row[0].title, 'Personaje': row[1].character, 'Anio_Estreno': row[0].year})
        retorno_promedio = try_or(ingresos, contador_peliculas, 0)        
        respuesta_OK = {'Actor':actor.name, 'Cantidad_Filmaciones':contador_peliculas, 'Retorno_Total':ingresos, 'Retorno_Promedio':retorno_promedio, 'Peliculas': list_peliculas}


        return JSONResponse(status_code = status.HTTP_200_OK, content = respuesta_OK)

@app.get('/get_director/{nombre_director}')
async def get_director(nombre_director:str):
    '''Este Endpoint devuelve el éxito de un director medido a través del retorno. (Cuandos dolares genera por cada dolar invertido). 
    Además, devuelve el nombre de cada película que ha realizado, incluyendo la fecha de estreno, el retorno individual, costo y ganancia de la misma.'''
    
    director = session.query(Crew).where(and_(Crew.name.ilike(f'%{nombre_director}%'), Crew.job == 'Director')).group_by(Crew.name).first()

    list_posibilidades = []

    if director == None:
        query2 = session.query(Crew).where(and_(Crew.name.ilike(f'%{nombre_director[:2]}%{nombre_director[-2:]}%'), Crew.job == 'Director')).group_by(Crew.name).limit(100)
        for row in query2:
            list_posibilidades.append(row.name)
        respuesta_ALERT = {'Error': 'No se encontraron registros, pruebe con alguna de las siguientes opciones', 'Nombres': list_posibilidades}
        
        return JSONResponse(status_code = status.HTTP_404_NOT_FOUND, content = respuesta_ALERT)

    else: 
        list_peliculas = []

        query = session.query(Movies, Crew).join(Crew).where(and_(Crew.name == director.name, Crew.job == 'Director')).order_by(Movies.release_date)
        presupuesto = 0
        ingresos = 0
        for row in query:
            presupuesto += row[0].budget
            ingresos += row[0].revenue
            list_peliculas.append({'Titulo': row[0].title, 'Anio_Estreno': row[0].year, 
            'Budget': row[0].budget, 'Revenue': row[0].revenue, 'Retorno': try_or(row[0].revenue, row[0].budget, 0)})
        retorno = try_or(ingresos, presupuesto, 0)
        respuesta_OK = {'Director': director.name,'Retorno_Total_Generado': retorno,'Peliculas': list_peliculas}  

        return JSONResponse(status_code = status.HTTP_200_OK, content = respuesta_OK)

@app.get('/movie_details/{movie_id}')
async def movie_details(movie_id: int):
    '''Este Endpoint devuelve los detalles completos de una película por su ID.'''
    movie = session.query(Movies).filter(Movies.movie_id == movie_id).first()
    if not movie:
        return JSONResponse(status_code=404, content={'error': 'Movie not found'})
    
    genres = session.query(Genders).filter(Genders.movie_id == movie_id).all()
    cast = session.query(Cast).filter(Cast.movie_id == movie_id).limit(10).all()
    crew = session.query(Crew).filter(Crew.movie_id == movie_id).all()
    
    # Get director
    director = "Unknown"
    for member in crew:
        if member.job == 'Director':
            director = member.name
            break

    details = {
        'Pelicula': movie.title,
        'Resumen': movie.overview,
        'Votos': movie.vote_average,
        'Estreno': movie.release_date.strftime('%Y-%m-%d') if movie.release_date else str(movie.year),
        'Duracion': f"{int(movie.runtime)} min" if movie.runtime else "Unknown",
        'Tagline': movie.tagline,
        'Generos': [g.name for g in genres],
        'Director': director,
        'Actores': [{'Nombre': a.name, 'Personaje': a.character} for a in cast],
        'ID': movie.movie_id
    }
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=details)

@app.get('/popular_movies')
async def popular_movies():
    '''Este Endpoint devuelve las 20 películas más populares.'''
    res = session.query(Movies).order_by(Movies.popularity.desc()).limit(20).all()
    
    list_movies = []
    for movie in res:
        # Intenta obtener el director para cada película popular
        crew = session.query(Crew).where(and_(Crew.movie_id == movie.movie_id, Crew.job == 'Director')).first()
        director = crew.name if crew else "Unknown"
        list_movies.append({
            'Pelicula': movie.title,
            'Director': director,
            'Estreno': movie.year,
            'Resumen': movie.overview,
            'Popularidad': movie.popularity,
            'Votos': movie.vote_average,
            'ID': movie.movie_id
        })
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=list_movies)

# Machine Learning - Recomencaiones de películas
@app.get('/recomendacion/{titulo}')
async def recomendacion(titulo:str):
    '''Este Endpoint genera una lista de películas recomendadas a partir del título de una película.'''

    indice_consulta = session.query(Movies, Machine_Learning).join(Machine_Learning).where(Movies.title.ilike(f'{titulo}')).first()

    if indice_consulta == None:

        return {'Error': 'No se encontró la película consultada.'}
    
    else: #Busca en el modelo ML.
        recomendaciones = sorted(list(enumerate(cercania[indice_consulta[1].id_ml])), reverse = True, key = lambda x:x[1])[1:16]

        # Itera sobre la lísta de recomendaciones, devolviendo el resultado por cada indice consultado.
        list_recomendaciones = [] 
        for index in recomendaciones:
            movie = session.query(Movies, Machine_Learning).join(Machine_Learning).where(Machine_Learning.id_ml == index[0]).first()
            crew = session.query(Movies, Crew).join(Crew).where(and_(Movies.movie_id == movie[0].movie_id, Crew.job == 'Director')).first()

            list_recomendaciones.append({'Pelicula': movie[0].title, 'Director': crew[1].name, 'Estreno': movie[0].year, 'Resumen': movie[0].overview, 'ID': movie[0].movie_id})

        return JSONResponse(status_code = status.HTTP_200_OK, content = {'Pelicula consultada': indice_consulta[0].title + ' - ' + str(indice_consulta[0].year),'lista recomendada': list_recomendaciones})

if __name__ == '__main__':
    uvicorn.run(app, port=8000)
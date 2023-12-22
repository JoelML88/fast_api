from fastapi import APIRouter, Path, Query,Depends
from fastapi.responses import JSONResponse
from config.database import Session
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middlewares.JWTBearer import JWTBearer
from typing import List
from services.movie import MovieService
from schemas.movie import Movie

movie_router = APIRouter()



#, dependencies=[Depends(JWTBearer())]
@movie_router.get('/movies', tags=['movies'], response_model = List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies()->List[Movie]:
    db = Session()
    result = MovieService(db).get_movies()
    return JSONResponse(status_code=200,content = jsonable_encoder(result))


@movie_router.get('/movie/{id}', tags=['movies'],  response_model = Movie, status_code=200)
def get_movie(id:int = Path(ge=1,le=2000)) -> Movie:
    
    db =  Session()
    result = MovieService(db).get_movie(id)
    #movie = list(filter(lambda x: x['id'] == id,movies))
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    return JSONResponse(status_code=200,content = jsonable_encoder({result}))


    
@movie_router.get('/movies/', tags=['movies'], response_model = List[Movie], status_code=200)
def get_movies_by_category(category:str = Query(min_length=2, max_length=20))->List[Movie]:
    
    db = Session()
    result = MovieService(db).get_movies_by_category(category)    
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    
    #data = [item for item in movies if item['category'] == category]
    return JSONResponse(status_code=200,content= jsonable_encoder(result))

@movie_router.post('/movies/', tags=['movies'], response_model=dict, status_code = 201)
def create_movie(movie: Movie) -> dict:
    db = Session()
    MovieService(db).creat_movie(movie)
    return JSONResponse(status_code = 201,content={"message":"Se registró correctamente"})

@movie_router.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def update_movie(id:int, movie:Movie) -> dict:
    
    db= Session()
    result = MovieService(db).get_movie(id)
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    
    MovieService(db).update_movie(id,movie)
            
    return JSONResponse(status_code=200,content= {'message': "Actualizado correctamente"})

@movie_router.delete('/movie/{id}', tags=['movies'], response_model=dict, status_code=200)
def delete_movie(id:int) -> dict:
    # Eliminar elementos con 'id' dado
    db= Session()
    result = MovieService(db).get_movie(id)
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    MovieService(db).delete_movie(id)
    
    return JSONResponse(status_code=200,content= {'message': "Eliminado correctamente"})
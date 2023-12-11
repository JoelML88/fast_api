from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
app.title = "Mi app de prueba con FastAPI"
app.version = "0.0.1"

movies = [
    {
        "id":1,
        "title": "Avatar",
        "Overview": "monos azules peleando",
        "year": 2009,
        "rating": 7.8,
        "category": "Accion",

    },
    {
        "id":2,
        "title": "XXX",
        "Overview": "monos",
        "year": 20015,
        "rating": 9.8,
        "category": "Por",
    },
    {
        "id":2,
        "title": "YYY",
        "Overview": "monos",
        "year": 20015,
        "rating": 9.8,
        "category": "Por",
    }
]


@app.get('/', tags=["home"])

def message():
    return HTMLResponse('<h1>Hey prro</h1>')

@app.get('/movies', tags=['movies'])
def get_movies():
    return movies


@app.get('/movie/{id}', tags=['movies'])
def get_movie(id:int):
    movie = list(filter(lambda x: x['id'] == id,movies))
    return movie if len(movie) > 0 else "No hay nada que ver"
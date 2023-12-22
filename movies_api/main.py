from fastapi import FastAPI,Body, UploadFile, File, Path, Query,Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from jwt_manager import create_token, validate_token

from config.database import Session,engine,Base
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middlewares.error_handler import ErrorHandler
from middlewares.JWTBearer import JWTBearer


from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime
import shutil
import os
import nistitl
from typing import IO
import base64
from PIL import Image
import wsq

app = FastAPI()
app.title = "Mi app de prueba con FastAPI"
app.version = "0.0.1"

app.add_middleware(ErrorHandler)

Base.metadata.create_all(bind= engine)

UPLOADS_DIR = "./uploads/"

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

class User(BaseModel):
    email:str
    password:str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=datetime.now().year)
    rating: float = Field(ge=1,le=10)
    category: str = Field(min_length=5, max_length=15)
    
    model_config = {
     "json_schema_extra": {
            "examples": [
                {
                "id":1,
                "title":"My movie",
                "overview": "My overview For the movie",
                "year":datetime.now().year,
                "rating":10.0,
                "category":"None none"
                }
            ]
        }
    }


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
        "year": 2015,
        "rating": 9.8,
        "category": "Por",
    },
    {
        "id":3,
        "title": "YYY",
        "Overview": "monos",
        "year": 2015,
        "rating": 9.8,
        "category": "Por",
    }
]


@app.get('/', tags=["home"])

@app.post('/login', tags=["auth"])
def login(user:User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())        
    return JSONResponse(status_code=200, content=token)

def message():
    return HTMLResponse('<h1>Hey prro</h1>')

@app.get('/movies', tags=['movies'], response_model = List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies()->List[Movie]:
    db = Session()
    result = db.query(MovieModel).all()
    return JSONResponse(status_code=200,content = jsonable_encoder(result))


@app.get('/movie/{id}', tags=['movies'],  response_model = Movie, status_code=200)
def get_movie(id:int = Path(ge=1,le=2000)) -> Movie:
    
    db =  Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()    
    #movie = list(filter(lambda x: x['id'] == id,movies))
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    return JSONResponse(status_code=200,content = jsonable_encoder({result}))


    
@app.get('/movies/', tags=['movies'], response_model = List[Movie], status_code=200)
def get_movies_by_category(category:str = Query(min_length=2, max_length=20))->List[Movie]:
    
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category).all()
    
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    
    #data = [item for item in movies if item['category'] == category]
    return JSONResponse(status_code=200,content= jsonable_encoder(result))

@app.post('/movies/', tags=['movies'], response_model=dict, status_code = 201)
def create_movie(movie: Movie) -> dict:
    db = Session()
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    movies.append(movie)
    return JSONResponse(status_code = 201,content={"message":"Se registró correctamente"})

@app.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def update_movie(id:int, movie:Movie) -> dict:
    
    db= Session()
    result = db.query(MovieModel).filter(MovieModel.id==id).first()
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    
    result.title = movie.title
    result.overview = movie.overview
    result.year = movie.year
    result.rating = movie.rating
    result.category = movie.category
    db.commit()
            
    return JSONResponse(status_code=200,content= {'message': "Actualizado correctamente"})

@app.delete('/movie/{id}', tags=['movies'], response_model=dict, status_code=200)
def delete_movie(id:int) -> dict:
    # Eliminar elementos con 'id' dado
    db= Session()
    result = db.query(MovieModel).filter(MovieModel.id==id).first()
    if not result:
        return JSONResponse(status_code=404, content={'message': "No encontrado"})
    db.delete(result)
    db.commit()
    
    return JSONResponse(status_code=200,content= {'message': "Eliminado correctamente"})

@app.post("/uploadNIST/")
async def upload_nist(file: UploadFile = File(...)):
    with open(f"{UPLOADS_DIR}{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
     # Llama a la función de desempaquetado después de guardar el archivo
    desempaquetar_archivo(UPLOADS_DIR+"/"+file.filename)
    return {"filename": file.filename}


def desempaquetar_archivo(file_path):
    
    with open(file_path, "rb") as file:
        buffer_data = file.read()
    
    msg = nistitl.Message()
    msg.parse(buffer_data)
    
      # --- Access type 1 record
    for record in msg.iter(1):
        print("Type1 content:\n",record)


    # --- Access type 2 record
    for record in msg.iter(2):
        print("Type2 content:\n",record)

    # --- Loop on all records of type 4
    i=0
    for r4 in msg.iter(4):
        
        i=i+1
        
        # Get all fields
        all_fields = r4.unpack("!BBBBBBBBHHB")
        imp = all_fields[0]
        fgp = list(all_fields[1:7])
        isr = all_fields[7]
        width = all_fields[8]
        height = all_fields[9]
        gca = all_fields[10]
        image = all_fields[11]        
        file_exists(UPLOADS_DIR+str(i)+".wsq")
        save_file_bytes(UPLOADS_DIR+str(i)+".wsq",image)
        
        img = Image.open(UPLOADS_DIR+str(i)+".wsq")   
        img = img.convert("1") 
        img.save(UPLOADS_DIR+str(i)+".bmp")
        #file.close()
        
        print(img)
        

    # --- Loop on all records of type 10
    i=0
    for r10 in msg.iter(10):
        i=i+1
        # Used pre-defined alias
        src = r10.SRC
        image = r10.DATA
        file_exists(UPLOADS_DIR+str(i)+".jpeg")
        save_file_bytes(UPLOADS_DIR+str(i)+".jpeg",image)
    
    print("Done")
    
def file_exists(file_path: str, default_content: str = None):
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            if default_content:
                file.write(default_content)
            print(f"El archivo '{file_path}' ha sido creado.")
        return True
    else:
        print(f"El archivo '{file_path}' ya existe.")
        return False
    
def save_file_bytes(file_path: str, bytes_data: bytes):
    with open(file_path, "wb") as file:
        file.write(bytes_data)
    #b64_string = base64.b64encode(bytes_data).decode('utf-8')
    #print(b64_string)
    print(file_path)  # Solo imprime los datos por ahora, ajusta según lo que necesites hacer con ellos
 